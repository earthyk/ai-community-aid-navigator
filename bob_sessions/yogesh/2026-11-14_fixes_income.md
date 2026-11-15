# Update `navigator/agents/agent_1_2/agent_1.py` and `tests/agent_1_2/test_agent_1_unittest.py`:

1. **Separate `reduced_pay` from `reduced_hours` in `navigator/agents/agent_1_2/agent_1.py`:**
   - Split `RE_REDUCED_HOURS_OR_PAY` into `RE_REDUCED_HOURS` (hours/shifts/schedule cut) and `RE_REDUCED_PAY` (pay/wage/wages/salary/paycheck cut/reduced/slashed/dropped), keeping `RE_REDUCED_HOURS_OR_PAY` as their union.
   - In `_understand_story` (Step 4b and Step 11): when `RE_REDUCED_PAY` matches (and not `RE_JOB_LOSS` or `RE_REDUCED_HOURS`), emit `triggering_events = ["reduced_pay"]`, `employment_status = "reduced_pay"`, and `income_assistance` with `description="Pay reduced"` and `urgency_reason="Pay reduced"`. Keep `"reduced_hours"` and `"Work hours reduced"` strictly for reduced work hours/shifts.
   - In `_parse_clarification` (Step 2 and Step 6b): mirror the same `reduced_pay` vs. `reduced_hours` distinction for `triggering_circumstances`, `employment_status`, and proposed `income_assistance` needs.

2. **Support `"800 a month"`, `"$800 a month"`, and `"800 dollars a month"` in `_parse_clarification`:**
   - In `_parse_clarification` (Step 3 Monthly Income Parsing), when `"household_gross_monthly_income"` is in `pending_fact_keys` and there are no rent/bill/balance keywords, extend `num_m` to also match `\$?([0-9,]+)\s*(?:dollars?\s*)?(?:a\s+month|per\s+month|monthly)\b` so `"800 a month"`, `"$800 a month"`, and `"800 dollars a month"` (standalone or inside sentences like `"800 a month for 3 people in our household."`) extract `household_gross_monthly_income = 800`.

3. **Add `safety_or_official_deadline_flags` detection to `_parse_clarification`:**
   - Extract a shared `_extract_safety_flags(text)` helper from `_understand_story` Step 1 (`RE_SAFETY_DISTRESS` guarded by `RE_BENIGN_SAFETY_CONTEXT`, keeping landlord lockout threats out of `safety` flags).
   - Call `_extract_safety_flags(ans)` in `_parse_clarification` and include `"safety_or_official_deadline_flags": safety_flags` in `env["result"]`.

4. **Add unit tests in `tests/agent_1_2/test_agent_1_unittest.py`:**
   - Test `"My pay was cut by half."` -> `employment_status="reduced_pay"`, `triggering_events=["reduced_pay"]`, `urgency_reason="Pay reduced"`, and confirm reduced hours still emits `reduced_hours` / `"Work hours reduced"`.
   - Add three separate tests for `parse_clarification_answer` with `pending_fact_keys=["household_gross_monthly_income"]` covering `"800 a month"`, `"$800 a month"`, and `"800 dollars a month"` (including `"800 a month for 3 people in our household."`), asserting `household_gross_monthly_income == 800`.
   - Test `parse_clarification_answer` safety flags: physical harm/self-harm text sets `safety_or_official_deadline_flags` (`type="safety"`), while a landlord lockout threat does not.
   - Run `python -m unittest discover tests` and confirm all tests pass.

---

**Status:** active  **Date:** 2026-11-14

---

### 👤 User

Update `navigator/agents/agent_1_2/agent_1.py` and `tests/agent_1_2/test_agent_1_unittest.py`:

1. **Separate `reduced_pay` from `reduced_hours` in `navigator/agents/agent_1_2/agent_1.py`:**
   - Split `RE_REDUCED_HOURS_OR_PAY` into `RE_REDUCED_HOURS` (hours/shifts/schedule cut) and `RE_REDUCED_PAY` (pay/wage/wages/salary/paycheck cut/reduced/slashed/dropped), keeping `RE_REDUCED_HOURS_OR_PAY` as their union.
   - In `_understand_story` (Step 4b and Step 11): when `RE_REDUCED_PAY` matches (and not `RE_JOB_LOSS` or `RE_REDUCED_HOURS`), emit `triggering_events = ["reduced_pay"]`, `employment_status = "reduced_pay"`, and `income_assistance` with `description="Pay reduced"` and `urgency_reason="Pay reduced"`. Keep `"reduced_hours"` and `"Work hours reduced"` strictly for reduced work hours/shifts.
   - In `_parse_clarification` (Step 2 and Step 6b): mirror the same `reduced_pay` vs. `reduced_hours` distinction for `triggering_circumstances`, `employment_status`, and proposed `income_assistance` needs.

2. **Support `"800 a month"`, `"$800 a month"`, and `"800 dollars a month"` in `_parse_clarification`:**
   - In `_parse_clarification` (Step 3 Monthly Income Parsing), when `"household_gross_monthly_income"` is in `pending_fact_keys` and there are no rent/bill/balance keywords, extend `num_m` to also match `\$?([0-9,]+)\s*(?:dollars?\s*)?(?:a\s+month|per\s+month|monthly)\b` so `"800 a month"`, `"$800 a month"`, and `"800 dollars a month"` (standalone or inside sentences like `"800 a month for 3 people in our household."`) extract `household_gross_monthly_income = 800`.

