"""
Context Builder and Metadata Normalizer for WhatsApp Message Notification Router.
Enriches raw messages with User, Group, and Business context models.
"""

from datetime import datetime, time
from typing import Optional, Tuple
from pydantic import BaseModel

from code.src.data.loader import DatasetLoader
from code.src.data.models import (
    Message, User, Group, GroupMember, BusinessAccount, UserBusinessHistory
)

WHATSAPP_SHORTENER_DOMAINS = ["wa.me", "link.wame.pro", "wame.pro", "whatsapp.com"]


class UserContext(BaseModel):
    """Enriched Context for User."""
    user_id: str
    dnd_window: str = ""
    is_dnd_active: bool = False
    open_ratio: float = 0.5
    reply_ratio: float = 0.0
    messages_reported_30d: int = 0


class GroupContext(BaseModel):
    """Enriched Context for Group Chat."""
    group_id: str
    group_name: str
    group_type: str = "casual"
    is_group_muted_by_user: bool = False
    is_user_admin: bool = False
    is_sender_admin: bool = False
    user_messages_read_30d: int = 0
    user_replies_sent_30d: int = 0
    admin_count: int = 1


class BusinessContext(BaseModel):
    """Enriched Context for Business Account."""
    business_id: str
    business_name: str
    category: str = "general"
    is_verified: bool = False
    allows_promotions: bool = True
    account_age_days: int = 365
    user_reports_30d: int = 0
    user_messages_sent_30d: int = 0
    user_messages_dismissed_30d: int = 0
    user_messages_replied_30d: int = 0
    user_activity_count_180d: int = 0
    relationship_reason: str = ""
    domain_used_by_sender: str = ""
    official_domain: str = ""
    is_domain_mismatched: bool = False


class EnrichedContext(BaseModel):
    """Unified container for all enriched message context metadata."""
    message: Message
    user_context: UserContext
    group_context: Optional[GroupContext] = None
    business_context: Optional[BusinessContext] = None


class ContextBuilder:
    """Builds unified EnrichedContext for incoming messages."""

    def __init__(self, loader: DatasetLoader):
        self.loader = loader

    def is_time_in_dnd(self, msg_time_str: str, dnd_window_str: Optional[str]) -> bool:
        """Checks if message creation timestamp falls within user DND quiet hours (e.g. '22:00-07:00')."""
        if not dnd_window_str or "-" not in dnd_window_str or not msg_time_str:
            return False

        try:
            parts = dnd_window_str.split("-")
            dnd_start_str, dnd_end_str = parts[0].strip(), parts[1].strip()

            msg_dt = None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
                try:
                    msg_dt = datetime.strptime(msg_time_str.strip(), fmt)
                    break
                except ValueError:
                    continue

            if not msg_dt:
                return False

            msg_t = msg_dt.time()
            start_t = datetime.strptime(dnd_start_str, "%H:%M").time()
            end_t = datetime.strptime(dnd_end_str, "%H:%M").time()

            if start_t <= end_t:
                return start_t <= msg_t <= end_t
            else:
                return msg_t >= start_t or msg_t <= end_t
        except Exception:
            return False

    def check_domain_mismatch(self, domain_used: str, official_domain: str) -> bool:
        """Validates if domain used by sender matches official brand domain (whitelisting WA shorteners)."""
        if not domain_used or not official_domain:
            return False

        d_used = domain_used.strip().lower()
        d_off = official_domain.strip().lower()

        if any(w in d_used for w in WHATSAPP_SHORTENER_DOMAINS):
            return False

        if d_used == d_off or d_used.endswith("." + d_off) or d_off.endswith("." + d_used):
            return False

        return True

    def build_context(self, message: Message) -> EnrichedContext:
        """Builds EnrichedContext for a given Message."""
        # 1. Build UserContext
        user = self.loader.users.get(message.user_id)
        if user:
            is_dnd = self.is_time_in_dnd(message.created_at, user.do_not_disturb_window)
            opened = user.messages_opened_30d or 0
            replied = user.messages_replied_30d or 0
            dismissed = user.notifications_dismissed_30d or 0
            total_activity = max(1, opened + replied + dismissed)
            open_ratio = round(opened / total_activity, 2)
            reply_ratio = round(replied / total_activity, 2)

            u_ctx = UserContext(
                user_id=user.user_id,
                dnd_window=user.do_not_disturb_window,
                is_dnd_active=is_dnd,
                open_ratio=open_ratio,
                reply_ratio=reply_ratio,
                messages_reported_30d=user.messages_reported_30d or 0
            )
        else:
            u_ctx = UserContext(user_id=message.user_id)

        # 2. Build GroupContext
        g_ctx: Optional[GroupContext] = None
        if message.conversation_type.strip().lower() == "group" and message.group_id:
            grp = self.loader.groups.get(message.group_id)
            gm_user = self.loader.group_members.get((message.group_id, message.user_id))
            gm_sender = self.loader.group_members.get((message.group_id, message.sender_user_id)) if message.sender_user_id else None

            grp_name = grp.group_name if grp else "Group Chat"
            grp_type = grp.group_type if grp else "casual"
            is_muted = bool(gm_user.group_muted_by_user) if gm_user else False
            is_user_admin = (gm_user.role.lower() == "admin") if gm_user else False
            is_sender_admin = (gm_sender.role.lower() == "admin") if gm_sender else False
            read_cnt = gm_user.messages_read_30d if gm_user else 0
            reply_cnt = gm_user.replies_sent_30d if gm_user else 0

            g_ctx = GroupContext(
                group_id=message.group_id,
                group_name=grp_name,
                group_type=grp_type,
                is_group_muted_by_user=is_muted,
                is_user_admin=is_user_admin,
                is_sender_admin=is_sender_admin,
                user_messages_read_30d=read_cnt,
                user_replies_sent_30d=reply_cnt,
            )

        # 3. Build BusinessContext
        b_ctx: Optional[BusinessContext] = None
        if message.conversation_type.strip().lower() == "business" and message.business_id:
            biz = self.loader.business_accounts.get(message.business_id)
            ubh = self.loader.user_business_history.get((message.user_id, message.business_id))

            if biz:
                domain_used = biz.domain_used_by_sender or ""
                official_dom = biz.official_domain or ""
                is_mismatched = self.check_domain_mismatch(domain_used, official_dom)

                b_ctx = BusinessContext(
                    business_id=biz.business_id,
                    business_name=biz.display_name or biz.brand_name or "Business",
                    category=biz.category or "general",
                    is_verified=bool(biz.verified),
                    allows_promotions=bool(ubh.allows_promotions) if ubh else True,
                    account_age_days=biz.account_age_days or 365,
                    user_reports_30d=biz.user_reports_30d or 0,
                    user_messages_sent_30d=biz.messages_sent_30d or 0,
                    user_messages_dismissed_30d=ubh.messages_dismissed_30d if ubh else 0,
                    user_messages_replied_30d=ubh.messages_replied_30d if ubh else 0,
                    user_activity_count_180d=ubh.activity_count_180d if ubh else 0,
                    relationship_reason=ubh.why_user_knows_account if ubh else "",
                    domain_used_by_sender=domain_used,
                    official_domain=official_dom,
                    is_domain_mismatched=is_mismatched
                )

        return EnrichedContext(
            message=message,
            user_context=u_ctx,
            group_context=g_ctx,
            business_context=b_ctx
        )
