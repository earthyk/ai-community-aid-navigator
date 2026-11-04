"""
AI Community Aid Navigator — Agent 2: Case Analysis & Clarification Filter
Zero-Dependency Standard Library Implementation (Python 3.11+)
Contracts: docs/contracts/SHARED_CONTRACTS.md (v1.1)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

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
    case_facts: List[Dict[str, Any]] = payload.get("case_facts", [])
    needs: List[Dict[str, Any]] = payload.get("needs", [])
    already_asked: List[str] = payload.get("already_asked", [])
    candidate_requirements: List[Dict[str, Any]] = payload.get("candidate_requirements", [])

    existing_fact_keys = {f["field"] for f in case_facts if f.get("value") is not None}
    asked_set = set(already_asked)

    clarification_requests: List[Dict[str, Any]] = []
    need_updates: List[Dict[str, Any]] = []

    has_food_need = any(n.get("category") == "food_assistance" for n in needs)
    has_income_need = any(n.get("category") == "income_assistance" for n in needs)
    has_income_fact = any(
        f.get("field") in ["employment_status", "income_disruption_cause"]
        for f in case_facts
    )
    has_income_loss = bool(has_income_need or has_income_fact)
    optional_food_check = bool(has_income_loss and not has_food_need)

    has_income_stated = "household_gross_monthly_income" in existing_fact_keys
    has_income_asked = "household_gross_monthly_income" in asked_set

    if not has_income_stated and not has_income_asked:
        clarification_requests.append({
            "fact_key": "household_gross_monthly_income",
            "question_intent": "Determine current monthly household income",
            "user_facing_question": "What is your approximate current monthly household income before taxes?",
            "reason": "Required to determine eligibility thresholds across community assistance programs",
            "applicable_program_ids": ["prog_calfresh", "prog_shra"],
            "verified_rule_ref": "rule_income_threshold",
            "necessity_level": "required_for_decision",
            "can_skip": False,
        })

    if len(clarification_requests) < 1:
        for req_item in candidate_requirements:
            fact_key = req_item.get("fact_key")
            rule_ref = req_item.get("verified_rule_ref")

            if fact_key in existing_fact_keys:
                continue
            if fact_key in asked_set:
                continue
            if not rule_ref:
                continue

            if fact_key == "has_written_eviction_notice":
                clarification_requests.append({
                    "fact_key": "has_written_eviction_notice",
                    "question_intent": "Determine if landlord issued a written notice and when",
                    "user_facing_question": "Have you received a written eviction notice or 3-day notice to quit from your landlord, and if so, when?",
                    "reason": "Distinguishes emergency rental assistance from formal legal defense representation",
                    "applicable_program_ids": [req_item.get("program_id", "prog_shra_legal")],
                    "verified_rule_ref": rule_ref,
                    "necessity_level": "required_for_decision",
                    "can_skip": True,
                })
            elif fact_key in ["prior_year_gross_income", "household_income"]:
                clarification_requests.append({
                    "fact_key": fact_key,
                    "question_intent": "Determine household income eligibility threshold",
                    "user_facing_question": "What was your approximate household income before taxes last year?",
                    "reason": "Required to assess eligibility under published income limits",
                    "applicable_program_ids": [req_item.get("program_id", "prog_ui")],
                    "verified_rule_ref": rule_ref,
                    "necessity_level": "required_for_decision",
                    "can_skip": True,
                })
            else:
                clarification_requests.append({
                    "fact_key": fact_key,
                    "question_intent": f"Determine {fact_key.replace('_', ' ')}",
                    "user_facing_question": f"Could you please share your {fact_key.replace('_', ' ')}?",
                    "reason": "Required by program criteria",
                    "applicable_program_ids": [req_item.get("program_id", "prog_general")],
                    "verified_rule_ref": rule_ref,
                    "necessity_level": "required_for_decision",
                    "can_skip": True,
                })

            if len(clarification_requests) >= 1:
                break

    for n in needs:
        if n.get("category") == "food_assistance":
            need_updates.append({
                "need_id": n["need_id"],
                "urgency": "immediate",
                "urgency_reason": "Immediate nutritional support needed"
            })

    status = "needs_clarification" if clarification_requests else "completed"

    return {
        "request_id": request_dict.get("request_id"),
        "run_id": request_dict.get("run_id"),
        "case_id": request_dict.get("case_id"),
        "case_version": request_dict.get("case_version", 1),
        "correlation_id": request_dict.get("correlation_id"),
        "agent_id": "agent_2",
        "schema_version": schema_version_out,
        "status": status,
        "result": {"need_updates": need_updates, "optional_food_check": optional_food_check},
        "issues": [],
        "clarification_requests": clarification_requests,
        "evidence_refs": [],
        "generated_at": now_iso,
        "is_mock": True,
    }