3. **Add `safety_or_official_deadline_flags` detection to `_parse_clarification`:**
   - Extract a shared `_extract_safety_flags(text)` helper from `_understand_story` Step 1 (`RE_SAFETY_DISTRESS` guarded by `RE_BENIGN_SAFETY_CONTEXT`, keeping landlord lockout threats out of `safety` flags).
   - Call `_extract_safety_flags(ans)` in `_parse_clarification` and include `"safety_or_official_deadline_flags": safety_flags` in `env["result"]`.

4. **Add unit tests in `tests/agent_1_2/test_agent_1_unittest.py`:**
   - Test `"My pay was cut by half."` -> `employment_status="reduced_pay"`, `triggering_events=["reduced_pay"]`, `urgency_reason="Pay reduced"`, and confirm reduced hours still emits `reduced_hours` / `"Work hours reduced"`.
   - Add three separate tests for `parse_clarification_answer` with `pending_fact_keys=["household_gross_monthly_income"]` covering `"800 a month"`, `"$800 a month"`, and `"800 dollars a month"` (including `"800 a month for 3 people in our household."`), asserting `household_gross_monthly_income == 800`.
   - Test `parse_clarification_answer` safety flags: physical harm/self-harm text sets `safety_or_official_deadline_flags` (`type="safety"`), while a landlord lockout threat does not.
   - Run `python -m unittest discover tests` and confirm all tests pass.

---

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Read agent_1.py to understand current structure
[ ] Read test_agent_1_unittest.py to understand current tests
[ ] Split RE_REDUCED_HOURS_OR_PAY into RE_REDUCED_HOURS and RE_REDUCED_PAY
[ ] Update _understand_story Step 4b and Step 11 for reduced_pay vs reduced_hours
[ ] Update _parse_clarification Step 2 and Step 6b for reduced_pay vs reduced_hours
[ ] Extend _parse_clarification Step 3 monthly income parsing for "800 a month" patterns
[ ] Extract _extract_safety_flags helper and call it in _parse_clarification
[ ] Add unit tests for reduced_pay scenario
[ ] Add unit tests for monthly income parsing ("800 a month", "$800 a month", "800 dollars a month")
[ ] Add unit tests for safety_or_official_deadline_flags in parse_clarification
[ ] Run tests and confirm all pass


### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — tests\agent_1_2\test_agent_1_unittest.py

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file

Now let me read the actual agent_1.py file in detail - especially the regex definitions and the relevant sections:

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — Step 11 reduced hours income assistance triggering events, employment_status reduced_hours work_hours_reduced, final result dict safety_or_official_deadline_flags

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — _parse_clarification Step 2 triggering_circumstances employment_status reduced_hours, Step 3 monthly income parsing num_m household_gross_monthly_income, Step 6b, food keywords, safety flags

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — Step 4 through 7 proposed needs income_assistance in _parse_clarification, 6b reduced_hours employment_status, food keywords, final env result

### 🤖 Assistant

> 🔧 called: read_file

Now I have a complete picture of the code. Let me also check the `RE_INCOME_STANDARD` regex:

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Read agent_1.py to understand current structure
[x] Read test_agent_1_unittest.py to understand current tests
[-] Split RE_REDUCED_HOURS_OR_PAY into RE_REDUCED_HOURS and RE_REDUCED_PAY
[ ] Update _understand_story Step 4b and Step 11 for reduced_pay vs reduced_hours
[ ] Update _parse_clarification Step 2 and Step 6b for reduced_pay vs reduced_hours
[ ] Extend _parse_clarification Step 3 monthly income parsing for "800 a month" patterns
[ ] Extract _extract_safety_flags helper and call it in _parse_clarification
[ ] Add unit tests for reduced_pay scenario
[ ] Add unit tests for monthly income parsing ("800 a month", "$800 a month", "800 dollars a month")
[ ] Add unit tests for safety_or_official_deadline_flags in parse_clarification
[ ] Run tests and confirm all pass


### 🤖 Assistant

> 🔧 called: apply_diff

Now I have everything I need. Let me implement all the changes to `agent_1.py`:

> 🔧 **apply_diff** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now let me update the `_understand_story` Step 1 to extract safety flags into a module-level helper, and update Step 4b and Step 11:

> 🔧 **apply_diff** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file

Now update `_understand_story` Step 1 to use the helper, and Step 4b and Step 11 to distinguish `reduced_pay` from `reduced_hours`. Let me find the current line numbers:

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now I'll apply all the remaining changes in one go:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:536
-------
    # 1. Life-Safety & Distress Detection (Neutral note; Supervisor selects directory contacts)
    safety_m = RE_SAFETY_DISTRESS.search(story)
    if safety_m and not RE_BENIGN_SAFETY_CONTEXT.search(story):
        quote_str = safety_m.group(0)
        is_harm_threat = bool(
            re.search(r"\b(?:threaten|threatened|threatening|hurt|harm|kill|beat|hit|attack|abuse)\b", quote_str, re.IGNORECASE)
        )
        flags.append({
            "type": "safety",
            "quote": quote_str,
            "note": "Threat of physical harm reported" if is_harm_threat else "Life-safety distress signal reported",
        })
