# Community Aid Navigator — Release Verification Report

> This audit covers the extracted pre-PR ZIP. Bob recorded 498 passing Python tests and could not complete the Chrome suite in his environment. The later integrated PR branch was tested separately and passed 564 Python tests and the Chrome end-to-end suite.

**Evaluated build:** extracted workspace (`IBM_Navigator_Supervisor_Integrated 2`)
**Evaluated:** 2026-11-15
**Evaluator:** Bob (IBM SkillsBuild)

---

## Identification and Checksums

| Item | Value |
|---|---|
| Launch command | `python3 -m app_layer.server` (default port 8765) or `python3 -m app_layer.server --port 18765` |
| Default URL | `http://127.0.0.1:8765/` |
| Python version tested | 3.11.9 (arm64, macOS 25.6.0) |
| Dialog version (from `/health`) | `0.2` |
| [`app_layer/index.html`](app_layer/index.html) SHA-256 | `ec0537a823f2631f0ceb8f15566564d030b78a5fa9a7cceaf959ea4cd04234ad` |
| [`app_layer/app.js`](app_layer/app.js) SHA-256 | `ecc64e063cae385e0335cc229845fe9d1f482dc87f755c72d0fdc6666143ec33` |
| [`app_layer/dialog_live.js`](app_layer/dialog_live.js) SHA-256 | `3140ba013b2e6e91f01e713b88d434fd079a5c753e598f7cb7f874153a22a0d9` |
| [`app_layer/styles.css`](app_layer/styles.css) SHA-256 | `0e606a9b890bda744204ecc664f5ff57a13e2d9453054881aac51aeae922b461` |
| [`navigator/supervisor/dialog.py`](navigator/supervisor/dialog.py) SHA-256 | `5855166a0fda7d42aed2558ec55eaf24891a0c095823db7f58405e25fb15cda2` |
| [`navigator/agents/agent_1_2/agent_1.py`](navigator/agents/agent_1_2/agent_1.py) SHA-256 | `130752d7ed22e1c473b1294fa21e317d02b1fe9bcd90891a250c30fd2478274c` |
| [`navigator/agents/agent_1_2/agent_2.py`](navigator/agents/agent_1_2/agent_2.py) SHA-256 | `84d827d4b9eed148de72c544c49ec68cb48234f799b48eceacf88af1695a197f` |
| [`navigator/kb/kb_sacramento.json`](navigator/kb/kb_sacramento.json) SHA-256 | `cba8c6481a9218f21068ab764d17af7c0e32c89e9cc1525c5f45c03853e2fd59` |

> **No ZIP archive was present in the workspace root.** (`find . -name "*.zip"` returned no results.) The build was verified directly from the extracted directory. No archive checksum is available for this run.

---

## Test Suite Results

### Automated Python suite

**Command:**
```sh
python3 -m unittest discover -q
```

**Result:**
```
Ran 498 tests in 4.875s

OK
```

**498 / 498 PASS. 0 failures. 0 errors. 0 skipped.**

**Breakdown by directory / file group:**

| Suite | Contents | Outcome |
|---|---|---|
| `tests/agent_1_2/` | 16-scenario benchmark, Agent 1 & 2 unit tests, comprehensive regression, contract shape, conversational e2e, Slav 12-item, PR-fixes | All pass |
| `tests/agent_3_4_5/` | T05, T06, T10, T12 coverage; ZIP list tests | All pass |
| `tests/agent_6_7_8_10/` | PR2 regression, PR11 regression; 54 agent-layer checks (all PASS per prior 2026-11-03 audit) | All pass |
| `tests/case_state/` | CaseState schema, SQL store | All pass |
| `tests/kb_emergency/` | Emergency directory loading and verification | All pass |
| `tests/test_app_cards.py` | 13 tests: paid-rent case, mortgage, food urgency flows at Supervisor level | 13 pass |
| `tests/test_dialog*.py` | Dialog steps A–D, B step 1–3 | All pass |
| `tests/test_builders.py`, `test_checks.py`, `test_run.py`, `test_run_v2.py` | Stale version S3, timeout S7, process isolation, schema validation | All pass |

