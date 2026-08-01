"""
Unit verification tests for Stage 4 Multimodal Extractor Pipeline.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.data.loader import DatasetLoader
from code.src.modalities.image import ImageExtractor
from code.src.modalities.voice import VoiceExtractor
from code.src.modalities.unified import UnifiedMultimodalExtractor, UnifiedTextPayload
from code.src.data.models import Message


def test_image_ocr_extraction():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    img_extractor = ImageExtractor(loader)

    text = img_extractor.extract_text_from_image_id("img_001")
    assert len(text) > 0, "Expected non-empty OCR text for img_001"
    assert "MEDAL" in text.upper() or "CERTIFICATE" in text.upper(), f"Expected poster keywords, got: {text}"
    print(f"✓ Image OCR extraction verified! Extracted: {text[:60]}...")


def test_voice_note_transcription():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    voice_extractor = VoiceExtractor(loader)

    transcript = voice_extractor.extract_transcript_from_voice_id("vn_001")
    assert len(transcript) > 0, "Expected non-empty transcript for vn_001"
    assert "call" in transcript.lower() or "urgent" in transcript.lower(), f"Expected keywords in transcript, got: {transcript}"
    print(f"✓ Voice note transcription verified! Transcript: {transcript}")


def test_unified_multimodal_extractor():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    unified_extractor = UnifiedMultimodalExtractor(loader)

    # Find voice message in messages.csv
    voice_msg = [m for m in loader.messages if m.media_type == "voice"][0]
    payload = unified_extractor.extract_unified_text(voice_msg)

    assert isinstance(payload, UnifiedTextPayload)
    assert payload.has_media is True
    assert len(payload.unified_text) > 0
    print(f"✓ Unified Multimodal Extractor verified! Message {payload.message_id} unified text: {payload.unified_text}")


if __name__ == "__main__":
    test_image_ocr_extraction()
    test_voice_note_transcription()
    test_unified_multimodal_extractor()
    print("✓ All Stage 4 Multimodal Extractor Pipeline tests passed cleanly!")
