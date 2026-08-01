"""
Context Enrichment Engine for WhatsApp Message Notification Router.
Joins message metadata with user profiles, group dynamics, business histories, and DND schedules.
"""

from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel

from code.src.data.models import (
    Message,
    User,
    Group,
    GroupMember,
    BusinessAccount,
    UserBusinessHistory,
)
from code.src.data.loader import DatasetLoader


def parse_time_str(time_str: str) -> Optional[time]:
    """Parses 'HH:MM' string into datetime.time object."""
    try:
        parts = time_str.strip().split(":")
        return time(int(parts[0]), int(parts[1]))
    except Exception:
        return None


def is_dnd_active(dnd_window: str, timestamp_str: str) -> bool:
    """
    Determines whether a message timestamp falls within the user's Do-Not-Disturb window.
    Handles overnight windows (e.g. '22:00-07:00') and standard windows (e.g. '09:00-17:00').
    """
    if not dnd_window or "-" not in dnd_window:
        return False

    try:
        # Extract time from timestamp "2026-07-31 11:09" or "2026-07-31 22:15"
        time_part = timestamp_str.strip().split(" ")[-1]
        msg_time = parse_time_str(time_part)
        if not msg_time:
            return False

        start_str, end_str = dnd_window.strip().split("-")
        start_time = parse_time_str(start_str)
        end_time = parse_time_str(end_str)

        if not start_time or not end_time:
            return False

        if start_time <= end_time:
            # Standard window (e.g. 09:00 to 17:00)
            return start_time <= msg_time <= end_time
        else:
            # Overnight window (e.g. 22:00 to 07:00)
            return msg_time >= start_time or msg_time <= end_time
    except Exception:
        return False


class UserContext(BaseModel):
    """Enriched user context including DND state and engagement ratios."""
    user_id: str
    do_not_disturb_window: str = ""
    is_dnd_active: bool = False
    messages_opened_30d: int = 0
    messages_replied_30d: int = 0
    notifications_dismissed_30d: int = 0
    messages_reported_30d: int = 0
    open_ratio: float = 0.0
    reply_ratio: float = 0.0


class GroupContext(BaseModel):
    """Enriched group context including user role and group mute status."""
    group_id: str
    group_name: str = ""
    group_type: str = ""
    member_count: int = 0
    admin_count: int = 0
    messages_30d: int = 0
    user_role: str = "member"
    is_user_admin: bool = False
    is_group_muted_by_user: bool = False
    user_messages_sent_30d: int = 0
    user_messages_read_30d: int = 0
    user_replies_sent_30d: int = 0


class BusinessContext(BaseModel):
    """Enriched business sender context including domain validation and opt-out history."""
    business_id: str
    display_name: str = ""
    brand_name: str = ""
    category: str = ""
    is_verified: bool = False
    official_domain: str = ""
    domain_used_by_sender: str = ""
    is_domain_mismatched: bool = False
    account_age_days: int = 0
    user_reports_30d: int = 0
    relationship_reason: str = ""
    allows_promotions: bool = True
    user_activity_count_180d: int = 0
    user_messages_opened_30d: int = 0
    user_messages_dismissed_30d: int = 0
    user_messages_replied_30d: int = 0


class EnrichedContext(BaseModel):
    """Consolidated message context passed downstream to decision modules."""
    message: Message
    user_context: UserContext
    group_context: Optional[GroupContext] = None
    business_context: Optional[BusinessContext] = None


class ContextBuilder:
    """Enriches incoming messages with relational user, group, and business metadata."""

    def __init__(self, loader: DatasetLoader):
        self.loader = loader

    def build_user_context(self, user_id: str, created_at: str) -> UserContext:
        user = self.loader.users.get(user_id)
        if not user:
            return UserContext(user_id=user_id)

        dnd_active = is_dnd_active(user.do_not_disturb_window, created_at)
        total_interactions = user.messages_opened_30d + user.notifications_dismissed_30d
        open_ratio = (user.messages_opened_30d / total_interactions) if total_interactions > 0 else 0.5
        reply_ratio = (user.messages_replied_30d / user.messages_opened_30d) if user.messages_opened_30d > 0 else 0.0

        return UserContext(
            user_id=user.user_id,
            do_not_disturb_window=user.do_not_disturb_window,
            is_dnd_active=dnd_active,
            messages_opened_30d=user.messages_opened_30d,
            messages_replied_30d=user.messages_replied_30d,
            notifications_dismissed_30d=user.notifications_dismissed_30d,
            messages_reported_30d=user.messages_reported_30d,
            open_ratio=round(open_ratio, 2),
            reply_ratio=round(reply_ratio, 2),
        )

    def build_group_context(self, group_id: str, user_id: str) -> Optional[GroupContext]:
        if not group_id:
            return None

        group = self.loader.groups.get(group_id)
        member = self.loader.group_members.get((group_id, user_id))

        if not group:
            return None

        user_role = member.role if member else "member"
        is_admin = user_role.lower() == "admin"
        is_muted = member.group_muted_by_user if member else False

        return GroupContext(
            group_id=group.group_id,
            group_name=group.group_name,
            group_type=group.group_type,
            member_count=group.member_count,
            admin_count=group.admin_count,
            messages_30d=group.messages_30d,
            user_role=user_role,
            is_user_admin=is_admin,
            is_group_muted_by_user=is_muted,
            user_messages_sent_30d=member.messages_sent_30d if member else 0,
            user_messages_read_30d=member.messages_read_30d if member else 0,
            user_replies_sent_30d=member.replies_sent_30d if member else 0,
        )

    def build_business_context(self, business_id: str, user_id: str) -> Optional[BusinessContext]:
        if not business_id:
            return None

        business = self.loader.business_accounts.get(business_id)
        history = self.loader.user_business_history.get((user_id, business_id))

        if not business:
            return None

        official = business.official_domain.strip().lower() if business.official_domain else ""
        sender_domain = business.domain_used_by_sender.strip().lower() if business.domain_used_by_sender else ""
        domain_mismatch = bool(official and sender_domain and official != sender_domain)

        allows_promo = history.allows_promotions if history else True
        rel_reason = history.why_user_knows_account if history else ""

        return BusinessContext(
            business_id=business.business_id,
            display_name=business.display_name,
            brand_name=business.brand_name,
            category=business.category,
            is_verified=business.verified,
            official_domain=official,
            domain_used_by_sender=sender_domain,
            is_domain_mismatched=domain_mismatch,
            account_age_days=business.account_age_days,
            user_reports_30d=business.user_reports_30d,
            relationship_reason=rel_reason,
            allows_promotions=allows_promo,
            user_activity_count_180d=history.activity_count_180d if history else 0,
            user_messages_opened_30d=history.messages_opened_30d if history else 0,
            user_messages_dismissed_30d=history.messages_dismissed_30d if history else 0,
            user_messages_replied_30d=history.messages_replied_30d if history else 0,
        )

    def build_context(self, message: Message) -> EnrichedContext:
        user_ctx = self.build_user_context(message.user_id, message.created_at)
        group_ctx = self.build_group_context(message.group_id, message.user_id) if message.group_id else None
        biz_ctx = self.build_business_context(message.business_id, message.user_id) if message.business_id else None

        return EnrichedContext(
            message=message,
            user_context=user_ctx,
            group_context=group_ctx,
            business_context=biz_ctx,
        )
