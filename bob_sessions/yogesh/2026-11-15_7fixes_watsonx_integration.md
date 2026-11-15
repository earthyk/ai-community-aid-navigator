# Update `navigator/agents/agent_1_2/agent_1.py` and `tests/agent_1_2/` to fix these 7 items in the watsonx integration:

1. Empty env vars: Treat empty or whitespace-only values (`""`, `"   "`) for `WATSONX_MAX_CALLS`, `WATSONX_TIMEOUT`, `WATSONX_PROJECT_ID`, `WATSONX_URL`, and `WATSONX_MODEL_ID` as unset so defaults are used without raising `ValueError` on `int("")` or overriding defaults with `""`.

2. Strict grounding & rule-only facts: Keep `factual_claims` 100% rule-based—ignore any `factual_claims` returned by the model. Only allow the model to add `proposed_needs` for allowed non-duplicate categories where `original_quote` is a substantive verbatim substring of the normalized story (at least 8 characters and >= 2 words; reject trivial quotes like `"I"`).

3. Accurate urgency & reason on model-added needs: Stop hardcoding `urgency="high"` with `"urgency from rules"`. Compute urgency via a shared rule helper from the story/quote signals (defaulting to `"medium"` unless urgent signals apply) and set `urgency_reason` to accurately match how that urgency was derived.

4. Cross-process IAM token cache & call counter: Because Supervisor runs each agent call in its own subprocess (`isolate=True`), persist the IAM token cache (token + expiry) and call counter (counting all attempted calls, including failed/timed-out calls) in an atomic JSON state file in `tempfile.gettempdir()` (overridable in tests) so caching and `WATSONX_MAX_CALLS` work across processes.

5. Single overall timeout budget: Replace separate 15 s IAM + 15 s chat timeouts with one shared deadline/budget of ~18 s total (configurable via `WATSONX_TIMEOUT`, capped under 20 s) so IAM + chat together complete or fall back (`is_mock=True`) before the Supervisor's 30 s timeout.

6. Isolate `WATSONX_*` in tests: Clear all `WATSONX_*` environment variables across the test suite by default so running `python -I -m unittest discover -s tests -t .` with `.env` loaded never hits the network unless a test explicitly patches `os.environ`.

7. Unit tests: Add tests covering empty-string env vars, rejection of model-injected facts and 1-word quotes (`"I"`), model-added need urgency/reason consistency, cross-process persisted call count (including failed calls) and IAM token cache across separate Python subprocesses, and the shared timeout budget. Run `python -I -m unittest discover -s tests -t .` and verify 0 failures.

---

**Status:** active  **Date:** 2026-11-15

---

### 👤 User

Update `navigator/agents/agent_1_2/agent_1.py` and `tests/agent_1_2/` to fix these 7 items in the watsonx integration:

1. Empty env vars: Treat empty or whitespace-only values (`""`, `"   "`) for `WATSONX_MAX_CALLS`, `WATSONX_TIMEOUT`, `WATSONX_PROJECT_ID`, `WATSONX_URL`, and `WATSONX_MODEL_ID` as unset so defaults are used without raising `ValueError` on `int("")` or overriding defaults with `""`.

2. Strict grounding & rule-only facts: Keep `factual_claims` 100% rule-based—ignore any `factual_claims` returned by the model. Only allow the model to add `proposed_needs` for allowed non-duplicate categories where `original_quote` is a substantive verbatim substring of the normalized story (at least 8 characters and >= 2 words; reject trivial quotes like `"I"`).

3. Accurate urgency & reason on model-added needs: Stop hardcoding `urgency="high"` with `"urgency from rules"`. Compute urgency via a shared rule helper from the story/quote signals (defaulting to `"medium"` unless urgent signals apply) and set `urgency_reason` to accurately match how that urgency was derived.

4. Cross-process IAM token cache & call counter: Because Supervisor runs each agent call in its own subprocess (`isolate=True`), persist the IAM token cache (token + expiry) and call counter (counting all attempted calls, including failed/timed-out calls) in an atomic JSON state file in `tempfile.gettempdir()` (overridable in tests) so caching and `WATSONX_MAX_CALLS` work across processes.

5. Single overall timeout budget: Replace separate 15 s IAM + 15 s chat timeouts with one shared deadline/budget of ~18 s total (configurable via `WATSONX_TIMEOUT`, capped under 20 s) so IAM + chat together complete or fall back (`is_mock=True`) before the Supervisor's 30 s timeout.

6. Isolate `WATSONX_*` in tests: Clear all `WATSONX_*` environment variables across the test suite by default so running `python -I -m unittest discover -s tests -t .` with `.env` loaded never hits the network unless a test explicitly patches `os.environ`.

7. Unit tests: Add tests covering empty-string env vars, rejection of model-injected facts and 1-word quotes (`"I"`), model-added need urgency/reason consistency, cross-process persisted call count (including failed calls) and IAM token cache across separate Python subprocesses, and the shared timeout budget. Run `python -I -m unittest discover -s tests -t .` and verify 0 failures.

---

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Investigate current codebase structure and existing files
[ ] Fix item 1: Empty env vars treated as unset
[ ] Fix item 2: Strict grounding - rule-only facts, substantive quote validation
[ ] Fix item 3: Accurate urgency & reason on model-added needs
[ ] Fix item 4: Cross-process IAM token cache & call counter
[ ] Fix item 5: Single overall timeout budget (~18s)
[ ] Fix item 6: Isolate WATSONX_* in tests
[ ] Fix item 7: Add unit tests for all items
[ ] Run tests and verify 0 failures


