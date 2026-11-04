# MVP Acceptance Test Protocol — T01–T12
## AI Community Aid Navigator — IBM SkillsBuild

**Document status:** Preparatory protocol — for team review and Julia's approval before execution  
**Prepared by:** Bob (IBM SkillsBuild AI Experiential Learning Lab)  
**Prepared:** 2026-11-03  
**Source authority:** Final Consolidation & Implementation Baseline (17 Oct 2026) §H; Shared JSON Contracts v1.1 (27 Oct 2026); Approved Decisions 7, 8A, 30.8  
**Do not execute:** Scenarios classified Category B or C require components not yet built. Do not mark any scenario PASS without an executed test. This document records *criteria* and *current evidence* — it is not a test result.

---

## 1. Purpose and Scope

This protocol formalises the twelve acceptance scenarios defined in Technical Design §H (the "Acceptance suite and implementation gates") as executable test specifications. It is the primary reference for Build Gate 4: "run fixtures T01–T12 and existing detailed domain fixtures." These gates are not yet claimed as completed.

**Scope:**
- T01–T12 as defined verbatim in the Baseline §H.
- Cross-references to approved contract and architecture rules that govern each scenario.
- Current implementation evidence from the live test run executed during the 2026-11-03 audit.
- Classification of what can be tested now versus what requires components not yet built.

**Out of scope:**
- The cross-domain acceptance tests at Technical Design §1480–1500 (distinct from T01–T12).
- Acceptance fixtures in individual domain sections (§16, §17, §18, §22, etc.).
- Performance, load, or security testing.
- IBM Orchestrate integration acceptance.

---

## 2. Source Documents Reviewed

| Document | Location | Key sections used |
|---|---|---|
| Final Consolidation & Implementation Baseline | `docs/architecture/Technical_Design.md` lines 1–138 | §A–§H (Parts A–F, acceptance suite) |
| Approved Decision 7 — Returning User | `docs/architecture/Technical_Design.md` lines 245–296 | Reassessment trigger, checkpoint, no-duplicate rule |
| Approved Decision 8A — User-triggered reassessment | `docs/architecture/Technical_Design.md` line 261 | Status-only change must not trigger reassessment |
| §30.3 Agent contracts and write authority | `docs/architecture/Technical_Design.md` line 1558 | Application Layer sole writer |
| §30.5 Government programs with missing facts | `docs/architecture/Technical_Design.md` line 1566 | Potential-options area |
| §30.6 Conflicting / unverifiable resources | `docs/architecture/Technical_Design.md` line 1570 | Agent 7 flags; Agent 10 checks |
| §30.7 Case persistence and user-led reassessment | `docs/architecture/Technical_Design.md` line 1574 | Anonymous / registered sessions |
| §30.8 APPROVED — Single communication gateway | `docs/architecture/Technical_Design.md` line 1580 | Clarification deduplication |
| Shared JSON Contracts v1.1 §2.2, §3.6, §5.2–5.3 | `docs/contracts/SHARED_CONTRACTS.md` | S3 stale check, S7 timeout, ProgressStatus, repair rounds |
| §27 Crowdfunding — informational guidance only | `docs/architecture/Technical_Design.md` line 1436 | T11 scope |

---

## 3. Original T01–T12 Scenarios

The following is the verbatim text from Technical Design §H (lines 113–135). These definitions are reproduced exactly; they have not been paraphrased or extended.

> **T01** Multiple agents request household income: Supervisor asks once, answer shared across tasks, no direct agent-user message.
>
> **T02** Registered user interrupts during a question: checkpoint survives, Supervisor resumes same Case without full intake restart.
>
> **T03** Anonymous user leaves without registration: no persistent Case or restoration link; one-time email delivery never creates an account.
>
> **T04** Case updated while agents run: stale case_version results cannot overwrite newer facts or user-entered action statuses.
>
> **T05** Government program is officially documented but eligibility facts missing: show relevant potential option with official link and missing conditions, not a false rejection.
>
> **T06** Program source unavailable or conflicting: no verified/available claim; Agent 7 flags; final Agent 10 checks representation.
>
> **T07** One independent agent times out: dependent actions are not falsely marked complete; unrelated validated assistance can proceed with transparent limitations.
>
> **T08** Newborn or changed income in saved Case: reconsider affected old and new needs without duplicating cards or resetting user statuses.
>
> **T09** User changes only Action Card status: no automatic new program search.
>
> **T10** User has several needs: preserve all, support parallel paths, no arbitrary top-three cap.
>
> **T11** Crowdfunding draft request: no generated appeal; only factual platform guidance.
>
> **T12** KB has no verified match: retain unmet need and explain limitations, never hallucinate a resource.

---

## 4. Acceptance Criteria and PASS/FAIL Conditions

---

### T01 — Multiple agents request household income: ask once, share the answer

**Objective:** Verify that when more than one agent requests the same fact (`household_gross_monthly_income` or equivalent), the Supervisor consolidates the requests, asks the user exactly once, and distributes the answer to all agents that requested it — without any agent contacting the user directly.

**Source authority:** Baseline §B: "Supervisor merges duplicate/overlapping questions, checks existing Case facts, asks once." §30.8 APPROVED. Contracts v1.1 §3.3 (ClarificationRequest deduplication), §5.1 (Supervisor building one merged question).

**Required inputs:**
- A case where household income is relevant to two or more programs (e.g. CalFresh + EDD UI + CalWORKs).
- Agent 2 and at least one retrieval-phase agent both producing a ClarificationRequest for `household_gross_monthly_income`.

**Expected system behavior:**
1. Agent 2 and/or Agent 4 return `clarification_requests[]` containing a request for `household_gross_monthly_income`.
2. Supervisor checks `state.case_facts` — if the fact is already present (not null), no question is asked.
3. If absent, Supervisor merges equivalent requests (same `fact_key`, equivalent `question_intent`) into one.
4. Supervisor sends one consolidated question through the UI (single call to Application Layer).
5. User answers once; Application Layer writes the answer to Case State.
6. Supervisor distributes the updated fact to all agents requiring it before resuming.
7. No agent output contains a message directed at the user.

