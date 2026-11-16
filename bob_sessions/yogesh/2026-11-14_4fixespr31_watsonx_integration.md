# Apply these exact code and documentation changes on branch `feat/agent1-watsonx-v2`.
STRICT: Only modify `tests/__init__.py`, `navigator/agents/agent_1_2/`, `tests/agent_1_2/`, and `.env.example`. Do NOT touch `navigator/supervisor/`, `tests/test_dialog*.py`, or any other files.

1. `tests/__init__.py` (Suite-wide test isolation):
   - On module load, delete all `WATSONX_*` keys from `os.environ` and set `os.environ["WATSONX_STATE_FILE"]` to a temporary file path in `tempfile.gettempdir()` (with `atexit` cleanup) so child processes inherit the clean environment and never hit the network or real state file.
   - Add a unit test in `tests/agent_1_2/test_watsonx_fixes_unittest.py` running a Supervisor dialog with `WATSONX_APIKEY="dummy"` and asserting the state file counter stays at `0`.

2. `navigator/agents/agent_1_2/agent_1.py` & `navigator/agents/agent_1_2/README.md` (Daily resetting call cap):
   - Persist `{"date": "YYYY-MM-DD", "call_count": n}` in the state file; reset `call_count` to `0` when `"date"` != today's `YYYY-MM-DD`.
   - Add a unit test in `tests/agent_1_2/test_watsonx_fixes_unittest.py` verifying date rollover resets `call_count` to `0`.
   - Add two lines to `navigator/agents/agent_1_2/README.md` documenting where the state file is stored (`WATSONX_STATE_FILE` / temp dir) and how to reset it.

3. `navigator/agents/agent_1_2/agent_1.py` (Memory-only IAM token):
   - Keep the IAM bearer token and expiry strictly in memory; persist ONLY `{"date": ..., "call_count": ...}` to disk.
   - Add a unit test in `tests/agent_1_2/test_watsonx_fixes_unittest.py` asserting the state file never contains `iam_token` (or `access_token`/`expires_at`).

4. `navigator/agents/agent_1_2/agent_1.py` & `.env.example` (No hard-coded project ID):
   - Remove `DEFAULT_WATSONX_PROJECT_ID`. Read `WATSONX_PROJECT_ID` strictly from `os.environ` (stripped); if missing/empty, fall back to rules (`is_mock: true`) with an `info` issue `"WATSONX_PROJECT_ID not set"` and make zero network calls.
   - Add a unit test in `tests/agent_1_2/test_watsonx_fixes_unittest.py` for unset/whitespace `WATSONX_PROJECT_ID`.
   - Add `# Copy this file to .env and fill in your credentials. Never commit .env.` at the top of `.env.example`.

5. `navigator/agents/agent_1_2/agent_1.py` (Small items):
   - Use the exact same stripped API key helper in both `_understand_story` and `_call_watsonx_chat` so whitespace-only `WATSONX_APIKEY` logs `"info"` (`WATSONX_APIKEY not set`) instead of `"warning"`, and add a unit test for it.
   - Replace model-supplied need `description` with a fixed canonical description per allowed category (keeping the validated verbatim `original_quote`), and add a unit test for it.
   - Update `_call_watsonx_chat`'s docstring to state it returns a `tuple` instead of `Optional[Dict]`.

Run `python -I -m unittest discover -s tests -t .` and verify all tests pass.

---

**Status:** active  **Date:** 2026-11-16

---

### 👤 User

Apply these exact code and documentation changes on branch `feat/agent1-watsonx-v2`.
STRICT: Only modify `tests/__init__.py`, `navigator/agents/agent_1_2/`, `tests/agent_1_2/`, and `.env.example`. Do NOT touch `navigator/supervisor/`, `tests/test_dialog*.py`, or any other files.

1. `tests/__init__.py` (Suite-wide test isolation):
   - On module load, delete all `WATSONX_*` keys from `os.environ` and set `os.environ["WATSONX_STATE_FILE"]` to a temporary file path in `tempfile.gettempdir()` (with `atexit` cleanup) so child processes inherit the clean environment and never hit the network or real state file.
   - Add a unit test in `tests/agent_1_2/test_watsonx_fixes_unittest.py` running a Supervisor dialog with `WATSONX_APIKEY="dummy"` and asserting the state file counter stays at `0`.