### 🤖 Assistant

> 🔧 called: list_files



> 🔧 **list_files** — 

### 🤖 Assistant

> 🔧 called: list_files, list_files



> 🔧 **list_files** — navigator\agents\agent_1_2

> 🔧 **list_files** — tests\agent_1_2

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

> 🔧 called: read_file



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

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file

Now let me look at the existing tests to understand the test structure:

> 🔧 **read_file** — tests\agent_1_2\test_agent_1_unittest.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — tests\agent_1_2\test_agent_1_unittest.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — tests\agent_1_2\test_agent_1_unittest.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — tests\agent_1_2\test_agent_1_unittest.py

### 🤖 Assistant

> 🔧 called: read_file

Now let me look at the tests file to understand what already exists and the __init__.py:

> 🔧 **read_file** — tests\agent_1_2\test_agent_1_unittest.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — tests\agent_1_2\test_agent_1_unittest.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — tests\agent_1_2\test_agent_1_unittest.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — tests\agent_1_2\test_agent_1_unittest.py

### 🤖 Assistant

> 🔧 called: read_file, read_file

Now I have a good understanding of the codebase. Let me check the `__init__.py` files:

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

> 🔧 **read_file** — tests\agent_1_2\__init__.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have a thorough understanding. Let me plan the full set of changes needed:

> 🔧 **update_todo_list** — 
[x] Investigate current codebase structure and existing files
[-] Fix item 1: Empty env vars treated as unset (in _call_watsonx_chat and _get_iam_token)
[ ] Fix item 2: Strict grounding - rule-only facts, substantive quote validation (>=8 chars, >=2 words)
[ ] Fix item 3: Accurate urgency & reason on model-added needs (shared helper, not hardcoded "high")
[ ] Fix item 4: Cross-process IAM token cache & call counter (atomic JSON state file)
[ ] Fix item 5: Single overall timeout budget (~18s, configurable)
[ ] Fix item 6: Isolate WATSONX_* in tests (clear all WATSONX_* by default)
[ ] Fix item 7: Add unit tests for all items
[ ] Run tests and verify 0 failures


### 🤖 Assistant

> 🔧 called: read_file

Now let me read additional details about the `_understand_story` section around urgency, and see what `_default_urgency` currently looks like:

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now I have all the information I need. Let me create the comprehensive fix for `agent_1.py`. The changes are:

1. **Item 1**: Helper `_env_str`/`_env_int` to skip empty/whitespace values  
2. **Items 2 & 3**: Drop `factual_claims` from model, substantive quote validation (≥8 chars, ≥2 words), shared urgency helper `_wx_urgency`  
3. **Item 4**: Cross-process state file using `tempfile.gettempdir()` + atomic JSON  
4. **Item 5**: Single shared deadline/budget of `min(WATSONX_TIMEOUT, 18)` s  
5. **Items 6 & 7**: New test file  

> 🔧 **apply_diff** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file

Now let me apply all remaining fixes to `agent_1.py` in one diff — items 1, 2, 3, 4 (call counter), 5:

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now I'll apply all the remaining changes (items 1-5) in one shot:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:615
-------
# ---------------------------------------------------------------------------
# watsonx.ai helpers (standard-library only, injectable http_post_fn for tests)
# ---------------------------------------------------------------------------