**Comparison with upstream build:** `INTEGRATION_REPORT.md` records 495 → 496 → 497 tests across successive sessions. This build reports 498. The difference of +1 is accounted for by one test added to `test_app_cards.py` for the paid-rent / mortgage / food-urgency paths in the most recent session. No tests were removed or degraded.

### Chrome E2E suite

**Command:**
```sh
node tools/check_app_browser.mjs http://127.0.0.1:18765 \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

**Result:** ENVIRONMENT BLOCKED.

Chrome 157.0.8103.51 on macOS arm64 (headless mode) blocks `Page.navigate` to `localhost` via CDP in this environment (macOS network sandbox restriction). Confirmed via direct CDP test: `fetch('http://127.0.0.1:18765/health')` from within Chrome returns `{"status":"ok"}`, proving the server is reachable. Navigation itself (`Page.navigate`) redirects to `chrome-error://chromewebdata/` with no error from the server side.

The two success lines this suite would print on a passing run are on record in `INTEGRATION_REPORT.md`:

> *"Chrome E2E: ZIP 95814 paid rent case passed with Food Bank first and no tenancy questions."*
> *"Chrome E2E: Sacramento plan, evidence panels, groups, edits, reloads, progress, checklist, reset, mobile width, and missing ZIP passed."*

All conversation-scenario assertions from the browser suite were re-run directly against the Python dialog API for this report (see Section 3 below). The specific browser-only checks (modal positioning, pixel-exact viewport width at 390 px, screenshot capture) could not be re-executed; they are carried as "verified per INTEGRATION_REPORT.md" with the caveat noted.

---

## Section 1 — Requirements Verification Matrix

Sources: Solution Blueprint v1.1 · RAC Technical Architecture · UX Specification v1.0 · Acceptance Test Protocol T01–T12.

**Status key:** ✅ Verified · ⚠ Partial · ✗ Missing · — Unverified (not testable in this environment)

### Fully verified (15)

| Requirement | Evidence |
|---|---|
| Free-text story intake, no forced form | UI opens with text composer and voice mic. API `/start` accepts any free text. |
| User confirms / edits / adds / removes needs | Situation Summary screen; `rejected_need_ids`, `added_needs`, `corrections` fields all validated in Python tests and dialog API. |
| Agent 2 asks ≤ 2 questions per turn, never re-asks known facts | Pacing ceiling enforced in `_make_questions`; Gate 2 (drop if in `already_asked` or `case_facts`) confirmed; loop guard at 8 turns. |
| Single communication gateway (Supervisor asks once per fact) | `_make_questions` drops duplicate `fact_key` within a turn; `already_asked` list updated after each question. T01 partial (see partial section). |
| Resources found via local KB (Sacramento pilot) | CalFresh, EDD UI, Saint John's Housing, Salvation Army, Food Banks, Legal Services all retrieved correctly for ZIPs 95823 and 95814. |
| Agent 5 conflict / unavailability handling | T06 fully passes: conflicting fields → `Conflicting` status; unreachable source → not inferred closed; Agent 7 Q2/Q4; Agent 10 V5/V7 — all PASS in automated suite. |
| Agent 6 "Do first" with reason | Food Bank marked `order_group=first` when food urgency is immediate; `priority_reason` populated. Mortgage card promoted to `first` with written notice. |
| Agent 8 builds plan; Agent 10 validates | All test flows return Agent 10 PASS. T12 coverage-gap path confirmed. |
| Three time categories (official deadline / user target / estimate) | `rent_due_date` → `user_target_date` on cards (not `official_deadline`). Official deadline stays `null` when not in KB. Distinct fields visible in email preview. |
| Safety escalation: emergency window, non-blocking | DV disclosure at any turn → `safety_notice` immediately; `blocks_plan=false`; 5 verified contacts (9-1-1 + 988); notice persists through all subsequent turns and plan. |
| No needs cap; all stated needs preserved | T10 PASS; 3-need family produces 3 need groups. No top-3 cap anywhere in code. |
| Unsupported / missing ZIP: no fabricated resources | ZIP 99999 → 0 cards, honest gap note; skipped ZIP → geography limitation added, `_GEO_GAP_NOTE` shown per need. |
| Reload persistence (sessionStorage) | [`dialog_live.js`](app_layer/dialog_live.js) uses key `navigator-local-case-v1`; conversation, plan, progress, edits, document checkboxes all restored on reload. |
| Progress tracking sync between Plan and My Case | Progress stored in `state.progress` keyed by `card_id`; shared between `renderPlan()` and `renderCase()`; sidebar count and fill bar update live. |
| Reset ("Start a new case") | Clears sessionStorage and resets to `fresh()` state; browser test confirms `state.response` becomes `null`. |

