"""
Confidence Calibration Engine for WhatsApp Message Notification Router.
Calibrates output confidence scores [0.50, 0.99] based on security overrides,
signal agreement, trust scores, and priority matrices.
"""

from code.src.engine.router import FusionDecisionPayload


class ConfidenceCalibrator:
    """Computes calibrated probability/confidence scores for notification routing decisions."""

    def calibrate_confidence(self, decision: FusionDecisionPayload) -> float:
        base_confidence = 0.85

        # Hard Security Overrides carry high certainty
        if decision.scam_assessment.is_scam:
            return min(0.99, max(0.90, round(decision.scam_assessment.risk_score, 2)))
        if decision.spam_assessment.is_spam:
            return min(0.98, max(0.88, round(decision.spam_assessment.risk_score, 2)))

        # Signal Agreement Boost
        if decision.action == "notify":
            if decision.semantics.is_urgent or decision.priority_matrix.urgency_score >= 0.70:
                base_confidence += 0.08
            if decision.trust_score.overall_trust_score >= 0.70:
                base_confidence += 0.04
        elif decision.action == "mute":
            if decision.context.group_context and decision.context.group_context.is_group_muted_by_user:
                base_confidence += 0.08
            if decision.context.business_context and not decision.context.business_context.allows_promotions:
                base_confidence += 0.08
        elif decision.action == "digest":
            if decision.semantics.is_promotion or decision.message_type == "promotion":
                base_confidence += 0.05
            if decision.context.user_context.is_dnd_active:
                base_confidence += 0.05

        return round(max(0.50, min(0.99, base_confidence)), 2)
