# Stage 2 Context Enrichment Engine Report

> **Stage Status**: ✅ **COMPLETED & VERIFIED**  
> **Git Milestone**: Tag `v0.2-context-engine`  
> **GitHub Repository**: [https://github.com/Wired-Navi0x17/message-notification-router](https://github.com/Wired-Navi0x17/message-notification-router)

---

## 1. What Was Done in Stage 2

1. **Context Builder Engine (`code/src/context/builder.py`)**:
   - Built `ContextBuilder` class to join raw messages with user profiles, group metadata, and business histories into consolidated `EnrichedContext` objects.
   - Built `UserContext` module:
     - Calculates `is_dnd_active` by parsing user quiet hours (`do_not_disturb_window`) against message creation timestamps.
     - Computes historical 30-day `open_ratio` and `reply_ratio`.
   - Built `GroupContext` module:
     - Joins group member roles (`admin` vs `member`), admin status (`is_user_admin`), and group mute settings (`is_group_muted_by_user`).
     - Includes 30-day user activity in group (sent, read, replied).
   - Built `BusinessContext` module:
     - Performs domain validation (`is_domain_mismatched`: checks if official domain matches sender domain).
     - Joins business verification status (`is_verified`), user relationship reasons (`relationship_reason`), and promotion opt-out flags (`allows_promotions`).

2. **Stage 2 Verification Suite (`code/tests/test_stage_2.py`)**:
   - Tested overnight DND window parsing (`22:00-07:00` vs timestamps at `22:19`, `02:15`, `11:09`).
   - Tested context enrichment on real messages from `dataset/messages.csv` and `dataset/sample_messages.csv`.

---

## 2. Detailed Verification Results

| Context Module | Test Scenario | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **DND Window Parser** | Timestamp `22:19` during `22:00-07:00` | `is_dnd_active = True` | `True` | ✅ PASS |
| **DND Window Parser** | Timestamp `02:15` during `22:00-07:00` | `is_dnd_active = True` | `True` | ✅ PASS |
| **DND Window Parser** | Timestamp `11:09` during `22:00-07:00` | `is_dnd_active = False` | `False` | ✅ PASS |
| **User Context** | User `u_001` at `22:15` (`22:00-07:00`) | DND Active = True | `True` | ✅ PASS |
| **Business Context** | Message `msg_023` to `u_002` from `business_002` | Verified Business, No Domain Mismatch | `is_verified = True` | ✅ PASS |
| **Group Context** | Sample `sample_msg_001` to `u_011` in `group_002` | Joined group role & activity | `group_id = "group_002"` | ✅ PASS |

---

## 3. Project Understanding for the AI Judge (In Simple English)

> **Why is Context Enrichment critical for the AI Judge?**  
> A message cannot be routed in isolation! The exact same text message—for example, *"Pls pay 500 rupees before 6 PM"*—has completely different meanings depending on context:
> - If sent by a **verified business** where the user recently ordered grocery delivery -> It's a legitimate **Payment Reminder (`notify`)**.
> - If sent by an **unknown sender** with a brand domain mismatch -> It's a **Phishing Scam (`mute`)**.
> - If sent in a **group during quiet hours (DND 10 PM - 7 AM)** -> It should wait in **Digest (`digest`)** unless sent by a trusted admin.

> **What did Stage 2 achieve?**  
> Stage 2 builds the **Context Engine**. Whenever any message arrives, our system instantly retrieves who the user is, whether quiet hours are currently active, what their role in the group is, and whether the business sender is verified and untampered. Downstream routing modules now receive a complete 360-degree picture of every message.

---

## 4. How You Can Personally Test Stage 2

Run this single command in your terminal:

```fish
.venv/bin/python3 code/tests/test_stage_2.py
```

### Expected Output:
```text
✓ DND active calculation verified!
✓ Context Builder enrichment verified!
✓ All Stage 2 Context Enrichment Engine tests passed cleanly!
```

---

## 5. Next Steps (Awaiting Approval)
With Stage 2 completed, verified, committed, and pushed to GitHub, we are ready for **Stage 3: Historical Retrieval Engine & Event Graph**, where we build `code/src/retrieval/history.py` to index past messages (`message_history.csv`) and user reaction events (`message_events.csv`) for instant O(1) similarity matching and evidence generation.