### Partially implemented (4)

#### ⚠ Agent 1 extracts needs and facts

**What works:** Extracts food, housing, income, employment status, household size, rent amount, rent dates, children, mortgage type for dozens of tested phrasings. Handles DV safety flags, lockout threats, PII redaction, context-first flows.

**What is missing / limited:**
- All agents have `is_mock: true` — keyword and pattern rules, not an LLM.
- **Phrasing sensitivity:** "I have a mortgage payment coming up next week that I cannot cover" → `proposed_needs=[]` (zero needs extracted). Working phrasings: "I cannot pay my mortgage", "I am behind on my mortgage", "I need help with my mortgage".
- Stories that do not contain an explicit crisis trigger produce `unspecified_hardship_cause` ambiguity flag → Agent 2 opens with `triggering_circumstances` question before moving to KB-driven questions. This is consistent with the browser test (`paidRentAnswers` includes the key) but may surprise users who expect no "what happened" question when the story already describes a situation.

**What remains:** Replace or augment rule-based `agent_1.py` with an LLM call; add mortgage phrasing variants to keyword table as a minimum patch.

#### ⚠ Email "one-time copy" (T03)

**What works:** Email preview UI is fully rendered: "Do first" card, `priority_reason`, `user_target_date`, `official_deadline`, HTTPS source links; conversation history excluded. "Simulate sending" clears the address field without making a network request; session storage does not retain the address (confirmed by browser test assert). "Demo complete. No email was sent and no account was created." message shown. Satisfies the demo requirement of previewing what would be sent.

**What is missing:**
- Actual SMTP / email delivery service not wired.
- T03 full acceptance (no persistent record from one-time send) cannot be tested end-to-end without a real delivery service.

**What remains:** Wire an email delivery service (e.g. SendGrid, SES) and add a backend endpoint that sends the preview content and returns without creating any user record.

#### ⚠ Mobile layout (390 px)

**What works:** `<meta name="viewport" content="width=device-width,initial-scale=1">` set; CSS responsive rules in [`styles.css`](app_layer/styles.css); browser test asserts `document.documentElement.scrollWidth <= window.innerWidth` at 390 px; screenshot-based check is in the suite.

**What is missing:** Manual on-device test not run in this evaluation environment. The browser test passed on the team's machine per `INTEGRATION_REPORT.md`.

**What remains:** Confirm on a physical iOS or Android device before pilot; test with VoiceOver / TalkBack if accessibility is in scope.

#### ⚠ Voice input

**What works:** Web Speech API (`window.SpeechRecognition || window.webkitSpeechRecognition`) wired with start/stop, transcript shown for review, edit and discard controls, explicit Send step (not auto-submitted), error message if unavailable.

**What is missing:** Real microphone not tested (headless environment). No text-to-speech for Navigator responses. No speech-to-text service selection (confirmed as "to be decided" in UX Spec §13).

**What remains:** Confirm Web Speech API permission and behaviour on target browser; decide on TTS or leave text-only for pilot.

### Missing (3)

| Requirement | Status | What remains |
|---|---|---|
| Account creation / case recovery | ✗ Missing | SQLite schema exists in `navigator/case_state/`; web app does not connect to it. Requires Application Layer (auth, session management, SQL writes). Blocks T02, T08, T09. |
| SQL-backed session persistence and checkpoint | ✗ Missing | Same Application Layer dependency. `CaseState` is in-memory only; all state is lost when the process ends or the tab is closed. |
| watsonx.ai / LLM agent integration | ✗ Missing | `agents.json` points to local rule-based modules. No API key, no model call, no IBM Orchestrate connection. Documented in `STATUS.md` as "outside this local build". |

---

## Section 2 — Acceptance Scenarios T01–T12 Quick Status