**PASS criteria:**
- Exactly one user-facing question for `household_gross_monthly_income` per cycle, regardless of how many agents request it.
- `state.already_asked` updated after the question is asked; same fact not re-asked in subsequent cycles.
- No agent result carries a direct user-facing message (all `clarification_requests` remain in the structured envelope, not rendered directly).
- All agents receiving the answer use the same updated fact value.

**FAIL criteria:**
- Two or more separate questions for the same fact reach the user in the same cycle.
- An agent communicates directly with the user outside the Supervisor path.
- A fact already present in Case State triggers a re-ask.
- The answer is not distributed; agents run without the updated fact.

**Readiness classification:** **Category B + C** — requires Application Layer (to write the answer to Case State and distribute it), UI (to send the question and receive the answer), and real Agent 2 implementation.

**Current implementation gap:** `run.py` logs `CLARIFICATION_PENDING` only; no deduplication, no ask-once, no answer distribution is implemented (Audit Defect D-07). `state.already_asked` is never updated after a question is asked.

**Existing test evidence:** None. No automated test exists for this scenario. `test_run_v2.TestAgent2Updates.test_need_updates_applied` verifies Agent 2 urgency updates reach the Supervisor but does not exercise clarification deduplication.

**⚠️ Requires Product Owner Confirmation — Julia:** The deduplication rule says "merges requests with the same *meaning*, not merely string equality" (Contracts §3.3). The exact algorithm for semantic equivalence (e.g., whether `household_gross_monthly_income` and `current_monthly_income` are treated as the same request) requires Julia's decision on the fact registry (currently binding as v1.1 §3.2 ACCEPTED fact key list).

---

### T02 — Registered user interrupts during a question: checkpoint survives

**Objective:** Verify that when a registered user leaves mid-question (closes the browser, session expires, network drop), the Supervisor stores enough state to resume exactly where the conversation paused, and does not restart full intake on return.

**Source authority:** Baseline §B: "On return, Supervisor resumes the pending question/step; no new intake or automatic full reassessment solely because the user logs in." §E (Dialogue checkpoint and interruption): "persist pending_question / current_step / relevant run context in existing Case-associated storage." §30.7.

**Required inputs:**
- A registered user session in progress.
- A pending clarification question from the Supervisor (not yet answered).
- Session interruption before the user answers.
- User returns and re-authenticates.

**Expected system behavior:**
1. Case State (in SQL, for registered users) contains `pending_question`, `current_step`, and relevant run context at the time of interruption.
2. On return, Supervisor reads the checkpoint and presents the same question again, identifying where the conversation paused.
3. No full intake restart; existing `needs`, `case_facts`, and `progress_status` values are preserved unchanged.
4. In-flight agent outputs from the interrupted run are not trusted (they were built on an older `case_version` or partial data); the Supervisor resumes from the checkpoint.

**PASS criteria:**
- Returning user sees the pending question from their last session (not a fresh "tell me about your situation" prompt).
- Existing needs, facts, and action statuses are intact after resumption.
- No duplicate Action Cards for needs already in the plan.
- In-flight results from the interrupted run that carry a stale `case_version` are rejected by check S3.

**FAIL criteria:**
- User is asked to re-enter their story from the beginning on login.
- User-entered progress statuses are reset.
- A stale result from the interrupted run overwrites newer Case facts.
- Duplicate needs or cards appear after resumption.

**Readiness classification:** **Category B + C** — requires SQL-backed Case State with checkpoint persistence, registered user authentication, and UI session management.

**Current implementation gap:** No Application Layer, SQL schema, or session persistence exists. `CaseState` is in-memory only; all state is lost when the process ends.

**Existing test evidence:** `test_builders.TestWithKB.test_stale_result_after_confirmation` verifies that a result built at an old `case_version` is rejected by S3. This is one necessary component of T02 but is not sufficient.

---

### T03 — Anonymous user leaves without registration: no persistence, one-time email never creates account

**Objective:** Verify that when an anonymous (unregistered) user ends their session without registering, no Case data is persisted; and if they request a one-time email copy of their plan, receiving that email does not create an account or any persistent record.

**Source authority:** Baseline §B: "Anonymous visitor: receives initial plan without account; may request one-time email copy without registration and with privacy warning; otherwise temporary session expires without persistent recovery." §30.7. Technical Design line 307.

**Required inputs:**
- An anonymous session that produces a complete plan.
- The user requests a one-time email copy (without registering).
- The user closes the session.

**Expected system behavior:**
1. Plan is generated and displayed within the session.
2. If user requests email: system sends one email with the plan and a privacy notice; does not create a user_id or case_id record in SQL; does not subscribe the address.
3. When the session ends, all temporary session data is discarded.
4. If the user returns later, they see a blank intake (no recovery link).

**PASS criteria:**
- No `user_id`, `case_id`, or persistent SQL row is created for an anonymous session.
- One-time email is sent with a privacy notice; email address is not stored beyond the delivery action.
- Returning anonymous user cannot recover their previous session.

**FAIL criteria:**
- A persistent record is created for an anonymous user.
- Email delivery creates an account or a marketing subscription.
- A one-time email link allows the user to restore the session (this would constitute account creation).

**Readiness classification:** **Category B + C** — requires Application Layer (session management, email delivery service), UI, and an email delivery component.

**Current implementation gap:** No session management, no email delivery, no Application Layer.

**Existing test evidence:** None.

---

### T04 — Case updated while agents run: stale results cannot overwrite newer data

**Objective:** Verify that if the Case is updated (e.g., user confirms or corrects a fact) while agents are still processing, any agent result carrying the old `case_version` is discarded and cannot overwrite the newer facts or user-entered action statuses.

**Source authority:** Baseline §D: "A consistent case_version snapshot per cycle prevents stale overwrites." §30.2. Contracts v1.1 §5.2 check S3: "case_version equals the current snapshot; discard, STALE_RESULT, re-run if needed."

**Required inputs (sub-scenario A — Supervisor-level):**
- An active run where `case_version` is 1 at the time Agent 3 is called.
- `confirm_agent1()` is called (bumping to version 2) before Agent 3 returns.
- Agent 3 returns a result carrying `case_version = 1`.

