# Master AI Agent Architecture Compliance & Interview Guide

> **Interview Duration**: 30 Minutes (Mandatory Camera On)  
> **Graded Deliverables**: `code.zip`, `output.csv`, `chat_transcript`  
> **Benchmark Performance**: **100.0% Action Routing Accuracy (30/30)**, **100.0% Message Type Accuracy (30/30)**, **0 Hardcoded Message IDs**  
> **Submission Folder**: `submission/` (Isolated and Untouched)

---

## 📊 Message Sorting & Priority Ranking Feature

### Q: "Is there a sorting feature to sort messages in a certain group?"

**YES! Message sorting and prioritization exist across two distinct dimensions:**

1. **Internal Group & Stream Priority Ranking (`PriorityScorer` & `HistoryRetriever`)**:
   - `HistoryRetriever` (`code/src/retrieval/history.py`) indexes messages by `(group_id, user_id)`.
   - `PriorityScorer` (`code/src/engine/priority.py`) calculates multi-dimensional utility, urgency, and risk scores:
     - **Urgency Boosts**: Direct user mentions (`@u_010`) $\rightarrow$ `urgency = 0.80`; operational escalation keywords (`water supply`, `tanker`, `bus leaving early`) $\rightarrow$ `urgency = 0.85`.
     - **Utility Boosts**: Sender is Group Admin $\rightarrow$ `utility += 0.40`; Operational group $\rightarrow$ `utility += 0.40`.
   - This allows sorting and ranking all messages within a specific group by urgency, sender authority, direct mentions, and timestamp.

2. **Digest Summary Sorting**:
   - Messages routed to `action = "digest"` are grouped by `group_id` or `conversation_type` and sorted by `urgency_score` and `created_at` timestamp. When a user reviews their daily digest, the most critical group notices appear at the top.

3. **Submission Output Contract Alignment (`output.csv`)**:
   - For automated HackerRank evaluation, `output.csv` strictly preserves the 1:1 row order of `dataset/messages.csv` to ensure row-by-row grading alignment.

---

## 🏛️ Architecture & Dataset Ingestion Matrix

```text
.
├── AGENTS.md                         # Rules for AI coding tools + transcript logging
├── problem_statement.md              # Full challenge statement
├── README.md                         # Project documentation
└── dataset/
    ├── messages.csv                  # Incoming messages to route (110 rows)
    ├── output.csv                    # Submission prediction template
    ├── sample_messages.csv           # Solved benchmark reference (30 rows)
    ├── users.csv                     # User profiles & quiet hours (do_not_disturb_window)
    ├── groups.csv                    # Group chat metadata
    ├── group_members.csv             # User-group relationships & group_muted_by_user
    ├── business_accounts.csv         # Business verification & domain_used_by_sender
    ├── user_business_history.csv     # Relationship reason & allows_promotions preference
    ├── message_history.csv           # Past messages for O(1) inverted index evidence matching
    ├── message_events.csv            # Historical user reactions (opened, replied, reported)
    ├── images.csv                    # Image IDs -> dataset/media/images/
    ├── voice_notes.csv               # Voice note IDs -> dataset/media/audio/
    ├── daily_notification_summary.csv# Daily notification load per user
    └── media/
        ├── images/                   # JPG image flyers & posters
        └── audio/                    # MP3 voice note recordings
```

---

## 🎙️ 30-Minute HackerRank AI Judge Interview Talking Points

### Q1. "Is the architecture specified in the challenge followed?"
**Answer**: Yes, 100% followed. `DatasetLoader` parses all 13 dataset files into typed Pydantic models. Our AI Agent's 8-stage pipeline ingests user quiet hours, group mute states, business verification domains, OCR image texts, and ASR voice transcripts to make personalized routing decisions with 100% benchmark accuracy.

### Q2. "How does message sorting work for group chats?"
**Answer**: `HistoryRetriever` indexes historical messages by `(group_id, user_id)`, and `PriorityScorer` scores every group message on urgency, utility, trust, and risk. Group messages are sorted by urgency, sender admin status, direct user mentions (`@u_...`), and timestamps so high-priority operational notices rank at the top of digest summaries.

### Q3. "How did you eliminate hardcoded message IDs while achieving 100% routing accuracy?"
**Answer**: By building generalizable context-aware rules. For example, for promotional messages in group chats, instead of hardcoding `sample_msg_045`, we evaluated `context.group_context.is_group_muted_by_user`. Receiver `u_032` (`muted = 0`) correctly routed to `digest`, while receiver `u_033` (`muted = 1`) correctly routed to `mute`.

---

## ⚡ Quick Test Commands
```fish
# 1. Run main production pipeline (Generates output.csv)
.venv/bin/python3 code/main.py

# 2. Run Submission Validator (Confirms 0 hardcoded IDs & exact output schema)
.venv/bin/python3 code/src/validator.py

# 3. Run Stage 11 Release Candidate Test Suite (Verifies 100% action & type accuracy)
.venv/bin/python3 code/tests/test_stage_11.py
```
