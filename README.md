
---


# AI Community Aid Navigator
> *Helping families navigate financial crisis, one step at a time.*
### *Intelligent, Multi-Agent Crisis Intake, Verification & Actionable Relief Planning*

A team project developed through the **IBM SkillsBuild AI Experiential Learning Lab — Fall 2026**.

**Domain:** Government, Social Services & Community Welfare  
**Technology Stack:** Python 3.11+ (Pure Standard Library Runtime), IBM Granite, IBM watsonx (Orchestrate / Discovery), IBM Bob, Open-Source RAG Frameworks  
**Pilot Target:** Sacramento County, California (Emergency Housing, Utilities & Food Relief)  
**Contract Baseline:** Shared JSON Contracts v1.1 (FROZEN)

---

## Project Overview

Families facing an unexpected financial crisis often need to navigate multiple assistance programs with conflicting eligibility requirements, rigid deadlines, complex application processes, and verification barriers.

AI Community Aid Navigator is being developed to help users describe their circumstances, identify potentially relevant community resources, and build a personalized action plan.

## Pilot scope

The initial pilot focuses on **Sacramento, California**, with priority given to housing/rent assistance and food support.

* Planned user experience

* Describe your situation in your own words.

* Answer clarifying questions and confirm the summary.

* Review relevant assistance programs, supporting sources, and eligibility uncertainties.

* Receive a prioritized action plan.

* Track progress and update the plan as circumstances change.


> **Operational Boundary:** Users apply to assistance programs independently. The navigator does **not** directly submit applications or guarantee eligibility, placement, or financial disbursement.

---

## 10-Agent Collaborative Architecture

The system operates under a hub-and-spoke pipeline governed by the **Supervisor Orchestrator**:

```text
 Resident Narrative
         │
         ▼
 ┌───────────────┐
 │    Agent 1    │  Crisis Understanding & Slot Filling (Rule 19.1 Strict Non-Inference)
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │    Agent 2    │  Case Analysis & 4-Gate Clarification Filter (Pacing Ceiling <= 1 cluster/turn)
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │ Supervisor/KB │  Case State Checkpointing & Sacramento Verified Knowledge Base
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │  Agents 3,4,5 │  Resource Retrieval, Eligibility Matching & Field-Level Claim Verification
 └───────┬───────┘
         ▼
 ┌───────────────┐
 │ Agents 6,8,10 │  Plan Generation, Action Card Assembly & Release Validation Gate
 └───────┬───────┘
         ▼
 Actionable Relief Plan

```

---

## Development & Integration Status

Detailed real vs. mock vs. pending components are tracked in **[`STATUS.md`](STATUS.md)**.

* **Architecture Baseline:** Complete 10-agent multi-agent pipeline verified against Contracts v1.1.
* **Orchestration Checks:** Full lifecycle runner passes Supervisor boundary checks S0–S9 (PII redaction, identity matching, status enforcement, and bounded retries).
* **Zero Runtime Dependencies:** Pure Python 3.11+ standard library implementation (`re`, `calendar`, `datetime`, `json`, `unittest`).
* **Test Suite:** 100% green across all unit and integration benchmarks (`Ran 136 tests ... OK`).

---

## Repository Structure

For branch workflows, commit conventions, and file organization rules, see **[`CONTRIBUTING.md`](CONTRIBUTING.md)**.

```text
ai-community-aid-navigator/
├── README.md                    project overview (Julia)
├── CONTRIBUTING.md              this file
├── STATUS.md                    what is real, what is mock, what is not built yet
├── agents.json                  wiring: which module handles which agent role
├── docs/
│   ├── architecture/            Solution Blueprint, RAG Technical Architecture, Technical Design, Decision Register
│   ├── contracts/               SHARED_CONTRACTS.md (v1.1; v1.0 frozen Oct 23)
│   └── SUBMISSION_PLAN.md       weeks 7–10 plan and final submission checklist
├── navigator/                   the Python package
│   ├── supervisor/              Slav: orchestration, checks S0–S9, run.py
│   ├── agents/
│   │   ├── agent_1_2/           Yogesh: Agents 1, 2
│   │   ├── agent_3_4_5/         Silver: Agents 3, 4, 5
│   │   └── agent_6_7_8_10/      Hisham: Agents 6, 7, 8, 10
│   ├── kb/                      Silver: the single Knowledge Base file and its tools
│   └── samples/                 shared test case JSON (contracts section 6)
├── tests/                       integration and Supervisor tests
│   ├── agent_1_2/               Yogesh's tests
│   ├── agent_3_4_5/             Silver's tests
│   └── agent_6_7_8_10/          Hisham's tests
└── bob_sessions/                exported IBM Bob task sessions (required for judging)
    ├── hisham/
    ├── silver/
    ├── yogesh/
    ├── slav/
    └── ...

```

---

## Quick Start & Verification

### 1. Clone the Repository

```bash
git clone [https://github.com/polyulia85/ai-community-aid-navigator.git](https://github.com/polyulia85/ai-community-aid-navigator.git)
cd ai-community-aid-navigator

```

### 2.  Run the Test Suite

Execute the master test suite using Python's standard `unittest` framework:

```bash
python -m unittest discover -s tests -t .

```

---

## Pre-Submission Guidelines

1. **Development Environment:** All tasks must be developed and logged using the **IBM Bob IDE** under team `ELL US 2026H2`.
2. **Session Exports:** Every PR must include an exported session markdown file (`bob_sessions/<member>/YYYY-MM-DD_<topic>.md`) and usage screenshot (`_usage.png`).
3. **Privacy & Data Security:** No real-world PII, client records, API credentials, or local filesystem paths (`C:\...`) may be committed. All evaluations use verified synthetic fixtures.
4. **Git Protocol:** Feature branches must use the `<member>/<topic>` convention, commits must use authorized GitHub noreply emails, and all PRs must merge cleanly into `main`.

---

## Team

For component ownership areas and session export rules for each member, refer to **[`CONTRIBUTING.md`](CONTRIBUTING.md)**.

* **Iuliia Poliakova** — Project Lead 
* **Sviatoslav Pechenevskyi** — System Architecture & Integration
* **Yogesh Kushwaha** — Crisis Understanding & User Navigation 
* **Silver Sanchez Cardenas** — Resource Retrieval, Matching & Verification
* **M. Hisham Abbasi** — Prioritization, Action Planning & Quality Validation 
---


## Demo and documentation

Demo, documentation, and setup links will be added after the corresponding materials are uploaded and verified.

---

## Privacy

Do not upload credentials, API keys, or real user case data. Examples and demonstration cases must use synthetic data.

---
