"""
AI Community Aid Navigator — Agent 2: Case Analysis & Clarification
Contracts: docs/contracts/SHARED_CONTRACTS.md (v1.1)
Pure standard library implementation (Python 3.11+). Zero external dependencies.
Rules: 4-Gate Question Filter, Pacing Ceiling (<= 2/turn §30.8), Preservation of Unknowns

Contract invariants enforced:
- ZIP Code Question (Item 2): if zip_code is not known and not asked, Agent 2 asks for the
  resident's Sacramento ZIP code with can_skip=False on Turn 1.
- Household Size Question (Item 3): if household_size is not known and not asked, and either
  candidate_requirements ask for it or food_assistance is in needs, ask with can_skip=True.
- Income Question: if household_gross_monthly_income is not known, not asked, AND no
  candidate_requirements are provided, Agent 2 MUST generate a question for it with can_skip=False.
- Eviction Notice Details: When has_written_eviction_notice is True in case_facts, Agent 2 asks
  document type and date with can_skip=False (fact_key: eviction_notice_type).
- Gate 3 (verified_rule_ref): questions without a valid rule ref are suppressed.
- Gate 2: already-asked facts are never re-asked.
- Gate 1: known facts are never asked (except eviction follow-up).
- Pacing ceiling: max 2 clarification requests per turn (§30.8).
- Backward Compatibility (Item 4): triggering_circumstances already_asked key covers
  triggering_events / employment_status root-cause tokens from previous turns.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Set


def handle_agent_2(request_dict: Dict[str, Any]) -> Dict[str, Any]:
    task_type = request_dict.get("task_type")
    schema_version_out = request_dict.get("schema_version") or "1.0"
    now_iso = datetime.now(timezone.utc).isoformat()

    if task_type not in ["clarify_case"]:
        return {
            "request_id": request_dict.get("request_id", "req-unknown"),
            "run_id": request_dict.get("run_id", "run-unknown"),
            "case_id": request_dict.get("case_id", "case-unknown"),
            "case_version": request_dict.get("case_version", 1),
            "correlation_id": request_dict.get("correlation_id", "corr-unknown"),
            "agent_id": "agent_2",
            "schema_version": schema_version_out,
            "status": "failed",
            "result": {},
            "issues": [
                {
                    "code": "UNSUPPORTED_TASK",
                    "severity": "critical",
                    "message": f"Agent 2 does not support task_type: '{task_type}'.",
                    "related_ref": None,
                }
            ],
            "clarification_requests": [],
            "evidence_refs": [],
            "generated_at": now_iso,
            "is_mock": True,
        }

    payload = request_dict.get("payload") or {}
    needs: List[Dict[str, Any]] = payload.get("needs") or []
    case_facts: List[Dict[str, Any]] = payload.get("case_facts") or []
    raw_already_asked = payload.get("already_asked") or []
    candidate_requirements: List[Dict[str, Any]] = payload.get("candidate_requirements") or []
    raw_ambiguity_flags: List[Any] = payload.get("ambiguity_flags") or []

    # Normalize ambiguity_flags: support both Contract 4.1 objects and legacy strings
    ambiguity_flag_notes: Set[str] = set()
    for af in raw_ambiguity_flags:
        if isinstance(af, str):
            ambiguity_flag_notes.add(af.strip())
        elif isinstance(af, dict):
            note = af.get("note")
            if note:
                ambiguity_flag_notes.add(str(note).strip())

    # 1. Normalize already_asked (Gate 2)
    already_asked_keys: Set[str] = set()
    for item in raw_already_asked:
        if isinstance(item, str):
            already_asked_keys.add(item.strip())
        elif isinstance(item, dict):
            k = item.get("fact_key") or item.get("field")
            if k:
                already_asked_keys.add(str(k).strip())

    # 2. Gate 1: Known facts with actual values
    known_keys: Set[str] = set()
    known_facts: Dict[str, Any] = {}
    for f in case_facts:
        if isinstance(f, dict):
            field = f.get("field") or f.get("fact_key")
            val = f.get("value")
            if field and val is not None and val != "":
                k_str = str(field).strip()
                known_keys.add(k_str)
                known_facts[k_str] = val

    clarification_requests: List[Dict[str, Any]] = []
    seen_keys: Set[str] = set()

    # Backward Compatibility (Item 4): if triggering_circumstances was previously asked,
    # treat it as covering triggering_events and employment_status root-cause tokens.
    if "triggering_circumstances" in already_asked_keys:
        already_asked_keys.add("triggering_events")
        already_asked_keys.add("employment_status")

    # Step 1 — Circumstance-First Gate: ask about root cause before anything else
    unspecified_hardship = "unspecified_hardship_cause" in ambiguity_flag_notes
    circumstances_already_asked = "triggering_circumstances" in already_asked_keys
    circumstances_in_facts = "triggering_circumstances" in known_keys

    if unspecified_hardship and not circumstances_already_asked and not circumstances_in_facts:
        clarification_requests.append({
            "fact_key": "triggering_circumstances",
            "question_intent": "Identify root cause and circumstances of hardship",
            "user_facing_question": (
                "I'm sorry your family is going through a difficult time. "
                "Could you tell me a little more about what happened that led to these financial difficulties?"
            ),
            "reason": "Understanding what caused the hardship determines applicable crisis and emergency programs",
            "applicable_program_ids": [],
            "verified_rule_ref": None,
            "necessity_level": "helpful_for_discovery",
            "can_skip": True,
        })
        seen_keys.add("triggering_circumstances")

        return {
            "request_id": request_dict.get("request_id", "req-unknown"),
            "run_id": request_dict.get("run_id", "run-unknown"),
            "case_id": request_dict.get("case_id", "case-unknown"),
            "case_version": request_dict.get("case_version", 1),
            "correlation_id": request_dict.get("correlation_id", "corr-unknown"),
            "agent_id": "agent_2",
            "schema_version": schema_version_out,
            "status": "needs_clarification",
            "result": {
                "need_updates": [],
                "optional_food_check": False,
            },
            "issues": [],
            "clarification_requests": clarification_requests,
            "evidence_refs": [],
            "generated_at": now_iso,
            "is_mock": True,
        }

    # 2. ZIP Code Question — ask when zip_code is not known, not already asked,
    #    there is at least one service need, no unspecified_hardship gate is active,
    #    and no urgent eviction follow-up is displacing the turn.
    #    On Turn 1 (empty already_asked): ask unconditionally.
    #    After Turn 1: ask when circumstances were already asked (ZIP fallthrough).
    has_zip_fact = "zip_code" in known_keys
    zip_already_asked = "zip_code" in already_asked_keys
    notice_is_reported_early = known_facts.get("has_written_eviction_notice") is True
    eviction_followup_pending = (
        notice_is_reported_early
        and ("eviction_notice_type" not in already_asked_keys)
        and ("eviction_notice_type" not in known_keys)
    )
    is_turn_1 = len(raw_already_asked) == 0
    # ZIP fallthrough: after Turn 1 only when unspecified_hardship_cause is still active
    # (caller passes the original flags) AND circumstances have been asked/resolved.
    circumstances_resolved = circumstances_already_asked or circumstances_in_facts
    zip_fallthrough = unspecified_hardship and circumstances_resolved

    if (
        not has_zip_fact
        and not zip_already_asked
        and needs  # only when there is an actual service need
        and not eviction_followup_pending
        and (is_turn_1 or zip_fallthrough)  # Turn 1 or post-circumstances fallthrough
        and not (unspecified_hardship and not circumstances_resolved)  # never when hardship gate is active
    ):
        if len(clarification_requests) < 2:
            clarification_requests.append({
                "fact_key": "zip_code",
                "question_intent": "Determine resident's Sacramento service area ZIP code",
                "user_facing_question": (
                    "What is your Sacramento ZIP code? "
                    "This helps us find the right local programs in your area."
                ),
                "reason": "ZIP code is required to match geographic eligibility for local programs",
                "applicable_program_ids": [],
                "verified_rule_ref": None,
                "necessity_level": "required_for_decision",
                "can_skip": False,
            })
            seen_keys.add("zip_code")

    # 3. Income Question — ask only when:
    #    - income is not already known
    #    - income has not been asked
    #    - no candidate_requirements are pending
    #    - circumstances are not flagged as unspecified
    #    - no active eviction notice follow-up is being asked on this turn
    has_income_fact = "household_gross_monthly_income" in known_keys
    income_already_asked = "household_gross_monthly_income" in already_asked_keys
    notice_is_reported = known_facts.get("has_written_eviction_notice") is True
    eviction_followup_pending = (
        notice_is_reported
        and ("eviction_notice_type" not in already_asked_keys)
        and ("eviction_notice_type" not in known_keys)
    )

    if (
        not has_income_fact
        and not income_already_asked
        and not candidate_requirements
        and not unspecified_hardship
        and not eviction_followup_pending
    ):
        clarification_requests.append({
            "fact_key": "household_gross_monthly_income",
            "question_intent": "Determine current monthly household income",
            "user_facing_question": "What is your approximate gross monthly household income?",
            "reason": "Required to determine eligibility thresholds across community assistance programs",
            "applicable_program_ids": [],
            "verified_rule_ref": None,
            "necessity_level": "required_for_decision",
            "can_skip": False,
        })
        seen_keys.add("household_gross_monthly_income")

    # 4. Eviction Notice Follow-up: Document Type & Date
    #    Only when has_written_eviction_notice is True in case_facts (Gate 1 pass),
    #    and the follow-up has not already been asked.
    notice_is_reported = known_facts.get("has_written_eviction_notice") is True
    eviction_type_already_asked = (
        "eviction_notice_type" in already_asked_keys
        or "eviction_notice_details" in already_asked_keys
    )
    has_eviction_type_fact = "eviction_notice_type" in known_keys

    if notice_is_reported and not has_eviction_type_fact and not eviction_type_already_asked:
        if len(clarification_requests) < 2:
            clarification_requests.append({
                "fact_key": "eviction_notice_type",
                "question_intent": "Determine legal eviction notice type and receipt date for emergency rental defense",
                "user_facing_question": (
                    "What type of eviction notice did you receive (such as a 3-day notice), "
                    "and what date is listed on it?"
                ),
                "reason": "Notice type and receipt date determine legal response timelines and court defense eligibility",
                "applicable_program_ids": [],
                "verified_rule_ref": None,
                "necessity_level": "required_for_decision",
                "can_skip": False,
            })
            seen_keys.add("eviction_notice_type")

    # 5. 4-Gate Filter on candidate_requirements (Rule 19.2)
    for req in candidate_requirements:
        if not isinstance(req, dict):
            continue

        fact_key = req.get("fact_key")
        if not fact_key:
            continue
        fact_key = str(fact_key).strip()

        # Gate 2: skip already-asked keys immediately
        if fact_key in already_asked_keys:
            continue

        # Gate 3: suppress questions without a verified rule ref
        verified_rule_ref = req.get("verified_rule_ref")
        if (
            verified_rule_ref is None
            or str(verified_rule_ref).strip() == ""
            or str(verified_rule_ref).lower() == "none"
        ):
            continue

        # Gate 1: skip known facts (except eviction notice — handled separately above)
        if fact_key in known_keys and fact_key != "has_written_eviction_notice":
            continue

        # Gate 4: deduplication within this turn
        if fact_key in seen_keys:
            continue

        # Special case: if has_written_eviction_notice is True (already known), don't re-ask the boolean
        if fact_key == "has_written_eviction_notice" and known_facts.get("has_written_eviction_notice") is True:
            continue

        # Special case: if has_written_eviction_notice is False, skip all eviction questions
        if fact_key == "has_written_eviction_notice" and known_facts.get("has_written_eviction_notice") is False:
            continue

        if len(clarification_requests) >= 2:
            break

        seen_keys.add(fact_key)

        q_text, intent, reason, can_skip = _build_question(fact_key, req)

        clarification_requests.append({
            "fact_key": fact_key,
            "question_intent": intent,
            "user_facing_question": q_text,
            "reason": reason,
            "applicable_program_ids": [req.get("program_id")] if req.get("program_id") else [],
            "verified_rule_ref": str(verified_rule_ref),
            "necessity_level": req.get("necessity_level", "required_for_decision"),
            "can_skip": can_skip,
        })

    # 5b. Household Size Question (Item 3) — asked after all higher-priority questions are settled:
    #    - household_size is not known and not already asked
    #    - AND (candidate_requirements referenced it OR food_assistance is a need)
    #    - AND income is already known (not pending this turn)
    #    - AND no other question was generated this turn (pacing: fill only when the turn is otherwise empty)
    has_hh_size_fact = "household_size" in known_keys
    hh_size_already_asked = "household_size" in already_asked_keys
    cand_needs_hh_size = any(
        isinstance(r, dict) and str(r.get("fact_key", "")).strip() == "household_size"
        for r in candidate_requirements
    )
    has_food_need_for_hh = any(
        isinstance(n, dict) and n.get("category") == "food_assistance" for n in needs
    )

    if (
        not has_hh_size_fact
        and not hh_size_already_asked
        and "household_size" not in seen_keys
        and (cand_needs_hh_size or has_food_need_for_hh)
        and has_income_fact  # income must already be known, not being asked this turn
        and len(clarification_requests) == 0  # only when no other question was generated this turn
    ):
        clarification_requests.append({
            "fact_key": "household_size",
            "question_intent": "Determine total number of people in the household",
            "user_facing_question": (
                "How many people are currently living in your household, including yourself?"
            ),
            "reason": "Household size affects eligibility thresholds for food and assistance programs",
            "applicable_program_ids": [],
            "verified_rule_ref": None,
            "necessity_level": "required_for_decision",
            "can_skip": True,
        })
        seen_keys.add("household_size")

    # 6. Conditional Food Check (§19.1)
    has_food_need = any(isinstance(n, dict) and n.get("category") == "food_assistance" for n in needs)
    has_income_need_flag = any(n.get("category") == "income_assistance" for n in needs if isinstance(n, dict))
    has_income_loss_fact = any(
        any(k in str(f.get("value", "")) for k in ["laid_off", "bereavement", "unemployed", "fired"])
        for f in case_facts if isinstance(f, dict)
    )
    optional_food_check = (has_income_need_flag or has_income_loss_fact) and not has_food_need

    # 7. Food Urgency Escalation
    need_updates: List[Dict[str, Any]] = []
    for n in needs:
        if isinstance(n, dict) and n.get("category") == "food_assistance":
            need_updates.append({
                "need_id": n.get("need_id"),
                "urgency": "immediate",
                "urgency_reason": "Immediate nutritional support needed for dependents within current week",
            })

    status = "needs_clarification" if len(clarification_requests) > 0 else "completed"

    return {
        "request_id": request_dict.get("request_id", "req-unknown"),
        "run_id": request_dict.get("run_id", "run-unknown"),
        "case_id": request_dict.get("case_id", "case-unknown"),
        "case_version": request_dict.get("case_version", 1),
        "correlation_id": request_dict.get("correlation_id", "corr-unknown"),
        "agent_id": "agent_2",
        "schema_version": schema_version_out,
        "status": status,
        "result": {
            "need_updates": need_updates,
            "optional_food_check": optional_food_check,
        },
        "issues": [],
        "clarification_requests": clarification_requests,
        "evidence_refs": [],
        "generated_at": now_iso,
        "is_mock": True,
    }


def _build_question(
    fact_key: str, req: Dict[str, Any]
) -> tuple:
    if fact_key == "has_written_eviction_notice":
        return (
            "Have you received a formal written notice from your landlord? "
            "If so, what type of document is it (such as a 3-day notice) and what date is listed on it?",
            "Determine legal eviction status and document type/date for SHRA / legal aid qualification",
            "Distinguishes rental assistance from formal legal defense representation",
            False,
        )
    elif fact_key in ["household_gross_monthly_income", "prior_year_gross_income", "household_income"]:
        return (
            "What was your approximate household income before taxes last year?",
            "Determine household income eligibility threshold",
            "Required to assess eligibility under published income limits",
            False,
        )
    else:
        return (
            f"Could you provide information regarding {fact_key.replace('_', ' ')}?",
            f"Determine {fact_key.replace('_', ' ')}",
            "Required by program criteria",
            req.get("can_skip", True),
        )