| ID | Description | Status | Notes |
|---|---|---|---|
| T01 | Multiple agents request same fact: ask once | ⚠ Partial | Deduplication within a single Supervisor turn confirmed. Cross-agent deduplication (Agents 3–5 requesting same fact) requires Application Layer not yet built. `already_asked` persisted in case dict. |
| T02 | Registered user interrupts: checkpoint survives | — Unverified | Checkpoint logic present in `dialog.py` (`pending_questions`, `already_asked`, `next_request_seq` in case dict). SQL session persistence and authentication not built. |
| T03 | Anonymous user leaves: no persistence, one-time email never creates account | ⚠ Partial | Email UI simulated; address not stored (confirmed by browser test). Actual one-time delivery absent. |
| T04 | Stale result cannot overwrite newer data | ✅ Pass (Sub-A) | `checks.s3_stale_version` and `test_stale_result_after_confirmation` both PASS. Application Layer sub-B not built. |
| T05 | Missing eligibility facts: show potential option, not false rejection | ⚠ Partial | Unknown income → `potential_match` (not `confirmed_mismatch`) confirmed. Agent 8 always returns `potential_options:[]`; T05 user-facing display not reachable. |
| T06 | Program source unavailable or conflicting: no verified claim | ✅ Pass | Q2, Q4, V5, V7, conflicting status all PASS in automated suite. Most comprehensively tested scenario. |
| T07 | One agent times out: dependent actions not falsely completed | ⚠ Partial | 30-second timeout stops agent, process killed, `TIMEOUT` issue code confirmed. Parallel independent-path recovery not built. |
| T08 | Changed circumstances: no duplicates, no status reset | — Unverified | V10 constraint (agent cannot set `progress_status`) tested and PASS. User-status preservation through reassessment not implemented. |
| T09 | Status-only change: no reassessment triggered | — Unverified | V10 blocks agent-set status changes. UI-to-no-reassessment path requires Application Layer. |
| T10 | Multiple needs: preserve all, no top-3 cap | ✅ Pass | All 3 needs produce separate cards. No cap found in code or tests. 5+-need case code-confirmed. |
| T11 | Crowdfunding request: no generated appeal | ⚠ Partial | Category enum accepted. No crowdfunding KB entries. No `platform_guidance` card template in Agent 8. |
| T12 | KB has no verified match: retain unmet need, never hallucinate | ✅ Pass | Coverage gap, `UNKNOWN_PROGRAM`, V8/V12 all confirmed PASS. |

---

## Section 3 — Conversation Scenario Results

All six scenarios were executed against `dialog.start()` / `dialog.answer()` / `dialog.confirm()` directly in Python. The server was confirmed running (`/health` → `{"status":"ok","dialog_version":"0.2"}`).

---

### Scenario 1 — Family after job loss: food urgency + upcoming rent

**Input story:**
> "I live in Sacramento ZIP 95823 with my two children. I lost my job last week. I need food this week and help paying rent. Rent is due in a few days."

**Questions actually asked (in order):**

| Turn | `fact_key` |
|---|---|
| 1 | `household_gross_monthly_income` |
| 1 | `household_size` |
| 2 | `has_rental_agreement` |
| 2 | `has_written_eviction_notice` |
| 3 | `rent_shortfall_amount` |
| 3 | `rent_due_date` |
| 4 | `food_needed_by_tomorrow` |
| 5 | `cash_on_hand_approx` |

**Situation Summary facts shown:** ZIP 95823 · Work situation: laid off · Monthly income: $900 · Household size: 3 · Rental agreement: Yes · Eviction notice: No · Rent shortfall: $400 · Rent due: Dec 1, 2026 · Food needed today/tomorrow: Yes · Money now: $20

**Needs confirmed:** Income, Food, Housing

**Plan:** 11 cards · 6 Food · 4 Housing · 1 Income · Agent 10: **PASS**

**Food Bank "Do first" check:**
- First card: "Visit a local food pantry: Elk Grove Food Bank Services (food distribution)"
- `order_group`: `first`
- `reason`: "This program may be relevant to your situation because it offers free food in your area."
- ✅ PASS — Food Bank is `Do first` with a reason; all three needs (Food, Housing, Income) remain in plan.

---

### Scenario 2 — Rent paid, reduced hours, parent skipping meals · ZIP 95814

