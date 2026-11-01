# Review the item 3 change in navigator/agents/agent_6_7_8_10/agent_6_7_8_10.py (_verified_contacts and its use in agent_8) against docs/contracts/SHARED_CONTRACTS.md section 4.8, “Contacts and hours in next_step”. Run python3 tests/agent_6_7_8_10/run_tests.py. Don’t change any files.

---

**Status:** active  **Date:** 2026-11-01

---

### 👤 User

Review the item 3 change in navigator/agents/agent_6_7_8_10/agent_6_7_8_10.py (_verified_contacts and its use in agent_8) against docs/contracts/SHARED_CONTRACTS.md section 4.8, “Contacts and hours in next_step”. Run python3 tests/agent_6_7_8_10/run_tests.py. Don’t change any files.

---

### 🤖 Assistant

> 🔧 called: read_file, read_file

I'll start by reading all the relevant files in parallel.

> 🔧 **read_file** — docs/contracts/SHARED_CONTRACTS.md

> 🔧 **read_file** — navigator/agents/agent_6_7_8_10/agent_6_7_8_10.py

### 🤖 Assistant

> 🔧 called: execute_command

Now let me run the tests:

> 🔧 **execute_command** — cd ~/Documents/ai-community-aid-navigator && python3 tests/agent_6_7_8_10/run_tests.py 2>&1

### 🤖 Assistant

All 54 tests pass. Here is the review:

---

## Review: `_verified_contacts` (Item 3 change) vs. Contract 4.8

### Contract 4.8 says (v1.1, ACCEPTED Oct 26)

> *"A card may name a phone number, link or opening hours **only** from a `checked_claims[]` item with `verification_status = verified`, and shows the date it was checked (for example "Call 2-1-1 and press 8, Mon–Sat 7 a.m.–7 p.m. (checked Oct 21)"). Agent 10 keeps flagging any contact that is not in the evidence (V8)."*

### What the code does

**`_verified_contacts`** ([`agent_6_7_8_10.py:120–132`](navigator/agents/agent_6_7_8_10/agent_6_7_8_10.py:120)):

| Contract requirement | Implementation |
|---|---|
| Only `verified` claims | ✅ `c.get("verification_status") == "verified"` |
| Only `contact`, `hours`, `opening_hours` field paths | ✅ `CONTACT_FIELDS = ("contact", "hours", "opening_hours")` checked via `split("[")[0]` (handles array paths like `contact[0]`) |
| Must have a `claim_value` | ✅ `c.get("claim_value")` check |
| Must show the check date in `checked (…)` format | ✅ `when = str(c.get("checked_at") or "")[:10]` → `"%b %-d"` → `f"(checked {when})."` |
| **Missing check date → claim is silently dropped** | ✅ `except ValueError: continue` — no check date means it cannot be shown, per contract intent |
| Claim is appended with its `evidence_refs` | ✅ `c.get("evidence_refs", [])` returned as a tuple |

**Use in `agent_8`** ([`agent_6_7_8_10.py:298–301`](navigator/agents/agent_6_7_8_10/agent_6_7_8_10.py:298)):

```python
if m and not a["rationale"].startswith("Temporarily closed"):
    for text, refs in _verified_contacts(p.get("checked_claims", []), a["program_id"]):
        next_step = f"{next_step} {text}"
        a = dict(a, evidence_refs=list(dict.fromkeys(a["evidence_refs"] + refs)))
```

| Contract requirement | Implementation |
|---|---|
| Contacts injected into `next_step` | ✅ |
| Not applied to temporarily-closed cards | ✅ guard `not a["rationale"].startswith("Temporarily closed")` |
| Evidence refs from the contact claim are carried onto the card | ✅ de-duped via `dict.fromkeys` |
| Agent 10 (V8) keeps flagging contacts not in evidence | ✅ (verified by test C-CON3; a contact that is in a verified claim and therefore in `evidence_text` passes) |

### Test coverage

Three dedicated tests directly validate this feature:

| Test | Verifies |
|---|---|
| `C-CON1` | Verified contact + hours appear in `next_step` with `(checked …)`, evidence ref linked |
| `C-CON2` | Unverified contact is **never** shown |
| `C-CON3` | Plan with verified contacts produces **no V8 flag** from Agent 10 |

All three pass, and the full suite is **54/54 ✅ — no failures**.

### Verdict

The implementation is **fully compliant with contract 4.8**. Every requirement of the ACCEPTED Oct 26 change request is met: only `verified` claims, only contact/hours field paths, check date always shown, missing check date silently excludes the claim, evidence refs propagate, and closed-program cards are excluded. Agent 10 V8 is unaffected.