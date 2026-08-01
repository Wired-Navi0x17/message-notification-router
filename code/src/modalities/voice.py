"""
Voice Note Audio Transcriber for WhatsApp Message Notification Router.
Converts audio files (.mp3, .ogg, .wav) to WAV format and transcribes speech to text
using SpeechRecognition with local JSON disk caching for 100% deterministic execution.
"""

import os
import json
import subprocess
from pathlib import Path
from pydantic import BaseModel
import speech_recognition as sr

CACHE_FILE_PATH = Path(__file__).resolve().parents[2] / ".cache" / "voice_transcripts.json"


class VoiceNoteMetadata(BaseModel):
    """Container for voice note extraction metadata."""
    audio_path: str
    transcription_text: str = ""
    duration_seconds: float = 0.0
    extraction_status: str = "PENDING"
    error_message: str = ""


class VoiceExtractor:
    """Extracts spoken text from voice note audio files with deterministic disk caching."""

    def __init__(self, loader=None):
        self.loader = loader
        self.recognizer = sr.Recognizer()
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Loads transcriptions from local JSON disk cache."""
        if CACHE_FILE_PATH.exists():
            try:
                with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache(self):
        """Saves transcriptions to local JSON disk cache."""
        try:
            CACHE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def extract_transcript_from_voice_id(self, media_id: str) -> str:
        """Extracts transcription string for a given voice note media ID."""
        if self.loader and hasattr(self.loader, "voice_notes") and media_id in self.loader.voice_notes:
            vn = self.loader.voice_notes[media_id]
            audio_path = os.path.join(self.loader.dataset_dir, "media", "audio", vn.filename) if hasattr(vn, "filename") else ""
            if not audio_path or not os.path.exists(audio_path):
                audio_path = os.path.join(self.loader.dataset_dir, "media", "audio", f"{media_id}.mp3")
            meta = self.extract_voice_text(audio_path)
            return meta.transcription_text

        return ""

    def extract_voice_text(self, audio_path: str) -> VoiceNoteMetadata:
        """Transcribes speech from audio file with local caching."""
        if not audio_path or not os.path.exists(audio_path):
            return VoiceNoteMetadata(
                audio_path=audio_path or "",
                extraction_status="FILE_NOT_FOUND",
                error_message="Audio file path does not exist."
            )

        cache_key = os.path.basename(audio_path)
        if cache_key in self.cache:
            cached_text = self.cache[cache_key]
            return VoiceNoteMetadata(
                audio_path=audio_path,
                transcription_text=cached_text,
                extraction_status="SUCCESS_CACHED"
            )

        wav_path = audio_path + ".converted.wav"
        try:
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", audio_path,
                "-ac", "1", "-ar", "16000", wav_path
            ]
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)

            if os.path.exists(wav_path):
                os.remove(wav_path)

            self.cache[cache_key] = text
            self._save_cache()

            return VoiceNoteMetadata(
                audio_path=audio_path,
                transcription_text=text,
                extraction_status="SUCCESS"
            )
        except Exception as e:
            if os.path.exists(wav_path):
                os.remove(wav_path)

            return VoiceNoteMetadata(
                audio_path=audio_path,
                extraction_status="ERROR",
                error_message=str(e)
            )
