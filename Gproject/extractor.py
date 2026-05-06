import re
import os
import pdfplumber
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from pdf2image import convert_from_path
from dotenv import load_dotenv

load_dotenv()

_tesseract_cmd = os.getenv("TESSERACT_CMD")
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd


# ── Language Detection ────────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    """Detect Arabic vs English by counting Arabic Unicode characters."""
    if not text:
        return "english"
    arabic_chars = sum(1 for c in text if "؀" <= c <= "ۿ")
    return "arabic" if arabic_chars > max(10, len(text) * 0.15) else "english"


# ── Image Pre-processing ─────────────────────────────────────────────────────

def preprocess_image(image: Image.Image) -> Image.Image:
    """Enhance image quality for better Tesseract accuracy."""
    image = image.convert("L")                          # grayscale
    image = ImageEnhance.Contrast(image).enhance(2.0)  # boost contrast
    image = image.filter(ImageFilter.SHARPEN)           # sharpen edges
    return image


# ── Text Extraction ──────────────────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> tuple:
    """
    Step 1: Try pdfplumber (fast path for digital PDFs).
    Step 2: Fall back to pdf2image + Tesseract OCR for scanned PDFs.
    Returns (full_text, lines, ocr_used).
    """
    lines = []

    # Fast path: digital PDF
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines.extend(text.split("\n"))
    except Exception:
        pass

    if lines:
        return "\n".join(lines), lines, False

    # Fallback: OCR for scanned PDFs
    try:
        images = convert_from_path(file_path, dpi=300)
        for img in images:
            processed = preprocess_image(img)
            ocr_text = pytesseract.image_to_string(processed, lang="ara+eng")
            if ocr_text:
                lines.extend(ocr_text.split("\n"))
    except Exception as e:
        print(f"OCR fallback error: {e}")

    return "\n".join(lines), lines, True


# ── English Field Extraction ─────────────────────────────────────────────────

def extract_english_fields(full_text: str, lines: list) -> dict:
    result = {
        "Vendor Name": None,
        "Invoice Number": None,
        "Shipment Date": None,
        "Total Amount": None,
    }

    # Invoice number: INV-YYYY-XXXX pattern
    inv_match = re.search(r"INV-\d{4}-\d{4}", full_text)
    if inv_match:
        result["Invoice Number"] = inv_match.group(0)

    # Shipment date: prefer a line containing "date", otherwise first YYYY-MM-DD
    for line in lines:
        if re.search(r"(shipment|invoice|date)\s*[:\-]", line, re.IGNORECASE):
            date_match = re.search(
                r"\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}", line
            )
            if date_match:
                result["Shipment Date"] = date_match.group(0)
                break

    if not result["Shipment Date"]:
        # Fallback: first standalone date not inside the invoice number
        date_match = re.search(r"(?<!INV-\d{4}-)(\d{4}-\d{2}-\d{2})", full_text)
        if date_match:
            result["Shipment Date"] = date_match.group(1)

    # Vendor name: label-based extraction
    for line in lines:
        if "Bill To (Vendor):" in line:
            vendor_part = line.split("Bill To (Vendor):")[-1].strip()
            if vendor_part:
                result["Vendor Name"] = vendor_part
                break
        elif re.search(r"vendor\s*[:\-]", line, re.IGNORECASE):
            vendor_part = re.split(r"vendor\s*[:\-]", line, flags=re.IGNORECASE)[-1].strip()
            if vendor_part:
                result["Vendor Name"] = vendor_part
                break

    # Total amount: Grand Total / Total line
    for line in lines:
        if re.search(r"grand\s*total|total\s*amount", line, re.IGNORECASE):
            total_match = re.search(r"(\d[\d,]*\.\d{2})", line)
            if total_match:
                result["Total Amount"] = total_match.group(1)
                break

    return result


# ── Arabic Field Extraction ──────────────────────────────────────────────────

def extract_arabic_fields(full_text: str, lines: list) -> dict:
    result = {
        "Vendor Name": None,
        "Invoice Number": None,
        "Shipment Date": None,
        "Total Amount": None,
    }

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Invoice number — رقم الفاتورة
        if any(kw in line for kw in ["رقم الفاتورة", "رقم الفاتوره", "رقم فاتورة"]):
            after = line.split(":")[-1].strip()
            num = re.search(r"[\w\-]+\d[\w\-]*", after)
            if num:
                result["Invoice Number"] = num.group(0)
            else:
                inv_match = re.search(r"INV-\d{4}-\d{4}|\d{4,}", line)
                if inv_match:
                    result["Invoice Number"] = inv_match.group(0)

        # Vendor name — اسم المورد / البائع / المورد
        if any(kw in line for kw in ["اسم المورد", "البائع", "المورد", "اسم البائع"]):
            after = line.split(":")[-1].strip()
            if after:
                result["Vendor Name"] = after

        # Shipment / invoice date — تاريخ
        if "تاريخ" in line:
            date_match = re.search(
                r"\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}", line
            )
            if date_match and not result["Shipment Date"]:
                result["Shipment Date"] = date_match.group(0)

        # Total amount — الإجمالي / المبلغ / المجموع
        if any(kw in line for kw in ["الإجمالي", "المبلغ الإجمالي", "المجموع", "إجمالي"]):
            total_match = re.search(r"(\d[\d,]*\.\d{2})", line)
            if total_match:
                result["Total Amount"] = total_match.group(1)

    # Fallback: try English patterns on bilingual docs
    if not result["Invoice Number"]:
        inv_match = re.search(r"INV-\d{4}-\d{4}", full_text)
        if inv_match:
            result["Invoice Number"] = inv_match.group(0)

    if not result["Shipment Date"]:
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", full_text)
        if date_match:
            result["Shipment Date"] = date_match.group(0)

    return result


# ── Confidence Score ─────────────────────────────────────────────────────────

def calculate_confidence(fields: dict) -> str:
    filled = sum(
        1 for k, v in fields.items()
        if k not in ("confidence_score", "language") and v is not None
    )
    if filled == 4:
        return "High"
    elif filled >= 2:
        return "Medium"
    return "Low"


# ── Main Entry Point ─────────────────────────────────────────────────────────

def extract_invoice_data(file_path: str) -> dict:
    full_text, lines, ocr_used = extract_text_from_pdf(file_path)

    if not full_text.strip():
        return {
            "Vendor Name": None,
            "Invoice Number": None,
            "Shipment Date": None,
            "Total Amount": None,
            "confidence_score": "Low",
            "language": "unknown",
        }

    language = detect_language(full_text)

    if language == "arabic":
        fields = extract_arabic_fields(full_text, lines)
    else:
        fields = extract_english_fields(full_text, lines)

    fields["confidence_score"] = calculate_confidence(fields)
    fields["language"] = language

    return fields