def _get_iam_token(
    apikey: str,
    http_post_fn: Optional[Callable] = None,
) -> str:
    """Return a cached IAM bearer token, refreshing when < 60s from expiry."""
    global _iam_token_cache
    token, expires_at = _iam_token_cache
    now = time.monotonic()
    if token and now < expires_at - 60:
        return token

    iam_url = "https://iam.cloud.ibm.com/identity/token"
    body = urllib.parse.urlencode({
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": apikey,
    }).encode()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    timeout = int(os.environ.get("WATSONX_TIMEOUT", DEFAULT_WATSONX_TIMEOUT))

    if http_post_fn is not None:
        resp_bytes = http_post_fn(iam_url, body, headers)
    else:
        req = urllib.request.Request(iam_url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_bytes = resp.read()

    data = json.loads(resp_bytes)
    new_token = data["access_token"]
    expires_in = int(data.get("expires_in", 3600))
    _iam_token_cache = (new_token, time.monotonic() + expires_in)
    return new_token


def _call_watsonx_chat(
    story_text: str,
    http_post_fn: Optional[Callable] = None,
) -> Optional[Dict[str, Any]]:
    """
    Call watsonx.ai text/chat and return parsed JSON dict from the assistant message,
    or None on any error (timeout, HTTP error, invalid JSON, call cap reached).
    Privacy: never logs story_text, prompts, API keys, or model output text.
    Returns (result_dict_or_None, latency_ms, used_call).
    """
    global _watsonx_call_count

    apikey = os.environ.get("WATSONX_APIKEY", "")
    if not apikey:
        return None, 0, False

    max_calls = int(os.environ.get("WATSONX_MAX_CALLS", DEFAULT_WATSONX_MAX_CALLS))
    if _watsonx_call_count >= max_calls:
        return None, 0, False  # call cap reached

    model_id = os.environ.get("WATSONX_MODEL_ID", DEFAULT_WATSONX_MODEL_ID)
    wx_url = os.environ.get("WATSONX_URL", DEFAULT_WATSONX_URL).rstrip("/")
    project_id = os.environ.get("WATSONX_PROJECT_ID", DEFAULT_WATSONX_PROJECT_ID)
    timeout = int(os.environ.get("WATSONX_TIMEOUT", DEFAULT_WATSONX_TIMEOUT))

    endpoint = (
        f"{wx_url}/ml/v1/text/chat?version=2024-05-31"
    )

    system_prompt = (
        "You are an intake assistant for a community aid navigator. "
        "Extract structured crisis information from the applicant story. "
        "Return ONLY a JSON object with two optional keys: "
        "\"proposed_needs\" (array) and \"factual_claims\" (array). "
        "Each proposed_need: {category, description, original_quote}. "
        "Each factual_claim: {field, value}. "
        "Do NOT include urgency — it is determined by rules. "
        "Do NOT invent information not stated in the story."
    )

    payload = {
        "model_id": model_id,
        "project_id": project_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": story_text},
        ],
        "parameters": {
            "temperature": 0,
            "max_new_tokens": 512,
        },
    }
    body = json.dumps(payload).encode()

    try:
        bearer = _get_iam_token(apikey, http_post_fn=http_post_fn)
    except Exception:
        return None, 0, False

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer}",
    }

    t0 = time.monotonic()
    try:
        if http_post_fn is not None:
            resp_bytes = http_post_fn(endpoint, body, headers)
        else:
            req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_bytes = resp.read()
        _watsonx_call_count += 1
    except Exception:
        return None, 0, False

    latency_ms = int((time.monotonic() - t0) * 1000)

    try:
        outer = json.loads(resp_bytes)
        # watsonx chat response: choices[0].message.content
        content = outer["choices"][0]["message"]["content"]
        # Strip markdown fences if present
        content = re.sub(r"^```(?:json)?\s*", "", content.strip(), flags=re.IGNORECASE)
        content = re.sub(r"\s*```$", "", content.strip())
        result = json.loads(content)
        if not isinstance(result, dict):
            return None, latency_ms, True
    except Exception:
        return None, latency_ms, True

    return result, latency_ms, True


def _merge_watsonx_into_result(
    wx_result: Dict[str, Any],
    story: str,
    facts: List[Dict[str, Any]],
    proposed_needs: List[Dict[str, Any]],
    need_idx: int,
    fact_idx: int,
    urgency_fn: Callable,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int, int]:
    """
    Merge strictly validated additions from watsonx into rule-derived facts/needs.
    Never modifies safety_or_official_deadline_flags.
    Never trusts model urgency — always derives from rules.
    """
    existing_fact_fields = {f["field"] for f in facts}
    existing_need_cats = {n["category"] for n in proposed_needs}

    # Merge proposed_needs
    wx_needs = wx_result.get("proposed_needs", [])
    if isinstance(wx_needs, list):
        for item in wx_needs:
            if not isinstance(item, dict):
                continue
            cat = item.get("category", "")
            if cat not in _ALLOWED_NEED_CATEGORIES:
                continue
            if cat in existing_need_cats:
                continue
            original_quote = item.get("original_quote", "")
            # Grounding check: quote must appear verbatim in story (case-insensitive)
            if not original_quote or original_quote.strip().lower() not in story.lower():
                continue
            desc = item.get("description", cat.replace("_", " ").title())
            urgency = urgency_fn(cat)
            proposed_needs.append(_make_need(
                cat,
                need_idx,
                description=str(desc)[:200],
                original_quote=original_quote,
                urgency=urgency,
                urgency_reason=f"Identified by AI enhancement (urgency from rules)",
            ))
            existing_need_cats.add(cat)
            need_idx += 1

    # Merge factual_claims
    wx_facts = wx_result.get("factual_claims", [])
    if isinstance(wx_facts, list):
        for item in wx_facts:
            if not isinstance(item, dict):
                continue
            field = item.get("field", "")
            if field not in _ALLOWED_FACTUAL_FIELDS:
                continue
            if field in existing_fact_fields:
                continue
            value = item.get("value")
            # Type/enum validation per field
            if field == "employment_status":
                if value not in _ALLOWED_EMPLOYMENT_STATUS:
                    continue
            elif field == "eviction_notice_type":
                if value not in _ALLOWED_EVICTION_NOTICE_TYPE:
                    continue
            elif field == "has_written_eviction_notice":
                if not isinstance(value, bool):
                    continue
            elif field == "household_size":
                if not isinstance(value, int) or value < 1:
                    continue
            elif field == "children_ages":
                if not isinstance(value, list) or not all(isinstance(a, int) for a in value):
                    continue
            elif field in ("rent_amount_monthly", "cash_on_hand_approx",
                           "household_gross_monthly_income", "rent_arrears_amount"):
                if not isinstance(value, (int, float)):
                    continue
            facts.append(_make_fact(field, value, fact_idx))
            existing_fact_fields.add(field)
            fact_idx += 1

    return facts, proposed_needs, need_idx, fact_idx
=======
# ---------------------------------------------------------------------------
# watsonx.ai helpers (standard-library only, injectable http_post_fn for tests)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Item 1: Helper to read env vars — treat empty/whitespace-only as unset.
# ---------------------------------------------------------------------------

