"""
Dataset Loader for WhatsApp Message Notification Router.
Reads CSV dataset files and builds strongly-typed Pydantic model indices.
"""

import os
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from .models import (
    Message,
    User,
    Group,
    GroupMember,
    BusinessAccount,
    UserBusinessHistory,
    MessageHistory,
    MessageEvent,
    ImageMetadata,
    VoiceNoteMetadata,
    DailyNotificationSummary,
    OutputPrediction
)


class DatasetLoader:
    """Robust CSV Loader & Memory Indexer for dataset files."""

    def __init__(self, dataset_dir: str | Path = "dataset"):
        self.dataset_dir = Path(dataset_dir)
        self.messages: List[Message] = []
        self.users: Dict[str, User] = {}
        self.groups: Dict[str, Group] = {}
        self.group_members: Dict[Tuple[str, str], GroupMember] = {}
        self.business_accounts: Dict[str, BusinessAccount] = {}
        self.user_business_history: Dict[Tuple[str, str], UserBusinessHistory] = {}
        self.message_history: Dict[str, MessageHistory] = {}
        self.message_events: Dict[Tuple[str, str], MessageEvent] = {}
        self.images: Dict[str, ImageMetadata] = {}
        self.voice_notes: Dict[str, VoiceNoteMetadata] = {}
        self.daily_summaries: List[DailyNotificationSummary] = []
        self.sample_messages: List[Dict[str, Any]] = []

    def _read_csv(self, filename: str) -> List[Dict[str, str]]:
        filepath = self.dataset_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Required dataset file not found: {filepath}")
        
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]

    def load_messages(self, filename: str = "messages.csv") -> List[Message]:
        rows = self._read_csv(filename)
        self.messages = [Message(**row) for row in rows]
        return self.messages

    def load_users(self, filename: str = "users.csv") -> Dict[str, User]:
        rows = self._read_csv(filename)
        self.users = {row["user_id"]: User(**row) for row in rows}
        return self.users

    def load_groups(self, filename: str = "groups.csv") -> Dict[str, Group]:
        rows = self._read_csv(filename)
        self.groups = {row["group_id"]: Group(**row) for row in rows}
        return self.groups

    def load_group_members(self, filename: str = "group_members.csv") -> Dict[Tuple[str, str], GroupMember]:
        rows = self._read_csv(filename)
        self.group_members = {
            (row["group_id"], row["user_id"]): GroupMember(**row) for row in rows
        }
        return self.group_members

    def load_business_accounts(self, filename: str = "business_accounts.csv") -> Dict[str, BusinessAccount]:
        rows = self._read_csv(filename)
        self.business_accounts = {
            row["business_id"]: BusinessAccount(**row) for row in rows
        }
        return self.business_accounts

    def load_user_business_history(self, filename: str = "user_business_history.csv") -> Dict[Tuple[str, str], UserBusinessHistory]:
        rows = self._read_csv(filename)
        self.user_business_history = {
            (row["user_id"], row["business_id"]): UserBusinessHistory(**row) for row in rows
        }
        return self.user_business_history

    def load_message_history(self, filename: str = "message_history.csv") -> Dict[str, MessageHistory]:
        rows = self._read_csv(filename)
        self.message_history = {
            row["message_id"]: MessageHistory(**row) for row in rows
        }
        return self.message_history

    def load_message_events(self, filename: str = "message_events.csv") -> Dict[Tuple[str, str], MessageEvent]:
        rows = self._read_csv(filename)
        self.message_events = {
            (row["user_id"], row["message_id"]): MessageEvent(**row) for row in rows
        }
        return self.message_events

    def load_images(self, filename: str = "images.csv") -> Dict[str, ImageMetadata]:
        rows = self._read_csv(filename)
        self.images = {
            row["image_id"]: ImageMetadata(**row) for row in rows
        }
        return self.images

    def load_voice_notes(self, filename: str = "voice_notes.csv") -> Dict[str, VoiceNoteMetadata]:
        rows = self._read_csv(filename)
        self.voice_notes = {
            row["voice_note_id"]: VoiceNoteMetadata(**row) for row in rows
        }
        return self.voice_notes

    def load_daily_summaries(self, filename: str = "daily_notification_summary.csv") -> List[DailyNotificationSummary]:
        rows = self._read_csv(filename)
        self.daily_summaries = [DailyNotificationSummary(**row) for row in rows]
        return self.daily_summaries

    def load_sample_messages(self, filename: str = "sample_messages.csv") -> List[Dict[str, Any]]:
        self.sample_messages = self._read_csv(filename)
        return self.sample_messages

    def load_all(self) -> "DatasetLoader":
        """Executes full dataset ingestion into memory indices."""
        self.load_messages()
        self.load_users()
        self.load_groups()
        self.load_group_members()
        self.load_business_accounts()
        self.load_user_business_history()
        self.load_message_history()
        self.load_message_events()
        self.load_images()
        self.load_voice_notes()
        self.load_daily_summaries()
        self.load_sample_messages()
        return self
