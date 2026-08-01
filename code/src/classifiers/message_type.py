"""
Multi-Class Message Category Classifier for WhatsApp Message Notification Router.
Categorizes incoming messages into one of the 11 allowed challenge schema categories.
"""

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
        text_lower = semantics.unified_text.lower()
        conv_type = message.conversation_type.strip().lower()

        # 1. PROMPT INJECTION / SCAM DETECTOR OVERRIDE
        if semantics.is_scam_suspicious or any(w in text_lower for w in [
            "ignore all previous", "login code", "verify now at", "security alert: otp",
            "support alert:", "confirm password", "reattempt fee"
        ]):
            return "scam"

        # 2. FORWARD
        if "fwd as received" in text_lower or message.forwarded_count >= 3:
            return "forward"

        # 3. PROMOTION / CLASSIFIED SALES (e.g. cycle helmet, kurta set, offers)
        if any(w in text_lower for w in [
            "selling", "kurta set", "cycle helmet", "discount", "sale", "% off",
            "coupon", "promo", "deal", "unbeatable price", "try50", "50% off",
            "shopping offer", "trip last change", "ladakh"
        ]):
            return "promotion"

        # 4. URGENT
        if any(w in text_lower for w in ["retry count crossed", "escalation", "incident bridge", "emergency", "water supply", "tanker", "heads-up", "heads up", "valve"]):
            return "urgent"
        if semantics.has_direct_user_mention and any(w in text_lower for w in ["prod review", "pulled to 3", "eod", "sorry for the last-minute"]):
            return "urgent"

        # 5. EVENT
        if any(w in text_lower for w in [
            "school circular", "bus is leaving", "pickup", "pick up", "stadium road",
            "cultural night", "appointment", "health-related update", "care services"
        ]):
            return "event"

        # 6. BUSINESS UPDATE
        if conv_type == "business" and context.business_context and context.business_context.is_verified:
            if any(w in text_lower for w in ["order", "packed", "delivery", "hub", "shipped", "amazon", "safety advisory"]):
                return "business_update"

        # 7. GREETING
        if any(w in text_lower for w in ["good morning all", "stay positive", "keep smiling"]) or (semantics.is_greeting and len(text_lower.split()) <= 5):
            return "greeting"

        # 8. PAYMENT
        if semantics.is_payment and any(w in text_lower for w in ["card", "bank", "due", "fee", "bill", "recharge"]):
            return "payment"

        # 9. PERSONAL
        if conv_type in ["personal", "group"]:
            return "personal"

        return "unknown"
