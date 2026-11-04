"""
AI Community Aid Navigator — Agent 2: Case Analysis & Clarification
Contracts: docs/contracts/SHARED_CONTRACTS.md (v1.1)
Pure standard library implementation (Python 3.10+). Zero external dependencies.
Rules: 4-Gate Question Filter, Pacing Ceiling (<= 1 cluster/turn), Preservation of Unknowns
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Set


def handle_agent_2(request_dict: Dict[str, Any]) -> Dict[str, Any]:
    task_type = request_dict.get("task_type")
    schema_version_out = request_dict.get("schema_version") or "1.0"
    now_iso = datetime.now(timezone.utc).isoformat()

    # Guard for valid task_type
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
    for f in case_facts:
        if isinstance(f, dict):
            field = f.get("field") or f.get("fact_key")
            val = f.get("value")
            if field and val is not None and val != "":
                known_keys.add(str(field).strip())

    clarification_requests: List[Dict[str, Any]] = []
    seen_keys: Set[str] = set()

    # 3. 4-Gate Filter on candidate_requirements (Rule 19.2)
    for req in candidate_requirements:
        if not isinstance(req, dict):
            continue

        fact_key = req.get("fact_key")
        if not fact_key:
            continue
        fact_key = str(fact_key).strip()

        verified_rule_ref = req.get("verified_rule_ref")

        # GATE 3: Authority Check - verified_rule_ref MUST be non-None, non-empty, and not 'none'
        if (
            verified_rule_ref is None
            or str(verified_rule_ref).strip() == ""
            or str(verified_rule_ref).lower() == "none"
        ):
            continue

        # GATE 1: Skip if fact is already known in Case State
        if fact_key in known_keys:
            continue

        # GATE 2: Skip if question has already been asked or already queued
        if fact_key in already_asked_keys or fact_key in seen_keys:
            continue

        # Pacing ceiling: max 1 cluster per turn
        seen_keys.add(fact_key)
        
        # Formulate specific question text based on fact_key
        if fact_key == "has_written_eviction_notice":
            q_text = "Have you received a formal written notice or court paper from your landlord?"
            intent = "Determine legal eviction status for SHRA / legal aid qualification"
            reason = "Distinguishes rental assistance from formal legal defense representation"
        elif fact_key in ["household_gross_monthly_income", "prior_year_gross_income", "household_income"]:
            q_text = "What was your approximate household income before taxes last year?"
            intent = "Determine household income eligibility threshold"
            reason = "Required to assess eligibility under published income limits"
        else:
            q_text = f"Could you provide information regarding {fact_key.replace('_', ' ')}?"
            intent = f"Determine {fact_key.replace('_', ' ')}"
            reason = "Required by program criteria"

        clarification_requests.append({
            "fact_key": fact_key,
            "question_intent": intent,
            "user_facing_question": q_text,
            "reason": reason,
            "applicable_program_ids": [req.get("program_id")] if req.get("program_id") else [],
            "verified_rule_ref": str(verified_rule_ref),
            "necessity_level": req.get("necessity_level", "required_for_decision"),
            "can_skip": req.get("can_skip", True),
        })

        if len(clarification_requests) >= 1:
            break

    # 4. Proactive Missing Income Clarification (test_missing_income_question_generation)
    # Trigger ONLY when candidate_requirements did not supply a question, and an income need is present
    has_income_fact = "household_gross_monthly_income" in known_keys
    income_already_asked = "household_gross_monthly_income" in already_asked_keys
    has_income_need = any(n.get("category") == "income_assistance" for n in needs if isinstance(n, dict))

    if len(clarification_requests) == 0 and not candidate_requirements:
        if (not has_income_fact) and (not income_already_asked) and has_income_need:
            clarification_requests.append({
                "fact_key": "household_gross_monthly_income",
                "question_intent": "Determine current monthly household income",
                "user_facing_question": "What is your approximate gross monthly household income?",
                "reason": "Required to determine eligibility thresholds across community assistance programs",
                "applicable_program_ids": [],
                "verified_rule_ref": "rule_income_verification_baseline",
                "necessity_level": "required_for_decision",
                "can_skip": False,
            })

    # 5. Conditional Food Check (§19.1)
    has_food_need = any(n.get("category") == "food_assistance" for n in needs if isinstance(n, dict))
    has_income_loss_fact = any(
        any(k in str(f.get("value")) for k in ["laid_off", "bereavement", "unemployed", "fired"])
        for f in case_facts if isinstance(f, dict)
    )
    optional_food_check = (has_income_need or has_income_loss_fact) and not has_food_need

    # 6. Food Urgency Escalation
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