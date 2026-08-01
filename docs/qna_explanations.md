# Q&A — Project Concepts & Explanations

Beginner-friendly explanations of the Message Notification Router project: what it is, the tech stack, and the core concepts.

---

## Q1. Is a frontend needed for this project?

**No.** This is a batch offline classification task, not a product:

- The only graded deliverable is `output.csv` — predictions for 110 messages in `dataset/messages.csv`, compared against hidden ground-truth labels.
- Submission is exactly 3 artifacts: `code.zip` (runnable solution + README), `output.csv`, and `chat_transcript`.
- No API, no UI, no web component anywhere in the spec. Evaluation is fully automated.

What is needed *instead* of a frontend:

- A **CLI runnable from the terminal** (`code/main.py`) that loads `dataset/`, runs routing, writes `output.csv`
- `code/src/data/loader.py` + `models.py` — the data layer
- README with setup + run instructions
- `chat_transcript` — your conversation log (the only "frontend-ish" artifact)

Optional demo (ungraded, only if spare time): a single static HTML page showing routing stats, per-message decisions, and media previews. Zero effect on score.

---

## Q2. What is this project?

A **Message Notification Router** for WhatsApp — an AI system that reads each incoming multimodal message (text, image posters/screenshots, voice notes) and decides:

- `notify`: interrupt the user now
- `digest`: useful but can be shown later
- `mute`: low-value, repetitive, unwanted, suspicious, or unsafe

The decision is **personalized**: a sale poster may be useful for one user and noise for another; a payment reminder may be legitimate from a trusted admin but risky from a new sender; a muted family group can still contain an urgent direct mention. Clear scam/safety risk is muted regardless.

Judged by comparing `output.csv` (columns: `message_id,action,message_type,reason,confidence,evidence_message_ids`) against hidden ground truth.

## Tech Stack

| Layer | Tech | Purpose |
|---|---|---|
| Language | Python 3.14.6 | Core system |
| Data layer | pandas 3.0.5, numpy 2.5.1 | CSV reading, feature math |
| Typing | Pydantic 2.13.4 | Strongly-typed domain models + validators |
| Multimodal | Tesseract 5.5.3 (via pytesseract 0.3.13), Pillow 12.3.0 | OCR text extraction from images |
| Audio | FFmpeg 8.1.2 (system binary) | Voice-note decoding (ASR comes later) |
| ML | scikit-learn 1.9.0 | Classifier (planned, Stage 6) |
| Testing | pytest 9.1.1 | Verification suites |
| Env | `.venv`, `requirements.txt`, `.gitignore` | Reproducible setup |
| Git | 2.55.0, tags `v0.0-bootstrap` / `v0.1-data-engine` | Milestone versioning |

## Architecture (12-stage roadmap in `artifacts/progress.md`)

**Phase 0 — Foundation (2/12 done):**
- ✅ S0 Bootstrap — env, binaries, git
- ✅ S1 Data Engine — Pydantic models + `DatasetLoader` (O(1) dict lookups)
- ⏳ S2 Context Enrichment — `UserContext`, `GroupContext`, `BusinessContext` joiners
- ⏳ S3 History Retrieval — historical retrieval engine & event graph
- ⏳ S4 Multimodal Pipeline — OCR (images) + audio transcription → unified plain-text layer
- ⏳ S5 Semantic Engine — intent/feature extraction
- ⏳ S6 Type Classifier — 11-category classifier
- ⏳ S7 Security Overrides — hard scam/spam mute rules
- ⏳ S8 Trust Engine — personalized trust & preference scoring
- ⏳ S9 Decision Fusion — action router (notify/digest/mute)
- ⏳ S10 Confidence & Evidence — calibration + reason/evidence selection
- ⏳ S11 RC — benchmark + final `output.csv` + zip

**Phase 1** (Multimodal Understanding & Semantic Layer) and **Phase 2** (Decision Engine, Fusion & Optimization) — planned, 0/13 + 0/13 done.

Current state: `code/main.py` and `code/evaluation/main.py` are empty stubs. Data layer (S1) is the only real code. Next: Stage 2 Context Enrichment Engine.

---

## Q3. What is "Typing" (Pydantic)?

**The problem**: CSV files are just text. When code reads `"1"`, `"1.0"`, or `"1.00"` — is that a number, a string, or a boolean `true`? Python doesn't know. A timestamp might be missing, a count might be `"none"`. If code assumes the wrong type, it crashes mid-run.

**What typing does**: You declare upfront what each piece of data **must** look like:

