"""
AI Community Aid Navigator — Agent 1: Crisis Understanding & Clarification Parser
Zero-Dependency Standard Library Implementation (Python 3.11+)
Contracts: docs/contracts/SHARED_CONTRACTS.md (v1.1)
"""
from __future__ import annotations

import calendar
from datetime import date, datetime, timezone
import re
from typing import Any, Dict, List, Optional

RE_ZIP = re.compile(r"\b(9\d{4})\b")
RE_RENT_EXPLICIT = re.compile(r"(?:rent\s+(?:is|of|was)?\s*\$?|rent\s*=\s*\$?)\s*([0-9,]+)", re.IGNORECASE)
RE_CASH_LIQUID = re.compile(
    r"(?:(?:have|left|cash|savings(?:\s+in\s+my\s+bank\s+account)?(?:\s+of)?)\s+(?:about\s+)?\$([0-9,]+))|"
    r"(?:(?:have|left)\s+(?:about\s+)?([0-9,]+)\s*(?:dollars|in\s+cash|in\s+savings|left))",
    re.IGNORECASE
)

RE_INCOME_ZERO = re.compile(r"\b(?:no\s+income|zero\s+income|0\s+income|without\s+any\s+income|no\s+money\s+coming\s+in)\b", re.IGNORECASE)
RE_INCOME_MONTHLY = re.compile(
    r"(?:(?:make|earn|income(?:\s+is)?|bring\s+in)\s+(?:about\s+)?\$?([0-9,]+)\s*(?:a|per|\/)\s*month)|"
    r"(?:monthly\s+(?:income|pay|earnings?)\s+(?:of\s+|is\s+)?(?:about\s+)?\$?([0-9,]+))",
    re.IGNORECASE
)

RE_KIDS_PROXIMITY = re.compile(
    r"\b(?:kids?|children|child)\b(?:[^\d\n;$]|,(?!\s*\$)){0,35}?(?:ages?\s*)?(\d{1,2}(?:(?:,\s*|\s+and\s+)\d{1,2})*)",
    re.IGNORECASE
)
RE_AGE_EXPLICIT = re.compile(r"\b(?:ages?)\s*(\d{1,2}(?:(?:,\s*|\s+and\s+)\d{1,2})*)", re.IGNORECASE)
RE_SINGLE_PARENT = re.compile(r"\b(single\s+(?:mom|dad|mother|father|parent)|myself\s+and|just\s+me\s+and)\b", re.IGNORECASE)

RE_SSN_STRICT = re.compile(r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b")
RE_SSN_9DIGIT = re.compile(r"\b\d{9}\b")
RE_SSN_LABELED = re.compile(r"\b(?:ssn|social\s*security(?:\s*number)?)\b[\s:=#-]*\d{3}[-\s]?\d{2}[-\s]?\d{4}\b|\b(?:ssn|social\s*security)\b[\s:=#-]*\d{9}\b", re.IGNORECASE)
RE_CARD_FULL = re.compile(r"\b(?:debit|credit)?\s*(?:card)?\s*(?:number)?\b[\s:=#-Pub]*(?:\d{4}[-\s]?){3}\d{4}\b|\b(?:\d{4}[-\s]?){3}\d{4}\b", re.IGNORECASE)
RE_BANK_FULL = re.compile(r"\b(?:routing|account)[\s#:]+\d{8,12}\b", re.IGNORECASE)
RE_FORBIDDEN_WORDS = re.compile(r"\b(ssn|social\s+security|credit\s+card|debit\s+card|bank\s+account|routing\s+number)\b", re.IGNORECASE)

RE_SAFETY_DISTRESS = re.compile(
    r"\b("
    r"kill\s+myself|"
    r"want\s+to\s+die|"
    r"don'?t\s+want\s+to\s+live|"
    r"end\s+my\s+life|"
    r"ending\s+it\s+all|"
    r"end\s+it\s+all|"
    r"can'?t\s+go\s+on\s+like\s+this|"
    r"can'?t\s+take\s+this\s+anymore|"
    r"suicide|"
    r"harm\s+myself|"
    r"hurt\s+myself|"
    r"abuse|"
    r"abusive|"
    r"hits\s+me|"
    r"hitting\s+me|"
    r"beats\s+me|"
    r"beating\s+me|"
    r"partner\s+hurts\s+me|"
    r"threatened\s+me|"
    r"violence|"
    r"scared\s+he\s+will\s+come\s+back|"
    r"scared\s+she\s+will\s+come\s+back|"
    r"he\s+will\s+hurt\s+us|"
    r"unsafe\s+at\s+home|"
    r"not\s+safe\s+at\s+home|"
    r"danger\s+at\s+home|"
    r"might\s+hurt\s+someone|"
    r"going\s+to\s+hurt\s+someone|"
    r"harm\s+others|"
    r"fleeing"
    r")\b",
    re.IGNORECASE
)

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}
MONTHS_PATTERN = "|".join(MONTH_MAP.keys())

