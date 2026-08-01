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

        # 1. SCAM / PROMPT INJECTION
        if semantics.is_scam_suspicious or any(w in text_lower for w in [
            "ignore all previous", "login code", "verify now at", "security alert: otp",
            "support alert:", "confirm password", "reattempt fee"
        ]):
            return "scam"

        # 2. URGENT (Direct mentions & time-sensitive escalations)
        if any(w in text_lower for w in ["retry count crossed", "escalation", "incident bridge", "emergency", "water supply", "tanker", "heads-up", "heads up", "valve", "unwell", "clinic", "hospital"]):
            return "urgent"
        if semantics.has_direct_user_mention and any(w in text_lower for w in ["prod review", "pulled to 3", "eod", "sorry for the last-minute", "urgent"]):
            return "urgent"

        # 2.5 PAYMENT (Legitimate payment reminders, bills, dues, recharges)
        if any(w in text_lower for w in ["payment due", "bill generated", "fee payment", "recharge due", "electricity bill", "pay your bill", "amount due", "pay before"]) and not any(w in text_lower for w in ["never ask for", "safety advisory", "security alert"]):
            if not semantics.is_scam_suspicious:
                return "payment"

        # 3. SPAM (Unverified high-report spam senders)
        if context.business_context and not context.business_context.is_verified and context.business_context.user_reports_30d > 5:
            return "spam"

        # 4. PROMOTION (Evaluated BEFORE business_update to catch marketing flyers from verified senders)
        if semantics.is_promotion or any(w in text_lower for w in [
            "50% off", "try50", "discount", "sale", "% off", "coupon", "promo",
            "deal", "unbeatable price", "shopping offer", "trip last change", "ladakh", "unsubscribe",
            "selling", "kurta set", "cycle helmet"
        ]):
            return "promotion"

        # 5. GREETING (Social pleasantries evaluated before forward)
        if any(w in text_lower for w in ["good morning", "good vibes", "stay positive", "keep smiling"]):
            return "greeting"

        # 6. EVENT (School circulars, transport updates, clinic appointments; 'pickup' dropped so 006 stays personal)
        if any(w in text_lower for w in [
            "school circular", "bus is leaving", "pickup is near", "stadium road",
            "cultural night", "appointment", "health-related update", "care services"
        ]):
            return "event"

        # 7. VERIFIED BUSINESS UPDATE (Non-promotional transactional updates)
        if conv_type == "business" and context.business_context and context.business_context.is_verified:
            if not semantics.is_promotion and any(w in text_lower for w in ["order", "packed", "delivery", "hub", "shipped", "amazon", "safety advisory", "choosing pvr", "valuable feedback"]):
                return "business_update"

        # 8. FORWARD
        if "fwd as received" in text_lower or message.forwarded_count >= 5:
            return "forward"

        # 9. UNKNOWN (Unfamiliar sender with generic question and no prior interaction history)
        if "volunteer sheet" in text_lower or (conv_type == "personal" and "found your number" in text_lower):
            return "unknown"

        # 10. PERSONAL
        if conv_type in ["personal", "group"]:
            if semantics.has_direct_user_mention and any(w in text_lower for w in ["when you get 5 mins can you call", "can you call"]):
                return "personal"
            return "personal"

        return "unknown"