def _env_str(name: str, default: str) -> str:
    """Return env var value, falling back to default if absent or blank."""
    val = os.environ.get(name, "")
    return val.strip() if val.strip() else default


def _env_int(name: str, default: int) -> int:
    """Return env var as int, falling back to default if absent, blank, or non-integer."""
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Item 3: Shared urgency helper for model-added proposed_needs.
# Derives urgency from story/quote signals; never hardcodes "high".
# ---------------------------------------------------------------------------

_IMMEDIATE_SIGNAL_RE = re.compile(
    r"\b(lock(?:ed)?\s+(?:us|me)\s+out|change\s+the\s+locks|actual\s+lockout|"
    r"eviction\s+notice|3[-\s]day\s+notice|sleeping\s+in\s+(?:my|our|the)\s+car|"
    r"homeless|no\s+shelter|disconnection\s+notice|shut\s*off\s+notice|"
    r"past\s+due|overdue|behind\s+on\s+rent|was\s+due)\b",
    re.IGNORECASE,
)


def _wx_urgency(category: str, story: str, original_quote: str) -> Tuple[str, str]:
    """
    Return (urgency, urgency_reason) for a model-identified proposed_need.
    Checks story and quote for urgent signals; defaults to 'medium'.
    """
    combined = (story + " " + original_quote).lower()
    if _IMMEDIATE_SIGNAL_RE.search(combined):
        return "immediate", "Urgent signal detected in story or quote"
    # High-urgency patterns: eviction threats, food shortage, job loss
    if re.search(
        r"\b(evict|threaten|lock\s+out|hungry|running\s+low\s+on\s+food|"
        r"laid\s+off|fired|lost\s+(?:my|our)\s+job|no\s+food|not\s+enough\s+food)\b",
        combined,
    ):
        return "high", "High-urgency signal detected in story or quote"
    return "medium", "AI-identified need; no urgent signals detected"


def _get_iam_token(
    apikey: str,
    http_post_fn: Optional[Callable] = None,
    deadline: Optional[float] = None,
) -> str:
    """Return a cached IAM bearer token, refreshing when < 60s from expiry.

    Checks both in-process cache and cross-process persisted cache.
    deadline: monotonic deadline; if remaining budget is too small, raises TimeoutError.
    """
    global _iam_token_cache

    # 1. In-process cache check
    token, expires_at = _iam_token_cache
    now = time.monotonic()
    if token and now < expires_at - 60:
        return token

    # 2. Cross-process persistent cache check
    p_token, p_expires_at = _get_persisted_iam_token()
    if p_token and time.monotonic() < p_expires_at - 60:
        _iam_token_cache = (p_token, p_expires_at)
        return p_token

    # Need to fetch a new token — compute remaining budget
    # Item 5: use remaining deadline budget for IAM call, not a full separate timeout
    if deadline is not None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("No time budget remaining for IAM token fetch")
        iam_timeout = max(1, int(remaining))
    else:
        iam_timeout = _env_int("WATSONX_TIMEOUT", DEFAULT_WATSONX_TIMEOUT)

    iam_url = "https://iam.cloud.ibm.com/identity/token"
    body = urllib.parse.urlencode({
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": apikey,
    }).encode()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    if http_post_fn is not None:
        resp_bytes = http_post_fn(iam_url, body, headers)
    else:
        req = urllib.request.Request(iam_url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=iam_timeout) as resp:
            resp_bytes = resp.read()

    data = json.loads(resp_bytes)
    new_token = data["access_token"]
    expires_in = int(data.get("expires_in", 3600))
    mono_expires = time.monotonic() + expires_in
    _iam_token_cache = (new_token, mono_expires)
    _persist_iam_token(new_token, expires_in)
    return new_token


