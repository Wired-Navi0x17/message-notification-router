"""
User Preference Scorer for WhatsApp Message Notification Router.
Evaluates quiet hours (DND), overall notification engagement, and historical dismissal rates.
"""

from pydantic import BaseModel
from code.src.context.builder import EnrichedContext, UserContext


class UserPreferenceAssessment(BaseModel):
    """Container for user preference alignment metrics."""
    preference_score: float = 0.5
    is_quiet_hours_active: bool = False
    open_ratio: float = 0.5
    reply_ratio: float = 0.0
    dismissal_ratio: float = 0.0


class UserPreferenceScorer:
    """Evaluates user quiet hours and overall notification receptivity."""

    def evaluate_user_preference(self, context: EnrichedContext) -> UserPreferenceAssessment:
        u_ctx = context.user_context
        score = 0.50  # Baseline

        # DND Quiet Hours Penalty (-0.40 for non-urgent messages)
        is_dnd = u_ctx.is_dnd_active
        if is_dnd:
            score -= 0.40

        # Open & Reply Ratio Boost (+0.30)
        score += (u_ctx.open_ratio * 0.20) + (u_ctx.reply_ratio * 0.20)

        # High Report History Penalty (-0.30)
        if u_ctx.messages_reported_30d > 0:
            score -= (u_ctx.messages_reported_30d * 0.10)

        final_score = max(0.0, min(1.0, round(score, 2)))

        return UserPreferenceAssessment(
            preference_score=final_score,
            is_quiet_hours_active=is_dnd,
            open_ratio=u_ctx.open_ratio,
            reply_ratio=u_ctx.reply_ratio,
        )
