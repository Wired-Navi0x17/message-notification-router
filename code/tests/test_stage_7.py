"""
Unit verification tests for Stage 7 Safety, Security & Risk Override Modules.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.data.loader import DatasetLoader
from code.src.context.builder import ContextBuilder, BusinessContext
from code.src.semantics.intent import IntentFeatureExtractor
from code.src.security.scam_detector import ScamDetector, ScamRiskAssessment
from code.src.security.spam_detector import SpamDetector, SpamRiskAssessment
from code.src.data.models import Message


def test_scam_detector_phishing_otp():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    context_builder = ContextBuilder(loader)
    intent_extractor = IntentFeatureExtractor()
    scam_detector = ScamDetector()

    # Phishing message requesting OTP reattempt fee
    msg = Message(
        message_id="test_scam_001",
        user_id="u_001",
        conversation_type="business",
        business_id="business_036",
        created_at="2026-05-23 17:46",
        message_text="Delivery failed. Pay small reattempt fee at amazonpay-delivery.in and enter OTP to release package."
    )
    ctx = context_builder.build_context(msg)
    semantics = intent_extractor.extract_features(msg.message_text, msg.user_id)

    assessment = scam_detector.evaluate_scam_risk(msg, ctx, semantics)

    assert isinstance(assessment, ScamRiskAssessment)
    assert assessment.is_scam is True
    assert assessment.override_action == "mute"
    assert assessment.override_message_type == "scam"
    print(f"✓ Scam Detector verified! Reason: {assessment.reason}")


def test_spam_detector_viral_forward():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    context_builder = ContextBuilder(loader)
    intent_extractor = IntentFeatureExtractor()
    spam_detector = SpamDetector()

    # Highly forwarded promotional message
    msg = Message(
        message_id="test_spam_001",
        user_id="u_001",
        conversation_type="group",
        group_id="group_001",
        created_at="2026-07-31 10:00",
        message_text="Forwarded many times: Win 10000 rupees cashback instantly by downloading this app!",
        forwarded_count=12
    )
    ctx = context_builder.build_context(msg)
    semantics = intent_extractor.extract_features(msg.message_text, msg.user_id)

    assessment = spam_detector.evaluate_spam_risk(msg, ctx, semantics)

    assert isinstance(assessment, SpamRiskAssessment)
    assert assessment.is_spam is True
    assert assessment.override_action == "mute"
    assert assessment.override_message_type == "spam"
    print(f"✓ Spam Detector verified! Reason: {assessment.reason}")


if __name__ == "__main__":
    test_scam_detector_phishing_otp()
    test_spam_detector_viral_forward()
    print("✓ All Stage 7 Safety, Security & Risk Override Modules tests passed cleanly!")