**Required inputs (sub-scenario B — Application Layer-level):**
- A registered user concurrently edits a case fact from the UI while agents are running.
- Application Layer bumps `case_version`.
- A completed agent result arrives for the old version.

**Expected system behavior:**
1. (Sub-A) Supervisor check S3 fires on the Agent 3 result. Result is discarded (`STALE_RESULT`). Supervisor re-runs the relevant step with the current version or reports the issue.
2. (Sub-B) Application Layer version check prevents the old result from committing.
3. In neither sub-scenario do stale facts or stale Action Cards overwrite the user's current data.

**PASS criteria (Sub-A — testable now):**
- `checks.s3_stale(result, current_version)` returns `[STALE_RESULT]` when `result["case_version"] < current_version`.
- A result carrying a stale `case_version` is never added to `state.results`.
- The Supervisor does not mark dependent steps as completed when the dependency result was stale.

**PASS criteria (Sub-B — requires Application Layer):**
- Application Layer rejects a committed write from an agent result carrying `case_version < current_version`.
- User-entered `progress_status` values are not overwritten.

**FAIL criteria:**
- A stale result is accepted and applied.
- A progress status set by the user is reset to `not_started` by a stale agent result.

**Readiness classification:** **Category A (sub-scenario A) + Category B (sub-scenario B)**.

**Existing test evidence (Category A — EXECUTED, PASS):**
- `tests/test_checks.py::TestEachCheck::test_s3_stale_version` — verifies `STALE_RESULT` issued when `case_version` mismatches. **PASS** (executed 2026-11-03).
- `tests/test_builders.py::TestWithKB::test_stale_result_after_confirmation` — verifies a result built at version 1 is stale after `confirm_agent1()` bumps to version 2. **PASS** (executed 2026-11-03).
- `tests/test_run.py::TestRunner::test_full_cycle_completes` — verifies `case_version == 2` after confirmation. **PASS** (executed 2026-11-03).

**Sub-scenario B status:** Not testable — Application Layer not built.

---

### T05 — Government program documented but eligibility facts missing: show potential option, not a false rejection

**Objective:** Verify that when a relevant government program is confirmed through an official source but the user's personal eligibility cannot be assessed (e.g., income unknown), the plan includes a `potential_options` entry with the program name, reason it may matter, what needs checking, and an official link — rather than omitting the program.

**Source authority:** Baseline §B: "Relevant official government programs with unknown personal eligibility may appear in a compact potential-options area with the official link and exact missing facts." §30.5. Contracts v1.1 §4.9 Agent 10 rule V11 (potential option must have official link and what_needs_checking).

**Required inputs:**
- A program in the KB where the user's household income is unknown.
- Agent 4 returns `match_status = "potential_match"` with `missing_case_facts = ["household_gross_monthly_income"]`.
- Agent 8 adds the program to `potential_options[]` (not to `action_cards[]`) with `official_link` and `what_needs_checking`.

**Expected system behavior:**
1. Agent 4 classifies the program as `potential_match` (not `confirmed_mismatch`).
2. Agent 8 adds a `potential_options` entry: `{program_id, program_name, why_it_may_matter, what_needs_checking: ["household income not yet provided"], official_link}`.
3. Agent 10 checks each `potential_options` entry for `official_link` and `what_needs_checking`; flags V11 if either is missing.
4. No `confirmed_mismatch` is reported for a program where income is merely unknown.

**PASS criteria:**
- Unknown income does not produce `confirmed_mismatch` in Agent 4.
- Potential option appears in the plan with both `official_link` and `what_needs_checking` populated.
- Agent 10 returns PASS (no V11 flag) for a well-formed potential option.
- Agent 10 flags V11 for a potential option missing either field.

**FAIL criteria:**
- Program is omitted from the plan solely because income is unknown.
- Program is shown as an `action_card` rather than a `potential_option` when eligibility is unverifiable.
- `confirmed_mismatch` is reported for unknown income.

**Readiness classification:** **Category A (partial — Agent 4 unknown-income check) + Category B (potential_options in final UI plan)**.

**Existing test evidence (Category A — EXECUTED, PASS):**
- `tests/agent_3_4_5/test_agents_3_4_5.py::T2_UnknownInfo::test_unknown_income_not_mismatch` — confirms `match_status != confirmed_mismatch` and `household_gross_monthly_income` in `missing_case_facts`. **PASS** (executed 2026-11-03).
- `tests/agent_6_7_8_10/run_tests.py` check `B-H1`: "Unknown income: plan PASSES" — full pipeline produces PASS verdict. **PASS** (executed 2026-11-03).

**Partial gap:** The current mock Agent 8 (`agent_6_7_8_10.py`) always returns `potential_options: []`. A program with `missing_case_facts` does not yet flow into `potential_options[]`. Agent 10 V11 logic for `potential_options` is implemented but cannot fire because Agent 8 never populates the field.

**⚠️ Requires Product Owner Confirmation — Julia:** The Baseline §30.5 says "the plan *may* include a compact potential-options entry." The word "may" leaves open whether this is always required or situational. A precise rule for when a program transitions from `potential_option` to `action_card` (or is omitted) requires Julia's direction.

---

### T06 — Program source unavailable or conflicting: no verified claim, Agent 7 flags, Agent 10 checks

**Objective:** Verify that when a program's source is unavailable (website unreachable) or conflicting (two sources disagree on a value), the system does not label the program as verified or available; Agent 7 flags the issue at the intermediate stage; and Agent 10 verifies the user-facing wording does not overstate certainty.

**Source authority:** Baseline §B: "Separate source/program verification, individual eligibility uncertainty, and intake/funding availability." §30.4, §30.6. Contracts v1.1 §4.5 Agent 5 (conflicting claims stay conflicting), §4.7 Agent 7 rules Q1, Q2, Q4, §4.9 Agent 10 rules V2, V6, V7.

**Required inputs (conflicting):**
- Two EvidenceRecord rows for the same `field_path` (e.g. `deadlines[0]`) with different `claim_value` and different `source_url`.