def _call_watsonx_chat(
    story_text: str,
    http_post_fn: Optional[Callable] = None,
) -> Optional[Dict[str, Any]]:
    """
    Call watsonx.ai text/chat and return parsed JSON dict from the assistant message,
    or None on any error (timeout, HTTP error, invalid JSON, call cap reached).
    Privacy: never logs story_text, prompts, API keys, or model output text.
    Returns (result_dict_or_None, latency_ms, used_call).

    Item 5: Uses a single shared deadline budget (<=18 s) across IAM + chat.
    Item 4: Counts ALL attempted calls (including failed/timed-out) in persisted state.
    Item 1: Empty/whitespace env vars fall back to defaults.
    """
    global _watsonx_call_count

    # Item 1: treat empty WATSONX_APIKEY as unset
    apikey = os.environ.get("WATSONX_APIKEY", "").strip()
    if not apikey:
        return None, 0, False

    # Item 1: safe int parse for MAX_CALLS
    max_calls = _env_int("WATSONX_MAX_CALLS", DEFAULT_WATSONX_MAX_CALLS)

    # Item 4: check persisted cross-process call count (use whichever is larger)
    persisted_count = _get_call_count()
    effective_count = max(_watsonx_call_count, persisted_count)
    if effective_count >= max_calls:
        return None, 0, False  # call cap reached

    # Item 1: safe reads for other string env vars
    model_id = _env_str("WATSONX_MODEL_ID", DEFAULT_WATSONX_MODEL_ID)
    wx_url = _env_str("WATSONX_URL", DEFAULT_WATSONX_URL).rstrip("/")
    project_id = _env_str("WATSONX_PROJECT_ID", DEFAULT_WATSONX_PROJECT_ID)

    # Item 5: single shared timeout budget, capped at 18 s (< Supervisor's 30 s limit)
    raw_timeout = _env_int("WATSONX_TIMEOUT", DEFAULT_WATSONX_TIMEOUT)
    budget = min(raw_timeout, 18)
    deadline = time.monotonic() + budget

    endpoint = f"{wx_url}/ml/v1/text/chat?version=2024-05-31"

    system_prompt = (
        "You are an intake assistant for a community aid navigator. "
        "Extract structured crisis information from the applicant story. "
        "Return ONLY a JSON object with one optional key: "
        "\"proposed_needs\" (array). "
        "Each proposed_need: {category, description, original_quote}. "
        "Do NOT include urgency — it is determined by rules. "
        "Do NOT return factual_claims — facts are extracted by deterministic rules. "
        "Do NOT invent information not stated in the story."
    )

    payload = {
        "model_id": model_id,
        "project_id": project_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": story_text},
        ],
        "parameters": {
            "temperature": 0,
            "max_new_tokens": 512,
        },
    }
    body = json.dumps(payload).encode()

    # Item 4: increment persisted call count before the attempt (counts failures too)
    new_count = _increment_call_count()
    _watsonx_call_count = new_count

    try:
        # Item 5: pass remaining deadline budget to IAM fetch
        bearer = _get_iam_token(apikey, http_post_fn=http_post_fn, deadline=deadline)
    except Exception:
        return None, 0, True  # used_call=True: call was attempted and counted

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer}",
    }

    # Item 5: remaining budget for the actual chat call
    remaining = deadline - time.monotonic()
    chat_timeout = max(1, int(remaining))

    t0 = time.monotonic()
    try:
        if http_post_fn is not None:
            resp_bytes = http_post_fn(endpoint, body, headers)
        else:
            req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=chat_timeout) as resp:
                resp_bytes = resp.read()
    except Exception:
        return None, 0, True  # counted but failed

    latency_ms = int((time.monotonic() - t0) * 1000)

    try:
        outer = json.loads(resp_bytes)
        # watsonx chat response: choices[0].message.content
        content = outer["choices"][0]["message"]["content"]
        # Strip markdown fences if present
        content = re.sub(r"^```(?:json)?\s*", "", content.strip(), flags=re.IGNORECASE)
        content = re.sub(r"\s*```$", "", content.strip())
        result = json.loads(content)
        if not isinstance(result, dict):
            return None, latency_ms, True
    except Exception:
        return None, latency_ms, True

    return result, latency_ms, True


def _merge_watsonx_into_result(
    wx_result: Dict[str, Any],
    story: str,
    facts: List[Dict[str, Any]],
    proposed_needs: List[Dict[str, Any]],
    need_idx: int,
    fact_idx: int,
    urgency_fn: Callable,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int, int]:
    """
    Merge strictly validated proposed_needs additions from watsonx into rule-derived needs.
    Never modifies safety_or_official_deadline_flags.
    Never trusts model urgency — always derives from rules via urgency_fn.
    Item 2: factual_claims from the model are ignored (100% rule-based).
    Item 2: original_quote must be substantive (>=8 chars, >=2 words).
    """
    existing_need_cats = {n["category"] for n in proposed_needs}

    # Merge proposed_needs only (Item 2: factual_claims section removed)
    wx_needs = wx_result.get("proposed_needs", [])
    if isinstance(wx_needs, list):
        for item in wx_needs:
            if not isinstance(item, dict):
                continue
            cat = item.get("category", "")
            if cat not in _ALLOWED_NEED_CATEGORIES:
                continue
            if cat in existing_need_cats:
                continue
            original_quote = item.get("original_quote", "")
            q_stripped = original_quote.strip()
            # Item 2: Substantive grounding check:
            #   - quote must be at least 8 characters
            #   - quote must contain at least 2 words
            #   - quote must appear verbatim in story (case-insensitive)
            if (
                len(q_stripped) < 8
                or len(q_stripped.split()) < 2
                or q_stripped.lower() not in story.lower()
            ):
                continue
            desc = item.get("description", cat.replace("_", " ").title())
            # Item 3: derive urgency from shared rule helper, not hardcoded
            urgency, urgency_reason = urgency_fn(cat, story, q_stripped)
            proposed_needs.append(_make_need(
                cat,
                need_idx,
                description=str(desc)[:200],
                original_quote=original_quote,
                urgency=urgency,
                urgency_reason=urgency_reason,
            ))
            existing_need_cats.add(cat)
            need_idx += 1

    # Item 2: factual_claims from the model are intentionally ignored.
    # All factual_claims are 100% rule-derived.

    return facts, proposed_needs, need_idx, fact_idx
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: read_file

Now update the `_understand_story` section where `_default_urgency` is defined to use the new `_wx_urgency` helper:

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:1493
-------
        else:
            def _default_urgency(category: str) -> str:
                return "high"

            facts, proposed_needs, need_idx, fact_idx = _merge_watsonx_into_result(
                wx_result=wx_result,
                story=story,
                facts=facts,
                proposed_needs=proposed_needs,
                need_idx=need_idx,
                fact_idx=fact_idx,
                urgency_fn=_default_urgency,
            )
            env["is_mock"] = False
            env["issues"].append({
                "code": "WATSONX_USED",
                "severity": "info",
                "message": f"watsonx.ai call succeeded.",
                "call_count": _watsonx_call_count,
                "latency_ms": latency_ms,
            })
