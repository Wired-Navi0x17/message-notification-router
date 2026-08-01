"""
Unit verification tests for Stage 5 Semantic Feature & Intent Engine.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.semantics.intent import IntentFeatureExtractor, SemanticFeatures


def test_urgent_water_tanker_intent():
    extractor = IntentFeatureExtractor()
    text = "Tower B folks, quick heads-up. The tanker guy is saying he can wait maybe 20 mins max because he has another stop after this."
    features = extractor.extract_features(text, user_id="u_011")

    assert isinstance(features, SemanticFeatures)
    assert features.is_urgent is True
    assert "heads-up" in features.matched_urgency_keywords or "tanker" in features.matched_urgency_keywords
    print(f"✓ Urgent water tanker intent verified! Matched keywords: {features.matched_urgency_keywords}")


def test_direct_mention_intent():
    extractor = IntentFeatureExtractor()
    text = "@u_010 prod review got pulled to 3, sorry for the last-minute shuffle."
    features = extractor.extract_features(text, user_id="u_010")

    assert features.has_direct_user_mention is True
    assert features.is_urgent is True
    print("✓ Direct user mention intent verified!")


def test_promotion_intent():
    extractor = IntentFeatureExtractor()
    text = "Get 40% OFF at INOX on all movie tickets today! Visit VR website to book now."
    features = extractor.extract_features(text)

    assert features.is_promotion is True
    assert len(features.matched_promo_keywords) > 0
    print(f"✓ Promotion intent verified! Matched keywords: {features.matched_promo_keywords}")


def test_scam_phishing_intent():
    extractor = IntentFeatureExtractor()
    text = "Delivery failed. Pay small reattempt fee at amazonpay-delivery.in and enter OTP to release package."
    features = extractor.extract_features(text)

    assert features.is_scam_suspicious is True
    assert "enter otp" in features.matched_scam_keywords or "reattempt fee" in features.matched_scam_keywords
    print(f"✓ Scam/phishing intent verified! Matched keywords: {features.matched_scam_keywords}")


if __name__ == "__main__":
    test_urgent_water_tanker_intent()
    test_direct_mention_intent()
    test_promotion_intent()
    test_scam_phishing_intent()
    print("✓ All Stage 5 Semantic Feature & Intent Engine tests passed cleanly!")
