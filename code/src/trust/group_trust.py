"""
Group Trust Scorer for WhatsApp Message Notification Router.
Evaluates group dynamics, sender admin authority, group type weights, and user mute states.
"""

from pydantic import BaseModel
from code.src.context.builder import EnrichedContext, GroupContext


class GroupTrustAssessment(BaseModel):
    """Container for group trust metrics."""
    trust_score: float = 0.5
    is_group_muted: bool = False
    is_sender_admin: bool = False
    group_type: str = ""
    user_engagement_score: float = 0.5


class GroupTrustScorer:
    """Evaluates authority and trust level of group chat senders."""

    def evaluate_group_trust(self, context: EnrichedContext, sender_user_id: str = "") -> GroupTrustAssessment:
        grp = context.group_context
        if not grp:
            return GroupTrustAssessment()

        score = 0.30  # Baseline

        # Group Type Weighting
        gtype = grp.group_type.strip().lower()
        if gtype in ["family", "school", "work"]:
            score += 0.30
        elif gtype in ["society", "apartment", "building"]:
            score += 0.20
        else:
            score += 0.10

        # Sender Admin Role Boost (+0.35)
        # Note: If sender_user_id matches group admin or user is admin
        is_sender_admin = False
        if grp.is_user_admin or (sender_user_id and grp.admin_count > 0):
            # In group context, admin updates carry higher priority
            score += 0.25

        # User Activity in Group Boost (+0.20)
        total_group_interactions = grp.user_messages_read_30d + grp.user_replies_sent_30d
        if total_group_interactions > 5:
            score += 0.20
        elif total_group_interactions > 0:
            score += 0.10

        # Group Muted Penalty (-0.50)
        if grp.is_group_muted_by_user:
            score -= 0.50

        final_score = max(0.0, min(1.0, round(score, 2)))

        return GroupTrustAssessment(
            trust_score=final_score,
            is_group_muted=grp.is_group_muted_by_user,
            is_sender_admin=grp.is_user_admin,
            group_type=grp.group_type,
            user_engagement_score=min(1.0, round(total_group_interactions / 20.0, 2)),
        )
