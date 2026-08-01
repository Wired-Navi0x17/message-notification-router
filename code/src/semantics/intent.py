"""
Semantic Feature and Intent Extraction Engine for WhatsApp Message Notification Router.
Analyzes unified text payloads to extract intent categories, urgency markers, and security indicators.
"""

import re
from typing import List, Dict, Set
from pydantic import BaseModel


class SemanticFeatures(BaseModel):
    """Container for extracted semantic features and intent scores."""
    unified_text: str
    is_urgent: bool = False
    is_payment: bool = False
    is_promotion: bool = False
    is_greeting: bool = False
    is_event: bool = False
    is_scam_suspicious: bool = False
    has_direct_user_mention: bool = False
    matched_urgency_keywords: List[str] = []
    matched_payment_keywords: List[str] = []
    matched_promo_keywords: List[str] = []
    matched_scam_keywords: List[str] = []
    intent_scores: Dict[str, float] = {}


# Keyword Taxonomies
URGENCY_KEYWORDS = [
    r"\burgent\b", r"\bemergency\b", r"\bheads-up\b", r"\bheads up\b", r"\bheadsup\b",
    r"\bimmediately\b", r"\basap\b", r"\bnow\b", r"\bdeadline\b", r"\beod\b",
    r"\btanker\b", r"\bwater supply\b", r"\bvalve\b", r"\bunwell\b", r"\bclinic\b",
    r"\bhospital\b", r"\bspiking\b", r"\bincident bridge\b", r"\bfailing\b"
]

PAYMENT_KEYWORDS = [
    r"\bpayment\b", r"\bpay\b", r"\bdue\b", r"\bcard\b", r"\bbank\b",
    r"\baccount\b", r"\brecharge\b", r"\bfee\b", r"\brupees\b", r"\brs\b",
    r"\bbill\b", r"\botp\b", r"\bcheckout\b"
]

PROMOTION_KEYWORDS = [
    r"\bdiscount\b", r"\bsale\b", r"\b%\s*off\b", r"\bunbeatable price\b",
    r"\boffer\b", r"\bcashback\b", r"\bcoupon\b", r"\bpromo\b", r"\bdeal\b",
    r"\bbuy 1 get 1\b", r"\bflat\s*\d+%\b"
]

EVENT_KEYWORDS = [
    r"\bmeeting\b", r"\breview\b", r"\bpickup\b", r"\bappointment\b",
    r"\bschedule\b", r"\btoday\b", r"\btomorrow\b", r"\bbus\b", r"\bcab\b",
    r"\bdriver\b", r"\bevent\b", r"\bclass\b", r"\bwebinar\b"
]

GREETING_KEYWORDS = [
    r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bgood morning\b", r"\bgood evening\b",
    r"\bcongrats\b", r"\bcongratulations\b", r"\bhappy birthday\b"
]

SCAM_KEYWORDS = [
    r"\benter otp\b", r"\bverify account\b", r"\baccount suspended\b",
    r"\breattempt fee\b", r"\bclick link\b", r"\bclaim prize\b", r"\bwinner\b",
    r"amazonpay-delivery", r"\bfree money\b"
]


class IntentFeatureExtractor:
    """Extracts semantic features, intent categories, and keyword markers from text."""

    def extract_features(self, text: str, user_id: str = "") -> SemanticFeatures:
        if not text:
            return SemanticFeatures(unified_text="")

        text_lower = text.lower()

        # Direct mention extraction (e.g. @u_010 or @u_)
        has_direct_mention = False
        if user_id:
            user_handle = f"@{user_id.lower()}"
            has_direct_mention = user_handle in text_lower
        if not has_direct_mention:
            has_direct_mention = bool(re.search(r"@u_\d+", text_lower))

        # Keyword matching helper
        def match_patterns(patterns: List[str]) -> List[str]:
            matched = []
            for pat in patterns:
                if re.search(pat, text_lower):
                    # Clean clean regex string for readability
                    clean_kw = pat.replace(r"\b", "").replace(r"\s*", " ").strip()
                    matched.append(clean_kw)
            return matched

        urgent_matches = match_patterns(URGENCY_KEYWORDS)
        payment_matches = match_patterns(PAYMENT_KEYWORDS)
        promo_matches = match_patterns(PROMOTION_KEYWORDS)
        event_matches = match_patterns(EVENT_KEYWORDS)
        greeting_matches = match_patterns(GREETING_KEYWORDS)
        scam_matches = match_patterns(SCAM_KEYWORDS)

        is_urgent = bool(urgent_matches or has_direct_mention)
        is_payment = bool(payment_matches)
        is_promotion = bool(promo_matches)
        is_event = bool(event_matches)
        is_greeting = bool(greeting_matches)
        is_scam = bool(scam_matches)

        # Compute numerical intent scores [0.0 - 1.0]
        scores = {
            "urgent": min(1.0, len(urgent_matches) * 0.4 + (0.5 if has_direct_mention else 0.0)),
            "payment": min(1.0, len(payment_matches) * 0.4),
            "promotion": min(1.0, len(promo_matches) * 0.4),
            "event": min(1.0, len(event_matches) * 0.35),
            "greeting": min(1.0, len(greeting_matches) * 0.5),
            "scam": min(1.0, len(scam_matches) * 0.5),
        }

        return SemanticFeatures(
            unified_text=text,
            is_urgent=is_urgent,
            is_payment=is_payment,
            is_promotion=is_promotion,
            is_greeting=is_greeting,
            is_event=is_event,
            is_scam_suspicious=is_scam,
            has_direct_user_mention=has_direct_mention,
            matched_urgency_keywords=urgent_matches,
            matched_payment_keywords=payment_matches,
            matched_promo_keywords=promo_matches,
            matched_scam_keywords=scam_matches,
            intent_scores=scores,
        )
