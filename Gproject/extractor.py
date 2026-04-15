import re
import pdfplumber

def extract_invoice_data(file_path: str) -> dict:
    # 1. هيكلة المخرجات ككائن JSON
    extracted_data = {
        "Vendor Name": None,
        "Invoice Number": None,
        "Shipment Date": None,
        "Total Amount": None
    }

    try:
        # 2. قراءة النص سطرًا بسطر لتسهيل البحث
        lines = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # تقسيم النص إلى أسطر
                    lines.extend(text.split('\n'))
                    
        # ضم الأسطر في نص واحد لتسهيل بحث الأنماط العامة
        full_text = "\n".join(lines)

        # 3. مطابقة الأنماط (Pattern-matching) واستخراج الحقول

        # استخراج رقم الفاتورة (نمط: INV-YYYY-XXXX)
        inv_match = re.search(r'INV-\d{4}-\d{4}', full_text)
        if inv_match:
            extracted_data["Invoice Number"] = inv_match.group(0)

        # استخراج تاريخ الشحنة (نمط: YYYY-MM-DD)
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', full_text)
        if date_match:
            extracted_data["Shipment Date"] = date_match.group(0)

        # استخراج اسم المورد (Vendor)
        for line in lines:
            if "Bill To (Vendor):" in line:
                # نأخذ النص الذي يظهر بعد هذه العبارة مباشرة
                vendor_part = line.split("Bill To (Vendor):")[-1].strip()
                if vendor_part:
                     extracted_data["Vendor Name"] = vendor_part
                     break
                     
        # استخراج المبلغ الإجمالي (Total Amount)
        for line in lines:
            if "Grand Total:" in line:
                # نبحث عن الرقم الذي يحتوي على فاصلة عشرية في نفس سطر الإجمالي
                total_match = re.search(r'(\d+\.\d{2})', line)
                if total_match:
                    extracted_data["Total Amount"] = total_match.group(1)
                    break

    except Exception as e:
        print(f"Error reading document: {str(e)}")

    return extracted_data