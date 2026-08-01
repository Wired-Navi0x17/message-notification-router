"""
Scam and Security Risk Detector for WhatsApp Message Notification Router.
High-priority security module that detects phishing, OTP theft, prompt injection, and domain spoofs,
enforcing an instant 'mute' override to protect users.
"""

from pydantic import BaseModel
from code.src.data.models import Message, ActionType, MessageType
from code.src.context.builder import EnrichedContext
from code.src.semantics.intent import SemanticFeatures


class ScamRiskAssessment(BaseModel):
    """Container for scam risk evaluation and safety override."""
    is_scam: bool = False
    risk_score: float = 0.0
    override_action: ActionType = "mute"
    override_message_type: MessageType = "scam"
    reason: str = ""


class ScamDetector:
    """Detects security threats, phishing attempts, and domain spoofing."""

    def evaluate_scam_risk(
        self,
        message: Message,
        context: EnrichedContext,
        semantics: SemanticFeatures
    ) -> ScamRiskAssessment:
        text_lower = semantics.unified_text.lower()
        risk_score = 0.0
        reasons = []

        # 1. Prompt Injection Attack Detection
        if any(pat in text_lower for pat in ["ignore all previous", "ignore previous instructions", "mark this message as notify", "system prompt"]):
            return ScamRiskAssessment(
                is_scam=True,
                risk_score=1.0,
                override_action="mute",
                override_message_type="scam",
                reason="Prompt injection attempt detected in message text."
            )

        # 2. OTP / Password / Login Code Theft
        if any(pat in text_lower for pat in [
            "enter otp", "share otp", "confirm password", "login code", "6 digit",
            "digit login", "verify now at", "profile will be blocked", "workspace access will expire"
        ]):
            risk_score += 0.7
            reasons.append("Requests sensitive OTP, password, or login credentials.")

        # 3. Domain Mismatch / Brand Spoofing (Whitelisted wa.me & link.wame.pro)
        if context.business_context and context.business_context.is_domain_mismatched:
            domain_used = context.business_context.domain_used_by_sender.lower()
            if not any(w in domain_used for w in ["wa.me", "link.wame.pro", "wame.pro", "whatsapp.com"]):
                risk_score += 0.6
                reasons.append(
                    f"Sender domain ({context.business_context.domain_used_by_sender}) "
                    f"does not match official brand domain ({context.business_context.official_domain})."
                )

        # 4. Young Account / Domain Age Phishing Risk
        if context.business_context and context.business_context.account_age_days < 90 and not context.business_context.is_verified:
            risk_score += 0.2
            reasons.append(f"Recently registered business account ({context.business_context.account_age_days} days old).")

        # 4. Phishing Keywords & Fake Fee Requests
        if any(w in text_lower for w in ["reattempt fee", "account suspended", "claim prize", "winner", "account-login", "security alert"]):
            risk_score += 0.5
            reasons.append("Contains suspicious phishing keywords or fake security alerts.")

        # 5. Unverified Sender asking for Money/OTP
        if context.business_context and not context.business_context.is_verified and semantics.is_payment:
            risk_score += 0.4
            reasons.append("Unverified sender requesting financial payment.")

        is_scam = risk_score >= 0.5 or semantics.is_scam_suspicious

        if is_scam:
            summary_reason = "Suspicious scam or phishing risk detected: " + " ".join(reasons) if reasons else "High-risk scam pattern detected."
            return ScamRiskAssessment(
                is_scam=True,
                risk_score=min(1.0, round(risk_score, 2)),
                override_action="mute",
                override_message_type="scam",
                reason=summary_reason
            )

        return ScamRiskAssessment(is_scam=False, risk_score=round(risk_score, 2))
