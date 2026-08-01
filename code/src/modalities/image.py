"""
Image OCR Extractor Module for WhatsApp Message Notification Router.
Uses PIL and Tesseract OCR to extract text from images, posters, and screenshots.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional
from PIL import Image
import pytesseract

from code.src.data.loader import DatasetLoader
from code.src.data.models import ImageMetadata


def clean_ocr_text(text: str) -> str:
    """Cleans raw OCR output by stripping whitespace and noise lines."""
    if not text:
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = " ".join(lines)
    # Collapse multiple spaces
    return re.sub(r'\s+', ' ', cleaned)


class ImageExtractor:
    """Extracts text content from image files via Tesseract OCR."""

    def __init__(self, loader: DatasetLoader):
        self.loader = loader
        self.dataset_dir = Path(loader.dataset_dir)
        self._cache: Dict[str, str] = {}

    def extract_text_from_image_id(self, image_id: str) -> str:
        """Extracts text for a given image_id using cached results when available."""
        if image_id in self._cache:
            return self._cache[image_id]

        img_meta = self.loader.images.get(image_id)
        if not img_meta:
            # Fallback path construct
            img_path = self.dataset_dir / "media" / "images" / f"{image_id}.jpg"
        else:
            img_path = self.dataset_dir / img_meta.file_path

        if not img_path.exists():
            return ""

        try:
            image = Image.open(img_path)
            raw_text = pytesseract.image_to_string(image)
            cleaned = clean_ocr_text(raw_text)
            self._cache[image_id] = cleaned
            return cleaned
        except Exception as e:
            print(f"Warning: OCR failed on {img_path}: {e}")
            return ""