=======
    # 1. Life-Safety & Distress Detection (Neutral note; Supervisor selects directory contacts)
    flags.extend(_extract_safety_flags(story))
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:610
-------
    # 4b. Triggering Events: Reduced Hours / Pay Cut
    reduced_hours_m = RE_REDUCED_HOURS_OR_PAY.search(story)
    if reduced_hours_m and not job_loss_m:
        triggering_events.append("reduced_hours")
        facts.append(_make_fact(
            "employment_status",
            "reduced_hours",
            fact_idx,
            time_context="current",
        ))
        fact_idx += 1
=======
    # 4b. Triggering Events: Reduced Hours / Pay Cut
    reduced_hours_m = RE_REDUCED_HOURS.search(story)
    reduced_pay_m = RE_REDUCED_PAY.search(story)
    if reduced_pay_m and not job_loss_m and not reduced_hours_m:
        triggering_events.append("reduced_pay")
        facts.append(_make_fact(
            "employment_status",
            "reduced_pay",
            fact_idx,
            time_context="current",
        ))
        fact_idx += 1
    elif reduced_hours_m and not job_loss_m:
        triggering_events.append("reduced_hours")
        facts.append(_make_fact(
            "employment_status",
            "reduced_hours",
            fact_idx,
            time_context="current",
        ))
        fact_idx += 1
    elif reduced_pay_m and not job_loss_m:
        # Both hours and pay signals present — keep reduced_hours as primary, add reduced_pay too
        triggering_events.append("reduced_pay")
        facts.append(_make_fact(
            "employment_status",
            "reduced_pay",
            fact_idx,
            time_context="current",
        ))
        fact_idx += 1
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:760
-------
    # 11. Proposed Needs — Multi-Domain Coverage
    # Item 10 & Follow-up Item 6: Propose income_assistance on income/job loss OR reduced work hours/pay cut
    if RE_INCOME_LOSS_SIGNAL.search(story) or RE_REDUCED_HOURS_OR_PAY.search(story):
        is_reduced_hours = bool(RE_REDUCED_HOURS_OR_PAY.search(story)) and not bool(RE_JOB_LOSS.search(story))
        income_quote = extract_full_sentence_quote(
            r"job|laid off|fired|unemployed|hours|paycheck|pay|wage|income",
            story,
        )
        proposed_needs.append(_make_need(
            "income_assistance",
            need_idx,
            description="Work hours or pay reduced" if is_reduced_hours else "Household income lost or severely reduced",
            original_quote=income_quote,
            urgency="high",
            urgency_reason="Work hours reduced" if is_reduced_hours else "Income loss or unemployment reported",
        ))
        need_idx += 1
=======
    # 11. Proposed Needs — Multi-Domain Coverage
    # Item 10 & Follow-up Item 6: Propose income_assistance on income/job loss OR reduced work hours/pay cut
    if RE_INCOME_LOSS_SIGNAL.search(story) or RE_REDUCED_HOURS_OR_PAY.search(story):
        _is_reduced_hours_only = bool(RE_REDUCED_HOURS.search(story)) and not bool(RE_JOB_LOSS.search(story)) and not bool(RE_REDUCED_PAY.search(story))
        _is_reduced_pay_only = bool(RE_REDUCED_PAY.search(story)) and not bool(RE_JOB_LOSS.search(story)) and not bool(RE_REDUCED_HOURS.search(story))
        income_quote = extract_full_sentence_quote(
            r"job|laid off|fired|unemployed|hours|paycheck|pay|wage|income",
            story,
        )
        if _is_reduced_pay_only:
            income_desc = "Pay reduced"
            income_reason = "Pay reduced"
        elif _is_reduced_hours_only:
            income_desc = "Work hours reduced"
            income_reason = "Work hours reduced"
        else:
            income_desc = "Household income lost or severely reduced"
            income_reason = "Income loss or unemployment reported"
        proposed_needs.append(_make_need(
            "income_assistance",
            need_idx,
            description=income_desc,
            original_quote=income_quote,
            urgency="high",
            urgency_reason=income_reason,
        ))
        need_idx += 1
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Read agent_1.py to understand current structure
[x] Read test_agent_1_unittest.py to understand current tests
[x] Split RE_REDUCED_HOURS_OR_PAY into RE_REDUCED_HOURS and RE_REDUCED_PAY
[x] Update _understand_story Step 4b and Step 11 for reduced_pay vs reduced_hours
[-] Update _parse_clarification Step 2 and Step 6b for reduced_pay vs reduced_hours
[ ] Extend _parse_clarification Step 3 monthly income parsing for "800 a month" patterns
[ ] Extract _extract_safety_flags helper and call it in _parse_clarification
[ ] Add unit tests for reduced_pay scenario
[ ] Add unit tests for monthly income parsing ("800 a month", "$800 a month", "800 dollars a month")
[ ] Add unit tests for safety_or_official_deadline_flags in parse_clarification
[ ] Run tests and confirm all pass


### 🤖 Assistant

> 🔧 called: read_file

