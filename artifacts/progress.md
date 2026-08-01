# Message Notification Router — 12-Stage Development Journey & Progress

> [!CAUTION]
> **STRICT GIT CONSTRAINT**: **NEVER PUSH TO GITHUB** under any circumstances unless the user explicitly and state-clearly issues a command/request to push. All commits and tags must remain strictly local.

---

## Executive Summary & Stage Roadmap

This document outlines the 12-stage engineering plan for building the WhatsApp Message Notification Router. The project is designed as an enterprise software product where every stage delivers a stable, runnable, non-breaking milestone with full empirical validation.

---

## Tooling & Environment Stack

| Category | Primary Tools / Libraries | Purpose |
| :--- | :--- | :--- |
| **Runtime & Core** | Python 3.12+, Pydantic v2, Dataclasses | Data models, type enforcement, core engine |
| **Data Processing** | Pandas, NumPy, CSV Standard Library | Fast indexing, CSV parsing, vector ops |
| **Image OCR** | Tesseract (v5.5.3), Pillow (PIL) | Text extraction from posters/screenshots |
| **Voice Transcription** | FFmpeg (v8.1.2), Whisper / SpeechRecognition | Audio decoding and transcript extraction |
| **NLP & Semantics** | SentenceTransformers, Scikit-learn, Regex | Intent classification, similarity, embeddings |
| **Configuration & Logging**| Python-dotenv, Logging module | Dynamic configuration, audit trails |
| **Validation & Testing** | Pytest, Custom Schema Validator | Format compliance, metric benchmarking |

---

## 12-Stage Engineering Matrix

### Stage 0: System Verification, Dependency Management & Bootstrapping
- **Goal**: Verify host system binaries, generate `requirements.txt`, setup virtualenv, and ensure clean repository baseline.
- **Tools**: `tesseract`, `ffmpeg`, `python3`, `pip`, `venv`.
- **Deliverables**:
  - `requirements.txt` with locked dependency versions.
  - Verified system binaries (`tesseract 5.5.3`, `ffmpeg 8.1.2`).
  - `.venv` virtual environment configuration.
- **Definition of Done**: Command `python -c "import pydantic, PIL"` runs cleanly inside activated virtual environment.
- **Git Milestone**: `v0.0-bootstrap`

---

### Stage 1: Dataset Schema & Unified Data Engine
- **Goal**: Read all 12 CSV dataset files and parse raw rows into unified `Message` and domain schema objects.
- **Tools**: Pydantic v2, `csv`, Python typing.
- **Deliverables**:
  - `code/src/data/models.py` (Unified `Message`, `User`, `Group`, `Business` dataclasses).
  - `code/src/data/loader.py` (Resilient dataset loader).
- **Definition of Done**: All incoming messages converted into uniform `Message` objects with normalized timestamps and media IDs.
- **Git Milestone**: `v0.1-data-engine`

---

### Stage 2: Context Enrichment Engine
- **Goal**: Join relational metadata into consolidated context containers (`UserContext`, `GroupContext`, `BusinessContext`, `ConversationContext`).
- **Tools**: Python dictionaries, Pandas indexing.
- **Deliverables**:
  - `code/src/context/builder.py` (Context lookup graph).
- **Definition of Done**: Given any `message_id`, retrieve complete enriched context in O(1) time.
- **Git Milestone**: `v0.2-context-engine`

---

### Stage 3: Historical Retrieval & Event Graph
- **Goal**: Index historical message streams (`message_history.csv`) and user reaction events (`message_events.csv`).
- **Tools**: Hash maps, inverted text indices, Pandas.
- **Deliverables**:
  - `code/src/retrieval/history.py` (Fast historical message & action lookup tables).
- **Definition of Done**: Instant query of user's past interaction history with specific senders, groups, or message patterns.
- **Git Milestone**: `v0.3-history-retrieval`

---

### Stage 4: Multimodal Extractor Pipeline
- **Goal**: Transcribe images and voice notes into unified plain text representation.
- **Tools**: `PIL`, `tesseract` (OCR), `ffmpeg` + `whisper` / audio decoder (ASR).
- **Deliverables**:
  - `code/src/modalities/image.py` (Image text extraction).
  - `code/src/modalities/voice.py` (Audio transcription).
  - `code/src/modalities/unified.py` (Plain text normalizer).
- **Definition of Done**: All multimodal messages (image posters, voice notes) produce clean text representations for the text routing engine.
- **Git Milestone**: `v0.4-multimodal-pipeline`

---

### Stage 5: Semantic Feature & Intent Engine
- **Goal**: Extract semantic intent signals (payments, deadlines, meetings, promotions, greetings, alerts).
- **Tools**: Regular expressions, Keyword taxonomies, SentenceTransformers / Scikit-learn.
- **Deliverables**:
  - `code/src/semantics/intent.py` (Semantic intent & keyword extractor).
- **Definition of Done**: Extracted intent scores and key phrases attached to every message object.
- **Git Milestone**: `v0.5-semantic-engine`

---

### Stage 6: Multi-Class Message Category Classifier
- **Goal**: Predict the best-fit `message_type` from the 11 allowed schema categories:
  `personal`, `urgent`, `event`, `payment`, `business_update`, `promotion`, `greeting`, `forward`, `spam`, `scam`, `unknown`.
