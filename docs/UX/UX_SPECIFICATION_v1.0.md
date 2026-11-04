# AI Community Aid Navigator
## UX Specification v1.0

*Product Owner working specification | November 3, 2026*

> This document defines the agreed user-facing interaction model and initial wireframe direction. It does not claim that the UI, Application Layer, speech services, account flow, or email flow are already implemented.

Conversation-first experience | Product Owner working specification | 3 November 2026


## 1. Purpose and status

This document defines the agreed user-facing interaction model and provides a first low-fidelity wireframe direction for the AI Community Aid Navigator. It is a Product Owner UX specification for review and implementation planning; it does not claim that the UI, Application Layer, speech services, account flow, or email flow are already implemented.

Source discipline: existing architecture requirements are retained where supported by the project materials. The detailed voice-first interaction and chat-style visual direction in this document are recorded as explicit Product Owner UX decisions from the design discussion and should be reconciled with the approved Solution Blueprint, Technical Design, and Shared JSON Contracts before implementation. They must not silently alter agent contracts or pipeline sequencing.


## 2. Core product principle: Conversation First

The Navigator should feel like one calm, capable assistant having a natural conversation with the user—not like a traditional government application form and not like a collection of separate agent screens.

- One continuous conversation is the primary user interface.
- User messages appear on the right; Navigator messages appear on the left.
- The user can use voice or text at any point and can switch between them within the same conversation.
- Internal agent names and orchestration details are not exposed to the user. The user interacts with one Navigator.
- Structured content (identified needs, clarification prompts, progress summaries) appears as cards embedded in the conversation.
- The Crisis Action Plan can also be opened in a separate structured view without creating a separate product or disconnected workflow.

## 3. End-to-end user journey

1. Welcome / Start: A brief, reassuring introduction. Invite the user to explain what happened in their own words. No long intake form at the start.
1. Tell Your Story: User records a voice message or types. Voice is transcribed to editable text. The user reviews and explicitly sends the message.
1. Agent 1 — Understanding: Agent 1 analyses the submitted story and extracts candidate needs, relevant facts, and circumstances according to the approved contract.
1. User review of identified needs: Navigator presents the identified needs in plain language. The user can confirm, edit, add, or remove items. These are proposed interpretations until confirmed.
1. Agent 2 — Clarification: Agent 2 identifies missing information and proposes clarification requests. The Supervisor checks existing Case facts, merges duplicate/overlapping questions, and asks each necessary question once.
1. Conversational clarification: Questions appear as Navigator messages in the same thread. The user answers by voice or text. The user can review/edit voice transcription before sending.
1. Resource discovery and matching: The relevant agents retrieve, assess, match, and validate resources according to the approved architecture. The user sees clear progress messaging, not internal agent activity.
1. Crisis Action Plan: Navigator presents a structured plan grouped by needs, priorities, recommended actions, and relevant resource information, including limitations or missing facts where applicable.
1. After-plan choices: The user may optionally create an account for persistent access, request a one-time email copy without account creation, or finish without saving, consistent with the approved anonymous-user decision.

## 4. Voice and text interaction requirements


### 4.1 Voice message lifecycle

- User activates the microphone and records a message.
- When recording ends, show a completed recording state and duration (for example, “Recording completed · 00:42”).
- Speech is transcribed and the complete transcript is displayed in the conversation composer/message review area.
- The user can play back the recording, edit the transcript, record again, or discard it.
- The transcript is not submitted to the agents automatically. The user explicitly selects Send.
- After sending, the submitted message appears as a user message on the right. The transcript remains readable in the conversation history, subject to the project’s privacy and retention rules.

### 4.2 Text input

A text composer remains available at every conversational step. Voice must not be mandatory. The user may type a message, send a voice message, or alternate between the two.


### 4.3 Voice response from Navigator

Voice playback of Navigator responses is a desired capability to evaluate for the MVP. The interface should not assume that spoken responses are available until the selected speech/voice technology and implementation path are confirmed. Text responses must remain visible.


## 5. Agent communication model as presented to the user


| Component | User-visible behavior |
|---|---|
| Agent 1 — Understanding | Analyses the user’s story and returns structured candidate needs/facts. Navigator displays the proposed needs for user review and confirmation. |
| Agent 2 — Clarification | Identifies missing facts and produces clarification requests. Questions are rendered by Navigator only after Supervisor checks existing facts and deduplicates requests. |
| Supervisor / communication gateway | Checks Case facts, merges duplicate or overlapping questions, asks once, records answers centrally, and distributes updated facts to relevant agents. |
| Agents 3–5 and later planning/validation agents | Work behind the scenes. Their results contribute to resource matching and the final plan; they do not send messages directly to the user. |