RE_SUBCLAUSES = re.compile(r"[.\n;]|(?:\s+and\s+)|(?:\s+but\s+)", re.IGNORECASE)
RE_RENT_MONTH = re.compile(
    r"\brent\b[^0-9]*?(?:is\s+|was\s+)?(?:due\s+(?:on\s+)?|by\s+)(" + MONTHS_PATTERN + r")\s+(\d{1,2})\b|"
    r"\brent\s+(?:of\s+\$?[0-9,]+\s+)?(?:is\s+|was\s+)?(?:due\s+(?:on\s+)?|by\s+)(" + MONTHS_PATTERN + r")\s+(\d{1,2})\b",
    re.IGNORECASE
)
RE_RENT_DAY_ONLY = re.compile(
    r"\brent\b.*?[\b\s]due\s+(?:on\s+)?(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?\b",
    re.IGNORECASE
)
RE_RENT_WORD = re.compile(r"\brent\b", re.IGNORECASE)
RE_OTHER_BILL = re.compile(r"\b(?:bill|electric|gas|utility|smud|pge|water)\b.*?[\b\s]due\b", re.IGNORECASE)
RE_CLAUSE_SPLIT = re.compile(r"[\n.]")
RE_RENT_DOLLAR_SPLIT = re.compile(r"(?:\brent\b|\$)", re.IGNORECASE)
RE_DIGIT_EXTRACT = re.compile(r"(?<!\$)\b(\d{1,2})(?!(?:st|nd|rd|th))\b")

RE_ANY_PII_TRIGGER = re.compile(
    r"\d{3}[-\s]?\d{2}[-\s]?\d{4}|\d{9}|\b(?:\d{4}[-\s]?){3}\d{4}\b|\b(?:routing|account)[\s#:]+\d{8,12}\b|\b(ssn|social\s+security|credit\s+card|debit\s+card|bank\s+account|routing\s+number)\b",
    re.IGNORECASE
)

def redact_pii_text(text: str) -> str:
    if not RE_ANY_PII_TRIGGER.search(text):
        return text
    text = RE_SSN_LABELED.sub("[REDACTED_PII]", text)
    text = RE_SSN_STRICT.sub("[REDACTED_PII]", text)
    text = RE_SSN_9DIGIT.sub("[REDACTED_PII]", text)
    text = RE_CARD_FULL.sub("[REDACTED_PII]", text)
    text = RE_BANK_FULL.sub("[REDACTED_PII]", text)
    text = RE_FORBIDDEN_WORDS.sub("[REDACTED_PII]", text)
    return text

