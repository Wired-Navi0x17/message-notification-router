# Message Notification Router — AI Judge Interview & Technical Reference Guide

> [!IMPORTANT]
> **AI Judge Interview Preparation**: This document serves as the authoritative technical reference and interview cheat-sheet for the 30-minute live AI Judge Interview following submission.

---

## 1. Executive Summary & Core Philosophy

- **Challenge**: HackerRank Orchestrate (August 2026) — Message Notification Router for WhatsApp.
- **Goal**: Build a personalized, multimodal notification routing system that categorizes incoming WhatsApp messages into `notify` (interrupt now), `digest` (batch for later), or `mute` (suppress as noise/risk).
- **Core Design Philosophy**:
  - **Product Engineering over Notebooks**: Built as a modular Python software package with strict versioning, comprehensive logging, schema validation, and zero runtime crashes.
  - **Deterministic, Debuggable Decision Fusion**: Combines hard security safety rules (scam/spam overrides) with semantic feature extraction and personalized context scoring.
  - **Unified Modality Pipeline**: Converts image posters (via Tesseract OCR) and voice notes (via FFmpeg/ASR transcription) into a normalized plain-text layer, allowing a single high-performance semantic classifier to operate across all modalities.

---

## 2. High-Level Architecture

```mermaid
flowchart TD
    subgraph Data Layer & Ingestion
        A[dataset/messages.csv] --> Loader
        B[dataset/images.csv & media/images/] --> Loader
        C[dataset/voice_notes.csv & media/audio/] --> Loader
        D[Metadata CSVs: users, groups, business, history] --> Loader
    end

    subgraph Modality Unification Layer
        Loader --> TextExtractor[Text Cleaner]
        Loader --> OCRExtractor[Tesseract OCR Engine]
        Loader --> ASRExtractor[FFmpeg / Audio Transcript Engine]
        TextExtractor & OCRExtractor & ASRExtractor --> UnifiedText[Unified Plain Text Object]
    end

    subgraph Context & Retrieval Graph
        UnifiedText --> UserContextBuilder[User Quiet Hours & Preference Analyzer]
        UnifiedText --> GroupBusinessBuilder[Group Role & Business Verification Scorer]
        UnifiedText --> HistoryRetriever[Historical Message & Event Indexer]
    end

    subgraph Decision & Safety Engine
        UserContextBuilder & GroupBusinessBuilder & HistoryRetriever --> SecurityOverride[Security Override Module: Scam/Spam/Phishing]
        SecurityOverride -- Pass --> DecisionFusion[Multi-Criteria Decision Fusion Engine]
        SecurityOverride -- Flagged Scam/Spam --> ForceMute[Action: Mute | Confidence: 0.95+]
        DecisionFusion --> Calibrator[Confidence Calibration & Evidence Matcher]
    end

    subgraph Output Generation
        Calibrator --> OutputGen[output.csv Generator]
        OutputGen --> Validator[Strict Schema Validator]
    end
```

---

## 3. Key Technical Decisions & Justifications

### Q1: Why convert multimodal inputs (images, voice notes) into a unified text layer?
- **Answer**: Image posters (e.g., society notices, sales flyers) and voice notes contain semantic information that boils down to text. Decoupling modality extraction from routing logic keeps the core decision engine deterministic, fast, and debuggable. Image OCR via Tesseract and audio transcription via FFmpeg/ASR feed cleanly into the downstream semantic classifier.

### Q2: Why use a Decision Fusion engine instead of an end-to-end black-box LLM prompt?
- **Answer**:
  1. **Latency & Cost**: Pure LLM inference on every incoming message is slow and expensive for real-time notification routing.
  2. **Security Guarantee**: A scam message must NEVER bypass filters due to LLM hallucinations. Our architecture enforces hard security overrides (e.g., unverified sender + payment request + brand domain mismatch = instant `mute`).
  3. **Explainability**: Our template-based reason generator guarantees consistent, human-readable explanations that directly trace back to decision rules.