Now let me update `_parse_clarification` — Step 2 (triggering circumstances), Step 3 (monthly income parsing), Step 6b (income_assistance need), and add safety flags. Let me get the current line numbers:

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now I can apply all the remaining `_parse_clarification` changes in one diff:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:1175
-------
    # 2. Triggering Circumstances
    circumstance_val = None
    if RE_REDUCED_HOURS_OR_PAY.search(ans):
        circumstance_val = "reduced_hours"
    elif re.search(r"\b(laid\s+off|lost\s+(?:my\s+)?job|fired|unemployed)\b", ans_lower):
        circumstance_val = "job_loss"
    elif re.search(r"\b(medical|hospital|hospitalization|sick|illness|injury|accident|asthma)\b", ans_lower):
        circumstance_val = "medical_emergency"
    elif re.search(r"\b(died|passed\s+away|bereavement|funeral)\b", ans_lower):
        circumstance_val = "bereavement"

    if circumstance_val:
        facts.append({
            "fact_id": _fact_id("triggering_circumstances", len(facts) + 1),
            "field": "triggering_circumstances",
            "value": circumstance_val,
            "confirmation_status": "proposed",
            "source": "user_statement",
            "time_context": "recent",
        })
        if circumstance_val == "reduced_hours":
            facts.append({
                "fact_id": _fact_id("employment_status", len(facts) + 1),
                "field": "employment_status",
                "value": "reduced_hours",
                "confirmation_status": "proposed",
                "source": "user_statement",
                "time_context": "current",
            })
=======
    # 2. Triggering Circumstances
    circumstance_val = None
    _ans_has_reduced_pay = bool(RE_REDUCED_PAY.search(ans))
    _ans_has_reduced_hours = bool(RE_REDUCED_HOURS.search(ans))
    if _ans_has_reduced_pay and not _ans_has_reduced_hours:
        circumstance_val = "reduced_pay"
    elif _ans_has_reduced_hours:
        circumstance_val = "reduced_hours"
    elif re.search(r"\b(laid\s+off|lost\s+(?:my\s+)?job|fired|unemployed)\b", ans_lower):
        circumstance_val = "job_loss"
    elif re.search(r"\b(medical|hospital|hospitalization|sick|illness|injury|accident|asthma)\b", ans_lower):
        circumstance_val = "medical_emergency"
    elif re.search(r"\b(died|passed\s+away|bereavement|funeral)\b", ans_lower):
        circumstance_val = "bereavement"

    if circumstance_val:
        facts.append({
            "fact_id": _fact_id("triggering_circumstances", len(facts) + 1),
            "field": "triggering_circumstances",
            "value": circumstance_val,
            "confirmation_status": "proposed",
            "source": "user_statement",
            "time_context": "recent",
        })
        if circumstance_val in ("reduced_hours", "reduced_pay"):
            emp_val = "reduced_hours" if circumstance_val == "reduced_hours" else "reduced_pay"
            facts.append({
                "fact_id": _fact_id("employment_status", len(facts) + 1),
                "field": "employment_status",
                "value": emp_val,
                "confirmation_status": "proposed",
                "source": "user_statement",
                "time_context": "current",
            })
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:1232
-------
        elif "household_gross_monthly_income" in keys:
            is_rent_or_due = bool(re.search(r"\b(rent|due|bill|owe|owing|left|account|balance)\b", ans_lower))
            if not is_rent_or_due:
                num_m = re.search(r"^\$?([0-9,]+)$|\b(?:about|around)\s+\$?([0-9,]+)\b", ans_lower)
                if num_m:
                    raw_num = num_m.group(1) or num_m.group(2)
                    try:
                        val = int(raw_num.replace(",", ""))
                        facts.append({
                            "fact_id": _fact_id("household_gross_monthly_income", len(facts) + 1),
                            "field": "household_gross_monthly_income",
                            "value": val,
                            "confirmation_status": "proposed",
                            "source": "user_statement",
                            "time_context": "current",
                        })
                    except ValueError:
                        pass
=======
        elif "household_gross_monthly_income" in keys:
            is_rent_or_due = bool(re.search(r"\b(rent|due|bill|owe|owing|left|account|balance)\b", ans_lower))
            if not is_rent_or_due:
                num_m = re.search(
                    r"^\$?([0-9,]+)$"
                    r"|\b(?:about|around)\s+\$?([0-9,]+)\b"
                    r"|\$?([0-9,]+)\s*(?:dollars?\s*)?(?:a\s+month|per\s+month|monthly)\b",
                    ans_lower,
                )
                if num_m:
                    raw_num = num_m.group(1) or num_m.group(2) or num_m.group(3)
                    try:
                        val = int(raw_num.replace(",", ""))
                        facts.append({
                            "fact_id": _fact_id("household_gross_monthly_income", len(facts) + 1),
                            "field": "household_gross_monthly_income",
                            "value": val,
                            "confirmation_status": "proposed",
                            "source": "user_statement",
                            "time_context": "current",
                        })
                    except ValueError:
                        pass
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:1379
-------
    # 6b. Follow-up Item 6: Reduced work hours / pay cut in clarification -> propose income_assistance
    if circumstance_val == "reduced_hours":
        existing_needs = payload.get("existing_needs") or []
        existing_need_cats = {n.get("category") for n in existing_needs if isinstance(n, dict)}
        if "income_assistance" not in existing_need_cats and not any(
            n.get("category") == "income_assistance" for n in proposed_needs
        ):
            max_idx = 0
            for n in existing_needs:
                if isinstance(n, dict):
                    m = re.match(r"^need_(\d+)$", str(n.get("need_id", "")))
                    if m:
                        max_idx = max(max_idx, int(m.group(1)))
            next_idx = max(max_idx, len(existing_needs) + len(proposed_needs)) + 1
            proposed_needs.append(_make_need(
                "income_assistance",
                next_idx,
                description="Work hours or pay reduced",
                original_quote=ans,
                urgency="high",
                urgency_reason="Work hours reduced",
            ))

    trig_events: List[str] = []
    for f in facts:
        if f.get("field") == "triggering_circumstances":
            trig_events.append(str(f.get("value")))

    env["result"] = {
        "factual_claims": facts,
        "proposed_needs": proposed_needs,
        "triggering_events": trig_events,
        "clarification_settled": len(facts) > 0,
        "ambiguity_flags": [],
    }
    return env