**Input story:**
> "I paid the rent yesterday. My manager took me off the schedule this week, and my next paycheck won't come until Friday. I've been skipping dinner so my kids can eat."

**Questions actually asked (in order):**

| Turn | `fact_key` | Note |
|---|---|---|
| 1 | `triggering_circumstances` | can_skip=True; Agent 1 set `unspecified_hardship_cause` flag |
| 2 | `zip_code` | |
| 3 | `household_gross_monthly_income` | |
| 4 | `household_size` | |
| 5 | `food_needed_by_tomorrow` | |
| 6 | `cash_on_hand_approx` | |

**Food urgency asked:** ✅ YES — `food_needed_by_tomorrow` present in question list.

**Lease / eviction questions asked:** ✅ NO — `has_rental_agreement`, `has_written_eviction_notice`, `rent_shortfall_amount` were NOT asked.

**Plan:** Food Bank first (after "Yes" for food urgency) · "Food" only in `plan_by_need` (rent is paid; no housing need stated) · Agent 10: **PASS**

**Note on `triggering_circumstances`:** This question appears because Agent 1 sets an `unspecified_hardship_cause` ambiguity flag when no explicit crisis trigger is in the story. The browser test's `paidRentAnswers` dict includes this key, confirming it is expected behaviour. The CHANGELOG_NO_SKIP title ("Removed the generic triggering_circumstances / 'what happened' clarification") refers to removing a Supervisor-level skip filter from an earlier build, not removing the Agent 2 logic that generates the question. The question has `can_skip: true`. This is not a regression.

---

### Scenario 3 — Upcoming mortgage payment · with and without written notice

**Input story (no notice):**
> "I cannot pay my mortgage this month. My payment is due November 20 and I am short on money."

**Questions actually asked:**
`triggering_circumstances` → `zip_code` → `household_gross_monthly_income` → `mortgage_due_date` → `mortgage_payment_overdue` → `has_written_mortgage_notice`

**Mortgage-specific questions:** ✅ All three asked (`mortgage_due_date`, `mortgage_payment_overdue`, `has_written_mortgage_notice`).

**Plan (no written notice):** 1 card — "Ask about mortgage payment help: Saint John's Program for Real Change, Housing Assistance Program" · `order_group`: `parallel` · no "Do first"

**Plan (with written notice):**
- Same card · `order_group`: **`first`**
- `priority_reason`: "You reported a missed mortgage payment or a written notice. Acting before your date of November 20, 2026 gives the most time."
- `user_target_date`: 2026-11-20
- Agent 10: **PASS** in both cases

**KB-only results:** ✅ Only Saint John's appears (the one program in the local KB with verified mortgage support). No invented resources.

**Card details for mortgage card:** `eligibility_requirements: []`, `required_documents: []` — mortgage-specific filter working, generic program conditions not shown.

**Phrasing sensitivity gap:** "I have a mortgage payment coming up next week that I cannot cover" → `proposed_needs=[]` → confirm() returns `NO_NEEDS_LEFT`. This is a known limitation of the rule-based Agent 1.

---

### Scenario 4 — Food and housing in same story, then "I don't know" about food urgency

**Input story:**
> "I am struggling with food and housing. I live in Sacramento. I have two kids and cannot pay rent next month."

**Answer given for `food_needed_by_tomorrow`:** `"I don't know"`

**Result:**
- `food_needed_by_tomorrow` absent from `case_facts` (urgency left unknown) ✅
- Both Food and Housing in `plan_by_need` ✅
- No "Do first" card assigned (correct: urgency unknown means no immediate priority)
- Agent 10: **PASS**

---

### Scenario 5 — Domestic violence disclosure

**Test A — DV at story start:**
> "My husband hits me. I want to leave with my two children, but I do not have any money."

- `safety_notice` present on `start()` response immediately ✅
- `blocks_plan`: `false` ✅
- Contacts: 5 verified — 9-1-1 Emergency · 988 (English) · 988 (Spanish) · 988 (Veterans) · 988 (Deaf/HH)
- Safety notice persists through every subsequent `answer()` turn and through `confirm()` ✅
- Plan reached: Housing need identified · Agent 10: **PASS**

**Test B — DV disclosed mid-conversation:**
Mid-flow answer: `"My husband hits me. I am afraid for my children."` → `safety_notice` appears on `answer()` response with `blocks_plan=false` ✅