The user sees one Navigator. Agents do not communicate directly with the user. User-facing questions and responses are routed through the Supervisor / approved single communication gateway.


## 6. Main conversation screen — wireframe sketch

### Main conversation screen — low-fidelity wireframe

```text
┌─────────────────────────────────────────────────────────────────────┐
│ AI COMMUNITY AID NAVIGATOR                              Navigator    │
│ You don't have to figure it out alone.                               │
│ Tell us what happened. You can speak or type.                        │
├─────────────────────────────────────────────────────────────────────┤
│ NAVIGATOR (left)                                                     │
│ Hello. I'm here to help you understand your situation and find      │
│ possible next steps.                                                 │
│                                                                     │
│                                      USER (right)                    │
│                                      I recently lost my job...       │
│                                      🎙 Voice message · 00:42         │
│                                                                     │
│                                      TRANSCRIPT — REVIEW BEFORE SEND │
│                                      I recently lost my job...       │
│                                      [Edit] [Record again] [Send]    │
│                                                                     │
│ NAVIGATOR (left)                                                     │
│ WHAT WE UNDERSTOOD — PLEASE REVIEW                                   │
│ • Recent job loss                                                    │
│ • Two children in the household                                     │
│ • Difficulty paying rent                                             │
│ • Difficulty affording groceries                                     │
│ [Confirm] [Edit] [Add a need]                                        │
├─────────────────────────────────────────────────────────────────────┤
│ Type a message…                       [+] [MICROPHONE] [SEND]        │
└─────────────────────────────────────────────────────────────────────┘
```



The sketch below is a layout concept, not a final visual design. It illustrates the chat pattern, a right-aligned user voice message, editable transcript, and an embedded “What we understood” card.


## 7. “What we understood” interaction

After Agent 1 analyses the submitted story, Navigator presents candidate needs in plain language within the conversation. The user can confirm the list, edit an item, add a missing need, or remove an incorrect item. The UI must clearly distinguish AI-inferred/candidate information from user-confirmed facts. Do not present an inference as a verified fact or confirmed eligibility.

- Use clear labels such as “What we understood” and “Please review”.
- Offer Confirm, Edit, Add a need, and Remove controls as appropriate.
- If the user corrects an item, the correction must be reflected in Case state through the Application Layer and passed to relevant agents according to the approved contracts.
- Do not silently discard a need. Multiple needs must be retained; do not impose an arbitrary top-three limit (consistent with T10).

## 8. Clarification interaction

Clarification is conversational and incremental. The Navigator should not dump a long questionnaire on the user. It should present the next necessary question or a small, understandable group of related questions, based on the approved clarification workflow.

- Before asking, check whether the required fact is already present in Case state.
- Merge duplicate or overlapping requests and ask each necessary question only once.
- Allow voice or text answers; voice answers follow the transcript-review-send lifecycle.
- Record answered or declined questions and preserve the already_asked state as required by the architecture.
- Do not let agents message the user directly.

## 9. Crisis Action Plan view — wireframe sketch

### Crisis Action Plan — separate structured view

```text
┌─────────────────────────────────────────────────────────────────────┐
│ YOUR CRISIS ACTION PLAN                                              │
│ Based on the information you confirmed.                              │
├─────────────────────────────────────────────────────────────────────┤
│ YOUR MAIN NEEDS                                                      │
│ Housing • Food • Income • Family support                             │
├─────────────────────────────────────────────────────────────────────┤
│ HOUSING ASSISTANCE                                                   │
│ Priority: Immediate / High                                           │
│ Next step: Review available rental assistance options...             │
│ [View details] [Update status]                                       │
├─────────────────────────────────────────────────────────────────────┤
│ FOOD ASSISTANCE                                                      │
│ Priority: High                                                       │
│ Next step: Review food assistance programs and access requirements. │
│ [View details] [Update status]                                       │
├─────────────────────────────────────────────────────────────────────┤
│ INCOME SUPPORT                                                       │
│ Priority: High                                                       │
│ Next step: Review unemployment and other income-support options.    │
│ [View details] [Update status]                                       │
└─────────────────────────────────────────────────────────────────────┘
```



The plan should be readable as a structured view, with the conversation still available. Organize by the user's needs and the approved priority logic. Show recommended next steps, relevant programs/resources, official links, missing information, and limitations where applicable. Do not invent eligibility, deadlines, or availability.


