"""
Historical Retrieval Engine and Event Graph for WhatsApp Message Notification Router.
Builds fast O(1) inverted indices over message_history.csv and message_events.csv
to retrieve user interaction patterns and match historical evidence IDs.
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from pydantic import BaseModel

from code.src.data.models import Message, MessageHistory, MessageEvent
from code.src.data.loader import DatasetLoader


def tokenize(text: str) -> Set[str]:
    """Cleans and tokenizes text into lowercase word tokens."""
    if not text:
        return set()
    words = re.findall(r'\w+', text.lower())
    # Filter out basic English stopwords
    stopwords = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "is", "it", "this", "that", "you", "your", "my", "we"}
    return {w for w in words if w not in stopwords}


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Calculates Jaccard similarity coefficient between two token sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0


class HistoricalEvidenceMatch(BaseModel):
    """Scored evidence candidate object."""
    message_id: str
    similarity_score: float
    user_action: str  # 'opened', 'replied', 'dismissed', 'muted', 'reported'
    created_at: str


class HistoryRetriever:
    """Fast O(1) Historical Retrieval & Evidence Matcher."""

    def __init__(self, loader: DatasetLoader):
        self.loader = loader
        self._user_messages: Dict[str, List[MessageHistory]] = {}
        self._sender_messages: Dict[Tuple[str, str], List[MessageHistory]] = {}
        self._group_messages: Dict[Tuple[str, str], List[MessageHistory]] = {}
        self._business_messages: Dict[Tuple[str, str], List[MessageHistory]] = {}
        self._events: Dict[Tuple[str, str], MessageEvent] = loader.message_events

        self._build_indices()

    def _build_indices(self):
        """Builds multi-key inverted index tables over message history."""
        for msg_id, msg in self.loader.message_history.items():
            user_id = msg.user_id
            
            # User index
            if user_id not in self._user_messages:
                self._user_messages[user_id] = []
            self._user_messages[user_id].append(msg)

            # Sender index (personal / group sender)
            if msg.sender_user_id:
                key = (user_id, msg.sender_user_id)
                if key not in self._sender_messages:
                    self._sender_messages[key] = []
                self._sender_messages[key].append(msg)

            # Group index
            if msg.group_id:
                key = (user_id, msg.group_id)
                if key not in self._group_messages:
                    self._group_messages[key] = []
                self._group_messages[key].append(msg)

            # Business index
            if msg.business_id:
                key = (user_id, msg.business_id)
                if key not in self._business_messages:
                    self._business_messages[key] = []
                self._business_messages[key].append(msg)

    def get_user_past_messages(self, user_id: str) -> List[MessageHistory]:
        return self._user_messages.get(user_id, [])

    def get_sender_past_messages(self, user_id: str, sender_id: str) -> List[MessageHistory]:
        return self._sender_messages.get((user_id, sender_id), [])

    def get_group_past_messages(self, user_id: str, group_id: str) -> List[MessageHistory]:
        return self._group_messages.get((user_id, group_id), [])

    def get_business_past_messages(self, user_id: str, business_id: str) -> List[MessageHistory]:
        return self._business_messages.get((user_id, business_id), [])

    def get_message_event(self, user_id: str, message_id: str) -> Optional[MessageEvent]:
        return self._events.get((user_id, message_id))

    def get_candidate_past_messages(self, message: Message) -> List[MessageHistory]:
        """Retrieves candidate past messages relevant to the incoming message."""
        candidates: List[MessageHistory] = []
        user_id = message.user_id

        if message.conversation_type == "business" and message.business_id:
            candidates.extend(self.get_business_past_messages(user_id, message.business_id))
        elif message.conversation_type == "group" and message.group_id:
            candidates.extend(self.get_group_past_messages(user_id, message.group_id))
            if message.sender_user_id:
                candidates.extend(self.get_sender_past_messages(user_id, message.sender_user_id))
        elif message.conversation_type == "personal" and message.sender_user_id:
            candidates.extend(self.get_sender_past_messages(user_id, message.sender_user_id))

        # Fallback to general user history if no specific conversation match
        if not candidates:
            candidates = self.get_user_past_messages(user_id)

        # Deduplicate candidates while preserving order
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c.message_id not in seen:
                seen.add(c.message_id)
                unique_candidates.append(c)

        return unique_candidates

    def find_relevant_evidence_ids(self, message: Message, top_k: int = 2) -> List[str]:
        """
        Ranks historical candidate messages for the given incoming message
        and returns top-K matching evidence message IDs. Returns ['none'] if no evidence found.
        """
        candidates = self.get_candidate_past_messages(message)
        if not candidates:
            return ["none"]

        msg_tokens = tokenize(message.message_text)
        scored_candidates: List[Tuple[float, MessageHistory]] = []

        for cand in candidates:
            cand_tokens = tokenize(cand.message_text)
            text_sim = jaccard_similarity(msg_tokens, cand_tokens)

            # Base score from conversation context match
            base_score = 0.3 if (
                (message.business_id and cand.business_id == message.business_id) or
                (message.group_id and cand.group_id == message.group_id) or
                (message.sender_user_id and cand.sender_user_id == message.sender_user_id)
            ) else 0.1

            # Event boost if user previously opened, replied, or reported
            event = self.get_message_event(message.user_id, cand.message_id)
            event_boost = 0.0
            if event:
                if event.message_replied:
                    event_boost += 0.3
                elif event.message_opened:
                    event_boost += 0.15
                if event.message_reported:
                    event_boost += 0.4  # Scam/Spam evidence match

            total_score = base_score + (text_sim * 0.5) + event_boost
            scored_candidates.append((total_score, cand))

        # Sort by total score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # Filter candidates above minimum confidence threshold (0.2)
        valid = [cand.message_id for score, cand in scored_candidates if score >= 0.25]
        if not valid:
            return ["none"]

        return valid[:top_k]