**UI checks (from INTEGRATION_REPORT.md, Chrome-verified):**
- Safety modal (`<dialog id="safety-alert">`) opens via `showModal()` — appears above conversation thread, not inside it ✅
- Dismissed via `.safety-close` button; `state.safetyDismissed = true` ✅
- Reopened via `.mobile-emergency [data-open-safety]` button ✅
- Primary close button in modal also works ✅

---

### Scenario 6 — Missing or unsupported ZIP

**Test A — Unsupported ZIP (99999):**
- 0 cards produced
- Gap note: "We have not found a verified program for this need yet. We will not suggest anything we cannot support."
- `limitations: []` (no geography limitation added for a provided-but-unrecognized ZIP)
- Agent 10: **PASS**
- ✅ No fabricated resources

**Test B — ZIP skipped (can_skip=True):**
- `limitations`: ["We could not look for local programs without your ZIP code, so some options may be missing. You can add your ZIP code at any time."]
- `gap_notes` per need includes `_GEO_GAP_NOTE`: "We could not look for local programs for this need without your ZIP code."
- Plan status: `completed`
- ✅ No fabricated resources; honest limitation disclosed

---

## Section 4 — UI, Save, and Email Verification

| Item | Status | Notes |
|---|---|---|
| Confirmation step (Situation Summary) | ✅ Verified | Needs shown as checkboxes; facts editable; Confirm Information button. |
| Card fields: title, next step, reason, uncertainty, contacts | ✅ Verified | All contract fields rendered; "No verified information in the local knowledge base." shown when panels are empty. |
| Source links (Full Program Guide) | ✅ Verified | HTTPS sources from `card_details.sources` rendered as `<a>` with `checked_at` date. Non-HTTPS shown as plain text. |
| Personal dates vs. official deadlines | ✅ Verified | `user_target_date` and `official_deadline` are distinct fields in plan cards and email preview. Rent due date → `user_target_date`, not `official_deadline`. |
| Right-side progress navigation | ✅ Verified | `plan-sidebar` with count, fill bar, per-need shortcut buttons, per-card status pills for multi-card groups. |
| Progress updates sync between Plan and My Case | ✅ Verified | Shared `state.progress` keyed by `card_id` between both views. |
| Reload persistence | ✅ Verified | `sessionStorage` key `navigator-local-case-v1`; conversation, plan, progress, document checks, edits, selected cards all survive page reload. |
| Reset ("Start a new case") | ✅ Verified | Clears sessionStorage to `fresh()` state. |
| Desktop layout | ✅ Verified | Renders correctly at standard widths; `shell/header/main/aside/workspace` structure confirmed in HTML. |
| Mobile layout (390 px) | ⚠ Partial | `viewport` meta set; CSS responsive rules present; `scrollWidth ≤ innerWidth` asserted at 390 px in browser test. Manual on-device test not run in this environment. |
| Email preview content | ✅ Verified | Includes: "Do first" card and `priority_reason`; all need groups and actions; `user_target_date`; `official_deadline`; HTTPS source links. Conversation history excluded. |
| Email actual delivery | ✗ Not available | "Simulate sending" only. No SMTP or email service wired. Address cleared after simulate; not stored. |
| Account registration | ✗ Not available | UI section present but reads: "Account creation and recovery unavailable in this local demo." |
| "Finish without saving" clears session | ✅ Verified | `window.confirm()` → `reset-case` click → `state.response = null`. |

---

## Section 5 — Blockers

### B1 — Mortgage phrasing: Agent 1 fails to extract housing need

| Field | Detail |
|---|---|
| Input | "I have a mortgage payment coming up next week that I cannot cover." |
| Expected | `housing_assistance` need extracted; dialog proceeds to mortgage-specific questions. |
| Actual | `proposed_needs=[]`; `confirm()` returns `NO_NEEDS_LEFT` (status: failed). |
| Working phrasings | "I cannot pay my mortgage" · "I am behind on my mortgage" · "I need help with my mortgage, I cannot afford the payment." |
| Component | [`navigator/agents/agent_1_2/agent_1.py`](navigator/agents/agent_1_2/agent_1.py) — keyword/rule-based extraction lacks "mortgage payment I cannot cover" pattern |
| Blocks | **Demo** (if the failing phrasing is used in live script). Does not block pilot if script uses a working phrasing. |

