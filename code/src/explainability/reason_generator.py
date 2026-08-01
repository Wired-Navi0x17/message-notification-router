"""
Reason and Evidence Generator for WhatsApp Message Notification Router.
Generates human-readable explanation strings and retrieves historical evidence IDs.
"""

from typing import Tuple, List
from code.src.engine.router import FusionDecisionPayload
from code.src.retrieval.history import HistoryRetriever


class ReasonGenerator:
    """Generates concise explanation reasons and matches evidence IDs."""

    def __init__(self, history_retriever: HistoryRetriever):
        self.retriever = history_retriever

    def generate_reason_and_evidence(self, decision: FusionDecisionPayload) -> Tuple[str, str]:
        msg = decision.context.message
        action = decision.action
        msg_type = decision.message_type

        # 1. Generate Explanation Reason
        if decision.scam_assessment.is_scam:
            reason = decision.scam_assessment.reason or "Security alert: Suspicious scam or phishing risk detected."
        elif decision.spam_assessment.is_spam:
            reason = decision.spam_assessment.reason or "Unwanted spam noise or viral forward detected."
        elif msg_type == "urgent":
            if decision.semantics.has_direct_user_mention:
                reason = "Direct user mention requiring immediate attention or action."
            else:
                reason = "Time-sensitive operational or emergency update requiring immediate notification."
        elif msg_type == "business_update":
            reason = "Legitimate business transaction or delivery status update from a verified account."
        elif msg_type == "event":
            reason = "Scheduled event reminder or operational school/transport update."
        elif msg_type == "promotion":
            if action == "mute":
                reason = "Promotional offer muted due to user opt-out settings or muted group preference."
            else:
                reason = "Promotional offer saved in digest for review at a convenient time."
        elif msg_type == "greeting":
            if action == "mute":
                reason = "Social greeting in muted group saved to avoid interruption."
            else:
                reason = "Social greeting included in non-intrusive digest summary."
        elif msg_type == "forward":
            reason = "Forwarded message routed to digest or muted based on user interaction history."
        elif msg_type == "unknown":
            reason = "Unfamiliar sender query without prior conversation history."
        else:
            if action == "notify":
                reason = "High-priority direct personal message."
            elif action == "digest":
                reason = "Non-urgent personal message summarized for later reading."
            else:
                reason = "Low-priority message muted based on user preference."

        # 2. Retrieve Matching Historical Evidence IDs (semicolon-separated or 'none')
        evidence_ids = self.retriever.find_relevant_evidence_ids(msg, top_k=2)
        if evidence_ids and evidence_ids != ["none"]:
            evidence_str = "; ".join(sorted(evidence_ids))
        else:
            evidence_str = "none"

        return reason, evidence_str