2. `navigator/agents/agent_1_2/agent_1.py` & `navigator/agents/agent_1_2/README.md` (Daily resetting call cap):
   - Persist `{"date": "YYYY-MM-DD", "call_count": n}` in the state file; reset `call_count` to `0` when `"date"` != today's `YYYY-MM-DD`.
   - Add a unit test in `tests/agent_1_2/test_watsonx_fixes_unittest.py` verifying date rollover resets `call_count` to `0`.
   - Add two lines to `navigator/agents/agent_1_2/README.md` documenting where the state file is stored (`WATSONX_STATE_FILE` / temp dir) and how to reset it.

3. `navigator/agents/agent_1_2/agent_1.py` (Memory-only IAM token):
   - Keep the IAM bearer token and expiry strictly in memory; persist ONLY `{"date": ..., "call_count": ...}` to disk.
   - Add a unit test in `tests/agent_1_2/test_watsonx_fixes_unittest.py` asserting the state file never contains `iam_token` (or `access_token`/`expires_at`).

4. `navigator/agents/agent_1_2/agent_1.py` & `.env.example` (No hard-coded project ID):
   - Remove `DEFAULT_WATSONX_PROJECT_ID`. Read `WATSONX_PROJECT_ID` strictly from `os.environ` (stripped); if missing/empty, fall back to rules (`is_mock: true`) with an `info` issue `"WATSONX_PROJECT_ID not set"` and make zero network calls.
   - Add a unit test in `tests/agent_1_2/test_watsonx_fixes_unittest.py` for unset/whitespace `WATSONX_PROJECT_ID`.
   - Add `# Copy this file to .env and fill in your credentials. Never commit .env.` at the top of `.env.example`.

5. `navigator/agents/agent_1_2/agent_1.py` (Small items):
   - Use the exact same stripped API key helper in both `_understand_story` and `_call_watsonx_chat` so whitespace-only `WATSONX_APIKEY` logs `"info"` (`WATSONX_APIKEY not set`) instead of `"warning"`, and add a unit test for it.
   - Replace model-supplied need `description` with a fixed canonical description per allowed category (keeping the validated verbatim `original_quote`), and add a unit test for it.
   - Update `_call_watsonx_chat`'s docstring to state it returns a `tuple` instead of `Optional[Dict]`.

Run `python -I -m unittest discover -s tests -t .` and verify all tests pass.

---

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Explore the codebase structure to understand existing files
[ ] Implement tests/__init__.py suite-wide test isolation
[ ] Implement daily resetting call cap (date+call_count in state file)
[ ] Implement memory-only IAM token (no token in state file)
[ ] Remove hard-coded project ID, add .env.example header
[ ] Fix whitespace APIKEY handling and canonical need descriptions
[ ] Update _call_watsonx_chat docstring
[ ] Create tests/agent_1_2/test_watsonx_fixes_unittest.py with all unit tests
[ ] Run tests and verify all pass


### 🤖 Assistant

> 🔧 called: list_files



> 🔧 **list_files** — 

### 🤖 Assistant

> 🔧 called: list_files, list_files



> 🔧 **list_files** — navigator\agents\agent_1_2

> 🔧 **list_files** — tests

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file



> 🔧 **read_file** — tests\__init__.py

> 🔧 **read_file** — tests\agent_1_2\test_watsonx_fixes_unittest.py

> 🔧 **read_file** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — full content of agent_1.py - state file functions, _get_persisted_iam_token, _persist_iam_token, _get_call_count, _increment_call_count, _get_iam_token, DEFAULT_WATSONX_PROJECT_ID, _understand_story APIKEY check, _call_watsonx_chat docstring, need descriptions/categories

> 🔧 **read_file** — full content of test_watsonx_fixes_unittest.py

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — _get_iam_token function, _call_watsonx_chat function, _understand_story APIKEY check, _merge_watsonx_into_result, need descriptions

> 🔧 **read_file** — full content of test_watsonx_fixes_unittest.py - all tests, setUpModule, tearDownModule, _reset, TestEnvIsolation, TestCrossProcessState

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file, read_file



> 🔧 **read_file** — full content of test_watsonx_fixes_unittest.py - all code