=======
        else:
            # Item 3: use shared _wx_urgency helper (not hardcoded "high")
            facts, proposed_needs, need_idx, fact_idx = _merge_watsonx_into_result(
                wx_result=wx_result,
                story=story,
                facts=facts,
                proposed_needs=proposed_needs,
                need_idx=need_idx,
                fact_idx=fact_idx,
                urgency_fn=_wx_urgency,
            )
            env["is_mock"] = False
            env["issues"].append({
                "code": "WATSONX_USED",
                "severity": "info",
                "message": "watsonx.ai call succeeded.",
                "call_count": _watsonx_call_count,
                "latency_ms": latency_ms,
            })
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: grep

Now, the existing test `test_mocked_success_watsonx_used_issue` checks that `cg_need["urgency"] == "high"`. With the new `_wx_urgency` helper and a story containing "lost my job" but no immediate signals, the urgency would be `"high"` (due to `laid_off` matching) — so that test still passes. Let me verify the existing test `test_max_calls_cap_enforced` which resets `_watsonx_call_count = 0` via `_reset_module()` but now also uses a persisted state file. The tests need to also reset the persisted state. Let me check the `_reset_module` usage carefully:

> 🔧 **grep** — _reset_module|_watsonx_call_count|_iam_token_cache

### 🤖 Assistant

> 🔧 called: apply_diff

I need to update `_reset_module` to also clear the persisted state. Let me update the existing test's `_reset_module`:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:854
-------
    @staticmethod
    def _reset_module():
        """Reset module-level watsonx state before a test."""
        import navigator.agents.agent_1_2.agent_1 as a1_mod
        a1_mod._watsonx_call_count = 0
        a1_mod._iam_token_cache = ("", 0.0)
=======
    @staticmethod
    def _reset_module():
        """Reset module-level watsonx state before a test (in-process + persisted)."""
        import navigator.agents.agent_1_2.agent_1 as a1_mod
        a1_mod._watsonx_call_count = 0
        a1_mod._iam_token_cache = ("", 0.0)
        # Also clear the cross-process persistent state file
        a1_mod._write_state({})
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: update_todo_list

Now I also need to look at `test_mocked_success_watsonx_used_issue` — the crowdfunding quote is `"We also need help with crowdfunding to get back on our feet."` and the story is `"I lost my job last month and can't pay rent in 95823. We also need help with crowdfunding to get back on our feet."` — the urgency will be `"high"` (because story has "laid_off"/"lost my job"). The test asserts `urgency == "high"`, so it still passes.

Now let me also check that test `test_max_calls_cap_enforced` — it uses `_reset_module()` before the loop, and runs 3 calls. With the new code, `_increment_call_count()` is called before the HTTP attempt. So after 3 calls, `wx_calls` list should still have 2 entries (the 3rd is capped before HTTP). The key insight: the counter is incremented **before** the check at the start of `_call_watsonx_chat`. Let me re-read the flow:

In the new `_call_watsonx_chat`:
1. Check `effective_count >= max_calls` → return early (no increment)
2. Increment counter (counts the attempt)
3. Try IAM + HTTP

So with max_calls=2, run_1: effective=0, increment to 1, HTTP call #1. run_2: effective=1, increment to 2, HTTP call #2. run_3: effective=2 >= 2, return early (no HTTP call). `wx_calls` = [1, 1] = 2. ✓

Then after the loop, the test does another call: effective=2 >= 2, `is_mock=True`. ✓

Now let me create the new test file for items 6 and 7:

> 🔧 **update_todo_list** — 
[x] Investigate current codebase structure and existing files
[x] Fix item 1: Empty env vars treated as unset (in _call_watsonx_chat and _get_iam_token)
[x] Fix item 2: Strict grounding - rule-only facts, substantive quote validation (>=8 chars, >=2 words)
[x] Fix item 3: Accurate urgency & reason on model-added needs (shared helper, not hardcoded "high")
[x] Fix item 4: Cross-process IAM token cache & call counter (atomic JSON state file)
[x] Fix item 5: Single overall timeout budget (~18s, configurable)
[-] Fix item 6: Isolate WATSONX_* in tests (clear all WATSONX_* by default)
[ ] Fix item 7: Add unit tests for all items
[ ] Run tests and verify 0 failures


### 🤖 Assistant

> 🔧 called: glob, glob

Now I need to look at how the existing test suite handles env vars and add an isolation mechanism. Let me check `conftest.py` or similar:

> 🔧 **glob** — tests/**/conftest.py

> 🔧 **glob** — tests/**/__init__.py

### 🤖 Assistant

> 🔧 called: glob



> 🔧 **glob** — tests/**/*.py

### 🤖 Assistant

> 🔧 called: glob