=======
    # 6b. Follow-up Item 6: Reduced work hours / pay cut in clarification -> propose income_assistance
    if circumstance_val in ("reduced_hours", "reduced_pay"):
        existing_needs = payload.get("existing_needs") or []
        existing_need_cats = {n.get("category") for n in existing_needs if isinstance(n, dict)}
        if "income_assistance" not in existing_need_cats and not any(
            n.get("category") == "income_assistance" for n in proposed_needs
        ):
            max_idx = 0
            for n in existing_needs:
                if isinstance(n, dict):
                    m = re.match(r"^need_(\d+)$", str(n.get("need_id", "")))
                    if m:
                        max_idx = max(max_idx, int(m.group(1)))
            next_idx = max(max_idx, len(existing_needs) + len(proposed_needs)) + 1
            if circumstance_val == "reduced_pay":
                need_desc = "Pay reduced"
                need_reason = "Pay reduced"
            else:
                need_desc = "Work hours reduced"
                need_reason = "Work hours reduced"
            proposed_needs.append(_make_need(
                "income_assistance",
                next_idx,
                description=need_desc,
                original_quote=ans,
                urgency="high",
                urgency_reason=need_reason,
            ))

    # 7. Safety flags detection in clarification answers
    safety_flags = _extract_safety_flags(ans)

    trig_events: List[str] = []
    for f in facts:
        if f.get("field") == "triggering_circumstances":
            trig_events.append(str(f.get("value")))

    env["result"] = {
        "factual_claims": facts,
        "proposed_needs": proposed_needs,
        "triggering_events": trig_events,
        "clarification_settled": len(facts) > 0,
        "ambiguity_flags": [],
        "safety_or_official_deadline_flags": safety_flags,
    }
    return env
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Read agent_1.py to understand current structure
[x] Read test_agent_1_unittest.py to understand current tests
[x] Split RE_REDUCED_HOURS_OR_PAY into RE_REDUCED_HOURS and RE_REDUCED_PAY
[x] Update _understand_story Step 4b and Step 11 for reduced_pay vs reduced_hours
[x] Update _parse_clarification Step 2 and Step 6b for reduced_pay vs reduced_hours
[x] Extend _parse_clarification Step 3 monthly income parsing for "800 a month" patterns
[x] Extract _extract_safety_flags helper and call it in _parse_clarification
[-] Add unit tests for reduced_pay scenario
[ ] Add unit tests for monthly income parsing ("800 a month", "$800 a month", "800 dollars a month")
[ ] Add unit tests for safety_or_official_deadline_flags in parse_clarification
[ ] Run tests and confirm all pass


### 🤖 Assistant

> 🔧 called: apply_diff

Now let me add all the new tests to `test_agent_1_unittest.py`:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:395
-------
if __name__ == "__main__":
    unittest.main()
