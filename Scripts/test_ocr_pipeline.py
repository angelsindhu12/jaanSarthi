import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from PIL import Image, ImageDraw, ImageFont
from app.services.ocr_service import DocumentOCRService
from app.services.document_analyzer import DocumentAnalyzer

def create_sample_notice_image(filepath: Path):
    """Creates a synthetic image simulating an official government notice."""
    img = Image.new("RGB", (800, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    text_lines = [
        "GOVERNMENT OF INDIA - MINISTRY OF AGRICULTURE",
        "NOTIFICATION: PRADHAN MANTRI KISAN SAMMAN NIDHI",
        "Financial assistance of Rs 6000 per year in three equal installments",
        "Direct Benefit Transfer DBT for all eligible landholding farmer families.",
        "Apply online at pmkisan.gov.in with Aadhaar and Land records.",
        "Last date for eKYC: 31-12-2026."
    ]

    y = 30
    for line in text_lines:
        draw.text((40, y), line, fill=(10, 10, 10))
        y += 50

    img.save(filepath)
    print(f"[Setup] Created sample notice image at {filepath}")

def main():
    sample_img_path = Path("data/sample_pm_kisan_notice.png")
    create_sample_notice_image(sample_img_path)

    print("\n[1/2] Testing OCR Extraction...")
    ocr_service = DocumentOCRService.get_instance()
    with open(sample_img_path, "rb") as f:
        img_bytes = f.read()

    ocr_result = ocr_service.process_file(img_bytes, filename="sample_pm_kisan_notice.png")
    print(f"Extraction Method: {ocr_result['extraction_method']}")
    print(f"Extracted Text:\n{ocr_result['extracted_text']}\n")

    print("[2/2] Testing Plain Language Document Analyzer...")
    analyzer = DocumentAnalyzer.get_instance()
    analysis = analyzer.analyze_document(ocr_result['extracted_text'], preferred_language="hi")

    print(f"Document Type: {analysis['document_type']}")
    print(f"Extracted Amounts: {analysis['extracted_entities']['money_amounts']}")
    print(f"Extracted Dates: {analysis['extracted_entities']['dates']}")
    print(f"\nSimple Language Explanation (Hindi):\n{analysis['simple_explanation']}")

    if analysis['matched_scheme']:
        print(f"\nMatched Scheme: {analysis['matched_scheme']['title_en']}")
        print(f"Similarity Score: {analysis['matched_scheme']['similarity_score']}")
        print(f"Apply Link: {analysis['matched_scheme']['application_url']}")

if __name__ == "__main__":
    main()