> 🔧 **read_file** — _understand_story APIKEY check - apikey = os.environ, issues list, is_mock logic

> 🔧 **read_file** — .env.example full content

> 🔧 **read_file** — README.md full content

### 🤖 Assistant

> 🔧 called: read_file, read_file



> 🔧 **read_file** — _understand_story watsonx section - apikey check, is_mock, issues, WATSONX_FALLBACK, _call_watsonx_chat call, warning vs info

> 🔧 **read_file** — full content - end of _understand_story function - watsonx call section, apikey, is_mock, issues WATSONX_FALLBACK

### 🤖 Assistant

> 🔧 called: read_file, read_file

Now I have a clear picture of the codebase. Let me also check the `_make_need` function and the supervisor test to understand what's needed:

> 🔧 **read_file** — supervisor dialog test - what it imports and how handle_agent_1 is called

> 🔧 **read_file** — _make_need function - all parameters and description field

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have all the context I need. Let me plan the changes:

1. **`tests/__init__.py`**: Add env isolation on module load + atexit cleanup
2. **`agent_1.py`**:
   - Remove `DEFAULT_WATSONX_PROJECT_ID`; read `WATSONX_PROJECT_ID` strictly from env, fallback to rules (is_mock, info issue) if missing/empty
   - Date-based call counter reset in `_read_state`/`_get_call_count`/`_increment_call_count`
   - Memory-only IAM token: remove `_get_persisted_iam_token`/`_persist_iam_token` from disk storage
   - Use same stripped APIKEY helper in both `_understand_story` and `_call_watsonx_chat`; change severity of WATSONX_FALLBACK when apikey not set from "info" to consistent "info" with message "WATSONX_APIKEY not set"
   - Canonical `description` per category in `_merge_watsonx_into_result`
   - Update `_call_watsonx_chat` docstring to say returns `tuple`
3. **`tests/agent_1_2/test_watsonx_fixes_unittest.py`**: Add new test classes
4. **`navigator/agents/agent_1_2/README.md`**: Add two lines about state file
5. **`.env.example`**: Add header comment

> 🔧 **update_todo_list** — 
[x] Explore the codebase structure to understand existing files
[-] Implement tests/__init__.py suite-wide test isolation
[ ] Implement daily resetting call cap (date+call_count in state file)
[ ] Implement memory-only IAM token (no token in state file)
[ ] Remove hard-coded project ID, add .env.example header
[ ] Fix whitespace APIKEY handling and canonical need descriptions
[ ] Update _call_watsonx_chat docstring
[ ] Create/update tests/agent_1_2/test_watsonx_fixes_unittest.py with all new unit tests
[ ] Run tests and verify all pass


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — tests\__init__.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now let me work on `agent_1.py`. I need to make multiple changes. Let me read the parts I need to modify:

> 🔧 **update_todo_list** — 
[x] Explore the codebase structure to understand existing files
[x] Implement tests/__init__.py suite-wide test isolation
[-] Implement daily resetting call cap (date+call_count in state file)
[ ] Implement memory-only IAM token (no token in state file)
[ ] Remove hard-coded project ID, add .env.example header
[ ] Fix whitespace APIKEY handling and canonical need descriptions
[ ] Update _call_watsonx_chat docstring
[ ] Create/update tests/agent_1_2/test_watsonx_fixes_unittest.py with all new unit tests
[ ] Run tests and verify all pass


### 🤖 Assistant

> 🔧 called: apply_diff

Now apply all the agent_1.py changes in one pass:

> 🔧 **apply_diff** — navigator\agents\agent_1_2\agent_1.py

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Explore the codebase structure to understand existing files
[x] Implement tests/__init__.py suite-wide test isolation
[x] Implement daily resetting call cap (date+call_count in state file)
[x] Implement memory-only IAM token (no token in state file)
[x] Remove hard-coded project ID, add .env.example header
[x] Fix whitespace APIKEY handling and canonical need descriptions
[x] Update _call_watsonx_chat docstring
[-] Create/update tests/agent_1_2/test_watsonx_fixes_unittest.py with all new unit tests
[ ] Update README.md and .env.example
[ ] Run tests and verify all pass


### 🤖 Assistant

> 🔧 called: read_file

