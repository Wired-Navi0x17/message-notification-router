# Message Notification Router — Development Journey & Progress

This document tracks the software development roadmap, version milestones, git tags, and completion verification status for the WhatsApp Message Notification Router system.

Every version milestone represents a stable software increment that runs without crashing, generates a valid `output.csv`, and introduces exactly one major capability.

---

## Progress Overview

| Phase | Description | Total Milestones | Completed | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0** | Foundation & Pipeline Infrastructure | 12 (v0.1 – v0.12) | 0 / 12 | ⏳ Pending |
| **Phase 1** | Multimodal Understanding & Semantic Layer | 13 (v1.0 – v1.12) | 0 / 13 | ⏳ Pending |
| **Phase 2** | Decision Engine, Fusion & Optimization | 13 (v2.0 – v2.12) | 0 / 13 | ⏳ Pending |

---

## Milestone Matrix

### Phase 0: Foundation Pipeline

- [ ] **v0.1**: Project Bootstrap — Repository structure, configuration system, logger, dataset loader (`dataset/*.csv`).
- [ ] **v0.2**: Unified Data Model — Convert raw CSV rows into normalized `Message` dataclass/Pydantic objects.
- [ ] **v0.3**: Context Builder — Join `users`, `groups`, `group_members`, `business_accounts`, `user_business_history`, `daily_notification_summary` into `Context` objects.
- [ ] **v0.4**: Historical Retrieval Engine — Load `message_history` and `message_events`, build fast O(1) lookup tables for past messages and user actions.
- [ ] **v0.5**: Output Generator — Generate valid `output.csv` format from Day 1 (even with baseline placeholder predictions).
- [ ] **v0.6**: Reason Generator — Standardized, context-aware human-readable template explanations.
- [ ] **v0.7**: Confidence Engine — Base heuristic confidence scoring module (0.0 to 1.0).
- [ ] **v0.8**: Evidence Engine — Retrieve and rank relevant historical message IDs (`evidence_message_ids`).
- [ ] **v0.9**: Validation Pipeline — Validate schemas, null fields, media paths, duplicate IDs, and allowed enum values.
- [ ] **v0.10**: CLI Interface — Terminal command execution `python code/main.py` producing submission `output.csv`.
- [ ] **v0.11**: Integration — Complete end-to-end integration of Phase 0 infrastructure.
- [ ] **v0.12**: Phase 0 Freeze — Lock baseline infrastructure and tag release `v0.12`.

---

### Phase 1: Message Understanding & Multimodal Processing

- [ ] **v1.0**: Text Understanding — Intent, urgency, promotion, greeting, spam, scam, payment, business update, and event text classifier.
- [ ] **v1.1**: Image Understanding — OCR pipeline with Tesseract to extract image text into unified text layer.
- [ ] **v1.2**: Voice Understanding — Audio transcription pipeline with Whisper/ASR to convert audio to plain text.
- [ ] **v1.3**: Unified Semantic Layer — Normalize all incoming modalities (text, image, audio) into plain text representations.
- [ ] **v1.4**: Message Type Classifier — 11-category classifier (`personal`, `urgent`, `event`, `payment`, `business_update`, `promotion`, `greeting`, `forward`, `spam`, `scam`, `unknown`).
- [ ] **v1.5**: Spam Detector — Independent high-precision spam detection module.
- [ ] **v1.6**: Scam Detector — High-priority security and scam risk override module.
- [ ] **v1.7**: Urgency Detector — Emergency keyword, deadline, money due, and direct mention analyzer.
- [ ] **v1.8**: Business Trust Module — Business verification, domain matching, account age, and user interaction scorer.
- [ ] **v1.9**: Group Trust Module — Group context, admin role, user membership activity, and mute status scorer.
- [ ] **v1.10**: User Preference Module — DND quiet hours, past opens, replies, dismissals, and reports analyzer.
- [ ] **v1.11**: Personalization Layer — Synthesize semantic scores, trust scores, and user preferences into personal score.
- [ ] **v1.12**: Phase 1 Freeze — Lock message understanding pipeline and tag release `v1.12`.

---

### Phase 2: Decision Engine & Submission Candidate

- [ ] **v2.0**: Routing Engine — Action router mapping personalized scores to `notify`, `digest`, `mute`.
- [ ] **v2.1**: Hard Rule Engine — Override rules for security (scam/spam), quiet hours, and admin emergency alerts.
- [ ] **v2.2**: Priority Scoring — Multi-dimensional Utility, Risk, and Urgency matrix.
- [ ] **v2.3**: Decision Fusion — Combine rules, semantic predictions, context, and historical features.
- [ ] **v2.4**: Confidence Calibration — Calibrate probability output to match empirical precision.
- [ ] **v2.5**: Reason Selection — Synthesize decision path into short, accurate human-readable explanation.
- [ ] **v2.6**: Evidence Ranking — Rank and assign top historical message IDs for evidence output.
- [ ] **v2.7**: Full Inference Execution — Execute full inference across `dataset/messages.csv` (110 rows).
- [ ] **v2.8**: Error Analysis — Detailed evaluation against `dataset/sample_messages.csv` baseline.
- [ ] **v2.9**: Threshold Tuning — Optimize routing thresholds to maximize precision and recall metrics.
- [ ] **v2.10**: Performance Optimization — Implement caching, vector lookup optimizations, and batching.
- [ ] **v2.11**: Submission Validation — Complete validation of output format, row count, and zip bundle packaging.
- [ ] **v2.12**: Release Candidate — Final code freeze, full submission verification, and tag release `v2.12`.

---

## Log History & Milestones

| Timestamp | Version Tag | Git Commit | Milestone | Verification Note |
| :--- | :--- | :--- | :--- | :--- |
| 2026-08-01 | Initial | Init | Cloned base repository & initialized roadmap | Environment and repository verified |
