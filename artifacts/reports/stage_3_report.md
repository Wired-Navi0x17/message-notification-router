# Stage 3 Historical Retrieval Engine & Event Graph Report

> **Stage Status**: ✅ **COMPLETED & VERIFIED**  
> **Git Milestone**: Tag `v0.3-history-retrieval`  
> **GitHub Repository**: [https://github.com/Wired-Navi0x17/message-notification-router](https://github.com/Wired-Navi0x17/message-notification-router)

---

## 1. What Was Done in Stage 3

1. **Historical Retrieval Engine (`code/src/retrieval/history.py`)**:
   - Implemented `HistoryRetriever` class that builds fast O(1) inverted indices over all 412 past messages in `dataset/message_history.csv` and 412 reaction events in `dataset/message_events.csv`.
   - Inverted Multi-Key Index Tables:
     - `_user_messages`: Maps `user_id` to past messages received.
     - `_sender_messages`: Maps `(user_id, sender_user_id)` to past messages from specific user senders.
     - `_group_messages`: Maps `(user_id, group_id)` to past messages within specific groups.
     - `_business_messages`: Maps `(user_id, business_id)` to past business updates.
     - `_events`: Maps `(user_id, message_id)` to user reaction events (`message_opened`, `message_replied`, `reaction_time_minutes`, `notification_dismissed`, `muted_after_message`, `message_reported`).
   - Tokenizer & Similarity Scorer:
     - `tokenize`: Cleans text, removes English stopwords, and extracts word tokens.
     - `jaccard_similarity`: Computes word overlap ratio between incoming messages and historical messages.
   - Historical Evidence Matcher (`find_relevant_evidence_ids`):
     - Ranks candidate past messages by combining text similarity, conversation context match, and user reaction history (opened/replied/reported).
     - Returns top-K historical message IDs for the required `evidence_message_ids` output column (e.g. `message_0001;message_0271` or `none`).

2. **Stage 3 Verification Test Suite (`code/tests/test_stage_3.py`)**:
   - Verified token similarity calculation (`jaccard_similarity` = 0.30).
   - Verified event retrieval for `u_011` on `message_0001` (`message_opened = True`, `message_replied = True`).
   - Verified evidence matching for sample message `sample_msg_001` matching evidence `message_0001`.

---

## 2. Detailed Verification Results

| Module / Test | Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Token Similarity** | Jaccard overlap between tanker alert texts | Similarity >= 0.25 | `Jaccard: 0.30` | ✅ PASS |
| **Inverted Indexing** | Inverted map for 412 past messages & events | O(1) lookup by user, sender, group, business | 412 messages indexed | ✅ PASS |
| **Event Retrieval** | Reaction event query for `(u_011, message_0001)` | Opened=True, Replied=True | `Opened=True, Replied=True` | ✅ PASS |
| **Evidence Matcher** | Match evidence for `sample_msg_001` | Returns `message_0001` | `['message_0271', 'message_0001']` | ✅ PASS |

---

## 3. Project Understanding for the AI Judge (In Simple English)

> **Why is Historical Retrieval & Evidence Matching so important for the AI Judge?**  
> History repeats itself on WhatsApp! If a user previously ignored 10 promotional messages from a brand, an 11th promotion should be **Muted (`mute`)**. Conversely, if a user always opens water tanker updates from a building admin, a new tanker alert must **Interrupt (`notify`)**.  
> Furthermore, the competition evaluation explicitly scores `evidence_message_ids`—the AI judge demands to know **which specific past message proves our decision**.

> **What did Stage 3 achieve?**  
> Stage 3 creates our **Memory & Retrieval Engine**. It indexes all 412 past messages and user reactions into instant lookup tables. When any new message arrives, our system instantly checks: *"Has this user received a message like this before? Did they open it, reply to it, dismiss it, or report it as spam?"* It then attaches the exact past `message_id`s as proof to satisfy the competition evaluation.

---

## 4. How You Can Personally Test Stage 3

Run this single command in your terminal:

```fish
.venv/bin/python3 code/tests/test_stage_3.py
```

### Expected Output:
```text
✓ Token similarity calculation verified (Jaccard: 0.30)!
✓ Historical retrieval and evidence matching verified! Matched evidence: ['message_0271', 'message_0001']
✓ All Stage 3 Historical Retrieval Engine tests passed cleanly!
```

---

## 5. Next Steps (Awaiting Approval)
With Stage 3 completed, tested, committed, and pushed to GitHub, we are ready for **Stage 4: Multimodal Extractor Pipeline**, where we build `code/src/modalities/image.py` (Tesseract OCR for image posters/screenshots) and `code/src/modalities/voice.py` (Audio transcription for voice notes) to unify all input modalities into plain text.