=======
    def test_reduced_pay_story_emits_reduced_pay(self):
        """'My pay was cut by half.' must emit employment_status=reduced_pay,
        triggering_events=['reduced_pay'], and urgency_reason='Pay reduced'."""
        req = {
            "request_id": "req-pay-cut-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "My pay was cut by half."},
        }
        res = handle_agent_1(req)
        self.assertEqual(res["status"], "completed")
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("employment_status"), "reduced_pay")
        trig = res["result"]["triggering_events"]
        self.assertIn("reduced_pay", trig)
        self.assertNotIn("reduced_hours", trig)
        needs = res["result"]["proposed_needs"]
        income_needs = [n for n in needs if n["category"] == "income_assistance"]
        self.assertGreaterEqual(len(income_needs), 1)
        self.assertEqual(income_needs[0]["urgency_reason"], "Pay reduced")

    def test_reduced_hours_story_still_emits_reduced_hours(self):
        """'My hours were cut at work' must still emit employment_status=reduced_hours
        and urgency_reason='Work hours reduced' (not reduced_pay)."""
        req = {
            "request_id": "req-hours-cut-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "My hours were cut at work and I can't pay rent."},
        }
        res = handle_agent_1(req)
        self.assertEqual(res["status"], "completed")
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("employment_status"), "reduced_hours")
        trig = res["result"]["triggering_events"]
        self.assertIn("reduced_hours", trig)
        self.assertNotIn("reduced_pay", trig)
        needs = res["result"]["proposed_needs"]
        income_needs = [n for n in needs if n["category"] == "income_assistance"]
        self.assertGreaterEqual(len(income_needs), 1)
        self.assertEqual(income_needs[0]["urgency_reason"], "Work hours reduced")

    def test_parse_clarification_income_800_a_month_bare(self):
        """'800 a month' with pending household_gross_monthly_income extracts 800."""
        req = {
            "request_id": "req-inc-800-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "parse_clarification_answer",
            "payload": {
                "answer_text": "800 a month",
                "pending_fact_keys": ["household_gross_monthly_income"],
            },
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("household_gross_monthly_income"), 800)

    def test_parse_clarification_income_dollar_800_a_month(self):
        """'$800 a month' with pending household_gross_monthly_income extracts 800."""
        req = {
            "request_id": "req-inc-800-2",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "parse_clarification_answer",
            "payload": {
                "answer_text": "$800 a month",
                "pending_fact_keys": ["household_gross_monthly_income"],
            },
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("household_gross_monthly_income"), 800)

    def test_parse_clarification_income_800_dollars_a_month_in_sentence(self):
        """'800 a month for 3 people in our household.' and '800 dollars a month' extract 800."""
        for phrase in [
            "800 dollars a month",
            "800 a month for 3 people in our household.",
        ]:
            with self.subTest(phrase=phrase):
                req = {
                    "request_id": "req-inc-800-3",
                    "run_id": "run-001",
                    "case_id": "case-001",
                    "case_version": 1,
                    "role_id": "agent_1",
                    "task_type": "parse_clarification_answer",
                    "payload": {
                        "answer_text": phrase,
                        "pending_fact_keys": ["household_gross_monthly_income"],
                    },
                }
                res = handle_agent_1(req)
                facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
                self.assertEqual(
                    facts.get("household_gross_monthly_income"),
                    800,
                    f"Expected 800 for: {phrase}",
                )

    def test_parse_clarification_safety_flag_physical_harm(self):
        """Physical harm / self-harm text in clarification answer sets safety_or_official_deadline_flags
        with type='safety'."""
        for phrase in [
            "I want to kill myself",
            "He said he will hurt us if we don't leave.",
            "My partner hits me",
        ]:
            with self.subTest(phrase=phrase):
                req = {
                    "request_id": "req-clar-safe-1",
                    "run_id": "run-001",
                    "case_id": "case-001",
                    "case_version": 1,
                    "role_id": "agent_1",
                    "task_type": "parse_clarification_answer",
                    "payload": {
                        "answer_text": phrase,
                        "pending_fact_keys": ["triggering_circumstances"],
                    },
                }
                res = handle_agent_1(req)
                flags = res["result"].get("safety_or_official_deadline_flags", [])
                safety_flags = [f for f in flags if f.get("type") == "safety"]
                self.assertGreaterEqual(
                    len(safety_flags),
                    1,
                    f"Expected safety flag for: {phrase}",
                )

    def test_parse_clarification_landlord_lockout_no_safety_flag(self):
        """A landlord lockout threat in a clarification answer must NOT raise a safety flag."""
        req = {
            "request_id": "req-clar-lockout-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "parse_clarification_answer",
            "payload": {
                "answer_text": "My landlord threatened to lock us out if we don't pay by Friday.",
                "pending_fact_keys": ["has_written_eviction_notice"],
            },
        }
        res = handle_agent_1(req)
        flags = res["result"].get("safety_or_official_deadline_flags", [])
        safety_flags = [f for f in flags if f.get("type") == "safety"]
        self.assertEqual(
            len(safety_flags),
            0,
            "Landlord lockout threat must not set a safety flag",
        )


if __name__ == "__main__":
    unittest.main()
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Read agent_1.py to understand current structure
[x] Read test_agent_1_unittest.py to understand current tests
[x] Split RE_REDUCED_HOURS_OR_PAY into RE_REDUCED_HOURS and RE_REDUCED_PAY
[x] Update _understand_story Step 4b and Step 11 for reduced_pay vs reduced_hours
[x] Update _parse_clarification Step 2 and Step 6b for reduced_pay vs reduced_hours
[x] Extend _parse_clarification Step 3 monthly income parsing for "800 a month" patterns
[x] Extract _extract_safety_flags helper and call it in _parse_clarification
[x] Add unit tests for reduced_pay scenario
[x] Add unit tests for monthly income parsing ("800 a month", "$800 a month", "800 dollars a month")
[x] Add unit tests for safety_or_official_deadline_flags in parse_clarification
[-] Run tests and confirm all pass


### 🤖 Assistant

> 🔧 called: execute_command

Now let me check whether the landlord lockout test will actually pass. The test sends `"My landlord threatened to lock us out if we don't pay by Friday."` — `RE_SAFETY_DISTRESS` has `_HARM_SUBJECTS` which includes `landlord`, so I need to verify the regex won't fire on that phrase. Looking at the patterns, `RE_SAFETY_DISTRESS` matches things like `landlord threatened to attack/hurt/harm/kill/beat/abuse`. The phrase "lock us out" doesn't match any of those verbs, so it should be fine. Let me run the tests:

> 🔧 **execute_command** — python -m unittest discover tests 2>&1

### 🤖 Assistant

> 🔧 called: read_file

There's an existing test in another file that expects `"My pay was cut by half."` to yield `employment_status="reduced_hours"`. That test was written before this PR's new requirement. I need to check that test and update it since the new requirement explicitly changes this behavior:

> 🔧 **read_file** — test_20_pay_cut_by_half_emits_reduced_hours_and_income_assistance

### 🤖 Assistant

> 🔧 called: apply_diff

This existing test at line 353-362 expected the old behavior (pay cut = `reduced_hours`). The task explicitly says this old behavior should change — pay cut should now emit `reduced_pay`. I need to update this test to match the new expected behavior:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:353
-------
    def test_20_pay_cut_by_half_emits_reduced_hours_and_income_assistance(self):
        """Commit 2 Item 4: 'My pay was cut by half.' emits reduced_hours fact/triggering_event and income_assistance need."""
        res = handle_agent_1(_req_a1("My pay was cut by half."))
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        needs = res["result"]["proposed_needs"]
        self.assertEqual(facts.get("employment_status"), "reduced_hours")
        self.assertIn("reduced_hours", res["result"]["triggering_events"])
        self.assertTrue(
            any(n["category"] == "income_assistance" and n["urgency"] == "high" for n in needs)
        )
