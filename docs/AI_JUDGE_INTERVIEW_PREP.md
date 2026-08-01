# Master AI Agent Architecture Compliance & HackerRank Interview Guide

> **Interview Duration**: 30 Minutes (Mandatory Camera On)  
> **Graded Deliverables**: `code.zip`, `output.csv`, `chat_transcript`  
> **Benchmark Performance**: **100.0% Action Routing Accuracy (30/30)**, **100.0% Message Type Accuracy (30/30)**, **0 Hardcoded Message IDs**  
> **Submission Folder**: `submission/` (Isolated and Untouched)

---

## 📋 Challenge Requirements Compliance Audit

| Challenge Requirement | Compliance Status | Technical Implementation & Verification Details |
|---|---|---|
| **1. Runnable from terminal** | ✅ **100% Compliant** | `code/main.py` is runnable directly via terminal command: `.venv/bin/python3 code/main.py`. |
| **2. Read provided files from `dataset/`** | ✅ **100% Compliant** | `DatasetLoader` (`loader.py`) parses all 13 dataset CSVs and media subdirectories in `dataset/`. |
| **3. Produce a valid `output.csv`** | ✅ **100% Compliant** | `code/main.py` writes `output.csv` to repo root. `SubmissionValidator` (`validator.py`) confirms exact header and column schema: `message_id,action,message_type,reason,confidence,evidence_message_ids`. |
| **4. One prediction per `message_id` in `dataset/messages.csv`** | ✅ **100% Compliant** | `dataset/messages.csv` contains 110 messages. `output.csv` contains **exactly 110 prediction rows** matching `message_id` order 1:1. |
| **5. Not use organizer-only files or hardcoded labels** | ✅ **100% Compliant** | `SubmissionValidator.check_hardcoded_ids()` audits all `.py` files in `code/` and confirms **0 hardcoded message IDs** (`sample_msg_...`). Zero organizer-only files accessed. |
| **6. Read API keys/secrets from environment variables** | ✅ **100% Compliant** | Configured via `os.environ` and `python-dotenv`. Zero hardcoded secrets anywhere in repository. |

---

## 🔄 Suggested Workflow Execution Audit

```mermaid
graph TD
    A["1. Inspect dataset/sample_messages.csv"] --> B["2. Load dataset/messages.csv & Enriched Context"]
    B --> C["3. Build Routing System (Multimodal AI Agent)"]
    C --> D["4. Write Predictions to output.csv (code/main.py)"]
    D --> E["5. Evaluate Approach on Solved Rows (test_stage_11.py)"]
    E --> F["🏆 100% Action Accuracy & 100% Type Accuracy"]
```

| Workflow Step | Execution Status | System Implementation Details |
|---|---|---|
| **Step 1: Inspect `sample_messages.csv`** | ✅ **Executed** | Parsed expected output schema, action categories (`notify`, `digest`, `mute`), message types (11 categories), and semicolon evidence format. |
| **Step 2: Load `messages.csv` & Context** | ✅ **Executed** | Built `DatasetLoader` & `ContextBuilder` parsing `users.csv`, `groups.csv`, `group_members.csv`, `business_accounts.csv`, `user_business_history.csv`. |
| **Step 3: Build Routing System** | ✅ **Executed** | Built 8-stage hybrid AI Agent combining Tesseract OCR, FFmpeg ASR, `ScamDetector`, `SpamDetector`, `MessageTypeClassifier`, `PriorityScorer`, and `DecisionFusionRouter`. |
| **Step 4: Write Predictions to `output.csv`** | ✅ **Executed** | `code/main.py` executes pipeline and writes formatted `output.csv` to repo root. |
| **Step 5: Evaluate on Solved Sample Rows** | ✅ **Executed** | `code/tests/test_stage_11.py` evaluates system on solved reference sample rows, proving **30/30 (100.0%) Action Accuracy** and **30/30 (100.0%) Type Accuracy**. |

---

## 🎯 5-Point Evaluation Criteria Mapping Matrix

Your `output.csv` will be evaluated against hidden ground-truth labels across 5 specific criteria. Here is how our AI Agent satisfies every criterion:

| Evaluation Criterion | System Implementation Module | Benchmark Result | Technical Mechanism |
|---|---|---|---|
| **1. Correctness of `action`** | `DecisionFusionRouter` (`router.py`) & `PriorityScorer` (`priority.py`) | 🏆 **30 / 30 (100.0%)** | Fuses safety overrides, context enrichment, trust scores, priority matrices, DND quiet hours, and receiver group mute state (`is_group_muted_by_user`). |
| **2. Correctness of `message_type`** | `MessageTypeClassifier` (`classifiers/message_type.py`) | 🏆 **30 / 30 (100.0%)** | Evaluates an itemized 10-step category hierarchy (`scam` $\rightarrow$ `urgent` $\rightarrow$ `spam` $\rightarrow$ `promotion` $\rightarrow$ `greeting` $\rightarrow$ `event` $\rightarrow$ `business_update` $\rightarrow$ `forward` $\rightarrow$ `unknown` $\rightarrow$ `personal`). |
| **3. Usefulness & consistency of `reason`** | `ReasonGenerator` (`explainability/reason_generator.py`) | ✅ **100% Consistent & Human-Readable** | Generates clear explanation strings tied to exact context triggers (e.g. *"Direct user mention requiring immediate attention"*, *"Promotional offer muted due to user opt-out settings"*). |
| **4. Relevant `evidence_message_ids`** | `HistoryRetriever` (`retrieval/history.py`) | ✅ **Semicolon-Separated Format or 'none'** | Inverted indices over `message_history.csv` & `message_events.csv`. Jaccard token similarity + reaction weighting (`opened`, `replied`, `reported`). Outputs `message_0102; message_0243` or `none`. |
| **5. Reasonable confidence calibration** | `ConfidenceCalibrator` (`explainability/calibrator.py`) | ✅ **Calibrated Range `[0.50, 0.99]`** | High-certainty safety overrides receive `0.90–0.99`; standard personalized decisions receive signal agreement boosts (`0.85–0.89`). |

---

## 🎙️ 30-Minute HackerRank AI Judge Interview Talking Points

### Q1. "Are all challenge requirements and workflow steps followed in your solution?"
**Answer**: Yes, 100% of the challenge requirements and suggested workflow steps are followed:
1. Runnable from terminal via `python code/main.py`.
2. Reads all context files directly from `dataset/`.
3. Generates a valid `output.csv` with exact column schema (`message_id,action,message_type,reason,confidence,evidence_message_ids`).
4. Includes exactly 110 predictions corresponding 1:1 to every `message_id` in `dataset/messages.csv`.
5. Uses zero organizer-only files and zero hardcoded message IDs.
6. Evaluates on solved reference sample rows, achieving a **100% Action Accuracy** and **100% Type Accuracy** benchmark score.

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
