"""Sprint 4 — Extractor unit tests."""
import extractor


def test_language_detection_english():
    sample = "Invoice Number: INV-2026-1001\nTotal Amount: 1500.00"
    assert extractor.detect_language(sample) == "english"


def test_language_detection_arabic():
    sample = "رقم الفاتورة: INV-2026-1001\nالمبلغ الإجمالي: 1500.00 ريال سعودي"
    assert extractor.detect_language(sample) == "arabic"


def test_english_field_extraction():
    full_text = (
        "Commercial Invoice\n"
        "Invoice Number: INV-2026-1001\n"
        "Shipment Date: 2026-04-29\n"
        "Bill To (Vendor): Arabian Freight Solutions Co.\n"
        "Grand Total: 12391.25\n"
    )
    lines = full_text.split("\n")
    fields = extractor.extract_english_fields(full_text, lines)
    assert fields["Invoice Number"] == "INV-2026-1001"
    assert fields["Shipment Date"] == "2026-04-29"
    assert "Arabian Freight Solutions" in fields["Vendor Name"]
    assert fields["Total Amount"] == "12391.25"


def test_arabic_field_extraction():
    full_text = (
        "فاتورة تجارية\n"
        "رقم الفاتورة: INV-2026-2001\n"
        "تاريخ الشحنة: 2026-04-29\n"
        "اسم المورد: شركة الفجر للنقل\n"
        "الإجمالي: 12391.25\n"
    )
    lines = full_text.split("\n")
    fields = extractor.extract_arabic_fields(full_text, lines)
    assert fields["Invoice Number"] == "INV-2026-2001"
    assert fields["Shipment Date"] == "2026-04-29"
    assert "الفجر" in (fields["Vendor Name"] or "")
    assert fields["Total Amount"] == "12391.25"


def test_confidence_levels():
    assert extractor.calculate_confidence({
        "Vendor Name": "x", "Invoice Number": "x",
        "Shipment Date": "x", "Total Amount": "x",
    }) == "High"
    assert extractor.calculate_confidence({
        "Vendor Name": "x", "Invoice Number": "x",
        "Shipment Date": None, "Total Amount": None,
    }) == "Medium"
    assert extractor.calculate_confidence({
        "Vendor Name": None, "Invoice Number": None,
        "Shipment Date": None, "Total Amount": None,
    }) == "Low"


# Sprint 4 — Per-field confidence (US2 "low-confidence flagging")
def test_per_field_confidence_well_formed_inputs():
    conf = extractor.per_field_confidence({
        "Vendor Name": "Arabian Freight Solutions Co.",
        "Invoice Number": "INV-2026-1001",
        "Shipment Date": "2026-04-29",
        "Total Amount": "1500.00",
    }, ocr_used=False)
    assert conf["Vendor Name"] == "High"
    assert conf["Invoice Number"] == "High"
    assert conf["Shipment Date"] == "High"
    assert conf["Total Amount"] == "High"


def test_per_field_confidence_flags_missing_and_malformed():
    conf = extractor.per_field_confidence({
        "Vendor Name": None,
        "Invoice Number": "9999",            # wrong format → Medium
        "Shipment Date": "29/04/2026",       # alt format → Medium
        "Total Amount": "1500",              # no decimals → Medium
    }, ocr_used=True)
    assert conf["Vendor Name"] == "Missing"
    assert conf["Invoice Number"] == "Medium"
    assert conf["Shipment Date"] == "Medium"
    assert conf["Total Amount"] == "Medium"