=======
    def test_20_pay_cut_by_half_emits_reduced_pay_and_income_assistance(self):
        """'My pay was cut by half.' emits reduced_pay fact/triggering_event and income_assistance need."""
        res = handle_agent_1(_req_a1("My pay was cut by half."))
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        needs = res["result"]["proposed_needs"]
        self.assertEqual(facts.get("employment_status"), "reduced_pay")
        self.assertIn("reduced_pay", res["result"]["triggering_events"])
        self.assertTrue(
            any(n["category"] == "income_assistance" and n["urgency"] == "high" for n in needs)
        )
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: read_file

Also check if the existing test around line 342 for `urgency_reason="Work hours reduced"` in test_slav_12_items is testing a different scenario (hours cut vs pay cut):

> 🔧 **read_file** — tests\agent_1_2\test_slav_12_items.py

### 🤖 Assistant

> 🔧 called: execute_command

Good — test_18 is for `"My hours were cut at work"` which still correctly yields `"Work hours reduced"`. Now run the full test suite again:

> 🔧 **execute_command** — python -m unittest discover tests 2>&1

### 🤖 Assistant

> 🔧 called: execute_command

Wait, it says "FAILED" in the tool output but the bottom shows "OK". Let me re-read the output — actually there seems to be a PowerShell display issue. The exit code was 1 but the actual output says "OK". Let me check more carefully:

> 🔧 **execute_command** — python -m unittest discover tests; Write-Host "Exit: $LASTEXITCODE"

### 🤖 Assistant

> 🔧 called: update_todo_list

All 334 tests pass. The exit code is 0 and all tests are OK.

> 🔧 **update_todo_list** — 
[x] Read agent_1.py to understand current structure
[x] Read test_agent_1_unittest.py to understand current tests
[x] Split RE_REDUCED_HOURS_OR_PAY into RE_REDUCED_HOURS and RE_REDUCED_PAY
[x] Update _understand_story Step 4b and Step 11 for reduced_pay vs reduced_hours
[x] Update _parse_clarification Step 2 and Step 6b for reduced_pay vs reduced_hours
[x] Extend _parse_clarification Step 3 monthly income parsing for "800 a month" patterns
[x] Extract _extract_safety_flags helper and call it in _parse_clarification
[x] Add unit tests for reduced_pay scenario
[x] Add unit tests for monthly income parsing ("800 a month", "$800 a month", "800 dollars a month")
[x] Add unit tests for safety_or_official_deadline_flags in parse_clarification
[x] Run tests and confirm all pass


### 🤖 Assistant

All 334 tests pass. Here's a summary of every change made:

---

### [`navigator/agents/agent_1_2/agent_1.py`](navigator/agents/agent_1_2/agent_1.py)

**1. New regex constants (`RE_REDUCED_HOURS`, `RE_REDUCED_PAY`)**  
Added [`RE_REDUCED_HOURS`](navigator/agents/agent_1_2/agent_1.py:197) (hours/shifts/schedule patterns only) and [`RE_REDUCED_PAY`](navigator/agents/agent_1_2/agent_1.py:204) (pay/wage/wages/salary/paycheck patterns only) alongside the existing union [`RE_REDUCED_HOURS_OR_PAY`](navigator/agents/agent_1_2/agent_1.py:211).

**2. `_extract_safety_flags()` module-level helper** ([line ~417](navigator/agents/agent_1_2/agent_1.py:417))  
Extracted the Step 1 safety detection logic from `_understand_story` into a reusable `_extract_safety_flags(text)` function.

**3. `_understand_story` Step 1** — now calls `flags.extend(_extract_safety_flags(story))` instead of inline code.

**4. `_understand_story` Step 4b** — now separately checks `RE_REDUCED_PAY` and `RE_REDUCED_HOURS`: pure pay-cut-only → `triggering_events=["reduced_pay"]`, `employment_status="reduced_pay"`; hours-cut → still `"reduced_hours"`.

**5. `_understand_story` Step 11** — `income_assistance` need now emits `description/urgency_reason="Pay reduced"` for pay-only, `"Work hours reduced"` for hours-only, and the original fallback for mixed/job-loss cases.

**6. `_parse_clarification` Step 2** — `circumstance_val` now detects `"reduced_pay"` vs `"reduced_hours"` using the split regexes, and sets `employment_status` accordingly.

**7. `_parse_clarification` Step 3** — extended `num_m` regex with `\$?([0-9,]+)\s*(?:dollars?\s*)?(?:a\s+month|per\s+month|monthly)\b` to capture `"800 a month"`, `"$800 a month"`, `"800 dollars a month"` and embedded forms like `"800 a month for 3 people"`.

**8. `_parse_clarification` Step 6b** — income need emits `"Pay reduced"` / `"Work hours reduced"` based on `circumstance_val`.

**9. `_parse_clarification` Step 7 + result** — calls `_extract_safety_flags(ans)` and includes `"safety_or_official_deadline_flags"` in the result dict.

---

### [`tests/agent_1_2/test_agent_1_unittest.py`](tests/agent_1_2/test_agent_1_unittest.py) — 6 new test methods