- **Tools**: Multi-class rules + TF-IDF / Scikit-learn Naive Bayes / Transformer classifier.
- **Deliverables**:
  - `code/src/classifiers/message_type.py`.
- **Definition of Done**: Every message assigned a valid `message_type` from the 11 allowed values with zero schema violations.
- **Git Milestone**: `v0.6-type-classifier`

---

### Stage 7: Safety, Security & Risk Override Modules
- **Goal**: Detect scams, phishing links, unverified sender spoofing, and malicious spam to guarantee security overrides.
- **Tools**: Phishing heuristics, domain age verification, report history, regex pattern matcher.
- **Deliverables**:
  - `code/src/security/scam_detector.py`.
  - `code/src/security/spam_detector.py`.
- **Definition of Done**: High-risk messages (OTP scams, fake delivery payments, suspicious domain links) are flagged with 100% priority for `mute`.
- **Git Milestone**: `v0.7-security-overrides`

---

### Stage 8: Contextual & Behavioral Trust Engine
- **Goal**: Compute business trust score, group trust score, and user preference alignment score.
- **Tools**: Behavioral heuristics, weighted interaction matrix.
- **Deliverables**:
  - `code/src/trust/business_trust.py` (Verification, account age, domain matching).
  - `code/src/trust/group_trust.py` (Admin role, group type, user mute state).
  - `code/src/trust/user_preference.py` (Quiet hours / DND, open rates, dismissals).
- **Definition of Done**: Quantitative trust and preference scores attached to each message context.
- **Git Milestone**: `v0.8-trust-engine`

---

### Stage 9: Personalization & Decision Fusion Engine
- **Goal**: Fuse rules, semantic scores, trust metrics, and user preferences into final routing decisions (`notify`, `digest`, `mute`).
- **Tools**: Multi-criteria decision decision matrix, priority scoring engine.
- **Deliverables**:
  - `code/src/engine/router.py`.
  - `code/src/engine/priority.py` (Utility vs Risk vs Urgency matrix).
- **Definition of Done**: Deterministic and personalized action assignment for every incoming message.
- **Git Milestone**: `v0.9-decision-fusion`

---

### Stage 10: Confidence Calibration & Reason/Evidence Engine
- **Goal**: Calibrate confidence values (0.0 to 1.0), select top historical evidence message IDs, and generate clear human explanations.
- **Tools**: Probability scaler, historical similarity matcher, explanation templates.
- **Deliverables**:
  - `code/src/engine/confidence.py`.
  - `code/src/engine/reason.py`.
  - `code/src/engine/evidence.py`.
- **Definition of Done**: Every prediction includes calibrated `confidence`, human-readable `reason`, and relevant `evidence_message_ids` (or `none`).
- **Git Milestone**: `v0.10-confidence-evidence`

---

### Stage 11: Validation, Benchmark Evaluation & Release Candidate
- **Goal**: Run strict validation pipeline on `output.csv`, evaluate accuracy against `sample_messages.csv`, and assemble submission package `code.zip`.
- **Tools**: Custom validator script, Pytest benchmark suite, `zipfile`.
- **Deliverables**:
  - `code/src/validator.py` (Schema & null checking).
  - `code/evaluation/main.py` (Evaluation metrics runner).
  - `output.csv` (Final prediction file for all 110 messages).
  - `code.zip` (Submission package).
- **Definition of Done**: `output.csv` passes all schema checks, evaluation scripts report accuracy, and submission package is ready.
- **Git Milestone**: `v1.0-release-candidate`

---

## Detailed Milestone Execution Log

| Stage | Milestone Tag | Status | Verified Output | Commit Hash | Timestamp |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 0** | `v0.0-bootstrap` | ⏳ Pending | Tool binaries & virtualenv verified | — | — |
| **Stage 1** | `v0.1-data-engine` | ⏳ Pending | CSV models & loader functional | — | — |
| **Stage 2** | `v0.2-context-engine` | ⏳ Pending | Context enrichment functional | — | — |
| **Stage 3** | `v0.3-history-retrieval` | ⏳ Pending | Historical index functional | — | — |
| **Stage 4** | `v0.4-multimodal-pipeline` | ⏳ Pending | OCR & audio transcription active | — | — |
| **Stage 5** | `v0.5-semantic-engine` | ⏳ Pending | Intent features extracted | — | — |
| **Stage 6** | `v0.6-type-classifier` | ⏳ Pending | 11 message types categorized | — | — |
| **Stage 7** | `v0.7-security-overrides` | ⏳ Pending | Scam & spam overrides locked | — | — |
| **Stage 8** | `v0.8-trust-engine` | ⏳ Pending | Trust & preference scores active | — | — |
| **Stage 9** | `v0.9-decision-fusion` | ⏳ Pending | Action router functional | — | — |
| **Stage 10**| `v0.10-confidence-evidence`| ⏳ Pending | Calibrated reasons & evidence matched | — | — |
| **Stage 11**| `v1.0-release-candidate` | ⏳ Pending | Final output.csv & zip package verified | — | — |
