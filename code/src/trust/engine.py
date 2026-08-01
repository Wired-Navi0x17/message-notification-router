"""
Consolidated Personalized Trust Engine for WhatsApp Message Notification Router.
Merges business trust, group trust, and user preference scores into a single unified trust score.
"""

from pydantic import BaseModel
from code.src.context.builder import EnrichedContext
from code.src.trust.business_trust import BusinessTrustScorer, BusinessTrustAssessment
from code.src.trust.group_trust import GroupTrustScorer, GroupTrustAssessment
from code.src.trust.user_preference import UserPreferenceScorer, UserPreferenceAssessment


class PersonalizedTrustScore(BaseModel):
    """Unified trust and preference score container."""
    overall_trust_score: float = 0.5
    business_trust: BusinessTrustAssessment
    group_trust: GroupTrustAssessment
    user_preference: UserPreferenceAssessment


class PersonalizedTrustEngine:
    """Synthesizes business, group, and user preference signals into a unified score."""

    def __init__(self):
        self.biz_scorer = BusinessTrustScorer()
        self.grp_scorer = GroupTrustScorer()
        self.user_scorer = UserPreferenceScorer()

    def evaluate_trust(self, context: EnrichedContext, sender_user_id: str = "") -> PersonalizedTrustScore:
        biz_eval = self.biz_scorer.evaluate_business_trust(context)
        grp_eval = self.grp_scorer.evaluate_group_trust(context, sender_user_id)
        user_eval = self.user_scorer.evaluate_user_preference(context)

        # Weighted combination depending on conversation type
        conv_type = context.message.conversation_type.strip().lower()

        if conv_type == "business":
            overall = (biz_eval.trust_score * 0.70) + (user_eval.preference_score * 0.30)
        elif conv_type == "group":
            overall = (grp_eval.trust_score * 0.70) + (user_eval.preference_score * 0.30)
        else:
            overall = (user_eval.preference_score * 0.60) + 0.30

        # Mute penalty if group or domain is blacklisted
        if grp_eval.is_group_muted:
            overall *= 0.40
        if biz_eval.domain_mismatched:
            overall *= 0.20

        final_score = max(0.0, min(1.0, round(overall, 2)))

        return PersonalizedTrustScore(
            overall_trust_score=final_score,
            business_trust=biz_eval,
            group_trust=grp_eval,
            user_preference=user_eval,
        )