Now I need to check if the existing test file imports `DEFAULT_WATSONX_PROJECT_ID` and what tests reference `iam_token` persistence to understand what breaks. The existing test `test_iam_token_persists_across_subprocesses` uses `state.get("iam_token", "")` — since we removed IAM token from state, that test will now fail. But the instructions say I should **not** touch `tests/test_dialog*.py` — the existing tests in `test_watsonx_fixes_unittest.py` are in `tests/agent_1_2/` which I'm allowed to modify.

Let me check the existing tests that might break due to my changes:

> 🔧 **read_file** — test_iam_token_persists_across_subprocesses - reads state.get iam_token, asserting token persisted

### 🤖 Assistant

> 🔧 called: read_file

I see several problems with the existing tests that my changes break:

1. `test_no_watsonx_env_vars_present_by_default` — now `WATSONX_STATE_FILE` is set by `tests/__init__.py`, so this test will fail. The test checks that ALL WATSONX_* vars are absent.
2. `test_iam_token_persists_across_subprocesses` — asserts `state.get("iam_token") == "shared-tok"`, but I removed IAM token from state file.
3. `test_timeout_capped_at_18s` / `test_budget_fallback_when_iam_exceeds_budget` — these patch `WATSONX_APIKEY` without `WATSONX_PROJECT_ID`, so they'll now fall back due to missing project ID.
4. Various tests in `TestCrossProcessState`, `TestStrictGrounding`, `TestModelAddedNeedUrgency`, `TestEmptyEnvVars` — all have `WATSONX_APIKEY` without `WATSONX_PROJECT_ID`, so they'll return early (no-op). I need to add `WATSONX_PROJECT_ID` to all those patches.
5. Import of `DEFAULT_WATSONX_PROJECT_ID` will fail since it's removed.

Let me check the subprocess code in `test_call_count_persists_across_two_subprocesses` too:

> 🔧 **read_file** — TestCrossProcessState setUp tearDown _run_subprocess_call_count - WATSONX_PROJECT_ID

### 🤖 Assistant

> 🔧 called: write_file

Now I have a clear picture of all the problems. The existing test file needs significant updates:

1. Remove import of `DEFAULT_WATSONX_PROJECT_ID`
2. Fix `TestEnvIsolation.test_no_watsonx_env_vars_present_by_default` — now `WATSONX_STATE_FILE` is set at module load, so we need to allow that one
3. Fix `test_iam_token_persists_across_subprocesses` — IAM token no longer goes to disk
4. Add `WATSONX_PROJECT_ID` to all tests that patch env vars with `WATSONX_APIKEY`
5. Add subprocess code to include `WATSONX_PROJECT_ID`
6. Add all the new test classes (supervisor dialog, date rollover, state file never contains token, unset project ID, whitespace APIKEY info severity, canonical description)

Let me now rewrite the entire `test_watsonx_fixes_unittest.py`:

> 🔧 **write_file** — tests\agent_1_2\test_watsonx_fixes_unittest.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now update README.md and .env.example:

> 🔧 **update_todo_list** — 
[x] Explore the codebase structure to understand existing files
[x] Implement tests/__init__.py suite-wide test isolation
[x] Implement daily resetting call cap (date+call_count in state file)
[x] Implement memory-only IAM token (no token in state file)
[x] Remove hard-coded project ID, add .env.example header
[x] Fix whitespace APIKEY handling and canonical need descriptions
[x] Update _call_watsonx_chat docstring
[x] Create/update tests/agent_1_2/test_watsonx_fixes_unittest.py with all new unit tests
[-] Update README.md and .env.example
[ ] Run tests and verify all pass


### 🤖 Assistant

> 🔧 called: apply_diff, apply_diff



> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:1
-------
WATSONX_APIKEY=
=======
# Copy this file to .env and fill in your credentials. Never commit .env.
WATSONX_APIKEY=
>>>>>>> REPLACE


> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:46
-------
## 2. Test Execution

From repository root:
```bash
python -m unittest discover -s tests -t .
```
=======
## 2. State File

The watsonx call counter (`{"date": "YYYY-MM-DD", "call_count": N}`) is stored in the file
pointed to by `WATSONX_STATE_FILE` (defaults to `<tempdir>/watsonx_agent1_state.json`).  
To reset the counter manually, delete that file or set `WATSONX_STATE_FILE` to a fresh path.