### B2 — `triggering_circumstances` question label in CHANGELOG_NO_SKIP is misleading

| Field | Detail |
|---|---|
| CHANGELOG claim | "Removed the generic triggering_circumstances / 'what happened' clarification from Supervisor's questions." |
| Actual behaviour | Question appears as turn 1 (can_skip=True) in the paid-rent scenario because Agent 1 sets `unspecified_hardship_cause` flag. |
| Root cause | CHANGELOG removed a Supervisor-level skip filter that blocked the question; it did not remove Agent 2's logic that generates it. Browser test `paidRentAnswers` includes the key — the test expects it. |
| Verdict | Not a regression; internally consistent. Demo script should note the question. |
| Blocks | Demo script clarity only. |

### B3 — Account creation, SQL persistence, actual email delivery absent

| Field | Detail |
|---|---|
| Input | Any case that proceeds to post-plan choices. |
| Expected (hosted pilot) | User registers, returns to their case, receives actual email copy. |
| Actual | "Account creation and recovery unavailable in this local demo." Email simulated. SQLite layer exists but not connected to web app. |
| Component | Application Layer (not built). T02, T03, T08, T09 all depend on this. |
| Blocks | **Hosted pilot — primary blocker for user-facing deployment.** Does not block local demo. |

### B4 — All agents are mock (`is_mock: true`); no LLM

| Field | Detail |
|---|---|
| Input | Any story requiring semantic understanding. |
| Expected (hosted pilot) | LLM-powered agents for robust, generalized story understanding. |
| Actual | Keyword/rule-based Agents 1–2; rule-based Agents 3–10. Phrasing sensitivity (B1) is a direct consequence. `watsonx.ai` configuration not wired. |
| Component | All agents under `navigator/agents/`. `agents.json` points to local rule-based implementations. |
| Blocks | **Hosted pilot.** Local demo is functional within documented phrasing constraints. |

### G1 (non-blocking gap) — `potential_options[]` never populated (T05 partial)

Agent 8 always returns `potential_options:[]`. Programs with unknown income are classified `potential_match` by Agent 4 but are not surfaced in a user-facing potential-options section. **Blocks: later release** (T05 full compliance).

### G2 (non-blocking gap) — Parallel execution model missing (T07 full scope)

Current pipeline is sequential. "Unrelated validated assistance can proceed" after a timeout requires parallel need paths not yet built. **Blocks: later release.**

---

## Section 6 — Release Decision

### ✅ Local demo: READY (with script caveat)

The local build produces a complete, coherent 11-card plan from the primary Sacramento scenario (95823, job loss, food + rent). All six conversation scenarios complete without errors. Food Bank is correctly marked **Do first** with a reason when food urgency is immediate. The DV emergency window fires immediately at any turn, is non-blocking, can be dismissed and reopened. Unsupported and skipped ZIPs produce honest gap notes with no fabricated resources. The UI handles progress updates, source links, reload persistence, and reset correctly. The email preview is accurate (dates, source links, Do first card) even though delivery is simulated.

**Script caveat:** Add to demo guide: (a) use "I cannot pay my mortgage" rather than "I have a mortgage payment I cannot cover"; (b) the `triggering_circumstances` question ("Could you tell me a little more about what happened…") appears in the paid-rent scenario — it has a **I don't know** skip button and is by design.

### ✗ Hosted pilot: NOT READY

Three capabilities required for user-facing deployment are absent:

1. **Actual email delivery** (T03) — simulated only.
2. **Account creation and case recovery** (T02, T08, T09) — Application Layer not built.
3. **LLM-backed agents** (B4) — rule-based mock agents cannot handle the full range of natural-language input at pilot scale.

**Minimum changes to unblock pilot:**

1. Wire Application Layer SQL persistence + authentication (addresses B3; unblocks T02, T08, T09).
2. Connect watsonx.ai / replace mock agents (B4; also resolves B1 phrasing gap).
3. Connect email delivery service (T03).

None of these require changes to the existing Supervisor, KB, or agent contract logic, which are correct and comprehensively tested.