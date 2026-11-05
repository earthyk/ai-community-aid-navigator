# MASTER TECHNICAL AUDIT & MVP ACTION PLAN

## AI Community Aid Navigator — IBM SkillsBuild

Date: November 3, 2026
Status: Main technical audit and working action plan
Primary source: IBM Bob — Independent Architecture, Contract, and Code Audit, November 3, 2026
Purpose: Establish the verified technical state of the project, identify MVP blockers, assign corrective actions, and coordinate the next development stage.

# 1. EXECUTIVE SUMMARY

An independent technical audit of the current repository was completed on November 3, 2026.

The audit included:

Full architecture and documentation review.

Shared JSON Contracts v1.1 inspection.

Implementation review of agents, Supervisor, Knowledge Base, contracts, and tests.

Execution of the existing test suites.

Six targeted defect reproduction cases.

Verification of approved architectural boundaries.

### Test results

| Test suite | Result |
| --- | --- |
| Python unittest | 75 passed / 76 |
| Agents 6/7/8/10 script checks | 54/54 passed |
| Additional targeted reproductions | 6 executed |

The audit identified two critical P0 blockers, four additional confirmed defects, and several architectural gaps.

The most important conclusion is that individual components have made meaningful progress, but the current repository cannot yet execute a complete end-to-end demonstration using the declared agent configuration.

Our immediate objective is to resolve the critical blockers, complete missing mandatory components, and establish a reproducible MVP integration path.

# 2. CRITICAL DEFECTS — P0

These issues must be addressed before the next end-to-end MVP demonstration.

## D-01 — Supervisor Repair-Merge Defect

Severity: P0 — Critical
Affected component: Supervisor / Agent 8
Provisional owner: Slav

### Problem

When Agent 10 flags only some Action Cards and Agent 8 successfully repairs them, the Supervisor assembles the final plan using only the repaired cards.

Cards that already passed Agent 10 in the original round are silently dropped.

### Impact

Users may receive an incomplete Action Plan even though the missing cards previously passed validation.

This violates the approved repair behavior in Shared Contracts v1.1, Section 5.3.

### Required correction

Preserve all cards that passed validation in the original round.

Merge successfully repaired cards with previously approved cards.

Deduplicate by card_id.

Continue withholding only cards that remain flagged after the permitted repair rounds.

### Acceptance criteria

A passing card remains in the final plan after another card is repaired.

A successfully repaired card is included.

A card that remains flagged is withheld.

No duplicate cards appear.

A regression test reproduces the original defect and confirms the correction.

## D-04 — Agents 1 and 2 Missing from Repository

Severity: P0 — Critical
Affected components: Agent 1, Agent 2, agents.json
Provisional owner: Yogesh

### Problem

The repository contains only a README in:

navigator/agents/agent_1_2/

The actual Python implementation, __init__.py, and required handle() functions are absent.

However, agents.json references:

navigator.agents.agent_1_2:handle

The actual execution returns AgentConfigError before any pipeline step starts.

### Impact

No complete pipeline execution.

No end-to-end demonstration.

No validation of the complete intake and clarification flow.

Baseline acceptance tests T01–T12 cannot be demonstrated through the intended pipeline.

### Required correction

Yogesh must provide and commit the actual Agent 1 and Agent 2 implementations.

Required interface:

handle(request: dict) -> dict

The implementation must follow the approved Shared JSON Contracts and existing architecture.

Temporary fake-agent configuration may be used only for a clearly labeled internal integration test. It must not be treated as completion of either agent.

### Acceptance criteria

Both agent modules exist in the repository.

Both expose the required handle() interface.

agents.json successfully loads both agents.

Individual tests cover the approved intake and clarification requirements.

The Supervisor starts successfully with the real Agent 1 and Agent 2 implementations.

# 3. HIGH-PRIORITY DEFECTS — P1

These issues should be resolved before the November 8 readiness milestone.

## D-02 — Stale Test Following the November 2 KB Update

Provisional owner: Slav

The Sacramento KB correctly reflects the November 2 update.

Saint John's is now confirmed_open, while one existing test still expects temporarily_closed.

The result is 75/76 passing tests.

### Required correction

Update tests/test_builders.py to reflect the current KB state and ensure that both historical and current availability states can be tested appropriately.

### Acceptance criteria

The test no longer assumes an outdated KB state.

The current KB behavior is verified.

All existing unittest tests pass.

This is a stale test expectation, not a confirmed production defect in the KB.

## D-06 — Agent 2 Does Not Receive Candidate Requirements

Provisional owner: Slav, in coordination with Yogesh

### Problem

Agent 2 currently runs before Agent 3.

Therefore, it cannot receive program-specific candidate_requirements generated through retrieval.

### Required action