def parse_clarification_answer_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    answer_text = (payload.get("answer_text") or "").strip()
    pending_fact_keys = payload.get("pending_fact_keys") or []
    facts: List[Dict[str, Any]] = []

    text_lower = answer_text.lower()
    uncertainty_markers = (
        "not sure", "don't know", "dont know", "no idea", "unsure",
        "maybe", "haven't checked", "havent checked", "pending", "unknown", "still waiting"
    )
    if any(m in text_lower for m in uncertainty_markers):
        return []

    if re.search(r"\byes\s+(?:and|but)?\s*no\b|\bno\s+(?:and|but)?\s*yes\b", text_lower):
        return []

    explicit_notice_negatives = [
        "don't have one", "dont have one", "do not have one", "don't have a notice",
        "no notice", "haven't received", "havent received", "did not receive", "didn't receive",
        "never got", "no eviction notice", "none received"
    ]
    has_notice_neg_phrase = any(p in text_lower for p in explicit_notice_negatives)
    has_general_negative = bool(re.search(r"^(?:no|nope|none)\b|\b(?:no notice|nothing yet|nothing so far)\b", text_lower))
    has_notice_affirmative = bool(re.search(r"\b(?:yes|yeah|yep|i did|i received|received a|received the|got a|got the|served with|have one|have a notice)\b", text_lower))

    if has_notice_neg_phrase:
        is_affirmative = False
        is_negative = True
    elif has_notice_affirmative:
        is_affirmative = True
        is_negative = False
    elif has_general_negative:
        is_affirmative = False
        is_negative = True
    else:
        is_affirmative = False
        is_negative = False

    for fact_key in pending_fact_keys:
        if fact_key == "has_written_eviction_notice":
            if is_negative:
                facts.append({
                    "fact_id": "fact_clarified_eviction",
                    "field": "has_written_eviction_notice",
                    "value": False,
                    "confirmation_status": "proposed",
                    "source": "user_statement",
                    "time_context": "user_clarification"
                })
            elif is_affirmative:
                facts.append({
                    "fact_id": "fact_clarified_eviction",
                    "field": "has_written_eviction_notice",
                    "value": True,
                    "confirmation_status": "proposed",
                    "source": "user_statement",
                    "time_context": "user_clarification"
                })

    return facts

def extract_rent_due_date_fact(story_text: str, ref_date: date) -> Optional[Dict[str, Any]]:
    if "rent" not in story_text.lower():
        return None
    subclauses = RE_SUBCLAUSES.split(story_text)
    for sc in subclauses:
        if not RE_RENT_WORD.search(sc):
            continue
        if RE_OTHER_BILL.search(sc):
            continue

        m_month = RE_RENT_MONTH.search(sc)
        if m_month:
            m_str = (m_month.group(1) or m_month.group(3)).lower()
            d_val = int(m_month.group(2) or m_month.group(4))
            month_num = MONTH_MAP[m_str]
            year = ref_date.year
            max_d = calendar.monthrange(year, month_num)[1]
            if d_val < 1 or d_val > max_d:
                return None
            
            candidate = date(year, month_num, d_val)
            if candidate < ref_date:
                diff_days = (ref_date - candidate).days
                if diff_days <= 180:
                    return {
                        "fact_id": "fact_rent_due_date",
                        "field": "rent_due_date",
                        "value": candidate.isoformat(),
                        "confirmation_status": "proposed",
                        "source": "user_statement",
                        "time_context": "user-stated date, overdue",
                        "is_overdue": True,
                    }
                else:
                    year += 1
                    max_d_next = calendar.monthrange(year, month_num)[1]
                    if d_val > max_d_next:
                        return None
                    candidate = date(year, month_num, d_val)

            return {
                "fact_id": "fact_rent_due_date",
                "field": "rent_due_date",
                "value": candidate.isoformat(),
                "confirmation_status": "proposed",
                "source": "user_statement",
                "time_context": "user-stated date, not an official deadline",
                "is_overdue": False,
            }

        m_day = RE_RENT_DAY_ONLY.search(sc)
        if m_day:
            d_val = int(m_day.group(1))
            year = ref_date.year
            month = ref_date.month
            max_d = calendar.monthrange(year, month)[1]
            if d_val < 1 or d_val > 31:
                return None
            if d_val >= ref_date.day and d_val <= max_d:
                candidate = date(year, month, d_val)
            else:
                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1
                max_d_next = calendar.monthrange(year, month)[1]
                if d_val <= max_d_next:
                    candidate = date(year, month, d_val)
                else:
                    return None
            return {
                "fact_id": "fact_rent_due_date",
                "field": "rent_due_date",
                "value": candidate.isoformat(),
                "confirmation_status": "proposed",
                "source": "user_statement",
                "time_context": "user-stated date, not an official deadline",
                "is_overdue": False,
            }

    return None

