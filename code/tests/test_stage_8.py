"""
Unit verification tests for Stage 8 Contextual & Behavioral Trust Engine.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from code.src.data.loader import DatasetLoader
from code.src.context.builder import ContextBuilder
from code.src.trust.engine import PersonalizedTrustEngine, PersonalizedTrustScore
from code.src.data.models import Message


def test_business_trust_scoring():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    context_builder = ContextBuilder(loader)
    trust_engine = PersonalizedTrustEngine()

    # Message from verified Amazon India business_001 to u_001
    msg = Message(
        message_id="test_biz_trust_001",
        user_id="u_001",
        conversation_type="business",
        business_id="business_001",
        created_at="2026-07-31 08:28",
        message_text="Your order ending 4821 has been packed."
    )
    ctx = context_builder.build_context(msg)
    trust_eval = trust_engine.evaluate_trust(ctx)

    assert isinstance(trust_eval, PersonalizedTrustScore)
    assert trust_eval.business_trust.is_verified is True
    assert trust_eval.business_trust.is_trusted is True
    assert trust_eval.overall_trust_score >= 0.70
    print(f"✓ Business Trust Scoring verified! Score: {trust_eval.overall_trust_score}")


def test_group_trust_scoring():
    loader = DatasetLoader(dataset_dir="dataset").load_all()
    context_builder = ContextBuilder(loader)
    trust_engine = PersonalizedTrustEngine()

    # Group message in unmuted group_002 to u_011
    msg = Message(
        message_id="test_grp_trust_002",
        user_id="u_011",
        conversation_type="group",
        group_id="group_002",
        sender_user_id="u_043",
        created_at="2026-07-31 11:09",
        message_text="Tower B water tanker update."
    )
    ctx = context_builder.build_context(msg)
    trust_eval = trust_engine.evaluate_trust(ctx, sender_user_id="u_043")

    assert trust_eval.group_trust.group_type == "society"
    assert trust_eval.group_trust.is_group_muted is False
    assert trust_eval.overall_trust_score >= 0.50
    print(f"✓ Unmuted Group Trust Scoring verified! Score: {trust_eval.overall_trust_score}")

    # Verify group_001 (muted by u_001) properly applies mute penalty
    msg_muted = Message(
        message_id="test_grp_muted_001",
        user_id="u_001",
        conversation_type="group",
        group_id="group_001",
        created_at="2026-07-31 11:09",
        message_text="Muted family group message."
    )
    ctx_muted = context_builder.build_context(msg_muted)
    trust_muted = trust_engine.evaluate_trust(ctx_muted)
    assert trust_muted.group_trust.is_group_muted is True
    assert trust_muted.overall_trust_score < 0.50
    print(f"✓ Muted Group Penalty verified! Score: {trust_muted.overall_trust_score}")


if __name__ == "__main__":
    test_business_trust_scoring()
    test_group_trust_scoring()
    print("✓ All Stage 8 Contextual & Behavioral Trust Engine tests passed cleanly!")