```python
class Message(BaseModel):
    message_id: str
    user_id: str
    forwarded_count: int        # must be a whole number
    created_at: str             # timestamp
```

- `str` = text, `int` = whole number, `float` = decimal, `bool` = true/false
- Pydantic **validates every row**: if `forwarded_count` arrives as string `"3"`, it auto-converts to number `3` (integer coercion). Invalid data raises a clear error instead of a confusing crash later.
- Result: by the time routing logic runs, every object is guaranteed clean.

**Analogy**: untyped data is a box of mixed Lego pieces ("is this a brick or a plate?"). Typed data is a labeled drawer system — everything is where you expect, in the form you expect.

## What is "Multimodal"?

"Multi" = many, "modal" = form/format. Messages arrive in **different formats**:

| Modality | Example in dataset | How the system reads it |
|---|---|---|
| Text | `message_text` column | Directly as string |
| Image | `media_type=image` → `media/images/img_001.jpg` | **OCR** extracts the words in the picture |
| Voice | `media_type=voice` → `media/audio/vn_001.mp3` | **ASR** transcribes speech to text |

**Key idea**: the system can't easily compare an image to a text rule, so everything is converted to **one common language — plain text**:

```
image poster  ──OCR──▶  "50% OFF SALE THIS WEEKEND ONLY"
voice note    ──ASR──▶  "Hey mom, reaching in 20 minutes, please open the gate"
text message  ───────▶  "Pls fill drinking water now"
```

Then a **single classifier** analyzes all three uniformly. A sale poster OCR'd to text looks exactly like a text promotion to the router.

**Why it matters**: the ground truth includes image and voice messages; a system that ignores them loses points.

## What is "Audio" (the audio pipeline)?

Machinery for the voice-note path:

1. **FFmpeg** (system binary) — decodes the `.mp3` file into raw audio data (like opening a zip before reading the files inside).
2. **ASR** (Automatic Speech Recognition — planned in Stage 4, e.g. whisper) — turns decoded audio's speech into text, like YouTube auto-captions.
3. That text joins the common text layer, and the classifier handles it like any other message.

Why not use audio directly? Speech-to-text lets the same text-based routing, keyword detection (e.g. "urgent", "deadline"), and evidence-matching logic work everywhere, and makes the `reason` column explainable — you can quote what the voice note actually said.

**TL;DR**: Typing = guaranteed-clean data so nothing crashes. Multimodal = the system understands text + images + voice, not just text. Audio = the pipeline that decodes mp3s and transcribes speech so voice notes become analyzable text.

---

## Q4. What am I actually building? (The Big Picture, Simplest Version)

**The whole project in one sentence**: You're building a **robot that reads every WhatsApp message and decides: ring the phone now, save it for later, or throw it away.** Everything else is machinery for that one decision.

### Why it's hard (the "context" problem)

The challenge is designed around one trap: **the same message means different things for different people.**

Take *"Pls pay 500 rupees before 6 PM"*:

- From **Flipkart, after you ordered something** → legit payment reminder → 🔔 **notify**
- From a **random number pretending to be Flipkart** → scam → 🔕 **mute**
- From a **group chat at 1 AM** during your quiet hours → 🔇 **digest** (wait until morning)

The message *text* is identical. The **surrounding facts** are what change the answer. Those surrounding facts = **context**. That's the entire point of the project: read the message *and* its context before deciding.

### What each stage builds (car analogy)

Think of it as building a car, one system at a time:

| Stage | What you build | Car analogy |
|---|---|---|
| ✅ 0 | Tools + env set up | Buying the garage & tools |
| ✅ 1 | Clean, typed data layer | Engine parts, sorted & labeled |
| ✅ 2 | Context engine (dossier per message: DND, business verification, group role) | Fuel + air injection system |
| ✅ 3 | History retrieval (what happened before? evidence matching) | Rear-view mirror + memory |
| ⏳ 4 | OCR + voice transcription | Eyes & ears (reading images, hearing voice notes) |
| ⏳ 5-6 | Understanding + categorizing messages | The brain's pattern recognition |
| ⏳ 7-8 | Safety rules + trust scores | The danger instincts |
| ⏳ 9 | Decision fusion (notify/digest/mute) | The steering wheel — makes the final call |
| ⏳ 10 | Confidence + reasons + evidence | The dashboard display |
| ⏳ 11 | Final test + package | The final inspection |

### The "aha" to hold onto

You are **not** building a chatbot, a website, or an app. You're building a **pipeline**: raw messages in → enriched with facts → categorized → safety-checked → decided → `output.csv` out. The judge only sees the last step (the CSV). Every stage you finish makes that final decision smarter.