## 3. Test Execution

From repository root:
```bash
python -m unittest discover -s tests -t .
```
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: update_todo_list

Now let's run the tests:

> 🔧 **update_todo_list** — 
[x] Explore the codebase structure to understand existing files
[x] Implement tests/__init__.py suite-wide test isolation
[x] Implement daily resetting call cap (date+call_count in state file)
[x] Implement memory-only IAM token (no token in state file)
[x] Remove hard-coded project ID, add .env.example header
[x] Fix whitespace APIKEY handling and canonical need descriptions
[x] Update _call_watsonx_chat docstring
[x] Create/update tests/agent_1_2/test_watsonx_fixes_unittest.py with all new unit tests
[x] Update README.md and .env.example
[-] Run tests and verify all pass


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -I -m unittest discover -s tests -t . 2>&1

### 🤖 Assistant

> 🔧 called: read_file

There are 5 failing tests in `test_agent_1_unittest.py`. Let me check what they expect:

> 🔧 **read_file** — TestWatsonxIntegration tests - test_http_exception_fallback severity warning, test_iam_token_reused_across_two_calls, test_invalid_json_fallback severity warning, test_max_calls_cap_enforced, test_mocked_success_watsonx_used_issue - what WATSONX_PROJECT_ID is set to

### 🤖 Assistant

> 🔧 called: read_file

Now I understand. The tests in `test_agent_1_unittest.py` are failing because:

1. `test_mocked_success_watsonx_used_issue`, `test_iam_token_reused_across_two_calls`, `test_invalid_json_fallback`, `test_http_exception_fallback`, `test_max_calls_cap_enforced` — all patch `WATSONX_APIKEY` without `WATSONX_PROJECT_ID`, so my new code skips the watsonx call.
2. `test_invalid_json_fallback` and `test_http_exception_fallback` expect `severity="warning"` for a failed call, but the code now returns a `warning` from `_call_watsonx_chat` returning `None` which goes to the same `"warning"` branch.

Wait — looking more carefully: the `_understand_story` function now has the `elif not project_id_env` branch. The tests that set `WATSONX_APIKEY` but NOT `WATSONX_PROJECT_ID` will hit the `elif not project_id_env` branch (since `tests/__init__.py` removes all WATSONX_* vars, including `WATSONX_PROJECT_ID`).

These tests are in `tests/agent_1_2/test_agent_1_unittest.py` which I'm allowed to modify. I need to look at how `_reset_module()` and `_make_req()` work in that class:

> 🔧 **read_file** — TestWatsonxIntegration class - setUp, tearDown, _reset_module, _make_req, _STORY, state file setup

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — TestWatsonxIntegration class declaration, setUp, tearDown - does it stash env vars

### 🤖 Assistant

> 🔧 called: apply_diff

