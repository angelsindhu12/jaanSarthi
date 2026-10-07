import io
import os
from pathlib import Path
from typing import Dict, Any, Union
import torch
import numpy as np
from PIL import Image, ImageOps, ImageEnhance
from pypdf import PdfReader
import easyocr

class DocumentOCRService:
    _instance = None

    def __init__(self):
        use_gpu = torch.cuda.is_available()
        print(f"[OCR] Initializing EasyOCR for English and Hindi (GPU: {use_gpu})...")
        # EasyOCR reader for English and Hindi (core official languages in tenders & notices)
        self.reader = easyocr.Reader(['en', 'hi'], gpu=use_gpu)
        print("[OCR] EasyOCR ready.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def preprocess_image(self, img: Image.Image) -> np.ndarray:
        """Corrects orientation from EXIF (smartphone photo uploads) and balances contrast."""
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        img = img.convert("RGB")
        
        # Optimize contrast slightly for newsprint / faded circular scans
        try:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
        except Exception:
            pass

        return np.array(img)

    def extract_from_pdf(self, file_bytes: bytes) -> tuple[str, str]:
        """Extracts text directly from digital PDF pages or falls back to OCR on embedded page images."""
        extracted_text = []
        method = "pypdf_text_layer"
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    extracted_text.append(text.strip())
            
            # If no digital text found (e.g. scanned newspaper circular or scanned tender NIT PDF)
            if not extracted_text:
                print("[OCR] Scanned PDF detected without text layer. Extracting page images for OCR...")
                ocr_pages = []
                for page_num, page in enumerate(reader.pages):
                    page_ocr_text = []
                    for img_obj in page.images:
                        try:
                            img_t = self.extract_from_image(img_obj.data)
                            if img_t.strip():
                                page_ocr_text.append(img_t.strip())
                        except Exception as img_err:
                            print(f"[OCR] Error scanning page {page_num} image: {img_err}")
                    if page_ocr_text:
                        ocr_pages.append(f"[Page {page_num + 1}]\n" + "\n".join(page_ocr_text))

                if ocr_pages:
                    extracted_text = ocr_pages
                    method = "scanned_pdf_easyocr_images"
        except Exception as e:
            print(f"[OCR] Error processing PDF: {e}")
            
        return "\n\n".join(extracted_text), method

    def extract_from_image(self, file_input: Union[bytes, str, Path]) -> str:
        """Extracts text from an image (bytes, path, or PIL) using EasyOCR with orientation & contrast preprocessing."""
        if isinstance(file_input, bytes):
            image = Image.open(io.BytesIO(file_input))
            image_np = self.preprocess_image(image)
            results = self.reader.readtext(image_np, detail=0)
        else:
            image = Image.open(str(file_input))
            image_np = self.preprocess_image(image)
            results = self.reader.readtext(image_np, detail=0)

        # Join text lines with spaces, preserving readable sentences
        return "\n".join(results) if len(results) > 1 else (" ".join(results))

    def process_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Processes either PDF or Image and returns clean extracted text with metadata."""
        ext = filename.lower().split(".")[-1]
        text = ""
        method = "none"

        if ext == "pdf":
            text, method = self.extract_from_pdf(file_bytes)
        elif ext in ["jpg", "jpeg", "png", "bmp", "webp", "tiff"]:
            text = self.extract_from_image(file_bytes)
            method = "easyocr_image_enhanced"
        else:
            raise ValueError(f"Unsupported file format: .{ext}. Please upload a PDF or Image (JPG, PNG).")

        return {
            "filename": filename,
            "extraction_method": method,
            "extracted_text": text.strip(),
            "character_count": len(text.strip()),
            "line_count": len(text.strip().splitlines()) if text.strip() else 0
        }