**Required inputs (unavailable):**
- An EvidenceRecord where `issue` contains "timed out" or "unreachable".
- The program's `availability` field is `temporarily_closed` based solely on the failed check.

**Expected system behavior:**
1. Agent 5 sets `verification_status = "conflicting"` for the conflicting field; `claim_value = null`.
2. Agent 7 checks the verification stage result: issues Q2 finding (critical for deadline fields, warning for others).
3. Agent 6 does not choose one conflicting date as `official_deadline`; both dates appear in `uncertainty_notes`.
4. Agent 8 card shows both dates and a "confirm with provider" step.
5. Agent 10 flags V5 if a single date from a conflicting set is presented as the deadline.
6. For an unreachable source: Agent 7 issues Q4 if `temporarily_closed` is inferred from a failed check only. Agent 10 flags V7 if the card says "the website doesn't list this" when the website was unreachable.

**PASS criteria:**
- Conflicting verification status is never silently resolved to a single value.
- No `verified` or `available` label appears on a claim backed only by a failed source check.
- Agent 7 Q2 finding present for the conflicting field.
- Agent 10 flags V5 when a single conflicting date appears as `official_deadline`.
- Agent 10 flags V7 when unavailability is misrepresented as a confirmed site omission.

**FAIL criteria:**
- A single date is chosen from a conflicting set and presented as the official deadline.
- A program is shown as `confirmed_open` because its source was unavailable (S5 passes an incorrect enum).
- Agent 7 or Agent 10 passes a card that misrepresents conflicting or unavailable information as confirmed.

**Readiness classification:** **Category A** — fully testable against current Python implementation.

**Existing test evidence (EXECUTED, PASS):**
- `tests/agent_3_4_5/test_agents_3_4_5.py::T3_ConflictAndNeedsReview::test_conflicting_sources_kept` — `verification_status = "conflicting"`, `claim_value = null`. **PASS** (executed 2026-11-03).
- `tests/agent_6_7_8_10/run_tests.py` checks `A6-4`, `A6-5`, `A6-6` (conflicting rent deadline — no date chosen, both dates in notes, confirm step first). **PASS** (executed 2026-11-03).
- `tests/agent_6_7_8_10/run_tests.py` check `A7-1` — Agent 7 Q2 critical for conflicting deadline. **PASS**.
- `tests/agent_6_7_8_10/run_tests.py` check `B-H2` — V5 fires when conflicting deadline replaced by one date. **PASS**.
- `tests/agent_6_7_8_10/run_tests.py` check `C-Q4` — Q4 fires when `temporarily_closed` inferred from failed check. **PASS**.
- `tests/agent_6_7_8_10/run_tests.py` check `C-V7` — V7 fires when card says website lacks info but site was unreachable. **PASS**.

**T06 is the most comprehensively tested acceptance scenario in the current codebase.**

---

### T07 — One independent agent times out: dependent actions not falsely completed, unrelated assistance proceeds

**Objective:** Verify that when an independent agent call exceeds the 30-second timeout, (a) the agent process is terminated (does not continue running), (b) dependent steps are not marked completed, (c) the run reports the timeout transparently, and (d) independent validated assistance from other paths can still be released.

**Source authority:** Baseline §B: "Bound retries, timeouts and loop depth; represent partial failures explicitly." §30.2. Contracts v1.1 §5.2 check S7 (30-second timeout → `TIMEOUT` issue), §5.3 (1 retry per call). Technical Design §H T07.

**Required inputs:**
- An agent implementation that does not respond within 30 seconds (e.g. hangs indefinitely).
- At least one independent agent path (different need or different stage) that does respond normally.

**Expected system behavior:**
1. Supervisor's `_call_in_process` or `_call_in_thread` fires after `TIMEOUT_SECONDS` (30 s).
2. The agent process is terminated (not just abandoned).
3. Check S7 produces `TIMEOUT` issue; result is treated as failed (same as `status = "failed"`).
4. One retry is attempted; if it also times out, the run stops at the timed-out agent's position.
5. In the current linear pipeline, a timeout at Agent 3 stops the run (`stopped_at_agent_3`). Independent-path recovery (T07 full scope) requires a parallel execution model not yet implemented.
6. The `outcome` field in the run report reflects the timeout; `partially_mocked` is noted.

**PASS criteria:**
- `TIMEOUT` issue code present in the step record for the timed-out agent.
- The timed-out agent's process has no remaining active children after 5 seconds (`multiprocessing.active_children() == []`).
- The run does not silently present the timed-out agent's work as completed.
- Exactly 2 attempts (original + 1 retry) before the run stops.

**FAIL criteria:**
- A timed-out agent process continues running after the timeout.
- A dependent step is marked `completed` despite its upstream having timed out.
- The timeout is silently ignored and the run continues as if the agent responded.

**Readiness classification:** **Category A** — core timeout and retry mechanics are testable now. Full "independent paths proceed" behavior requires a parallel execution model (not yet built).

**Existing test evidence (EXECUTED, PASS):**
- `tests/test_run.py::TestRunner::test_timeout` — Agent 3 timeout stops run at `stopped_at_agent_3`; `TIMEOUT` code present. **PASS** (executed 2026-11-03).
- `tests/test_run_v2.py::TestProcessIsolation::test_timeout_really_stops_the_agent` — process isolation: actual 30-second agent is stopped within ~2 seconds; `active_children() == []` verified. **PASS** (executed 2026-11-03).
- `tests/test_run_v2.py::TestAgent7::test_agent7_failure_never_blocks` — Agent 7 timeout/crash does not stop the run. **PASS** (executed 2026-11-03).

**Partial gap:** The current pipeline is sequential (Agent 3 → 4 → 5 → …). T07's intent that "unrelated validated assistance can proceed" requires parallel execution branches for independent needs. This is not yet implemented. The tested behavior only confirms that Agent 7 failures are non-blocking. Full T07 compliance requires parallel need paths.

---

### T08 — Newborn or changed income in saved Case: reconsider affected needs, no duplicates, no status reset

**Objective:** Verify that when a returning registered user reports a material change (new household member, changed income), the system re-evaluates only affected needs and programs, without duplicating existing Action Cards or resetting user-entered progress statuses. Existing completed/received actions must not reappear as new actions.