### Q3: How is personalization handled?
- **Answer**: Personalization is computed across three contextual vectors:
  - **User Vector**: Quiet hours (`do_not_disturb_window`), historical open/reply/dismissal ratios.
  - **Group Vector**: User role (admin vs member), group mute status, historical reply frequency.
  - **Business Vector**: Account age, verified status, domain age, opt-in/opt-out history, and user transaction records.

---

## 4. Evaluation Metrics & System Validation

| Metric Component | How Strategy Optimizes It |
| :--- | :--- |
| **Action Accuracy (`notify`/`digest`/`mute`)** | Priority Scoring Matrix balancing Utility Score, Risk Score, and Urgency Score. |
| **Message Type Categorization** | Multi-class feature classifier enforcing exact 11 allowed values. |
| **Reason Consistency** | Contextual template synthesizer linking decision path to human explanation. |
| **Evidence Matching** | Historical retrieval indexer matching incoming message text/sender to past `message_id`s in `message_history.csv`. |
| **Confidence Calibration** | Calibrated probability scaling (range `[0.0, 1.0]`) reflecting empirical accuracy on sample validation set. |

---

## 5. How AI Was Utilized During Development

- **Pair-Programming Agent**: Used **Antigravity** (Google DeepMind) for architecture design, incremental feature development, and code verification.
- **Log Transparency**: Every agent session and conversation turn is logged in real-time to `$HOME/hackerrank_orchestrate_august26/log.txt` as per challenge requirements.
- **Disciplined Incremental Software Engineering**: Development followed strict 12-stage version milestones (`v0.0-bootstrap` to `v1.0-release-candidate`), ensuring every commit is a stable, runnable milestone.
- **Git Safety**: Enforced strict policy of zero remote git pushes (`git push` prohibited) to maintain repository integrity.

---

## 6. AI Judge Interview Cheat-Sheet (30-Minute Q&A)

### Probe: "Walk me through how your system routes a message from start to finish."
> **Response**:
> "When a message enters the pipeline, it first passes through the Modality Unification Layer. If it's an image, Tesseract OCR extracts text; if it's a voice note, FFmpeg/ASR transcribes it. Next, the Context Builder retrieves the user's quiet hours, group role, business verification status, and historical interaction events in O(1) time. The message then hits our Safety & Risk Override Module. If flagged as a scam or suspicious phishing attempt, it is immediately muted. Otherwise, the Decision Fusion Engine calculates an Urgency Score, Utility Score, and Risk Score. These scores synthesize into an action (`notify`, `digest`, or `mute`), accompanied by a calibrated confidence score, contextual reason, and historical evidence IDs."

### Probe: "How do you ensure evidence_message_ids are accurate?"
> **Response**:
> "We construct an inverted historical index mapping `(user_id, sender_id, group_id)` to past messages in `message_history.csv` and user reactions in `message_events.csv`. When a new message arrives, we query past messages from the same sender/group for the receiving user, score semantic similarity, and select top-matching message IDs where the user previously interacted."

### Probe: "What happens if a message arrives during quiet hours (DND)?"
> **Response**:
> "Our User Preference Module checks `do_not_disturb_window` (e.g. 22:00-07:00). Unless the message is an urgent direct mention from a trusted family/work group admin or an emergency security alert, non-urgent messages during DND are automatically routed to `digest`."

---

## 7. Submission Checklist for August 7, 2026 Results

- [x] `output.csv` has exactly 110 prediction rows matching `dataset/messages.csv`.
- [x] Required columns in order: `message_id,action,message_type,reason,confidence,evidence_message_ids`.
- [x] Zero null or missing values; all values within allowed enums.
- [x] Runnable terminal command `python code/main.py` generates predictions reliably.
- [x] Full source code packaged into `code.zip`.
- [x] Complete conversation transcript saved at `$HOME/hackerrank_orchestrate_august26/log.txt`.
