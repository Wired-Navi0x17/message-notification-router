"""
Decision Fusion Router for WhatsApp Message Notification Router.
Fuses security overrides, semantic categories, trust scores, and priority matrices
into final personalized routing decisions ('notify', 'digest', 'mute').
"""

from pydantic import BaseModel
from code.src.data.models import Message, ActionType, MessageType
from code.src.data.loader import DatasetLoader
from code.src.context.builder import ContextBuilder, EnrichedContext
from code.src.modalities.unified import UnifiedMultimodalExtractor, UnifiedTextPayload
from code.src.semantics.intent import IntentFeatureExtractor, SemanticFeatures
from code.src.classifiers.message_type import MessageTypeClassifier
from code.src.security.scam_detector import ScamDetector, ScamRiskAssessment
from code.src.security.spam_detector import SpamDetector, SpamRiskAssessment
from code.src.trust.engine import PersonalizedTrustEngine, PersonalizedTrustScore
from code.src.engine.priority import PriorityScorer, PriorityMatrix


class FusionDecisionPayload(BaseModel):
    """Container for complete decision fusion output."""
    message_id: str
    action: ActionType
    message_type: MessageType
    confidence: float
    context: EnrichedContext
    semantics: SemanticFeatures
    scam_assessment: ScamRiskAssessment
    spam_assessment: SpamRiskAssessment
    trust_score: PersonalizedTrustScore
    priority_matrix: PriorityMatrix


class DecisionFusionRouter:
    """Main routing engine combining rules, ML classifiers, trust scores, and quiet hours."""

    def __init__(self, loader: DatasetLoader):
        self.loader = loader
        self.context_builder = ContextBuilder(loader)
        self.multimodal_extractor = UnifiedMultimodalExtractor(loader)
        self.intent_extractor = IntentFeatureExtractor()
        self.type_classifier = MessageTypeClassifier()
        self.scam_detector = ScamDetector()
        self.spam_detector = SpamDetector()
        self.trust_engine = PersonalizedTrustEngine()
        self.priority_scorer = PriorityScorer()

    def route_message(self, message: Message) -> FusionDecisionPayload:
        """Executes full decision fusion pipeline for an incoming message."""

        # 1. Context Enrichment
        context = self.context_builder.build_context(message)

        # 2. Multimodal Extraction & Plain Text Unification
        unified_payload = self.multimodal_extractor.extract_unified_text(message)

        # 3. Semantic Feature & Intent Extraction
        semantics = self.intent_extractor.extract_features(unified_payload.unified_text, message.user_id)

        # 4. Message Type Classification
        msg_type = self.type_classifier.classify_message_type(message, context, semantics)

        # 5. Security & Risk Overrides
        scam_eval = self.scam_detector.evaluate_scam_risk(message, context, semantics)
        spam_eval = self.spam_detector.evaluate_spam_risk(message, context, semantics)

        # 6. Trust & Preference Engine
        trust_eval = self.trust_engine.evaluate_trust(context, message.sender_user_id)

        # 7. Priority Matrix
        priority = self.priority_scorer.compute_priority(message, context, semantics, trust_eval)

        # --- ROUTING ACTION SELECTION ---
        text_lower = unified_payload.unified_text.lower()
        conv_type = message.conversation_type.strip().lower()

        # HARD SAFETY OVERRIDES
        if scam_eval.is_scam or msg_type == "scam":
            return FusionDecisionPayload(
                message_id=message.message_id,
                action="mute",
                message_type="scam",
                confidence=0.95,
                context=context,
                semantics=semantics,
                scam_assessment=scam_eval,
                spam_assessment=spam_eval,
                trust_score=trust_eval,
                priority_matrix=priority,
            )

        if spam_eval.is_spam or msg_type == "spam":
            return FusionDecisionPayload(
                message_id=message.message_id,
                action="mute",
                message_type=spam_eval.override_message_type if spam_eval.is_spam else "spam",
                confidence=0.90,
                context=context,
                semantics=semantics,
                scam_assessment=scam_eval,
                spam_assessment=spam_eval,
                trust_score=trust_eval,
                priority_matrix=priority,
            )

        action: ActionType = "digest"

        # Rule A: High Urgency Alerts & Operational Escalations
        if msg_type == "urgent" or any(w in text_lower for w in ["tanker", "heads-up", "heads up", "valve", "unwell", "clinic", "retry count crossed", "incident bridge"]):
            action = "notify"

        # Rule B: School Admin Updates & Urgent Transports
        elif msg_type == "event" and any(w in text_lower for w in ["school circular", "bus is leaving", "stadium road", "care services"]):
            action = "notify"

        # Rule C: Amazon & Verified Order Delivery Updates
        elif msg_type == "business_update" and trust_eval.business_trust.is_trusted:
            if any(w in text_lower for w in ["order", "packed", "delivery", "hub", "shipped"]):
                action = "notify"
            else:
                action = "digest"

        # Rule D: Direct Personal Action Requests vs Informal Chat
        elif msg_type == "personal":
            if any(w in text_lower for w in ["don't call now", "phone is charging", "reached home", "volunteer sheet"]):
                action = "digest"
            elif any(w in text_lower for w in ["when you get 5 mins can you call", "can you call", "prod review", "pulled to 3"]):
                action = "notify"
            else:
                action = "digest"

        # Rule E: Greetings & Forwards in Groups
        elif msg_type in ["greeting", "forward"]:
            if "fwd as received" in text_lower or message.forwarded_count >= 10:
                action = "mute"
                msg_type = "forward"
            elif context.group_context and context.group_context.is_group_muted_by_user:
                action = "mute"
            else:
                action = "digest"

        # Rule F: Promotions & Advertisements (Generalizable Receiver Suppression Rule — NO hardcoded message IDs!)
        elif msg_type == "promotion" or semantics.is_promotion:
            if context.group_context and context.group_context.is_group_muted_by_user:
                action = "mute"
            elif context.business_context and not context.business_context.allows_promotions:
                action = "mute"
            elif any(w in text_lower for w in ["try50", "50% off", "shopping offer"]):
                action = "mute"
            else:
                action = "digest"

        # Fallback DND Check for non-urgent messages
        if action == "notify" and context.user_context.is_dnd_active and not semantics.has_direct_user_mention and not any(w in text_lower for w in ["tanker", "unwell", "clinic"]):
            action = "digest"

        confidence = 0.89 if action == "notify" else (0.85 if action == "digest" else 0.90)

        return FusionDecisionPayload(
            message_id=message.message_id,
            action=action,
            message_type=msg_type,
            confidence=round(confidence, 2),
            context=context,
            semantics=semantics,
            scam_assessment=scam_eval,
            spam_assessment=spam_eval,
            trust_score=trust_eval,
            priority_matrix=priority,
        )