def handle_agent_1(request_dict: Dict[str, Any], ref_date: Optional[date] = None) -> Dict[str, Any]:
    task_type = request_dict.get("task_type")
    schema_version_out = request_dict.get("schema_version") or "1.0"
    now_iso = datetime.now(timezone.utc).isoformat()

    if ref_date is None:
        custom_ref = request_dict.get("ref_date") or (request_dict.get("payload") or {}).get("ref_date")
        if custom_ref:
            if isinstance(custom_ref, str):
                try:
                    ref_date = date.fromisoformat(custom_ref)
                except ValueError:
                    return {
                        "request_id": request_dict.get("request_id", "req-unknown"),
                        "run_id": request_dict.get("run_id", "run-unknown"),
                        "case_id": request_dict.get("case_id", "case-unknown"),
                        "case_version": request_dict.get("case_version", 1),
                        "correlation_id": request_dict.get("correlation_id", "corr-unknown"),
                        "agent_id": "agent_1",
                        "schema_version": schema_version_out,
                        "status": "failed",
                        "result": {},
                        "issues": [{
                            "code": "INVALID_REF_DATE",
                            "severity": "critical",
                            "message": f"Malformed ref_date: '{custom_ref}'. Expected ISO date string YYYY-MM-DD.",
                            "related_ref": None,
                        }],
                        "clarification_requests": [],
                        "evidence_refs": [],
                        "generated_at": now_iso,
                        "is_mock": True,
                    }
            elif isinstance(custom_ref, date):
                ref_date = custom_ref
            else:
                return {
                    "request_id": request_dict.get("request_id", "req-unknown"),
                    "run_id": request_dict.get("run_id", "run-unknown"),
                    "case_id": request_dict.get("case_id", "case-unknown"),
                    "case_version": request_dict.get("case_version", 1),
                    "correlation_id": request_dict.get("correlation_id", "corr-unknown"),
                    "agent_id": "agent_1",
                    "schema_version": schema_version_out,
                    "status": "failed",
                    "result": {},
                    "issues": [{
                        "code": "INVALID_REF_DATE",
                        "severity": "critical",
                        "message": f"Invalid ref_date type: '{type(custom_ref)}'.",
                        "related_ref": None,
                    }],
                    "clarification_requests": [],
                    "evidence_refs": [],
                    "generated_at": now_iso,
                    "is_mock": True,
                }
        else:
            ref_date = date.today()

    if task_type not in ["understand_story", "parse_clarification_answer"]:
        return {
            "request_id": request_dict.get("request_id", "req-unknown"),
            "run_id": request_dict.get("run_id", "run-unknown"),
            "case_id": request_dict.get("case_id", "case-unknown"),
            "case_version": request_dict.get("case_version", 1),
            "correlation_id": request_dict.get("correlation_id", "corr-unknown"),
            "agent_id": "agent_1",
            "schema_version": schema_version_out,
            "status": "failed",
            "result": {},
            "issues": [{
                "code": "UNSUPPORTED_TASK",
                "severity": "critical",
                "message": f"Agent 1 does not support task_type: '{task_type}'.",
                "related_ref": None,
            }],
            "clarification_requests": [],
            "evidence_refs": [],
            "generated_at": now_iso,
            "is_mock": True,
        }

    if task_type == "parse_clarification_answer":
        factual_claims = parse_clarification_answer_payload(request_dict.get("payload") or {})
        return {
            "request_id": request_dict.get("request_id"),
            "run_id": request_dict.get("run_id"),
            "case_id": request_dict.get("case_id"),
            "case_version": request_dict.get("case_version", 1),
            "correlation_id": request_dict.get("correlation_id"),
            "agent_id": "agent_1",
            "schema_version": schema_version_out,
            "status": "completed",
            "result": {"factual_claims": factual_claims},
            "issues": [],
            "clarification_requests": [],
            "evidence_refs": [],
            "generated_at": now_iso,
            "is_mock": True,
        }

    payload = request_dict.get("payload")
    if payload is None or not isinstance(payload, dict):
        return {
            "request_id": request_dict.get("request_id", "req-unknown"),
            "run_id": request_dict.get("run_id", "run-unknown"),
            "case_id": request_dict.get("case_id", "case-unknown"),
            "case_version": request_dict.get("case_version", 1),
            "correlation_id": request_dict.get("correlation_id", "corr-unknown"),
            "agent_id": "agent_1",
            "schema_version": schema_version_out,
            "status": "failed",
            "result": {},
            "issues": [{
                "code": "MISSING_PAYLOAD",
                "severity": "critical",
                "message": "Missing required payload object in AgentRequest.",
                "related_ref": None,
            }],
            "clarification_requests": [],
            "evidence_refs": [],
            "generated_at": now_iso,
            "is_mock": True,
        }

    raw_story = payload.get("story_text")
    if raw_story is None or not isinstance(raw_story, str) or not raw_story.strip():
        return {
            "request_id": request_dict.get("request_id", "req-unknown"),
            "run_id": request_dict.get("run_id", "run-unknown"),
            "case_id": request_dict.get("case_id", "case-unknown"),
            "case_version": request_dict.get("case_version", 1),
            "correlation_id": request_dict.get("correlation_id", "corr-unknown"),
            "agent_id": "agent_1",
            "schema_version": schema_version_out,
            "status": "failed",
            "result": {},
            "issues": [{
                "code": "EMPTY_STORY",
                "severity": "critical",
                "message": "story_text must be a non-empty string.",
                "related_ref": "payload.story_text",
            }],
            "clarification_requests": [],
            "evidence_refs": [],
            "generated_at": now_iso,
            "is_mock": True,
        }

    story_text = redact_pii_text(raw_story)
    text_lower = story_text.lower()

    proposed_needs: List[Dict[str, Any]] = []
    facts: List[Dict[str, Any]] = []
    triggering_events: List[str] = []
    safety_flags: List[Dict[str, Any]] = []

    has_explicit_job_loss = any(k in text_lower for k in ("laid off", "lost my job", "hours cut", "lost job", "unemployed", "fired from", "was fired", "got fired"))
    has_bereavement = any(k in text_lower for k in ("passed away", "died", "bereavement", "funeral", "lost my husband", "lost my wife", "widow", "sole earner"))

    if has_explicit_job_loss or has_bereavement:
        event = "job_loss" if has_explicit_job_loss else "bereavement"
        triggering_events.append(event)
        desc = "Income support following job loss" if has_explicit_job_loss else "Survivor income and bereavement support"
        proposed_needs.append({
            "need_id": f"need_{len(proposed_needs)+1:03d}",
            "category": "income_assistance",
            "description": desc,
            "original_quote": story_text,
            "confirmation_status": "proposed",
            "user_reported": True,
            "urgency": "high",
            "urgency_reason": "Income loss reported"
        })
        facts.append({
            "fact_id": f"fact_{len(facts)+1:03d}",
            "field": "employment_status",
            "value": "laid_off" if has_explicit_job_loss else "bereavement",
            "confirmation_status": "proposed",
            "source": "user_statement",
            "time_context": "recent"
        })

    if RE_INCOME_ZERO.search(story_text):
        facts.append({
            "fact_id": f"fact_{len(facts)+1:03d}",
            "field": "household_gross_monthly_income",
            "value": 0,
            "confirmation_status": "proposed",
            "source": "user_statement",
            "is_approximate": False,
        })
    else:
        m_inc = RE_INCOME_MONTHLY.search(story_text)
        if m_inc:
            inc_val_str = m_inc.group(1) or m_inc.group(2)
            inc_val = int(inc_val_str.replace(",", ""))
            is_approx = bool(re.search(r"\b(about|around|approx|approximately)\b", m_inc.group(0), re.IGNORECASE))
            facts.append({
                "fact_id": f"fact_{len(facts)+1:03d}",
                "field": "household_gross_monthly_income",
                "value": inc_val,
                "confirmation_status": "proposed",
                "source": "user_statement",
                "is_approximate": is_approx,
            })

    rent_match = RE_RENT_EXPLICIT.search(story_text)
    is_fire_disaster = any(w in text_lower for w in ("house fire", "apartment fire", "fire destroyed", "lost in a fire"))
    has_housing_terms = any(k in text_lower for k in (
        "rent", "eviction", "evicted", "homeless", "motel", "shelter", "landlord", "deposit",
        "sleeping in our car", "sleeping in my car", "sleeping in car", "sleep in our car", "living in our car", "nowhere to stay", "on the street"
    ))

    has_eviction_notice = bool(re.search(r"\b(?:got|received|served|have)\b.*?\b(?:eviction\s+notice|3-day\s+notice|pay\s+or\s+quit)\b|\b(?:eviction\s+notice)\b", text_lower))
    if has_eviction_notice:
        facts.append({
            "fact_id": f"fact_{len(facts)+1:03d}",
            "field": "has_written_eviction_notice",
            "value": True,
            "confirmation_status": "proposed",
            "source": "user_statement",
            "time_context": "user-stated notice, not an official deadline"
        })

    rent_due_fact = extract_rent_due_date_fact(story_text, ref_date)
    is_rent_overdue = rent_due_fact.get("is_overdue", False) if rent_due_fact else False
    if rent_due_fact:
        rent_due_fact.pop("is_overdue", None)
        rent_due_fact["fact_id"] = f"fact_{len(facts)+1:03d}"
        facts.append(rent_due_fact)

    if rent_match or (has_housing_terms and not is_fire_disaster):
        is_car_shelter = any(k in text_lower for k in ("sleeping in our car", "sleeping in my car", "sleeping in car", "sleep in our car", "living in our car", "homeless", "nowhere to stay", "shelter"))
        
        if is_rent_overdue:
            h_urgency = "immediate"
            h_reason = "Rent is overdue"
        elif has_eviction_notice:
            h_urgency = "immediate"
            h_reason = "Eviction notice reported"
        elif is_car_shelter:
            h_urgency = "immediate"
            h_reason = "Acute homelessness or car sleeping"
        else:
            h_urgency = "high"
            h_reason = "Housing or rent distress reported"

        proposed_needs.append({
            "need_id": f"need_{len(proposed_needs)+1:03d}",
            "category": "housing_assistance",
            "subcategory": "emergency_shelter" if (is_car_shelter or not rent_match) else "rental_assistance",
            "description": "Housing and rental assistance support" if not is_car_shelter else "Emergency shelter and housing support",
            "original_quote": story_text,
            "confirmation_status": "proposed",
            "user_reported": True,
            "urgency": h_urgency,
            "urgency_reason": h_reason,
        })
        if rent_match:
            rent_val = int(rent_match.group(1).replace(",", ""))
            facts.append({
                "fact_id": f"fact_{len(facts)+1:03d}",
                "field": "rent_amount_monthly",
                "value": rent_val,
                "confirmation_status": "proposed",
                "source": "user_statement"
            })

    cash_match = RE_CASH_LIQUID.search(story_text)
    if cash_match:
        val_str = cash_match.group(1) or cash_match.group(2)
        if val_str:
            cash_val = int(val_str.replace(",", ""))
            facts.append({
                "fact_id": f"fact_{len(facts)+1:03d}",
                "field": "cash_on_hand_approx",
                "value": cash_val,
                "confirmation_status": "proposed",
                "source": "user_statement",
                "time_context": "current"
            })

    if any(w in text_lower for w in ("food", "groceries", "hungry", "pantry", "calfresh", "meals")):
        proposed_needs.append({
            "need_id": f"need_{len(proposed_needs)+1:03d}",
            "category": "food_assistance",
            "description": "Food assistance required",
            "original_quote": story_text,
            "confirmation_status": "proposed",
            "user_reported": True,
            "urgency": "immediate",
            "urgency_reason": "Food shortage reported"
        })

    if any(u in text_lower for u in ("utility", "utilities", "electric", "power", "smud", "pge", "water bill", "shutoff", "disconnection", "turn off my gas")):
        proposed_needs.append({
            "need_id": f"need_{len(proposed_needs)+1:03d}",
            "category": "utility_assistance",
            "description": "Utility bill or shutoff prevention assistance",
            "original_quote": story_text,
            "confirmation_status": "proposed",
            "user_reported": True,
            "urgency": "high" if ("shutoff" in text_lower or "turn off" in text_lower) else "normal",
            "urgency_reason": "Utility payment difficulty reported"
        })

    if any(m in text_lower for m in ("medical", "medication", "prescription", "insulin", "doctor", "health coverage", "hospital bill", "medi-cal")):
        proposed_needs.append({
            "need_id": f"need_{len(proposed_needs)+1:03d}",
            "category": "medical_health_coverage",
            "description": "Medical care and prescription assistance",
            "original_quote": story_text,
            "confirmation_status": "proposed",
            "user_reported": True,
            "urgency": "high",
            "urgency_reason": "Health expense hardship"
        })

    if any(d in text_lower for d in ("debt", "credit card", "collector", "collections", "overdue loan", "bankruptcy")):
        proposed_needs.append({
            "need_id": f"need_{len(proposed_needs)+1:03d}",
            "category": "debt_hardship",
            "description": "Debt relief and counselor negotiation support",
            "original_quote": story_text,
            "confirmation_status": "proposed",
            "user_reported": True,
            "urgency": "normal",
            "urgency_reason": "Unmanageable consumer debt"
        })

    has_explicit_material = any(mat in text_lower for mat in ("furniture", "clothing", "clothes", "beds", "household goods"))
    if has_explicit_material or is_fire_disaster:
        proposed_needs.append({
            "need_id": f"need_{len(proposed_needs)+1:03d}",
            "category": "material_in_kind",
            "description": "Material in-kind replacement goods",
            "original_quote": story_text,
            "confirmation_status": "proposed",
            "user_reported": True,
            "urgency": "high",
            "urgency_reason": "Loss of essential household goods"
        })

    safety_match = RE_SAFETY_DISTRESS.search(story_text)
    if safety_match:
        safety_flags.append({
            "type": "safety",
            "quote": safety_match.group(0),
            "note": "Immediate life-safety distress signal detected. Route directly to Verified Crisis Lines / 988 / 2-1-1 Emergency Support."
        })

    zip_match = RE_ZIP.search(story_text)
    if zip_match:
        facts.append({
            "fact_id": f"fact_{len(facts)+1:03d}",
            "field": "zip_code",
            "value": zip_match.group(1),
            "confirmation_status": "proposed",
            "source": "user_statement"
        })

    extracted_ages: List[int] = []
    has_childcare_only = bool("childcare" in text_lower and not any(k in text_lower for k in ("kid", "kids", "child", "children")))

    if not has_childcare_only:
        for clause in RE_CLAUSE_SPLIT.split(story_text):
            clean_subclause = RE_RENT_DOLLAR_SPLIT.split(clause)[0]
            m_kids = RE_KIDS_PROXIMITY.search(clean_subclause) or RE_AGE_EXPLICIT.search(clean_subclause)
            if m_kids:
                raw_match = m_kids.group(1)
                raw_nums = RE_DIGIT_EXTRACT.findall(raw_match)
                valid_ages = [int(d) for d in raw_nums if 0 < int(d) < 19]
                if valid_ages:
                    extracted_ages.extend(valid_ages)
                    break

    if extracted_ages:
        facts.append({
            "fact_id": f"fact_{len(facts)+1:03d}",
            "field": "children_ages",
            "value": extracted_ages,
            "confirmation_status": "proposed",
            "source": "user_statement"
        })

    is_explicit_single_adult = bool(RE_SINGLE_PARENT.search(story_text))
    if is_explicit_single_adult and extracted_ages:
        facts.append({
            "fact_id": f"fact_{len(facts)+1:03d}",
            "field": "household_size",
            "value": 1 + len(extracted_ages),
            "confirmation_status": "proposed",
            "source": "user_statement"
        })

    return {
        "request_id": request_dict.get("request_id"),
        "run_id": request_dict.get("run_id"),
        "case_id": request_dict.get("case_id"),
        "case_version": request_dict.get("case_version", 1),
        "correlation_id": request_dict.get("correlation_id"),
        "agent_id": "agent_1",
        "schema_version": schema_version_out,
        "status": "completed",
        "result": {
            "narrative_summary": story_text[:160],
            "triggering_events": triggering_events,
            "proposed_needs": proposed_needs,
            "factual_claims": facts,
            "ambiguity_flags": [],
            "safety_or_official_deadline_flags": safety_flags,
        },
        "issues": [],
        "clarification_requests": [],
        "evidence_refs": [],
        "generated_at": now_iso,
        "is_mock": True,
    }
