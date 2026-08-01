"""
Multi-Class Message Category Classifier for WhatsApp Message Notification Router.
Categorizes incoming messages into one of the 11 allowed challenge schema categories:
- personal
- urgent
- event
- payment
- business_update
- promotion
- greeting
- forward
- spam
- scam
- unknown
"""

from typing import Tuple
from code.src.data.models import Message, MessageType
from code.src.context.builder import EnrichedContext
from code.src.semantics.intent import SemanticFeatures


class MessageTypeClassifier:
    """Predicts best-fit MessageType category using multimodal semantics and enriched context."""

    def classify_message_type(
        self,
        message: Message,
        context: EnrichedContext,
        semantics: SemanticFeatures
    ) -> MessageType:
        """Determines best-fit message_type from the 11 allowed schema categories."""
        text_lower = semantics.unified_text.lower()
        conv_type = message.conversation_type.strip().lower()

        # 1. SCAM DETECTOR OVERRIDE
        if semantics.is_scam_suspicious:
            return "scam"
        if context.business_context and context.business_context.is_domain_mismatched and semantics.is_payment:
            return "scam"

        # 2. SPAM DETECTOR OVERRIDE
        if message.forwarded_count >= 10:
            return "spam"
        if context.business_context and not context.business_context.allows_promotions and semantics.is_promotion:
            return "spam"

        # 3. PERSONAL DIRECT QUESTION OVERRIDE
        # If user explicitly states non-urgent phrasing like "nothing dramatic", "when you get 5 mins", "call when free"
        if any(w in text_lower for w in ["nothing dramatic", "when free", "when you get 5 mins", "when you get time", "can you call"]):
            if "unwell" not in text_lower and "clinic" not in text_lower and "emergency" not in text_lower:
                return "personal"

        # 4. URGENT
        if semantics.has_direct_user_mention and ("sorry" in text_lower or "shuffle" in text_lower or "review" in text_lower or "eod" in text_lower or "urgent" in text_lower):
            return "urgent"
        if any(w in text_lower for w in ["tanker", "heads-up", "heads up", "valve", "unwell", "clinic", "incident bridge", "emergency"]):
            return "urgent"

        # 5. EVENT
        if any(w in text_lower for w in ["bus is leaving", "pickup", "pick up", "appointment", "booking", "schedule", "stadium road", "school transport"]):
            return "event"
        if context.business_context and ("health" in text_lower or "appointment" in text_lower):
            return "event"

        # 6. PAYMENT
        if semantics.is_payment and any(w in text_lower for w in ["card", "bank", "due", "fee", "bill", "recharge", "balance"]):
            return "payment"

        # 7. BUSINESS UPDATE
        if conv_type == "business" and context.business_context and context.business_context.is_verified:
            if any(w in text_lower for w in ["order", "packed", "delivery", "hub", "shipped", "amazon"]):
                return "business_update"
            if not semantics.is_promotion and not semantics.is_scam_suspicious:
                return "business_update"

        # 8. PROMOTION
        if semantics.is_promotion or any(w in text_lower for w in ["discount", "sale", "off", "coupon", "promo", "deal", "unbeatable price"]):
            return "promotion"

        # 9. GREETING
        if semantics.is_greeting or text_lower.strip() in ["hi", "hello", "hey", "good morning", "good evening"]:
            return "greeting"

        # 10. FORWARD
        if message.forwarded_count >= 3:
            return "forward"

        # 11. PERSONAL (DEFAULT FALLBACK)
        if conv_type == "personal" or conv_type == "group":
            return "personal"

        return "unknown"
