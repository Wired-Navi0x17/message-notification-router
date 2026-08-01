"""
Pydantic Domain Models for WhatsApp Message Notification Router.
Converts raw dataset CSV rows into strongly-typed, validated Python objects.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

# Allowed Enum Literals per Challenge Specification
ActionType = Literal["notify", "digest", "mute"]

MessageType = Literal[
    "personal",
    "urgent",
    "event",
    "payment",
    "business_update",
    "promotion",
    "greeting",
    "forward",
    "spam",
    "scam",
    "unknown"
]

ConversationType = Literal["personal", "group", "business"]


def safe_int(val: str | int | None, default: int = 0) -> int:
    """Safely cast string numbers or empty values to integer."""
    if val is None or val == "":
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def safe_float(val: str | float | None, default: float = 0.0) -> float:
    """Safely cast string numbers or empty values to float."""
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_bool(val: str | int | bool | None) -> bool:
    """Safely convert '1', '0', True, False, 'true', 'false' to boolean."""
    if isinstance(val, bool):
        return val
    if val is None or val == "":
        return False
    val_str = str(val).strip().lower()
    return val_str in ("1", "true", "yes")


class Message(BaseModel):
    """Normalized incoming message representation from dataset/messages.csv."""
    message_id: str
    user_id: str
    conversation_type: str
    group_id: str = ""
    business_id: str = ""
    sender_user_id: str = ""
    created_at: str
    message_text: str = ""
    media_type: str = ""
    media_id: str = ""
    forwarded_count: int = 0

    @field_validator("forwarded_count", mode="before")
    @classmethod
    def parse_forwarded_count(cls, v):
        return safe_int(v, 0)


class User(BaseModel):
    """User profile and overall notification engagement behavior from dataset/users.csv."""
    user_id: str
    do_not_disturb_window: str = ""
    messages_opened_30d: int = 0
    messages_replied_30d: int = 0
    notifications_dismissed_30d: int = 0
    messages_reported_30d: int = 0

    @field_validator("messages_opened_30d", "messages_replied_30d", "notifications_dismissed_30d", "messages_reported_30d", mode="before")
    @classmethod
    def parse_ints(cls, v):
        return safe_int(v, 0)


class Group(BaseModel):
    """Group chat metadata from dataset/groups.csv."""
    group_id: str
    group_name: str = ""
    group_type: str = ""
    member_count: int = 0
    admin_count: int = 0
    created_at: str = ""
    messages_30d: int = 0

    @field_validator("member_count", "admin_count", "messages_30d", mode="before")
    @classmethod
    def parse_ints(cls, v):
        return safe_int(v, 0)


class GroupMember(BaseModel):
    """User-group membership details and user activity in group from dataset/group_members.csv."""
    group_id: str
    user_id: str
    role: str = "member"
    joined_at: str = ""
    messages_sent_30d: int = 0
    messages_read_30d: int = 0
    replies_sent_30d: int = 0
    notifications_dismissed_30d: int = 0
    group_muted_by_user: bool = False

    @field_validator("messages_sent_30d", "messages_read_30d", "replies_sent_30d", "notifications_dismissed_30d", mode="before")
    @classmethod
    def parse_ints(cls, v):
        return safe_int(v, 0)

    @field_validator("group_muted_by_user", mode="before")
    @classmethod
    def parse_bool(cls, v):
        return safe_bool(v)


class BusinessAccount(BaseModel):
    """Business sender identity and verification metadata from dataset/business_accounts.csv."""
    business_id: str
    display_name: str = ""
    brand_name: str = ""
    category: str = ""
    verified: bool = False
    official_domain: str = ""
    domain_used_by_sender: str = ""
    account_age_days: int = 0
    messages_sent_30d: int = 0
    user_reports_30d: int = 0
    domain_used_by_sender_age_days: int = 0

    @field_validator("verified", mode="before")
    @classmethod
    def parse_verified(cls, v):
        return safe_bool(v)

    @field_validator("account_age_days", "messages_sent_30d", "user_reports_30d", "domain_used_by_sender_age_days", mode="before")
    @classmethod
    def parse_ints(cls, v):
        return safe_int(v, 0)


class UserBusinessHistory(BaseModel):
    """User-business historical relationship and opt-out preferences from dataset/user_business_history.csv."""
    user_id: str
    business_id: str
    why_user_knows_account: str = ""
    last_activity_at: str = ""
    allows_promotions: bool = True
    promotions_opted_out_at: str = ""
    activity_count_180d: int = 0
    messages_opened_30d: int = 0
    messages_dismissed_30d: int = 0
    messages_replied_30d: int = 0
    last_reply_at: str = ""

    @field_validator("allows_promotions", mode="before")
    @classmethod
    def parse_allows_promo(cls, v):
        return safe_bool(v)

    @field_validator("activity_count_180d", "messages_opened_30d", "messages_dismissed_30d", "messages_replied_30d", mode="before")
    @classmethod
    def parse_ints(cls, v):
        return safe_int(v, 0)


class MessageHistory(BaseModel):
    """Past message received by user from dataset/message_history.csv."""
    message_id: str
    user_id: str
    conversation_type: str = ""
    group_id: str = ""
    business_id: str = ""
    sender_user_id: str = ""
    created_at: str = ""
    message_text: str = ""
    media_type: str = ""
    media_id: str = ""
    forwarded_count: int = 0

    @field_validator("forwarded_count", mode="before")
    @classmethod
    def parse_forwarded_count(cls, v):
        return safe_int(v, 0)


class MessageEvent(BaseModel):
    """User reaction event to historical message from dataset/message_events.csv."""
    user_id: str
    message_id: str
    message_opened: bool = False
    message_replied: bool = False
    reaction_time_minutes: float = 0.0
    notification_dismissed: bool = False
    muted_after_message: bool = False
    message_reported: bool = False

    @field_validator("message_opened", "message_replied", "notification_dismissed", "muted_after_message", "message_reported", mode="before")
    @classmethod
    def parse_bools(cls, v):
        return safe_bool(v)

    @field_validator("reaction_time_minutes", mode="before")
    @classmethod
    def parse_reaction_time(cls, v):
        return safe_float(v, 0.0)


class ImageMetadata(BaseModel):
    """Image metadata reference from dataset/images.csv."""
    image_id: str
    file_path: str


class VoiceNoteMetadata(BaseModel):
    """Voice note metadata reference from dataset/voice_notes.csv."""
    voice_note_id: str
    file_path: str


class DailyNotificationSummary(BaseModel):
    """Daily notification load per user from dataset/daily_notification_summary.csv."""
    user_id: str
    date: str
    notifications_sent: int = 0
    notifications_dismissed: int = 0

    @field_validator("notifications_sent", "notifications_dismissed", mode="before")
    @classmethod
    def parse_ints(cls, v):
        return safe_int(v, 0)


class OutputPrediction(BaseModel):
    """Prediction output matching exact dataset/output.csv schema."""
    message_id: str
    action: ActionType
    message_type: MessageType
    reason: str
    confidence: float
    evidence_message_ids: str = "none"

    @field_validator("confidence", mode="before")
    @classmethod
    def validate_confidence(cls, v):
        val = safe_float(v, 0.5)
        return max(0.0, min(1.0, round(val, 2)))