## 10. Post-plan choices

- Create an account: optional registration enables persistent access to the same Case/plan and progress tracking.
- Email me a copy: one-time email delivery without account creation or automatic subscription. Show the approved privacy notice before sending.
- Finish without saving: temporary session data is discarded; no persistent Case or recovery link is created for the anonymous user.
These options must remain separate. Email delivery must never silently create an account. This section follows the previously approved anonymous-user decision and acceptance scenario T03.


## 11. My Case and progress tracking

For a registered returning user, provide access to the same Case and current plan. The user can review recommendations, update user-controlled action statuses, and report changed circumstances. A status-only update must not automatically trigger a full program reassessment (T09). When the user reports material changes, the system follows the approved user-triggered reassessment behavior and preserves prior user-entered statuses where required (T08 and approved decisions).


## 12. Accessibility, safety, and trust

- Voice and text are both available; do not make speaking mandatory.
- Use plain, supportive language and short conversational turns.
- Make transcript editing and correction easy; do not treat unreviewed speech recognition as user-confirmed fact.
- Clearly distinguish user-stated facts, AI-inferred needs, missing information, and verified program information.
- Never imply that a user is eligible or that assistance is guaranteed unless supported by verified criteria.
- Do not expose sensitive details unnecessarily in notifications or email subject lines.
- Provide visible privacy information before one-time email delivery.
- Do not use color alone to communicate status; pair labels/icons with status text.

## 13. MVP scope and open implementation decisions

Product direction fixed in this UX specification:

- Chat-style, conversation-first primary interface.
- Right-aligned user messages and left-aligned Navigator messages.
- Voice and text input available throughout the conversation.
- Voice recording is transcribed and shown for user review/editing before sending.
- Agent 1 candidate needs are shown to the user for confirmation/correction.
- Agent 2 clarification questions are routed through the Supervisor and deduplicated.
- One visible Navigator identity; internal agents remain hidden.
To be confirmed with Slav/technical team before implementation:

- Which speech-to-text service is available and approved for the MVP, including language support and privacy/retention behavior.
- Whether text-to-speech / spoken Navigator responses fit the MVP or are deferred.
- Whether real-time streaming transcription is required or post-recording transcription is sufficient for the MVP.
- How audio is handled, retained, or discarded after transcription; do not assume persistent audio storage.
- How transcript edits and user confirmations are represented in Case state and Shared JSON Contracts.
- How the chat UI receives Supervisor clarification requests and submits user answers.
- Whether the initial wireframe is responsive across desktop and mobile for the MVP.
Important boundary: this UX document does not authorize unilateral changes to Shared JSON Contracts, agent responsibilities, Supervisor sequencing, or approved technical architecture. Any required contract or orchestration change must be reviewed and approved.


## 14. UX acceptance checklist

- [ ] User can start by speaking or typing without completing a long initial form.
- [ ] After recording, user sees recording duration and full transcript.
- [ ] User can play, edit, re-record, discard, and explicitly send a voice message.
- [ ] User messages appear on the right and Navigator messages on the left.
- [ ] Agent 1 results are presented as candidate needs for user review, not as unquestionable facts.
- [ ] User can confirm, edit, add, or remove identified needs.
- [ ] Clarification questions are delivered through Navigator/Supervisor, not directly by agents.
- [ ] Known facts are not unnecessarily requested again; duplicate questions are merged.
- [ ] User can answer every clarification by voice or text.
- [ ] Conversation progressively builds a coherent understanding without forcing a long questionnaire.
- [ ] Final plan is available in a structured view and retains all identified needs.
- [ ] Anonymous post-plan choices preserve the distinction between optional account creation, one-time email, and finish-without-saving.

## 15. Relationship to existing project documents

This UX specification should be read alongside the Solution Blueprint, Technical Design / Final Consolidation & Implementation Baseline, Shared JSON Contracts v1.1, approved product decisions, and Acceptance Test Protocol T01–T12. In particular:

- Technical Design §H and Acceptance Protocol T01–T12 define acceptance scenarios; this UX document does not replace them.
- Technical Design §30.8 and Shared JSON Contracts govern the single communication gateway, clarification deduplication, and ask-once behavior.
- T03 governs anonymous exit and one-time email without account creation.
- T08–T09 govern changed circumstances and status-only updates.
- T10 requires preservation of multiple needs without an arbitrary top-three cap.

---
