"""
Unified Multimodal Extractor Engine for WhatsApp Message Notification Router.
Normalizes all incoming modalities (text, image posters, voice notes) into a single plain text layer.
"""

from pydantic import BaseModel
from code.src.data.models import Message
from code.src.data.loader import DatasetLoader
from code.src.modalities.image import ImageExtractor
from code.src.modalities.voice import VoiceExtractor


class UnifiedTextPayload(BaseModel):
    """Container for unified text payload extracted from multimodal message."""
    message_id: str
    media_type: str
    original_text: str
    media_extracted_text: str
    unified_text: str
    has_media: bool


class UnifiedMultimodalExtractor:
    """Unifies text, image OCR, and voice ASR outputs into a single plain text representation."""

    def __init__(self, loader: DatasetLoader):
        self.loader = loader
        self.image_extractor = ImageExtractor(loader)
        self.voice_extractor = VoiceExtractor(loader)

    def extract_unified_text(self, message: Message) -> UnifiedTextPayload:
        """Extracts and normalizes text from text, image, or voice note message."""
        orig_text = message.message_text.strip() if message.message_text else ""
        media_type = message.media_type.strip().lower() if message.media_type else ""
        media_id = message.media_id.strip() if message.media_id else ""
        
        extracted_media_text = ""
        has_media = bool(media_type and media_id)

        if media_type == "image" and media_id:
            extracted_media_text = self.image_extractor.extract_text_from_image_id(media_id)
        elif media_type == "voice" and media_id:
            extracted_media_text = self.voice_extractor.extract_transcript_from_voice_id(media_id)

        # Merge original text and extracted media text into single unified string
        if orig_text and extracted_media_text:
            unified = f"{orig_text} {extracted_media_text}".strip()
        elif extracted_media_text:
            unified = extracted_media_text
        else:
            unified = orig_text

        return UnifiedTextPayload(
            message_id=message.message_id,
            media_type=media_type,
            original_text=orig_text,
            media_extracted_text=extracted_media_text,
            unified_text=unified,
            has_media=has_media,
        )