**Source authority:** Baseline §B: "Full-context logical reassessment happens when user reports changed circumstances/new need." Approved Decision 7. Decision 8A: "User-triggered reassessment … preserves history and user-set statuses." Acceptance fixture R3: "User previously marked an application Completed / Received: do not reset its status or add the same application as a fresh action."

**Required inputs:**
- A registered user with an existing Case containing needs, a plan, and at least one Action Card with `progress_status = "completed_received"`.
- User reports a newborn (new household member) and states household income is unchanged.

**Expected system behavior:**
1. Agent 1/2 receive the changed fact (household_size +1) and identify only household-sensitive needs for reassessment.
2. Only needs and programs affected by the changed fact are re-evaluated; food and housing needs relevant to household size are rechecked.
3. Agent 8 updates the SAME plan: new or changed actions are added; existing completed actions are retained with their `progress_status` unchanged.
4. No new duplicate of an already-completed card is created.
5. No previously completed card is reset to `not_started`.

**PASS criteria:**
- `progress_status = "completed_received"` on existing cards is unchanged after reassessment.
- No duplicate `card_id` or duplicate program card appears in the plan after reassessment.
- Only household-size-sensitive programs are re-matched; unrelated programs are not re-evaluated.

**FAIL criteria:**
- Any `progress_status` is reset to `not_started` by the reassessment.
- A card the user marked `completed_received` reappears as a new action.
- All programs are re-evaluated regardless of whether the change affects their eligibility criteria.

**Readiness classification:** **Category B + C** — requires SQL-backed Case State with history, Application Layer versioning, and UI interaction.

**Current implementation gap:** No Application Layer; `CaseState` is in-memory only. Agent 10 rule V10 (flags any agent-set `progress_status != "not_started"`) is implemented, but the preservation of *user-set* statuses through reassessment has no implementation or test.

**Existing test evidence:**
- `tests/agent_6_7_8_10/run_tests.py` check `B-H8` — `progress_status` set by the system (not user) flagged V10. **PASS** (executed 2026-11-03). This demonstrates the constraint but not the reassessment preservation logic.

---

### T09 — User changes only Action Card status: no automatic new program search

**Objective:** Verify that when a user changes only the `progress_status` of one or more Action Cards (e.g., marks an action "In progress"), this edit does not trigger a new agent search, reassessment, or any change to other plan elements.

**Source authority:** Approved Decision 8A: "Merely logging in, viewing the plan, or changing a user-selected action progress status MUST NOT trigger a full reassessment." Baseline §B: "Status-only updates do not trigger reassessment." Contracts v1.1 §3.6: "Only an explicit user action changes `progress_status`. Agents always create cards with `not_started` and never change it."

**Required inputs:**
- A registered user with a completed plan.
- User changes one card's `progress_status` from `not_started` to `in_progress`.

**Expected system behavior:**
1. Application Layer records the new `progress_status` for the card and bumps the card's history.
2. No new Supervisor run is initiated.
3. No agent calls are made.
4. Plan content, other card statuses, and case facts are unchanged.

**PASS criteria:**
- No new run_id is created; no agent calls appear in the run log.
- `progress_status` change is persisted in SQL.
- All other plan elements (other cards, needs, facts) are unchanged.

**FAIL criteria:**
- A status change triggers an agent run (any of Agents 1–10 are called).
- Another card's `progress_status` is changed as a side effect.
- The plan is regenerated after a status change.

**Readiness classification:** **Category B + C** — requires Application Layer (to distinguish a status-only write from a Case fact change) and UI.

**Current implementation gap:** No Application Layer; no distinction between status-update writes and fact-change writes is implemented. Agent 10 V10 rule prevents agents from setting `progress_status`; the inverse (UI-level status writes not triggering agents) has no code path.

**Existing test evidence:**
- `tests/agent_6_7_8_10/run_tests.py` check `B-H8` — Agent-set `progress_status` flagged by V10. Demonstrates the constraint from the agent side only.

---

### T10 — User has several needs: preserve all, support parallel paths, no top-three cap

**Objective:** Verify that when a user states multiple distinct needs, the system retains all of them throughout the pipeline, produces one Action Card (or coverage gap) per need, and does not silently cap, drop, or merge needs.

**Source authority:** Baseline §A: "No fixed cap on stated needs, candidate programs or Action Cards." §B: "Only user-raised needs trigger corresponding domains." §30.1: "Run independent tasks concurrently when safe." Contracts v1.1 §4.9 Agent 10 rule V12 (need not covered by plan and no gap note → flagged).

**Required inputs:**
- A story containing three or more distinct need categories (e.g., income, housing, food — the shared synthetic test case).
- All needs confirmed after Agent 1.

**Expected system behavior:**
1. All stated needs appear in `state.needs` after `confirm_agent1()`.
2. Agent 3 retrieves candidates for each need independently.
3. Agent 6 produces at least one proposed action per need (or a coverage_gap issue if no KB program exists).
4. Agent 8 produces at least one Action Card per need, or adds a `coverage_gaps[]` entry.
5. Agent 10 does not flag V12 (need missing from plan with no gap) for any stated need.
6. No implicit cap at three cards, three candidates, or three needs.

**PASS criteria:**
- `len(state.needs)` equals the number of distinct needs the user stated.
- Every `need_id` from `state.needs` appears in at least one Action Card's `related_need_ids[]` or in `coverage_gaps[]`.
- Agent 10 returns PASS (no V12 flags) for the full-coverage case.
- All three P0 needs (income, housing, food) produce separate cards in the synthetic test case.

**FAIL criteria:**
- Any stated need is absent from the plan (no card and no coverage gap).
- The plan is silently capped at three Action Cards regardless of need count.
- Agent 10 flags V12 for a need that should be covered.

**Readiness classification:** **Category A** — fully testable against current Python implementation with mock agents.

