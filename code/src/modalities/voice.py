"""
Voice Note ASR Transcriber Module for WhatsApp Message Notification Router.
Converts audio voice notes (.mp3 / .wav) into plain text transcripts using FFmpeg and SpeechRecognition.
"""

import os
import re
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Optional
import speech_recognition as sr

from code.src.data.loader import DatasetLoader
from code.src.data.models import VoiceNoteMetadata


def clean_transcript(text: str) -> str:
    """Cleans transcript text."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())


class VoiceExtractor:
    """Transcribes audio voice notes into plain text."""

    def __init__(self, loader: DatasetLoader):
        self.loader = loader
        self.dataset_dir = Path(loader.dataset_dir)
        self.recognizer = sr.Recognizer()
        self._cache: Dict[str, str] = {}

    def extract_transcript_from_voice_id(self, voice_id: str) -> str:
        """Transcribes audio for a given voice_note_id using cached results when available."""
        if voice_id in self._cache:
            return self._cache[voice_id]

        voice_meta = self.loader.voice_notes.get(voice_id)
        if not voice_meta:
            audio_path = self.dataset_dir / "media" / "audio" / f"{voice_id}.mp3"
        else:
            audio_path = self.dataset_dir / voice_meta.file_path

        if not audio_path.exists():
            return ""

        # Convert audio file to temporary 16kHz mono WAV for speech recognition
        temp_wav = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                temp_wav = tmp.name

            # Run FFmpeg conversion silently
            cmd = [
                "ffmpeg", "-y", "-i", str(audio_path),
                "-ar", "16000", "-ac", "1", temp_wav
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            with sr.AudioFile(temp_wav) as source:
                audio_data = self.recognizer.record(source)
                raw_text = self.recognizer.recognize_google(audio_data)
                cleaned = clean_transcript(raw_text)
                self._cache[voice_id] = cleaned
                return cleaned
        except Exception as e:
            print(f"Warning: Audio transcription failed for {audio_path}: {e}")
            return ""
        finally:
            if temp_wav and os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                except Exception:
                    pass