Review the approved contract and intended clarification workflow.

Evaluate whether a second Agent 2 invocation after Agent 3 is required and architecturally appropriate.

Do not change the execution sequence until the request/response flow and clarification responsibilities are confirmed.

### Acceptance criteria

Relevant program-specific missing requirements can be identified.

Existing case facts are considered.

No unnecessary duplicate questions are introduced.

The final sequence is consistent with the approved architecture.

## D-07 — Clarification Deduplication Not Implemented

Provisional owner: Slav, in coordination with Yogesh

### Problem

The Supervisor currently logs CLARIFICATION_PENDING, but does not implement the complete approved clarification workflow.

Missing functionality includes:

Checking existing Case facts.

Merging duplicate or overlapping questions.

Asking each necessary question only once.

Recording the answer centrally.

Distributing the answer to relevant agents.

Maintaining the already_asked list.

### Required correction

Implement the clarification orchestration required by the approved Baseline and Section 30.8.

### Acceptance criteria

Duplicate questions are merged.

Already-known facts are not requested again.

Each necessary question is presented once.

Answers are distributed to all relevant agents.

Answered or declined questions are recorded appropriately.

## AR-03 — Persistence of already_asked

Provisional owner: Slav

The current in-memory implementation does not persist already_asked after clarification interactions.

This creates a risk that returning users will be asked questions they have already answered.

### Required correction

Ensure the Application Layer preserves this information across returning sessions.

Do not implement a separate persistence mechanism inside individual agents.

### Acceptance criteria

A returning user must not be asked again for information already recorded as answered or declined, unless a legitimate reassessment requires clarification.

# 4. MEDIUM-PRIORITY DEFECTS — P2

These issues should be resolved before final submission.

## D-03 — Multi-Need Coverage Gap

Provisional owner: Hisham

Agent 6 currently uses only the first need_id from a matched program when calculating coverage.

When one program supports multiple needs, the other needs may incorrectly receive a COVERAGE_GAP warning.

### Required correction

Evaluate all relevant need_ids associated with each matched program.

### Acceptance criteria

A single program supporting multiple needs correctly covers every relevant need.

No false COVERAGE_GAP is generated.

Genuine uncovered needs are still identified.

Reordering need_ids does not change the result.

## D-05 — Repair Loses potential_options and coverage_gaps

Provisional owner: Hisham

Agent 8's repair response currently initializes:

potential_options: []

coverage_gaps: []

This can remove information from the original plan after repair.

### Required correction

Preserve the original informational outputs when rebuilding flagged cards.

### Acceptance criteria

Repairing an Action Card does not erase unrelated potential options.

Existing coverage gaps remain available.

The final plan preserves all unaffected information.

## Additional P2 Improvement — Repair Handlers

The audit also identified missing repair handlers for V3, V6, and V13.

Hisham should review these validation rules and determine the appropriate correction behavior.

Unresolved flags must continue to result in withholding the affected card when required. Do not weaken validation simply to increase the number of released cards.

# 5. ARCHITECTURAL REQUIREMENTS AND RISKS

These are not all confirmed runtime defects. Some cannot be validated until the Application Layer and UI exist.

## AR-01 — Application Layer and SQL Persistence

Owner: To be assigned

The current repository has no Application Layer, SQL schema, or persistent Case storage.

Required future responsibilities:

Case persistence.

Case version checking.

Approved plan updates.

Preservation of user-entered progress statuses.

Returning-user Case recovery.

The Application Layer must remain the only component authorized to commit approved Case and plan changes.

Agents must not write directly to SQL.

## AR-02 — Status-Only Changes

A status-only update must not trigger a full reassessment.

This requirement cannot yet be verified because the UI and Application Layer are not implemented.

The future implementation must distinguish between:

Changes to relevant Case facts.

Changes to user-controlled Action Card progress statuses.

## AR-04 — Agent 3 source_policy

The audit contains an inconsistency concerning whether source_policy is enforced.

It reports that Agent 3 does not explicitly inspect the policy, but elsewhere describes KB-only behavior as enforced.

### Required action

Inspect the actual Agent 3 implementation and verify:

Which source types it currently uses.

Whether source_policy is explicitly checked.

Whether external discovery can ever occur without the correct policy.

Whether the current verified-KB-only behavior is preserved.

No external discovery implementation should be added without explicit architectural approval.

## AR-05 — IBM watsonx Orchestrate Integration

Decision owner: Julia, with implementation owner to be assigned.

The current repository contains a local Python prototype.

It does not contain an IBM watsonx Orchestrate integration or IBM Granite model calls.

A local Python prototype alone does not establish completed IBM platform integration.

### Required action

Define the minimum demonstrable IBM integration path, including:

Which components will use IBM technology.