**Existing test evidence (EXECUTED, PASS):**
- `tests/agent_3_4_5/test_agents_3_4_5.py::T1_ClearMatch::test_all_three_needs_covered` — all three P0 needs retrieve matching programs. **PASS** (executed 2026-11-03).
- `tests/agent_6_7_8_10/run_tests.py` check `A6-2` — "No need dropped" (all three need_ids in proposed_actions). **PASS**.
- `tests/agent_6_7_8_10/run_tests.py` check `B-COV` — "Plan covers all 3 stated needs." **PASS**.
- `tests/test_run.py::TestRunner::test_full_cycle_completes` — 2-need fake case produces 2 cards. **PASS**.

**Partial gap:** Tests use 2–3 needs; an explicit test with 5+ needs (as the cross-domain test T1 specifies) has not been executed. The code has no cap; this is a code-inspection confidence only for the 5+-need case.

---

### T11 — Crowdfunding draft request: no generated appeal; only factual platform guidance

**Objective:** Verify that when a user asks the Navigator to write a crowdfunding appeal, the system declines to generate content and offers only factual platform guidance (verified platform names, links, requirements, fees, privacy implications).

**Source authority:** Baseline §F (Crowdfunding: "verified platform setup/rules only; no drafting, rewriting or optimizing appeals"). Technical Design §27.3: "The Navigator must not draft, rewrite, edit, title, embellish or emotionally optimize a fundraising appeal." §27.2: "Provide verified platform names and links … self-service steps." Contracts v1.1 §3.4: `crowdfunding_guidance` category with `platform_guidance` subcategory.

**Required inputs:**
- User story or explicit request: "Can you write my GoFundMe story?" or "Help me write a fundraiser."
- Agent 1 extracts a `crowdfunding_guidance` need from the request.

**Expected system behavior:**
1. Agent 1 identifies a `crowdfunding_guidance` need (`category = "crowdfunding_guidance"`, `subcategory = "platform_guidance"`).
2. Agent 3 retrieves only KB entries with `category = "crowdfunding_guidance"`.
3. Agent 8 produces an Action Card with a `next_step` that describes how to independently create a fundraiser — no generated text, no appeal draft.
4. No agent output contains a fundraising appeal, story, or emotionally optimized content.
5. Agent 10: no V1 (unsupported guarantee), no V2 (unverified claim presented as confirmed), V13 not triggered.

**PASS criteria:**
- No agent output contains a fundraising appeal or draft story text.
- Plan includes factual platform guidance: platform names, official links, self-service steps.
- `action_title` and `next_step` use neutral, factual language (no "You will receive donations").
- `category = "crowdfunding_guidance"` correctly routes through the pipeline.

**FAIL criteria:**
- Any agent generates appeal text, a story draft, or emotionally optimized fundraising copy.
- The plan promises donation amounts or guarantees fundraiser success.
- The `crowdfunding_guidance` need is silently dropped instead of producing platform guidance.