| Test | Covers |
|------|--------|
| `test_reduced_pay_story_emits_reduced_pay` | `"My pay was cut by half."` → `employment_status=reduced_pay`, `triggering_events=["reduced_pay"]`, `urgency_reason="Pay reduced"` |
| `test_reduced_hours_story_still_emits_reduced_hours` | `"My hours were cut at work"` → still `reduced_hours` / `"Work hours reduced"` |
| `test_parse_clarification_income_800_a_month_bare` | `"800 a month"` → `household_gross_monthly_income=800` |
| `test_parse_clarification_income_dollar_800_a_month` | `"$800 a month"` → `800` |
| `test_parse_clarification_income_800_dollars_a_month_in_sentence` | `"800 dollars a month"` and `"800 a month for 3 people in our household."` → `800` |
| `test_parse_clarification_safety_flag_physical_harm` | harm/self-harm phrases → `safety` flag set |
| `test_parse_clarification_landlord_lockout_no_safety_flag` | landlord lockout threat → no `safety` flag |

### [`tests/agent_1_2/test_slav_12_items.py`](tests/agent_1_2/test_slav_12_items.py)

Updated `test_20_pay_cut_by_half_emits_reduced_hours_and_income_assistance` to reflect the new expected behavior (`reduced_pay` instead of `reduced_hours`).


### Run
```text
@'
import json
from navigator.agents.agent_1_2.agent_1 import handle_agent_1

print("=== 1. reduced_pay (understand_story) ===")
r1 = handle_agent_1({
    "task_type": "understand_story",
    "payload": {
        "story_text": "My pay was cut by half and rent of $1400 is due next week in 95823.",
        "ref_date": "2026-11-15"
    }
})
print(json.dumps({
    "triggering_events": r1["result"]["triggering_events"],
    "factual_claims": r1["result"]["factual_claims"],
    "proposed_needs": r1["result"]["proposed_needs"]
}, indent=2))

print("\n=== 2. Monthly income phrasings (parse_clarification_answer) ===")
for ans in ["800 a month", "$800 a month", "800 dollars a month"]:
    r2 = handle_agent_1({
        "task_type": "parse_clarification_answer",
        "payload": {
            "answer_text": ans,
            "pending_fact_keys": ["household_gross_monthly_income"],
            "ref_date": "2026-11-15"
        }
    })
    print(ans, "->", json.dumps(r2["result"]["factual_claims"]))

print("\n=== 3. Safety flag in answer vs. landlord lockout threat ===")
for ans in ["My ex threatened to hurt me if I stay.", "My landlord threatened to change the locks."]:
    r3 = handle_agent_1({
        "task_type": "parse_clarification_answer",
        "payload": {
            "answer_text": ans,
            "pending_fact_keys": ["triggering_circumstances"],
            "ref_date": "2026-11-15"
        }
    })
    print(ans, "->", json.dumps(r3["result"]["safety_or_official_deadline_flags"]))
'@ | python -
```
### Actual outout
```text
=== 1. reduced_pay (understand_story) ===
{
  "triggering_events": [
    "reduced_pay"
  ],
  "factual_claims": [
    {
      "fact_id": "fact_zip_code_001",
      "field": "zip_code",
      "value": "95823",
      "confirmation_status": "proposed",
      "source": "user_statement",
      "time_context": null
    },
    {
      "fact_id": "fact_employment_status_002",
      "field": "employment_status",
      "value": "reduced_pay",
      "confirmation_status": "proposed",
      "source": "user_statement",
      "time_context": "current"
    },
    {
      "fact_id": "fact_rent_amount_monthly_003",
      "field": "rent_amount_monthly",
      "value": 1400,
      "confirmation_status": "proposed",
      "source": "user_statement",
      "time_context": null
    }
  ],
  "proposed_needs": [
    {
      "need_id": "need_001",
      "category": "income_assistance",
      "description": "Pay reduced",
      "original_quote": "My pay was cut by half and rent of $1400 is due next week in 95823.",
      "user_reported": true,
      "confirmation_status": "proposed",
      "urgency": "high",
      "urgency_reason": "Pay reduced",
      "user_priority": null
    },
    {
      "need_id": "need_002",
      "category": "housing_assistance",
      "description": "Rent assistance needed",
      "original_quote": "My pay was cut by half and rent of $1400 is due next week in 95823.",
      "user_reported": true,
      "confirmation_status": "proposed",
      "urgency": "high",
      "urgency_reason": "Rent assistance needed",
      "user_priority": null
    }
  ]
}

=== 2. Monthly income phrasings (parse_clarification_answer) ===
800 a month -> [{"fact_id": "fact_household_gross_monthly_income_001", "field": "household_gross_monthly_income", "value": 800, "confirmation_status": "proposed", "source": "user_statement", "time_context": "current"}]
$800 a month -> [{"fact_id": "fact_household_gross_monthly_income_001", "field": "household_gross_monthly_income", "value": 800, "confirmation_status": "proposed", "source": "user_statement", "time_context": "current"}]
800 dollars a month -> [{"fact_id": "fact_household_gross_monthly_income_001", "field": "household_gross_monthly_income", "value": 800, "confirmation_status": "proposed", "source": "user_statement", "time_context": "current"}]

=== 3. Safety flag in answer vs. landlord lockout threat ===
My ex threatened to hurt me if I stay. -> [{"type": "safety", "quote": "My ex threatened to hurt me", "note": "Threat of physical harm reported"}]
My landlord threatened to change the locks. -> []
```