> 🔧 **glob** — tests/*.py

### 🤖 Assistant

> 🔧 called: list_files



> 🔧 **list_files** — tests

### 🤖 Assistant

> 🔧 called: apply_diff

For item 6, I need to clear `WATSONX_*` env vars across the agent_1_2 test suite. The cleanest way with `unittest` (no pytest) is to add a `setUpModule`/module-level setup in a shared location, or use a `setUp` in each test class. Since we need to do it "across the test suite by default", the best approach for stdlib `unittest` is to add it to the `tests/agent_1_2/__init__.py` as a `load_tests` hook or add `setUp`/`tearDown` in a base class.

The simplest approach: add an `__init__.py` modification to `tests/agent_1_2/` that removes `WATSONX_*` vars before each test module loads, and create a `conftest`-equivalent by adding a `setUpModule` in a helper, **or** add a `BaseWatsonxTestCase` that patches `os.environ` in each test.

The most reliable approach is to add it to `tests/agent_1_2/__init__.py` as a `setUpModule` or by adding to the existing `TestWatsonxIntegration.setUp`. Let me look at whether there's a `setUp` already:

The `TestWatsonxIntegration` class has no `setUp`/`tearDown` currently. The existing tests use `unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-123"})` which is **additive** (doesn't clear other vars). 

For item 6, the goal is: "Clear all `WATSONX_*` environment variables across the test suite by default so running `python -I -m unittest discover ...` with `.env` loaded never hits the network unless a test explicitly patches `os.environ`."

The best place for this is a `setUpModule` in the test files, or even better, a `setUp`/`tearDown` on the `TestWatsonxIntegration` class that saves and clears all `WATSONX_*` vars. I'll add:

1. A `setUp`/`tearDown` to `TestWatsonxIntegration` that clears `WATSONX_*` env vars.
2. The new watsonx test file will also do this.

Since `python -I` is used (isolated mode, no site-packages), and `.env` is loaded separately, the safest is adding a `setUp` to both test classes and creating a `setUpModule` in `__init__.py`:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:838
-------
class TestWatsonxIntegration(unittest.TestCase):
    """
    Offline mocked tests for watsonx.ai integration in _understand_story.
    All network calls are intercepted via the _http_post_fn hook; WATSONX_APIKEY
    is controlled via os.environ patching.  Zero external dependencies.
    """
=======
# ---------------------------------------------------------------------------
# Item 6: Module-level WATSONX_* env isolation
# ---------------------------------------------------------------------------
_WATSONX_ENV_KEYS = [k for k in os.environ if k.startswith("WATSONX_")]
_SAVED_WATSONX_ENV: dict = {}


def setUpModule():
    """Remove all WATSONX_* env vars before any test in this module runs."""
    global _SAVED_WATSONX_ENV
    _SAVED_WATSONX_ENV = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}


def tearDownModule():
    """Restore WATSONX_* env vars after all tests in this module complete."""
    os.environ.update(_SAVED_WATSONX_ENV)


class TestWatsonxIntegration(unittest.TestCase):
    """
    Offline mocked tests for watsonx.ai integration in _understand_story.
    All network calls are intercepted via the _http_post_fn hook; WATSONX_APIKEY
    is controlled via os.environ patching.  Zero external dependencies.
    """

    def setUp(self):
        """Ensure no WATSONX_* env vars leak in from parent environment."""
        self._stashed = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self):
        """Restore any WATSONX_* vars stashed during setUp."""
        os.environ.update(self._stashed)
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: update_todo_list

Now create the new test file for item 7:

> 🔧 **update_todo_list** — 
[x] Investigate current codebase structure and existing files
[x] Fix item 1: Empty env vars treated as unset (in _call_watsonx_chat and _get_iam_token)
[x] Fix item 2: Strict grounding - rule-only facts, substantive quote validation (>=8 chars, >=2 words)
[x] Fix item 3: Accurate urgency & reason on model-added needs (shared helper, not hardcoded "high")
[x] Fix item 4: Cross-process IAM token cache & call counter (atomic JSON state file)
[x] Fix item 5: Single overall timeout budget (~18s, configurable)
[x] Fix item 6: Isolate WATSONX_* in tests (clear all WATSONX_* by default)
[-] Fix item 7: Add unit tests for all items
[ ] Run tests and verify 0 failures


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — tests\agent_1_2\test_watsonx_fixes_unittest.py

### 🤖 Assistant

> 🔧 called: execute_command

Now let's run the tests to see if they pass:

> 🔧 **execute_command** — cd "" ; python -I -m unittest discover -s tests -t . 2>&1 | Select-String -Pattern "ERROR|FAIL|OK|Ran|test_" | Select-Object -First 60

### 🤖 Assistant

> 🔧 called: execute_command

Wait, actually it says `OK` but exited with code 1. Let me get the full output:

> 🔧 **execute_command** — cd "" ; python -I -m unittest discover -s tests -t . 2>&1

### 🤖 Assistant

> 🔧 called: execute_command

Exit code 1 is coming from PowerShell misinterpreting the `ResourceWarning` output to stderr as an error, but the test runner actually says "Ran 586 tests in 7.582s OK". Let me confirm this explicitly:

> 🔧 **execute_command** — cd "" ; python -I -m unittest discover -s tests -t . ; Write-Host "Exit code: $LASTEXITCODE"

### 🤖 Assistant

> 🔧 called: execute_command

**Exit code: 0, 586 tests, OK** — all pass. Now let me also run just the new test file to confirm the new tests all pass:

> 🔧 **execute_command** — cd "" ; python -I -m unittest tests.agent_1_2.test_watsonx_fixes_unittest -v 2>&1 | Select-String -Pattern "ERROR|FAIL|OK|test_|Ran"

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd "" ; python -I -m unittest discover -s tests/agent_1_2 -t . -p "test_watsonx_fixes*" -v 2>&1 | Select-String -Pattern "ERROR|FAIL|OK|test_|Ran"

### 🤖 Assistant

> 🔧 called: execute_command

All 27 new tests pass. The exit code 1 from PowerShell is just from `2>&1` treating stderr warnings as errors — the actual test run is `OK`. Let me confirm the full suite still runs clean:

> 🔧 **execute_command** — cd "" ; python -I -m unittest discover -s tests -t . ; Write-Host "Exit: $LASTEXITCODE"

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Investigate current codebase structure and existing files
[x] Fix item 1: Empty env vars treated as unset (in _call_watsonx_chat and _get_iam_token)
[x] Fix item 2: Strict grounding - rule-only facts, substantive quote validation (>=8 chars, >=2 words)
[x] Fix item 3: Accurate urgency & reason on model-added needs (shared helper, not hardcoded "high")
[x] Fix item 4: Cross-process IAM token cache & call counter (atomic JSON state file)
[x] Fix item 5: Single overall timeout budget (~18s, configurable)
[x] Fix item 6: Isolate WATSONX_* in tests (clear all WATSONX_* by default)
[x] Fix item 7: Add unit tests for all items
[x] Run tests and verify 0 failures


### 🤖 Assistant

**586 tests, 0 failures, exit 0.** Here's a summary of every change made:

---

## Changes summary

### [`navigator/agents/agent_1_2/agent_1.py`](navigator/agents/agent_1_2/agent_1.py)

**Item 1 — Empty env vars**  
Added [`_env_str(name, default)`](navigator/agents/agent_1_2/agent_1.py) and [`_env_int(name, default)`](navigator/agents/agent_1_2/agent_1.py) helpers that treat blank/whitespace-only values as absent, then replaced all `int(os.environ.get(...))` / `os.environ.get(...)` calls for `WATSONX_*` vars with these helpers.

**Item 2 — Strict grounding & rule-only facts**  
Removed the entire `factual_claims` merge block from [`_merge_watsonx_into_result()`](navigator/agents/agent_1_2/agent_1.py). Added a substantive-quote guard: `original_quote` must be ≥ 8 characters **and** ≥ 2 words (before the existing verbatim-in-story check). Updated the system prompt to tell the model not to return `factual_claims`.

**Item 3 — Accurate urgency & reason**  
Added [`_wx_urgency(category, story, original_quote)`](navigator/agents/agent_1_2/agent_1.py) which returns `("immediate", ...)`, `("high", ...)`, or `("medium", "AI-identified need; no urgent signals detected")` based on signal regexes. Replaced the hardcoded `return "high"` / `"urgency from rules"` closure in `_understand_story` with `urgency_fn=_wx_urgency`. Updated `_merge_watsonx_into_result` to accept `(urgency, urgency_reason)` tuple from the new signature.

**Item 4 — Cross-process state**  
Added `_state_file_path()`, `_read_state()`, `_write_state()`, `_get_call_count()`, `_increment_call_count()`, `_get_persisted_iam_token()`, and `_persist_iam_token()` using an atomic `os.replace()` JSON file in `tempfile.gettempdir()` (overridable via `WATSONX_STATE_FILE`). `_call_watsonx_chat` now increments the persisted counter **before** each attempt (so failures are counted), and `_get_iam_token` checks the persisted token before fetching a new one.

**Item 5 — Single timeout budget**  
`_call_watsonx_chat` computes one `deadline = time.monotonic() + min(WATSONX_TIMEOUT, 18)`. The deadline is passed to `_get_iam_token` which uses the remaining budget for the IAM call. The remaining time after IAM is used for the chat call. Both failures now return `used_call=True`.

---

### [`tests/agent_1_2/test_agent_1_unittest.py`](tests/agent_1_2/test_agent_1_unittest.py)

**Item 6 — Env isolation**  
Added `setUpModule` / `tearDownModule` to clear and restore `WATSONX_*` vars for the entire module. Added `setUp` / `tearDown` on `TestWatsonxIntegration`. Updated `_reset_module()` to also call `a1_mod._write_state({})` to clear the cross-process state file.

---

### [`tests/agent_1_2/test_watsonx_fixes_unittest.py`](tests/agent_1_2/test_watsonx_fixes_unittest.py) *(new)*

**Item 7 — New tests** (27 tests across 5 classes):
- `TestEmptyEnvVars` — 9 tests covering all 5 empty/whitespace env vars + end-to-end no-raise
- `TestStrictGrounding` — 5 tests: model facts ignored, 1-word quote rejected, <8-char quote rejected, ungrounded quote rejected, substantive quote accepted
- `TestModelAddedNeedUrgency` — 5 tests: `_wx_urgency` returns medium/high/immediate + end-to-end urgency_reason consistency
- `TestCrossProcessState` — 3 tests: persisted count across two real subprocesses, failed call increments count, IAM token persisted for cross-process reuse
- `TestSharedTimeoutBudget` — 2 tests: timeout cap at 18 s, IAM failure uses fallback
- `TestEnvIsolation` — 2 tests: no `WATSONX_*` vars present by default, absent apikey → deterministic fallback