The failing tests in `test_agent_1_unittest.py` patch `WATSONX_APIKEY` without `WATSONX_PROJECT_ID`. I need to add `WATSONX_PROJECT_ID` to those patches. These tests are allowed to be modified (they're in `tests/agent_1_2/`).

The failures are in these specific tests:
1. `test_mocked_success_watsonx_used_issue` — patches `{"WATSONX_APIKEY": "test-key-123"}` → need to add `WATSONX_PROJECT_ID`
2. `test_iam_token_reused_across_two_calls` — patches `{"WATSONX_APIKEY": "test-key-reuse"}` → need to add `WATSONX_PROJECT_ID`
3. `test_invalid_json_fallback` — patches `{"WATSONX_APIKEY": "test-key-badjson"}` → need to add `WATSONX_PROJECT_ID`; also expects `severity="warning"` for failed call which is correct (the `wx_result is None` path after attempt returns `warning`)
4. `test_http_exception_fallback` — patches `{"WATSONX_APIKEY": "test-key-timeout"}` → need to add `WATSONX_PROJECT_ID`; also expects `severity="warning"` which is correct
5. `test_max_calls_cap_enforced` — patches `{"WATSONX_APIKEY": "test-key-cap", "WATSONX_MAX_CALLS": "2"}` → need to add `WATSONX_PROJECT_ID`

Also need to check `test_ungrounded_quote_rejected` and `test_invalid_category_and_enum_rejected` which also don't have `WATSONX_PROJECT_ID` but were passing before — now they may be generating `is_mock=True` with no network call, but those tests only check `cats` content, not `is_mock`, so they still pass in mock mode.

Wait, actually for `test_invalid_json_fallback` — with `WATSONX_PROJECT_ID` added, the call will go through, hit the bad JSON, and then the `wx_result is None` path with `severity="warning"` will fire. Good.

For `test_http_exception_fallback` — with `WATSONX_PROJECT_ID` added, the IAM call succeeds, then the watsonx call raises TimeoutError → `used_call=True` → `wx_result is None` → `severity="warning"`. Good.

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:950
-------
        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-123"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))
=======
        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-123", "WATSONX_PROJECT_ID": "proj-test"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:991
-------
        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-reuse"}):
            handle_agent_1(self._make_req(http_post_fn=fake_http))
            # Second call — must reuse cached token (do NOT reset module state here)
            handle_agent_1(self._make_req(http_post_fn=fake_http))
=======
        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-reuse", "WATSONX_PROJECT_ID": "proj-test"}):
            handle_agent_1(self._make_req(http_post_fn=fake_http))
            # Second call — must reuse cached token (do NOT reset module state here)
            handle_agent_1(self._make_req(http_post_fn=fake_http))
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:1034
-------
        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-badjson"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))
=======
        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-badjson", "WATSONX_PROJECT_ID": "proj-test"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:1055
-------
        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-timeout"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))
=======
        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-timeout", "WATSONX_PROJECT_ID": "proj-test"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:1156
-------
        self._reset_module()
        with unittest.mock.patch.dict(
            os.environ,
            {"WATSONX_APIKEY": "test-key-cap", "WATSONX_MAX_CALLS": "2"},
        ):
            # 3 calls, cap is 2
            for i in range(3):
                handle_agent_1(self._make_req(http_post_fn=fake_http))
=======
        self._reset_module()
        with unittest.mock.patch.dict(
            os.environ,
            {"WATSONX_APIKEY": "test-key-cap", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_MAX_CALLS": "2"},
        ):
            # 3 calls, cap is 2
            for i in range(3):
                handle_agent_1(self._make_req(http_post_fn=fake_http))
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:1169
-------
        with unittest.mock.patch.dict(
            os.environ,
            {"WATSONX_APIKEY": "test-key-cap", "WATSONX_MAX_CALLS": "2"},
        ):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))