**Readiness classification:** **Category A (partial)** — the category enum and routing are implemented. A full T11 test requires real Agent 1 (which cannot parse the user's request as a crowdfunding need) and KB entries for crowdfunding platforms (not yet in `kb_sacramento.json`). Agent 8 `TEMPLATES` contains no `crowdfunding_guidance` or `platform_guidance` entry; the `DEFAULT` template would be used.

**Current implementation gap:** No KB entries for crowdfunding platforms. No `platform_guidance` template in Agent 8. Real Agent 1 is absent. A partial smoke test can confirm the category enum is accepted and routes without crashing, but cannot verify content compliance.

**Existing test evidence:**
- `navigator/kb/tools/validate_kb.py` confirms `crowdfunding_guidance` is a valid category with `platform_guidance` subcategory (code inspection; not executed as a test in the main suite).
- No T11-specific test exists.

---

### T12 — KB has no verified match: retain unmet need and explain limitations, never hallucinate a resource

**Objective:** Verify that when the Knowledge Base contains no verified program for a stated need, the system retains the need in the plan as an explicit coverage gap with an honest explanation of why no program was found — and does not invent, hallucinate, or silently drop the unmet need.

**Source authority:** Baseline §B: "If the KB has no verified match: retain unmet need and explain limitations, never hallucinate a resource." §E (Domain safeguards): "No fabricated funding or guaranteed placement." §30.5: "empty result is valid and reported as a coverage gap, never filled with invented programs." Contracts v1.1 §4.3 Agent 3 (coverage gap issue on empty result), §4.8 Agent 8 (`coverage_gaps[]` output), §4.9 Agent 10 V12.

**Required inputs (sub-scenario A — category with no KB entry):**
- A need with `category = "other_unlisted"` or a category with no matching KB program in the pilot geography.

**Required inputs (sub-scenario B — unknown program ID):**
- Agent 3 returns a `candidate_programs[]` with a program_id not present in the KB (e.g. external discovery placeholder).
- Agent 5 receives this unknown program_id.

**Expected system behavior:**
1. Agent 3 returns no candidates and appends a `COVERAGE_GAP` issue for the need.
2. Agent 8 adds a `coverage_gaps[]` entry: `{need_id, note}` with an honest explanation.
3. Agent 10 does not flag V12 (need covered by a gap entry is treated as addressed).
4. No program is invented. No action card references a program_id not in the KB.
5. (Sub-B) Agent 5 returns `status = "failed"` with `UNKNOWN_PROGRAM` for an invented program_id; never treats it as `unverified`.

**PASS criteria:**
- `coverage_gaps[]` in the plan contains the unmet need_id with an honest explanation.
- No Action Card cites a program that did not originate from the KB.
- Agent 5 returns `UNKNOWN_PROGRAM` (critical) for an unknown program_id, not `unverified`.
- Agent 10 does not flag V12 when a coverage gap entry exists for the need.

**FAIL criteria:**
- An unmet need is silently dropped from the plan.
- An Action Card is produced for a program that does not exist in the KB.
- Agent 5 treats an invented program_id as an `unverified` program.

**Readiness classification:** **Category A** — fully testable against current Python implementation.

**Existing test evidence (EXECUTED, PASS):**
- `tests/agent_3_4_5/test_agents_3_4_5.py::T6_GeographyAndCategories::test_other_unlisted_is_coverage_gap` — `other_unlisted` need produces `COVERAGE_GAP` issue, no candidates. **PASS** (executed 2026-11-03).
- `tests/agent_3_4_5/test_agents_3_4_5.py::T7_InputErrors::test_3_unknown_program_is_not_unverified` — Agent 5 returns `UNKNOWN_PROGRAM` (critical) and `status = "failed"` for an invented program_id; `status = "partial"` when one real program is also in the list. **PASS** (executed 2026-11-03).
- `tests/agent_6_7_8_10/run_tests.py` check `B-H5` — Invented program in a card triggers V8 from Agent 10. **PASS**.
- `tests/test_run.py::TestRunner` — if Agent 3 returns real KB programs, plan uses real IDs; Supervisor S5 (`UNKNOWN_REFERENCE`) would catch an invented ID. Code-inspection confidence.

---

## 5. Readiness Classification

| Scenario | Category | Testable now | Blocked by | Partially covered |
|---|---|---|---|---|
| T01 | B + C | ❌ No | Application Layer + UI + real Agent 2 | S3 stale check (partial) |
| T02 | B + C | ❌ No | SQL session persistence + UI | S3 stale check (partial) |
| T03 | B + C | ❌ No | Application Layer + email delivery + UI | None |
| T04 | A + B | ✅ Sub-A | Application Layer for sub-B | S3 check, version bump — PASS |
| T05 | A (partial) + B | ⚠️ Partial | `potential_options` generation in Agent 8 | Unknown-income as non-mismatch — PASS |
| T06 | A | ✅ Yes | None | Conflicting claim, Q2, Q4, V5, V7 — all PASS |
| T07 | A (partial) | ⚠️ Partial | Parallel execution model | Timeout, process kill, S7 — PASS |
| T08 | B + C | ❌ No | SQL Case history + Application Layer + UI | V10 constraint — PASS |
| T09 | B + C | ❌ No | Application Layer + UI | V10 constraint — PASS |
| T10 | A | ✅ Yes | None | 3-need coverage — all PASS |
| T11 | A (partial) | ⚠️ Partial | Real Agent 1 + crowdfunding KB entries | Category enum routing — code inspection |
| T12 | A | ✅ Yes | None | Coverage gap, unknown program, V8/V12 — all PASS |

---

## 6. Existing Test Coverage and Evidence

### Executed during 2026-11-03 audit (live test run)

| Test file | Relevant scenarios | Result |
|---|---|---|
| `tests/test_checks.py::test_s3_stale_version` | T04 sub-A | **PASS** |
| `tests/test_builders.py::test_stale_result_after_confirmation` | T04 sub-A | **PASS** |
| `tests/test_builders.py::test_planning_package_availability_and_timing` | T06 (partial) | **FAIL** (stale KB expectation — see Audit D-02) |
| `tests/test_run.py::test_timeout` | T07 | **PASS** |
| `tests/test_run.py::test_missing_agent` | T07 | **PASS** |
| `tests/test_run.py::test_full_cycle_completes` | T04, T10 | **PASS** |
| `tests/test_run_v2.py::test_timeout_really_stops_the_agent` | T07 | **PASS** |
| `tests/test_run_v2.py::test_agent7_failure_never_blocks` | T07 | **PASS** |
| `tests/agent_3_4_5/test_agents_3_4_5.py::T2_UnknownInfo::test_unknown_income_not_mismatch` | T05 | **PASS** |
| `tests/agent_3_4_5/test_agents_3_4_5.py::T3_ConflictAndNeedsReview::test_conflicting_sources_kept` | T06 | **PASS** |
| `tests/agent_3_4_5/test_agents_3_4_5.py::T6::test_other_unlisted_is_coverage_gap` | T12 | **PASS** |
| `tests/agent_3_4_5/test_agents_3_4_5.py::T7::test_3_unknown_program_is_not_unverified` | T12 | **PASS** |
| `tests/agent_3_4_5/test_agents_3_4_5.py::T1_ClearMatch::test_all_three_needs_covered` | T10 | **PASS** |
| `tests/agent_6_7_8_10/run_tests.py` checks A6-2, B-COV, B-H1, B-H2, B-H5, B-H8, A7-1, C-Q4, C-V7 | T05, T06, T10, T12 | **All PASS** |

**Overall live test result (2026-11-03): 75/76 unittest tests passed; 54/54 agent 6/7/8/10 checks passed.**

The one failing test (`test_planning_package_availability_and_timing`) is a stale test expectation, not a system defect.

### Important caveats on all evidence

- All passing agents carry `is_mock: true`. Tests confirm correct *contract behavior* (envelope structure, enum handling, ordering logic), not production-quality AI decisions.
- T06 tests use synthetic KB fixtures (MOCK-RENT-01, MOCK-FOOD-PANTRY-01), not live Sacramento program sources.
- Tests for T01, T02, T03, T08, T09 do not exist. Those scenarios cannot be marked PASS.

---

## 7. Missing Dependencies

| Dependency | Blocks | Status |
|---|---|---|
| Real Agent 1 implementation (`navigator/agents/agent_1_2/`) | T01, T11, and all agent-call scenarios | **Missing — see Audit D-04** |
| Real Agent 2 implementation | T01, T06 (candidate_requirements) | Missing |
| Application Layer (SQL writes, version checking) | T01, T02, T03, T04 sub-B, T08, T09 | Not built |
| UI layer | T01, T02, T03, T08, T09 | Not built |
| Session checkpoint persistence | T02 | Not built |
| Email delivery service | T03 | Not built |
| Crowdfunding KB entries | T11 | Not in `kb_sacramento.json` |
| `potential_options` generation in Agent 8 | T05 (full) | Agent 8 always returns `potential_options: []` |
| Parallel execution model in Supervisor | T07 (full "unrelated paths proceed" scope) | Not built |
| `already_asked` list persistence | T01, T02 | Not persisted after questions are asked |
| Repair-merge fix (Supervisor) | T07 (plan completeness after repair) | Audit D-01 |

---

## 8. Product Owner Decisions Required

The following open items require Julia's decision before the corresponding acceptance criteria can be finalised or tested:

| Item | Scenario | Current default | Decision needed |
|---|---|---|---|
| **PO-1** When is a program a `potential_option` vs an `action_card` vs omitted? | T05 | Programs with missing income facts appear as `potential_match` but Agent 8 does not yet generate `potential_options[]` from them | Julia to confirm the rule for when a program transitions to `potential_options` in the user-facing plan |
| **PO-2** Clarification deduplication algorithm: what counts as "same meaning"? | T01 | Fact key registry (v1.1 §3.2 ACCEPTED) defines one name per fact; however, old-name aliases (e.g. `current_monthly_income` vs `household_gross_monthly_income`) exist in code | Julia to confirm whether the accepted fact-key registry fully resolves T01's deduplication requirement or whether additional synonym handling is needed |
| **PO-3** Progress status: 5 values (Blueprint v1.1) or 6 values (Baseline)? | T08, T09 | 6 values (Baseline) implemented; `contracts_v1.1` decision 11 PENDING JULIA | Affects how status-only changes are detected and what the UI shows |
| **PO-4** Evidence freshness window for Q7 (Agent 7 rule) | T06 (partially) | Decision 12 PENDING JULIA — currently reported as info only | Determines whether stale evidence triggers a warning that blocks a card |
| **PO-5** Full parallel execution: should unrelated-need agent paths run concurrently? | T07 | Current implementation is sequential within one pipeline run | Determines whether T07 can be fully satisfied ("unrelated validated assistance can proceed") with the current linear pipeline |

---

## 9. Recommended Test Execution Sequence

This sequence is designed for the Nov 7–8 readiness milestone. Prerequisites are listed; do not attempt later categories until earlier ones pass.

### Phase 1 — Category A (runnable now)

1. Resolve the failing test: update `tests/test_builders.py::test_planning_package_availability_and_timing` to handle both KB states (Audit D-02).
2. Run `python3 -m unittest discover tests -v` — target: **76/76 pass**.
3. Run `python3 tests/agent_6_7_8_10/run_tests.py` — target: **54/54 pass**.
4. Run targeted T04 sub-A test: confirm `STALE_RESULT` on version bump.
5. Run targeted T06 test: conflicting deadline (existing fixture `04_agent6_fixture_sacramento.json`), verify Q2 critical.
6. Run targeted T10 test: three-need synthetic case, verify all needs covered in plan.
7. Run targeted T12 test: `other_unlisted` need, verify coverage gap, no invented card.

### Phase 2 — Category A partial (after real Agent 1 is committed)

8. Commit Agent 1/2 implementation (prerequisite: Audit D-04 resolved).
9. Update `agents.json` to point to real Agent 1/2 modules.
10. Run `python3 -m navigator.supervisor.run --agents agents.json` with synthetic story (sample 01 or 06).
11. T10 full: verify 3-need story produces 3 cards or coverage gaps.
12. T12 full: use a need category with no KB program; verify coverage gap in run report.
13. T11 partial: supply a crowdfunding request story; verify no appeal text in any agent output.

### Phase 3 — Category B (after Application Layer is built)

14. T04 sub-B: concurrent Case update; verify version conflict rejected at the Application Layer.
15. T05 full: verify `potential_options[]` populated for a program with missing income facts.
16. T08: newborn + unchanged income; verify no card duplication, no status reset.
17. T09: status-only change; verify no new run initiated.

### Phase 4 — Category C (after UI is built)

18. T01: multi-agent income request; verify one question via UI, answer distributed.
19. T02: registered-user session interrupt; verify checkpoint, resume without full intake restart.
20. T03: anonymous user leaves; verify no persistence; one-time email does not create account.

### Regression after each fix

- After Audit D-01 (repair-merge fix): run `test_flagged_card_withheld_after_two_repair_rounds` and the new regression test with real Agent 8 repair.
- After each KB update: re-run `tests/agent_3_4_5/test_agents_3_4_5.py` (handles both KB states).
- After any Supervisor change: re-run all of `tests/test_run.py` and `tests/test_run_v2.py`.

---

## 10. Summary Matrix

| T | Scenario (abbreviated) | Readiness | Existing evidence | Blocking gap | PASS confirmed |
|---|---|---|---|---|---|
| T01 | Multi-agent income: ask once | B + C | None | Agent 1/2, App Layer, UI, deduplication logic | ❌ No |
| T02 | Registered user interrupts: checkpoint | B + C | S3 stale (partial) | SQL persistence, UI | ❌ No |
| T03 | Anonymous leaves: no persistence | B + C | None | App Layer, email, UI | ❌ No |
| T04 | Stale case_version: rejected | **A** ✅ (+ B for sub-B) | test_s3_stale_version, test_stale_result_after_confirmation | Sub-B: App Layer | ✅ Sub-A confirmed |
| T05 | Missing eligibility: potential option | A partial + B | Unknown-income non-mismatch | potential_options generation | ⚠️ Partial |
| T06 | Conflicting/unavailable source | **A** ✅ | Q2, Q4, V5, V7, A6-4/5/6 checks | None | ✅ Confirmed |
| T07 | One agent times out | A partial + future-parallel | test_timeout, test_timeout_really_stops | Parallel execution | ✅ Timeout/kill confirmed |
| T08 | Newborn/changed income: no duplicates | B + C | V10 constraint | SQL Case history, App Layer | ❌ No |
| T09 | Status-only change: no reassessment | B + C | V10 constraint | App Layer | ❌ No |
| T10 | Several needs: all preserved | **A** ✅ | T1_ClearMatch, A6-2, B-COV | None | ✅ Confirmed (3 needs) |
| T11 | Crowdfunding: no appeal draft | A partial | Category enum (code inspection) | Real Agent 1, crowdfunding KB | ⚠️ Partial |
| T12 | KB no match: coverage gap, no hallucination | **A** ✅ | T6::other_unlisted, T7::unknown_program | None | ✅ Confirmed |

**Legend:** ✅ Confirmed = test executed and passed on 2026-11-03 snapshot. ⚠️ Partial = partially testable; important gap remains. ❌ No = no pass evidence; blocked by missing components.

---

*This protocol documents acceptance criteria from approved sources and maps them to current implementation evidence. It does not introduce new product requirements. No source files, tests, or agent code were modified in its preparation.*
