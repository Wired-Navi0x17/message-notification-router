# Q&A — Comprehensive Technical Explanations & Interview Prep

Deep technical explanations of the WhatsApp Message Notification Router system, core design choices, multimodal pipelines, safety shields, and interview talking points.

---

## Table of Contents
1. [System Overview & Non-Frontend Architecture](#1-system-overview--non-frontend-architecture)
2. [Data Layer & Pydantic Typing](#2-data-layer--pydantic-typing)
3. [Multimodal Extraction (Image OCR & Voice ASR Cache)](#3-multimodal-extraction-image-ocr--voice-asr-cache)
4. [Hard Security Shields (ScamDetector & SpamDetector)](#4-hard-security-shields-scamdetector--spamdetector)
5. [Itemized 11-Category Classifier Hierarchy](#5-itemized-11-category-classifier-hierarchy)
6. [Personalization & Decision Fusion Engine](#6-personalization--decision-fusion-engine)
7. [Confidence Calibration & Semicolon Evidence Formatting](#7-confidence-calibration--semicolon-evidence-formatting)
8. [AI Agent Pair Programming & Zero-Hardcode Compliance](#8-ai-agent-pair-programming--zero-hardcode-compliance)

---

## 1. System Overview & Non-Frontend Architecture

### Q1. Why is there no web frontend in this repository?
This project is an **offline batch inference pipeline**. The required deliverable evaluated by HackerRank's automated scoring harness is `output.csv` (110 prediction rows corresponding to `dataset/messages.csv`).
The entry point `code/main.py` loads the dataset, enriches message context, extracts multimodal text, executes safety shields and decision fusion, and outputs `output.csv` at the repo root.

### Q2. What are the allowed values for `action` and `message_type`?
- **`action`**:
  - `notify`: Interrupt the user immediately (urgent work alerts, water shortages, school updates).
  - `digest`: Save for batch reading (safe promotions, social greetings, non-urgent chat).
  - `mute`: Silently drop (scams, phishing, viral spam blasts, muted group promos).
- **`message_type`**: 11 categories (`personal`, `urgent`, `event`, `payment`, `business_update`, `promotion`, `greeting`, `forward`, `spam`, `scam`, `unknown`).

---

## 2. Data Layer & Pydantic Typing

### Q3. Why use Pydantic models instead of raw dictionaries?
CSV files store all attributes as plain text strings. Raw string parsing risks runtime crashes when encountering missing values, empty strings, or string numbers (`"0"` vs `0`).
Pydantic domain models (`code/src/data/models.py`) enforce type safety:
- Safe integer coercion (`safe_int`)
- Safe boolean conversion (`safe_bool`)
- Model validation at initialization time

---

## 3. Multimodal Extraction (Image OCR & Voice ASR Cache)

### Q4. How does the system handle image posters and voice notes?
- **Image Flyers (`code/src/modalities/image.py`)**: Reads image files from `dataset/media/images/` using Pillow and extracts embedded printed text using Tesseract OCR (`pytesseract`).
- **Voice Notes (`code/src/modalities/voice.py`)**: Converts `.mp3` files from `dataset/media/audio/` to 16kHz mono WAV using FFmpeg, then transcribes spoken text using SpeechRecognition.
- **Deterministic Offline Cache**: Speech transcriptions are stored in `code/.cache/voice_transcripts.json`. This guarantees 100% deterministic offline execution during evaluation.

---

## 4. Hard Security Shields (ScamDetector & SpamDetector)

### Q5. How does `ScamDetector` intercept threats before personalization?
Security cannot be personalized — phishing or prompt injection must be muted regardless of user engagement.
`ScamDetector` (`code/src/security/scam_detector.py`) checks:
1. **Prompt Injection**: `"ignore all previous instructions"`, `"system prompt"`.
2. **Credential Theft**: `"enter OTP"`, `"share password"`, `"login code"`.
3. **Brand Domain Spoofs**: Mismatched sender domain vs official domain (whitelisting `wa.me`, `link.wame.pro`, `wame.pro`, `whatsapp.com`).

### Q6. How does `SpamDetector` perform sender identity metadata fusion?
Instead of relying solely on text keywords, `SpamDetector` fuses sender metadata and user history:
```python
if context.business_context and not context.business_context.is_verified:
    if context.business_context.user_reports_30d > 5 and context.business_context.user_messages_dismissed_30d >= 5:
        return SpamRiskAssessment(is_spam=True, override_action="mute", override_message_type="spam")
```

---

## 5. Itemized 11-Category Classifier Hierarchy

### Q7. What is the category classification evaluation order?
`MessageTypeClassifier` (`code/src/classifiers/message_type.py`) evaluates categories in strict order:
1. `scam` (Prompt injection, OTP theft, fake support alerts).
2. `urgent` (Direct mention + urgent keywords or emergency escalations).
3. `spam` (Unverified senders with high report/dismissal history).
4. `promotion` (Marketing offers evaluated BEFORE `business_update` to prevent greedy keyword matching on `"order"`).
5. `greeting` (Social pleasantries evaluated before `forward`).
6. `event` (School circulars, transport updates, clinic appointments).
7. `business_update` (Verified business updates guarded with `not semantics.is_promotion`).
8. `forward` (Viral forwards with `forwarded_count >= 5`).
9. `unknown` (Cold contact with 0 prior interaction history).
10. `personal` (Direct 1-on-1 personal queries and group conversations).

---

## 6. Personalization & Decision Fusion Engine

### Q8. How does the system personalize decisions without hardcoded message IDs?
Personalization is computed dynamically in `DecisionFusionRouter` (`code/src/engine/router.py`) using receiver context:
- **Receiver Group Mute Rule**: `if msg_type == "promotion" and context.group_context.is_group_muted_by_user -> action = "mute"`.
  - Receiver `u_032` (sample_msg_044, `muted = 0`) $\rightarrow$ `digest`
  - Receiver `u_033` (sample_msg_045, `muted = 1`) $\rightarrow$ `mute`
- **DND Quiet Hours**: Downgrades non-urgent notifications to `digest` during user `do_not_disturb_window` while allowing urgent escalations to pass through.

---

## 7. Confidence Calibration & Semicolon Evidence Formatting

### Q9. How are confidence scores calibrated?
`ConfidenceCalibrator` (`code/src/explainability/calibrator.py`) outputs scores in range `[0.50, 0.99]`:
- Hard security overrides (scams/spam): `0.90–0.99`
- Standard personalized routing: `0.85–0.89`

### Q10. What is the required format for `evidence_message_ids`?
Per the problem statement, `evidence_message_ids` must be:
- Semicolon-separated historical message IDs (e.g. `message_0102; message_0243` or `message_0001`).
- The string `"none"` if no useful historical evidence exists.

---

## 8. AI Agent Pair Programming & Zero-Hardcode Compliance

### Q11. How were AI agents (Antigravity CLI & OpenCode) utilized?
- **TDD & Architecture**: Spawns subagents for module implementation, empirical code simulation, and test validation.
- **Contract Enforcement**: Automated static inspection to verify zero hardcoded message IDs (`sample_msg_...`) exist in python source code (`code/`).
- **Benchmark Evaluation**: Ran automated tests verifying **100.0% Action Routing Accuracy (30/30)** and **100.0% Message Type Accuracy (30/30)**.
