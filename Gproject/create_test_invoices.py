"""
Run once to generate test invoice PDFs for the LogiFlow demo.
Usage: python create_test_invoices.py
"""

def make_pdf(filename, lines):
    """Build a minimal but valid PDF from a list of text lines. No dependencies needed."""

    # Build the PDF content stream (text drawing commands)
    ops = ["BT", "/F1 11 Tf"]
    for i, line in enumerate(lines):
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        y = 800 - i * 20
        if y < 40:
            break
        ops.append(f"1 0 0 1 50 {y} Tm")
        ops.append(f"({escaped}) Tj")
    ops.append("ET")

    stream = "\n".join(ops).encode("latin-1", errors="replace")
    stream_len = len(stream)

    offsets = {}
    pdf = bytearray()

    def w(data):
        if isinstance(data, str):
            data = data.encode("latin-1", errors="replace")
        pdf.extend(data)

    def obj(n, content):
        offsets[n] = len(pdf)
        w(f"{n} 0 obj\n")
        w(content if isinstance(content, bytes) else content.encode())
        w("\nendobj\n")

    w("%PDF-1.4\n")
    obj(1, b"<</Type/Catalog/Pages 2 0 R>>")
    obj(2, b"<</Type/Pages/Kids[3 0 R]/Count 1>>")
    obj(3, b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>")

    offsets[4] = len(pdf)
    w(f"4 0 obj\n<</Length {stream_len}>>\nstream\n")
    pdf.extend(stream)
    w("\nendstream\nendobj\n")

    obj(5, b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>")

    xref_pos = len(pdf)
    w("xref\n0 6\n")
    w("0000000000 65535 f \n")
    for i in range(1, 6):
        w(f"{offsets[i]:010d} 00000 n \n")
    w(f"trailer\n<</Size 6/Root 1 0 R>>\nstartxref\n{xref_pos}\n%%EOF\n")

    with open(filename, "wb") as f:
        f.write(bytes(pdf))
    print(f"  Created: {filename}")


# ── Invoice 1 ─────────────────────────────────────────────────────────────────

invoice_1 = [
    "================================================",
    "          COMMERCIAL INVOICE",
    "================================================",
    "",
    "LogiFlow Freight & Logistics Services",
    "Riyadh, Saudi Arabia | Tel: +966-11-000-0001",
    "www.logiflow-sa.com",
    "",
    "------------------------------------------------",
    "Invoice Number:  INV-2026-9001",
    "Invoice Date:    2026-04-29",
    "Shipment Date:   2026-04-29",
    "------------------------------------------------",
    "",
    "Bill To (Vendor): Arabian Freight Solutions Co.",
    "Address: King Fahd Road, Riyadh 12345, KSA",
    "",
    "------------------------------------------------",
    "ITEM                           QTY   UNIT    AMOUNT",
    "------------------------------------------------",
    "Sea Freight - Container 20ft    1   8500.00  8500.00",
    "Port Handling Charges           1   1200.00  1200.00",
    "Documentation & Customs Fee     1    350.00   350.00",
    "Cargo Insurance Premium         1    450.00   450.00",
    "Fuel Surcharge                  1    275.00   275.00",
    "------------------------------------------------",
    "Subtotal:                                10775.00",
    "VAT (15%):                                1616.25",
    "------------------------------------------------",
    "Grand Total: 12391.25",
    "------------------------------------------------",
    "",
    "Payment Terms:  Net 30 days",
    "Bank:           Al Rajhi Bank",
    "IBAN:           SA03 8000 0000 6080 1016 7519",
    "",
    "Authorized Signature: ___________________",
    "",
    "================================================",
    "     Thank you for your business!",
    "================================================",
]

# ── Invoice 2 ─────────────────────────────────────────────────────────────────

invoice_2 = [
    "================================================",
    "          COMMERCIAL INVOICE",
    "================================================",
    "",
    "Gulf Star Shipping Co.",
    "Jeddah Islamic Port, Jeddah, Saudi Arabia",
    "Tel: +966-12-000-9999",
    "",
    "------------------------------------------------",
    "Invoice Number:  INV-2026-9002",
    "Issue Date:      2026-04-20",
    "Shipment Date:   2026-04-22",
    "------------------------------------------------",
    "",
    "Bill To (Vendor): Riyadh Customs Clearance LLC",
    "P.O. Box 5512, Riyadh 11432, Saudi Arabia",
    "",
    "------------------------------------------------",
    "DESCRIPTION                    QTY   RATE    TOTAL",
    "------------------------------------------------",
    "Air Freight - Dubai to Riyadh   1   5200.00  5200.00",
    "Customs Brokerage Fee           1    800.00   800.00",
    "Storage (3 days)                3    150.00   450.00",
    "Handling & Labeling             1    200.00   200.00",
    "------------------------------------------------",
    "Subtotal:                                 6650.00",
    "VAT (15%):                                 997.50",
    "------------------------------------------------",
    "Grand Total: 7647.50",
    "------------------------------------------------",
    "",
    "Payment Terms:  Net 15 days",
    "Bank:           Saudi National Bank",
    "IBAN:           SA44 1000 0001 2345 6789 0123",
    "",
    "Authorized Signature: ___________________",
    "",
    "================================================",
    "       Gulf Star Shipping Co. - Est. 2010",
    "================================================",
]

# ── Invoice 3 (high value) ────────────────────────────────────────────────────

invoice_3 = [
    "================================================",
    "          COMMERCIAL INVOICE",
    "================================================",
    "",
    "Saudi Express Cargo & Logistics",
    "Dammam, Eastern Province, Saudi Arabia",
    "",
    "------------------------------------------------",
    "Invoice Number:  INV-2026-9003",
    "Invoice Date:    2026-04-25",
    "Shipment Date:   2026-04-27",
    "------------------------------------------------",
    "",
    "Bill To (Vendor): Aramco Supply Chain Division",
    "Dhahran, Eastern Province 31311, Saudi Arabia",
    "",
    "------------------------------------------------",
    "SERVICE                        QTY    RATE     TOTAL",
    "------------------------------------------------",
    "Heavy Cargo - Full Truck Load   1   18000.00  18000.00",
    "Hazmat Handling Surcharge       1    2500.00   2500.00",
    "GPS Tracking & Security         1     750.00    750.00",
    "Driver Allowance                2     300.00    600.00",
    "Toll & Road Charges             1     350.00    350.00",
    "------------------------------------------------",
    "Subtotal:                                 22200.00",
    "VAT (15%):                                 3330.00",
    "------------------------------------------------",
    "Grand Total: 25530.00",
    "------------------------------------------------",
    "",
    "Payment Terms:  Net 45 days",
    "Bank:           Riyad Bank",
    "IBAN:           SA72 2000 0001 0000 1234 5600",
    "",
    "Authorized Signature: ___________________",
    "",
    "================================================",
    "    Saudi Express Cargo & Logistics",
    "================================================",
]

if __name__ == "__main__":
    print("\nGenerating test invoice PDFs...\n")
    make_pdf("test_invoices/INV-2026-9001.pdf", invoice_1)
    make_pdf("test_invoices/INV-2026-9002.pdf", invoice_2)
    make_pdf("test_invoices/INV-2026-9003.pdf", invoice_3)
    print("\nDone! Upload these from the test_invoices/ folder.\n")
