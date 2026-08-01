# Implementation Plan - WhatsApp Message Notification Router

## Goal Description
Build an enterprise-grade, deterministic, debuggable **Message Notification Router** for WhatsApp messages that accurately routes incoming multimodal messages (text, image posters/screenshots, voice notes) into `notify`, `digest`, or `mute`.

The project is structured as a robust production software engineering pipeline rather than an ad-hoc notebook. The development roadmap is divided into **12 Stages** (Stage 0 to Stage 11), where every milestone delivers a stable, runnable, non-breaking version increment with empirical validation.

---

## Strict Security & Git Constraints

> [!CAUTION]
> **STRICT GIT PUSH PROHIBITION**: **NEVER PUSH TO GITHUB** under any circumstances unless the user explicitly and state-clearly issues a command/request to push. All git commits and version tags (`v0.0-bootstrap` ... `v1.0-release-candidate`) must remain strictly local on the `main` branch.

---

## User Review Required

> [!IMPORTANT]
> **Artifacts Directory Layout**: All project documentation `.md` files have been organized inside the `artifacts/` directory within the workspace:
> - `artifacts/progress.md`: Detailed 12-stage execution matrix with tool specifications and completion criteria.
> - `artifacts/project_details.md`: Comprehensive reference guide and Q&A cheat-sheet for the 30-minute **AI Judge Interview**.
> - `artifacts/AGENTS.md`: Agent execution contract and real-time conversation logging rules (`$HOME/hackerrank_orchestrate_august26/log.txt`).
> - `artifacts/implementation_plan.md`: This technical design document.

> [!NOTE]
> **Host Tool Verification (Stage 0)**:
> - Tesseract OCR binary: `/usr/bin/tesseract` (v5.5.3) — Verified available.
> - FFmpeg binary: `/usr/bin/ffmpeg` (v8.1.2) — Verified available.
> - Python 3 environment: Virtual environment `.venv` with `requirements.txt` containing `pydantic`, `pandas`, `pil`, `tesseract`, `whisper`, and `scikit-learn`.

---

## 12-Stage Software Architecture & Roadmap

```mermaid
flowchart TD
    subgraph Stage 0: Infrastructure & Tools
        S0[Tool Verification, requirements.txt, .venv, Repo Setup]
    end

    subgraph Stage 1-3: Ingestion, Context & History
        S1[Stage 1: Unified Message Data Model & CSV Loader]
        S2[Stage 2: Context Enrichment Graph: User, Group, Business]
        S3[Stage 3: Historical Retrieval Engine & Event Indexer]
    end

    subgraph Stage 4-6: Multimodal Processing & Semantics
        S4[Stage 4: Multimodal Extractor: OCR & Audio ASR to Text]
        S5[Stage 5: Semantic Intent & Keyword Analyzer]
        S6[Stage 6: Multi-Class 11-Category Message Type Classifier]
    end

    subgraph Stage 7-8: Security Overrides & Trust Engine
        S7[Stage 7: Security Overrides: Scam, Spam, Phishing Filter]
        S8[Stage 8: Behavioral Trust & User Preference Scorer]
    end

    subgraph Stage 9-11: Decision Fusion, Calibration & Release
        S9[Stage 9: Decision Fusion & Priority Router]
        S10[Stage 10: Confidence Calibration, Reason & Evidence Matcher]
        S11[Stage 11: Schema Validator, Benchmark Eval & Release Candidate]
    end

    S0 --> S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8 --> S9 --> S10 --> S11
```

---

## 12-Stage Roadmap Summary

| Stage | Goal | Core Tools | Definition of Done | Git Tag |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 0** | Tool verification, dependencies & setup | `tesseract`, `ffmpeg`, `pip`, `venv` | `requirements.txt` generated, `.venv` activated & verified | `v0.0-bootstrap` |
| **Stage 1** | Data model & CSV loader | Pydantic v2, Dataclasses, `csv` | All 12 CSV datasets parsed into uniform `Message` objects | `v0.1-data-engine` |
| **Stage 2** | Context enrichment engine | Python dicts, Pandas indexing | O(1) context lookup for user, group, and business | `v0.2-context-engine` |
| **Stage 3** | Historical retrieval index | Inverted index, hash maps | Instant lookup of past messages & user reaction events | `v0.3-history-retrieval` |
| **Stage 4** | Multimodal OCR & ASR pipeline | `PIL`, `tesseract`, `ffmpeg`, `whisper` | Images & audio converted into plain text layer | `v0.4-multimodal-pipeline` |
| **Stage 5** | Semantic intent & keyphrase engine | Regex, SentenceTransformers / Scikit-learn | Intent signals (payments, deadlines, promos) extracted | `v0.5-semantic-engine` |
| **Stage 6** | Message type classifier | Scikit-learn, Naive Bayes / Rules | Categorizes message into 11 allowed schema categories | `v0.6-type-classifier` |
| **Stage 7** | Security & risk override modules | Heuristic filters, domain age check | Scam/spam messages forced to 100% `mute` override | `v0.7-security-overrides` |
| **Stage 8** | Behavioral trust & preference scorer | Weighted interaction matrix | Quantitative trust & quiet hours (DND) scores computed | `v0.8-trust-engine` |
| **Stage 9** | Personalization & decision fusion | Priority matrix (Utility vs Risk) | Deterministic routing into `notify`, `digest`, `mute` | `v0.9-decision-fusion` |
| **Stage 10**| Confidence calibration & evidence | Calibrated scaler, similarity matcher | Calibrated confidence, reason & `evidence_message_ids` | `v0.10-confidence-evidence` |
| **Stage 11**| Validation, benchmark & release package | Schema validator, Pytest, `zipfile` | Valid `output.csv` (110 rows) & `code.zip` bundle ready | `v1.0-release-candidate` |

---

## AI Judge Interview Preparation Strategy

Following submission, a 30-minute AI Judge Interview will take place. The file [artifacts/project_details.md](file:///home/l41n-pr0t0/workspace/GitHub/HackThon/hackerrank-orchestrate-august26/artifacts/project_details.md) provides comprehensive guidance and answers for key technical topics:

1. **Architecture & Philosophy**: Explaining why a modular, deterministic decision fusion engine was chosen over pure LLM calls (latency, cost, zero security hallucination).
2. **Multimodal Unification**: How OCR (Tesseract) and ASR (FFmpeg/Audio processing) feed into a single plain-text semantic routing layer.
3. **Personalization & History Matching**: How inverted indices map user DND hours, group roles, and historical interaction events to determine true user intent.
4. **Confidence Calibration**: Scaling confidence metrics empirically against ground truth samples.

---

## Verification Plan

### Automated Verification
1. **Tooling & Environment Check (Stage 0)**:
   Verify system binaries: `tesseract --version` and `ffmpeg -version`.
   Verify Python virtual environment and dependencies.

2. **Schema & Integrity Validation (Stage 11)**:
   Run `python code/src/validator.py` to confirm:
   - `output.csv` has exactly 110 rows matching `dataset/messages.csv`.
   - Headers match `message_id,action,message_type,reason,confidence,evidence_message_ids`.
   - `action` is strictly in `['notify', 'digest', 'mute']`.
   - `message_type` is strictly in the 11 allowed categories.
   - `confidence` is a float in `[0.0, 1.0]`.

3. **Benchmark Evaluation**:
   Run `python code/evaluation/main.py` against `dataset/sample_messages.csv`.

### Manual Verification
1. Inspect generated `output.csv` for high-risk scam messages and group admin urgent alerts.
2. Confirm progress matrix updates in `artifacts/progress.md`.