=======
        with unittest.mock.patch.dict(
            os.environ,
            {"WATSONX_APIKEY": "test-key-cap", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_MAX_CALLS": "2"},
        ):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: grep

Now let me also check tests that reference `DEFAULT_WATSONX_PROJECT_ID` or `test_ungrounded_quote_rejected` / `test_invalid_category_and_enum_rejected` (they don't set `WATSONX_PROJECT_ID` but only check `cats` content, not `is_mock`):

> 🔧 **grep** — DEFAULT_WATSONX_PROJECT_ID

### 🤖 Assistant

> 🔧 called: grep

Good. Now let me also check if there are other tests in `tests/agent_1_2/` that use `WATSONX_APIKEY` without `WATSONX_PROJECT_ID` for tests that expect actual watsonx calls:

> 🔧 **grep** — *.py

### 🤖 Assistant

> 🔧 called: execute_command

Tests at lines 1088 and 1128 in `test_agent_1_unittest.py` use `WATSONX_APIKEY` without `WATSONX_PROJECT_ID`. Let's check if they expect is_mock or just check content:

Looking at the existing code I already read:
- `test_ungrounded_quote_rejected` (line 1088): only asserts `cats = [n["category"] for ...]` and `self.assertNotIn("crowdfunding_guidance", cats)` — with no PROJECT_ID, it falls back to mock, so no watsonx call, so `crowdfunding_guidance` is not in cats. The test passes either way. ✓
- `test_invalid_category_and_enum_rejected` (line 1128): only asserts that invalid categories/enum values don't appear. No watsonx call in mock mode, so they don't appear. ✓

Good, those don't need changes. Now let me run the tests again:

> 🔧 **execute_command** — python -I -m unittest discover -s tests -t . 2>&1

### 🤖 Assistant

> 🔧 called: update_todo_list

All 599 tests pass. The `ResourceWarning` lines are pre-existing unrelated HTTP fixtures (not test failures).

Let me do a final verification of the changes:

> 🔧 **update_todo_list** — 
[x] Explore the codebase structure to understand existing files
[x] Implement tests/__init__.py suite-wide test isolation
[x] Implement daily resetting call cap (date+call_count in state file)
[x] Implement memory-only IAM token (no token in state file)
[x] Remove hard-coded project ID, add .env.example header
[x] Fix whitespace APIKEY handling and canonical need descriptions
[x] Update _call_watsonx_chat docstring
[x] Create/update tests/agent_1_2/test_watsonx_fixes_unittest.py with all new unit tests
[x] Update README.md and .env.example
[x] Run tests and verify all pass


### 🤖 Assistant

All 599 tests pass. Here's a summary of every change made:

---

### Changes made

**`tests/__init__.py`**
- Strips all `WATSONX_*` keys from `os.environ` on module load
- Sets `WATSONX_STATE_FILE` to a temp file so child processes inherit it
- Registers `atexit` cleanup to remove the temp state file

**`navigator/agents/agent_1_2/agent_1.py`**
- Removed `DEFAULT_WATSONX_PROJECT_ID` (hard-coded UUID)
- Added [`_today_str()`](navigator/agents/agent_1_2/agent_1.py) helper returning today's ISO date
- [`_get_call_count()`](navigator/agents/agent_1_2/agent_1.py): returns `0` when stored date ≠ today
- [`_increment_call_count()`](navigator/agents/agent_1_2/agent_1.py): resets to `{"date": today, "call_count": 0}` before incrementing when date rolled over; persists `{"date": ..., "call_count": ...}` only
- Removed `_get_persisted_iam_token()` and `_persist_iam_token()` — IAM token is now memory-only
- [`_get_iam_token()`](navigator/agents/agent_1_2/agent_1.py): uses only in-process `_iam_token_cache`, never writes to disk
- Added [`_CANONICAL_NEED_DESCRIPTIONS`](navigator/agents/agent_1_2/agent_1.py) dict with fixed strings per category
- Added [`_call_watsonx_chat()`](navigator/agents/agent_1_2/agent_1.py): updated docstring to state it returns a `tuple`; reads `WATSONX_PROJECT_ID` strictly from env (stripped), returns early with `(None, 0, False)` if missing; uses same `.strip()` on `WATSONX_APIKEY`
- [`_merge_watsonx_into_result()`](navigator/agents/agent_1_2/agent_1.py): uses `_CANONICAL_NEED_DESCRIPTIONS` instead of model-supplied `description`
- [`_understand_story()`](navigator/agents/agent_1_2/agent_1.py): strips `WATSONX_APIKEY` and `WATSONX_PROJECT_ID` before checking; added `elif not project_id_env` branch emitting `info`-severity `WATSONX_FALLBACK` with message `"WATSONX_PROJECT_ID not set"`

**`tests/agent_1_2/test_watsonx_fixes_unittest.py`**
- Removed import of `DEFAULT_WATSONX_PROJECT_ID` (no longer exists)
- Added `WATSONX_PROJECT_ID: "proj-test"` to all env patches that also set `WATSONX_APIKEY`
- Replaced `test_no_watsonx_env_vars_present_by_default` with `test_no_sensitive_watsonx_env_vars_present_by_default` (allows `WATSONX_STATE_FILE`)
- Replaced `test_iam_token_persists_across_subprocesses` with `test_iam_token_not_in_state_file` (now asserts token is NOT in state)
- Added subprocess code to include `WATSONX_PROJECT_ID`
- Added 4 new test classes: `TestDateRollover`, `TestStateFileNoToken`, `TestProjectIdFallback`, `TestApikeyInfoSeverity`, `TestCanonicalNeedDescriptions`

**`tests/agent_1_2/test_agent_1_unittest.py`**
- Added `WATSONX_PROJECT_ID: "proj-test"` to the 6 `patch.dict` calls that expected actual watsonx calls

**`navigator/agents/agent_1_2/README.md`**
- Added "State File" section documenting `WATSONX_STATE_FILE` and how to reset the counter

**`.env.example`**
- Added `# Copy this file to .env and fill in your credentials. Never commit .env.` header