Where watsonx Orchestrate will participate.

Whether and where watsonx.ai / Granite will be used.

How the integration will be demonstrated and documented.

The IBM Technology Statement must accurately describe the actual implementation.

# 6. COMPONENT STATUS

| Component | Current status |
| --- | --- |
| Agent 1 | Missing implementation |
| Agent 2 | Missing implementation |
| Agent 3 | Implemented, mock |
| Agent 4 | Implemented, mock |
| Agent 5 | Implemented, mock |
| Agent 6 | Implemented, mock |
| Agent 7 | Implemented, mock |
| Agent 8 | Implemented, mock |
| Agent 9 | Deferred by design |
| Agent 10 | Implemented, mock |
| Supervisor | Working, with confirmed defects |
| Sacramento KB | Published, updated November 2 |
| UI | Not built |
| Application Layer | Not built |
| SQL persistence | Not built |
| Email/account flows | Not built |
| watsonx Orchestrate | Not integrated |

All agents currently identified as mocks must remain explicitly labeled as such until their actual implementations replace the mock behavior.

Agent 9 is not an immediate MVP blocker because its absence is consistent with the approved deferral.

# 7. MVP EXECUTION PRIORITIES

The following sequence is recommended.

### Phase 1 — Restore a runnable pipeline

Yogesh delivers Agents 1 and 2.

Slav fixes D-01.

The real agent configuration loads successfully.

A complete local pipeline execution is demonstrated.

### Phase 2 — Correct orchestration behavior

Fix clarification handling.

Confirm the correct Agent 2 execution sequence.

Implement ask-once behavior.

Preserve already_asked.

Verify Case facts are not unnecessarily requested again.

### Phase 3 — Stabilize planning and validation

Hisham fixes D-03.

Hisham fixes D-05.

Review missing repair handlers.

Slav fixes the stale test.

Run all regression tests.

### Phase 4 — Application and IBM integration

Define the minimal Application Layer.

Define the minimum persistence and version-checking approach.

Establish the IBM integration path.

Prepare the public prototype and demonstration.

# 8. INTEGRATION AND ACCEPTANCE GATES

The following gates should be used to determine whether the MVP is ready.

| Gate | Required evidence |
| --- | --- |
| Gate 1 | Agents 1 and 2 load and pass their individual tests |
| Gate 2 | Supervisor completes a full run using real agent modules |
| Gate 3 | Repair-merge regression test passes |
| Gate 4 | Clarification flow follows the approved ask-once rules |
| Gate 5 | All existing regression tests pass |
| Gate 6 | Baseline acceptance tests T01–T12 are formalized and executed |
| Gate 7 | Application Layer and required Case behavior are demonstrated |
| Gate 8 | IBM integration is demonstrated and documented |

The current project has not yet demonstrated all these gates.

Passing individual agent tests must not be treated as proof of successful end-to-end integration.

# 9. DEVELOPMENT AND QUALITY CONTROL RULES

Effective immediately, the following working rules apply:

Every owner must test their own implementation before submitting it.

Each submission must include the files changed, test results, and any known limitations.

Shared contracts must not be changed unilaterally.

No agent should independently rewrite another agent's implementation.

Existing working components must be preserved unless a specific defect requires a change.

Any change to Supervisor sequencing must be checked against the approved architecture.

No critical issue may be marked resolved without a reproducible regression test.

Integration must be performed incrementally, not postponed until every agent is declared complete.

Mock implementations must be clearly identified.

The final MVP must be reproducible from a clean repository checkout.

# 10. TEAM RESPONSIBILITY SUMMARY

| Team member | Primary responsibilities |
| --- | --- |
| Yogesh | Agent 1 and Agent 2 delivery, clarification agent coordination |
| Silver | Agents 3–5, Sacramento KB maintenance |
| Hisham | Agents 6–8 and 10, planning and validation corrections |
| Slav | Supervisor, orchestration, repair merge, clarification workflow, integration |
| Julia | Product decisions, architecture approval, acceptance testing, project coordination |

These assignments are provisional and should be reconciled with the latest team development plan.

# 11. FINAL PROJECT DIRECTION

The independent audit has identified important issues, but it also confirms that substantial foundational work has already been completed.

We should not restart development or rebuild functioning components.

Our immediate focus is:

Complete → Integrate → Test → Demonstrate.

The objective is a working, reliable MVP that follows the approved architecture and demonstrates a complete user journey.

The audit report and this action plan should serve as the primary technical reference for the next development stage.

Every team member is expected to review the findings relevant to their responsibilities, acknowledge the identified issues, and report their corrective actions and test evidence.

This document supersedes informal technical assumptions and serves as the consolidated working reference for MVP completion, subject to approved architecture decisions and subsequent verified updates.
