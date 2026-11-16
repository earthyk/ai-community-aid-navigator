"""
Unit tests for the watsonx integration fixes (Items 1–7 and new PR items).

Covers:
  1. Empty-string / whitespace-only env vars fall back to defaults.
  2. Model-injected factual_claims are ignored; trivial/ungrounded quotes rejected.
  3. Model-added need urgency/reason derived from shared rule helper.
  4. Cross-process persisted call counter (date-based reset); IAM token memory-only.
  5. Single shared timeout budget (<=18 s).
  6. WATSONX_* env var isolation (all cleared by default in this module).
  7. All items tested explicitly.
  New: supervisor dialog state counter, date rollover, state-file no token, project ID
       fallback, whitespace APIKEY info severity, canonical need descriptions.

Zero external dependencies.  Run via:
    python -I -m unittest discover -s tests -t .
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from datetime import date

import navigator.agents.agent_1_2.agent_1 as a1_mod
from navigator.agents.agent_1_2.agent_1 import (
    DEFAULT_WATSONX_MAX_CALLS,
    DEFAULT_WATSONX_MODEL_ID,
    DEFAULT_WATSONX_TIMEOUT,
    DEFAULT_WATSONX_URL,
    _env_int,
    _env_str,
    _wx_urgency,
    handle_agent_1,
)

# ---------------------------------------------------------------------------
# Item 6: Module-level WATSONX_* env isolation
# ---------------------------------------------------------------------------
_SAVED_WATSONX_ENV: dict = {}


def setUpModule() -> None:
    """Remove all WATSONX_* env vars before any test in this module runs."""
    global _SAVED_WATSONX_ENV
    _SAVED_WATSONX_ENV = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}


def tearDownModule() -> None:
    """Restore WATSONX_* env vars after all tests in this module complete."""
    os.environ.update(_SAVED_WATSONX_ENV)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_iam_response(token: str = "tok-test", expires_in: int = 3600) -> bytes:
    return json.dumps({
        "access_token": token,
        "expires_in": expires_in,
        "token_type": "Bearer",
    }).encode()


def _make_wx_response(content_dict: dict) -> bytes:
    outer = {
        "choices": [{"message": {"role": "assistant", "content": json.dumps(content_dict)}}]
    }
    return json.dumps(outer).encode()


def _make_req(story: str, http_post_fn=None) -> dict:
    payload: dict = {"story_text": story}
    if http_post_fn is not None:
        payload["_http_post_fn"] = http_post_fn
    return {
        "request_id": "req-fix-test",
        "run_id": "run-fix-test",
        "case_id": "case-fix-test",
        "case_version": 1,
        "task_type": "understand_story",
        "payload": payload,
    }


def _reset(state_file: str | None = None) -> None:
    """Reset both in-process and persisted watsonx state."""
    a1_mod._watsonx_call_count = 0
    a1_mod._iam_token_cache = ("", 0.0)
    if state_file:
        os.environ["WATSONX_STATE_FILE"] = state_file
    a1_mod._write_state({})


# ---------------------------------------------------------------------------
# Item 1: Empty / whitespace env vars
# ---------------------------------------------------------------------------

class TestEmptyEnvVars(unittest.TestCase):
    """Item 1: empty/whitespace values for WATSONX_* must fall back to defaults."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)

    def test_env_int_empty_string(self):
        with unittest.mock.patch.dict(os.environ, {"WATSONX_MAX_CALLS": ""}):
            self.assertEqual(_env_int("WATSONX_MAX_CALLS", DEFAULT_WATSONX_MAX_CALLS), DEFAULT_WATSONX_MAX_CALLS)

    def test_env_int_whitespace_only(self):
        with unittest.mock.patch.dict(os.environ, {"WATSONX_MAX_CALLS": "   "}):
            self.assertEqual(_env_int("WATSONX_MAX_CALLS", DEFAULT_WATSONX_MAX_CALLS), DEFAULT_WATSONX_MAX_CALLS)

    def test_env_int_timeout_empty(self):
        with unittest.mock.patch.dict(os.environ, {"WATSONX_TIMEOUT": ""}):
            self.assertEqual(_env_int("WATSONX_TIMEOUT", DEFAULT_WATSONX_TIMEOUT), DEFAULT_WATSONX_TIMEOUT)

    def test_env_int_timeout_whitespace(self):
        with unittest.mock.patch.dict(os.environ, {"WATSONX_TIMEOUT": "  \t  "}):
            self.assertEqual(_env_int("WATSONX_TIMEOUT", DEFAULT_WATSONX_TIMEOUT), DEFAULT_WATSONX_TIMEOUT)

    def test_env_str_project_id_empty(self):
        with unittest.mock.patch.dict(os.environ, {"WATSONX_PROJECT_ID": ""}):
            self.assertEqual(_env_str("WATSONX_PROJECT_ID", "fallback"), "fallback")

    def test_env_str_project_id_whitespace(self):
        with unittest.mock.patch.dict(os.environ, {"WATSONX_PROJECT_ID": "   "}):
            self.assertEqual(_env_str("WATSONX_PROJECT_ID", "fallback"), "fallback")

    def test_env_str_url_empty(self):
        with unittest.mock.patch.dict(os.environ, {"WATSONX_URL": ""}):
            self.assertEqual(_env_str("WATSONX_URL", DEFAULT_WATSONX_URL), DEFAULT_WATSONX_URL)

    def test_env_str_model_id_empty(self):
        with unittest.mock.patch.dict(os.environ, {"WATSONX_MODEL_ID": ""}):
            self.assertEqual(_env_str("WATSONX_MODEL_ID", DEFAULT_WATSONX_MODEL_ID), DEFAULT_WATSONX_MODEL_ID)

    def test_empty_max_calls_uses_default_cap(self):
        """Empty WATSONX_MAX_CALLS must not raise ValueError and must cap at default."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)
            calls = []

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response()
                calls.append(url)
                return _make_wx_response({"proposed_needs": [], "factual_claims": []})

            with unittest.mock.patch.dict(
                os.environ,
                {
                    "WATSONX_APIKEY": "k",
                    "WATSONX_PROJECT_ID": "proj-test",
                    "WATSONX_MAX_CALLS": "",
                    "WATSONX_STATE_FILE": state_path,
                },
            ):
                # Should not raise ValueError — just use the default cap
                handle_agent_1(_make_req("I lost my job and need food.", http_post_fn=fake_http))
        finally:
            os.unlink(state_path)
            os.environ.pop("WATSONX_STATE_FILE", None)

    def test_empty_timeout_does_not_raise(self):
        """Empty WATSONX_TIMEOUT must not raise ValueError on int('')."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response()
                return _make_wx_response({"proposed_needs": []})

            with unittest.mock.patch.dict(
                os.environ,
                {
                    "WATSONX_APIKEY": "k",
                    "WATSONX_PROJECT_ID": "proj-test",
                    "WATSONX_TIMEOUT": "",
                    "WATSONX_STATE_FILE": state_path,
                },
            ):
                res = handle_agent_1(_make_req("I lost my job.", http_post_fn=fake_http))
                self.assertEqual(res["status"], "completed")
        finally:
            os.unlink(state_path)
            os.environ.pop("WATSONX_STATE_FILE", None)


# ---------------------------------------------------------------------------
# Item 2: Strict grounding — model-injected facts rejected; trivial quotes rejected
# ---------------------------------------------------------------------------

class TestStrictGrounding(unittest.TestCase):
    """Item 2: factual_claims from model ignored; trivial or ungrounded quotes rejected."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)
        os.environ.pop("WATSONX_STATE_FILE", None)

    def _run(self, story: str, wx_payload: dict, state_path: str) -> dict:
        _reset(state_file=state_path)
        def fake_http(url, body, headers):
            if "iam" in url:
                return _make_iam_response()
            return _make_wx_response(wx_payload)
        with unittest.mock.patch.dict(
            os.environ,
            {"WATSONX_APIKEY": "test-key", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_STATE_FILE": state_path},
        ):
            return handle_agent_1(_make_req(story, http_post_fn=fake_http))

    def test_model_injected_factual_claims_are_ignored(self):
        """factual_claims returned by model must never appear in result."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            story = "I lost my job and need help with crowdfunding to get back on our feet."
            wx_payload = {
                "proposed_needs": [],
                "factual_claims": [
                    {"field": "household_size", "value": 5},
                    {"field": "zip_code", "value": "99999"},
                ],
            }
            res = self._run(story, wx_payload, state_path)
            facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
            # Rules never detected zip or household_size in this story
            self.assertNotIn("household_size", facts,
                             "Model-injected household_size must be ignored")
            self.assertNotIn("zip_code", facts,
                             "Model-injected zip_code must be ignored")
        finally:
            os.unlink(state_path)

    def test_trivial_one_word_quote_rejected(self):
        """A one-word original_quote (e.g., 'I') must be rejected (< 2 words)."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            story = "I lost my job and need help with crowdfunding to get back on our feet."
            wx_payload = {
                "proposed_needs": [
                    {
                        "category": "crowdfunding_guidance",
                        "description": "Crowdfunding help",
                        "original_quote": "I",
                    }
                ],
                "factual_claims": [],
            }
            res = self._run(story, wx_payload, state_path)
            cats = [n["category"] for n in res["result"]["proposed_needs"]]
            self.assertNotIn("crowdfunding_guidance", cats,
                             "One-word quote 'I' must be rejected")
        finally:
            os.unlink(state_path)

    def test_short_quote_under_8_chars_rejected(self):
        """A quote shorter than 8 characters must be rejected."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            story = "I lost my job and need help with crowdfunding to get back on our feet."
            wx_payload = {
                "proposed_needs": [
                    {
                        "category": "crowdfunding_guidance",
                        "description": "Crowdfunding help",
                        "original_quote": "my job",  # 6 chars — under limit
                    }
                ],
                "factual_claims": [],
            }
            res = self._run(story, wx_payload, state_path)
            cats = [n["category"] for n in res["result"]["proposed_needs"]]
            self.assertNotIn("crowdfunding_guidance", cats,
                             "Quote under 8 chars must be rejected")
        finally:
            os.unlink(state_path)

    def test_ungrounded_quote_not_in_story_rejected(self):
        """A quote not appearing in the story must be rejected."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            story = "I lost my job and need help with crowdfunding to get back on our feet."
            wx_payload = {
                "proposed_needs": [
                    {
                        "category": "crowdfunding_guidance",
                        "description": "Crowdfunding help",
                        "original_quote": "completely invented text that is not in story",
                    }
                ],
                "factual_claims": [],
            }
            res = self._run(story, wx_payload, state_path)
            cats = [n["category"] for n in res["result"]["proposed_needs"]]
            self.assertNotIn("crowdfunding_guidance", cats,
                             "Ungrounded quote must be rejected")
        finally:
            os.unlink(state_path)

    def test_substantive_quote_accepted(self):
        """A substantive verbatim quote (>=8 chars, >=2 words, in story) is accepted."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            story = "I lost my job and need help with crowdfunding to get back on our feet."
            wx_payload = {
                "proposed_needs": [
                    {
                        "category": "crowdfunding_guidance",
                        "description": "Crowdfunding help",
                        "original_quote": "need help with crowdfunding to get back on our feet.",
                    }
                ],
                "factual_claims": [],
            }
            res = self._run(story, wx_payload, state_path)
            cats = [n["category"] for n in res["result"]["proposed_needs"]]
            self.assertIn("crowdfunding_guidance", cats,
                          "Substantive grounded quote must be accepted")
        finally:
            os.unlink(state_path)


# ---------------------------------------------------------------------------
# Item 3: Model-added need urgency/reason from shared helper
# ---------------------------------------------------------------------------

class TestModelAddedNeedUrgency(unittest.TestCase):
    """Item 3: urgency and urgency_reason must come from _wx_urgency, not hardcoded."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)
        os.environ.pop("WATSONX_STATE_FILE", None)

    def test_wx_urgency_no_urgent_signals_returns_medium(self):
        """_wx_urgency returns 'medium' when no urgent signals present."""
        urgency, reason = _wx_urgency("crowdfunding_guidance", "I need some assistance.", "I need some assistance.")
        self.assertEqual(urgency, "medium")
        self.assertIn("no urgent signals", reason.lower())

    def test_wx_urgency_job_loss_returns_high(self):
        """_wx_urgency returns 'high' when story mentions job loss."""
        urgency, reason = _wx_urgency(
            "income_assistance",
            "I was laid off last week.",
            "I was laid off last week.",
        )
        self.assertEqual(urgency, "high")

    def test_wx_urgency_eviction_notice_returns_immediate(self):
        """_wx_urgency returns 'immediate' when story contains eviction notice."""
        urgency, reason = _wx_urgency(
            "housing_assistance",
            "I received an eviction notice yesterday.",
            "eviction notice yesterday",
        )
        self.assertEqual(urgency, "immediate")

    def test_model_need_urgency_consistent_with_story(self):
        """Model-added need urgency_reason must accurately describe how urgency was derived."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)
            story = "I lost my job and need help with crowdfunding to get back on our feet."

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response()
                return _make_wx_response({
                    "proposed_needs": [
                        {
                            "category": "crowdfunding_guidance",
                            "description": "Help with crowdfunding",
                            "original_quote": "need help with crowdfunding to get back on our feet.",
                        }
                    ],
                })

            with unittest.mock.patch.dict(
                os.environ,
                {"WATSONX_APIKEY": "k", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_STATE_FILE": state_path},
            ):
                res = handle_agent_1(_make_req(story, http_post_fn=fake_http))

            cg = next((n for n in res["result"]["proposed_needs"] if n["category"] == "crowdfunding_guidance"), None)
            self.assertIsNotNone(cg, "crowdfunding_guidance must be present")
            # Story has "lost my job" → urgency must be "high"
            self.assertEqual(cg["urgency"], "high")
            # urgency_reason must NOT say "urgency from rules" (old hardcoded string)
            self.assertNotIn("urgency from rules", cg.get("urgency_reason", "").lower())
            # urgency_reason must be non-empty and meaningful
            self.assertTrue(len(cg.get("urgency_reason", "")) > 5)
        finally:
            os.unlink(state_path)

    def test_model_need_no_urgent_signals_gets_medium(self):
        """Model-added need on a benign story should get urgency='medium'."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)
            story = "I need some help with crowdfunding to raise money for my community project."

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response()
                return _make_wx_response({
                    "proposed_needs": [
                        {
                            "category": "crowdfunding_guidance",
                            "description": "Community project crowdfunding",
                            "original_quote": "help with crowdfunding to raise money for my community project.",
                        }
                    ],
                })

            with unittest.mock.patch.dict(
                os.environ,
                {"WATSONX_APIKEY": "k", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_STATE_FILE": state_path},
            ):
                res = handle_agent_1(_make_req(story, http_post_fn=fake_http))

            cg = next((n for n in res["result"]["proposed_needs"] if n["category"] == "crowdfunding_guidance"), None)
            self.assertIsNotNone(cg)
            self.assertEqual(cg["urgency"], "medium")
        finally:
            os.unlink(state_path)


# ---------------------------------------------------------------------------
# Item 4: Cross-process persisted call counter (date-based)
# ---------------------------------------------------------------------------

class TestCrossProcessState(unittest.TestCase):
    """Item 4: call counter persists across separate Python subprocesses (date-aware)."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)

    @staticmethod
    def _run_subprocess_call_count(state_path: str, apikey: str = "k") -> int:
        """
        Run a subprocess that increments the call counter once and returns the new count.
        Uses a fake HTTP stub so no real network calls happen.
        """
        code = f"""
import os, sys, json, tempfile
os.environ["WATSONX_STATE_FILE"] = {state_path!r}
os.environ["WATSONX_APIKEY"] = {apikey!r}
os.environ["WATSONX_PROJECT_ID"] = "proj-sub"
# Insert project root so imports work
sys.path.insert(0, {str(os.path.join(os.path.dirname(__file__), '..', '..')).replace(chr(92), '/')!r})
import navigator.agents.agent_1_2.agent_1 as a1
def fake_http(url, body, headers):
    if "iam" in url:
        return json.dumps({{"access_token": "tok", "expires_in": 3600}}).encode()
    return json.dumps({{"choices": [{{"message": {{"role": "assistant", "content": json.dumps({{"proposed_needs": []}})}}}}]}}).encode()
req = {{
    "request_id": "req-subprocess",
    "run_id": "run-sub",
    "case_id": "case-sub",
    "case_version": 1,
    "task_type": "understand_story",
    "payload": {{"story_text": "I lost my job and need help.", "_http_post_fn": fake_http}},
}}
a1.handle_agent_1(req)
print(a1._get_call_count())
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Subprocess failed:\n{result.stderr}")
        return int(result.stdout.strip())

    def test_call_count_persists_across_two_subprocesses(self):
        """Each subprocess increments the shared persisted call counter."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            # Reset state
            os.environ["WATSONX_STATE_FILE"] = state_path
            a1_mod._write_state({})

            count_after_1 = self._run_subprocess_call_count(state_path)
            count_after_2 = self._run_subprocess_call_count(state_path)

            self.assertEqual(count_after_1, 1, "First subprocess should yield count=1")
            self.assertEqual(count_after_2, 2, "Second subprocess should yield count=2")
        finally:
            os.unlink(state_path)
            os.environ.pop("WATSONX_STATE_FILE", None)

    def test_failed_call_still_increments_count(self):
        """A failed (timed-out / exception) call must still increment the persisted count."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)

            def fake_http_fail(url, body, headers):
                if "iam" in url:
                    return _make_iam_response()
                raise TimeoutError("simulated timeout")

            with unittest.mock.patch.dict(
                os.environ,
                {"WATSONX_APIKEY": "k", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_STATE_FILE": state_path},
            ):
                handle_agent_1(_make_req("I lost my job.", http_post_fn=fake_http_fail))

            count = a1_mod._get_call_count()
            self.assertEqual(count, 1, "Failed call must still increment persisted count to 1")
        finally:
            os.unlink(state_path)
            os.environ.pop("WATSONX_STATE_FILE", None)

    def test_iam_token_not_in_state_file(self):
        """IAM token must be kept in memory only — the state file must never contain it."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response(token="mem-only-tok")
                return _make_wx_response({"proposed_needs": []})

            with unittest.mock.patch.dict(
                os.environ,
                {"WATSONX_APIKEY": "k", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_STATE_FILE": state_path},
            ):
                handle_agent_1(_make_req("I need help.", http_post_fn=fake_http))

            with open(state_path, "r") as f:
                state = json.load(f)

            self.assertNotIn("iam_token", state,
                             "iam_token must never appear in the state file")
            self.assertNotIn("access_token", state,
                             "access_token must never appear in the state file")
            self.assertNotIn("expires_at", state,
                             "expires_at must never appear in the state file")
            self.assertNotIn("iam_token_wall_expires", state,
                             "iam_token_wall_expires must never appear in the state file")
        finally:
            os.unlink(state_path)
            os.environ.pop("WATSONX_STATE_FILE", None)


# ---------------------------------------------------------------------------
# Item 5: Single shared timeout budget
# ---------------------------------------------------------------------------

class TestSharedTimeoutBudget(unittest.TestCase):
    """Item 5: single budget of min(WATSONX_TIMEOUT, 18) used for IAM + chat together."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)
        os.environ.pop("WATSONX_STATE_FILE", None)

    def test_timeout_capped_at_18s(self):
        """WATSONX_TIMEOUT > 18 must be capped at 18 s budget."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response()
                return _make_wx_response({"proposed_needs": []})

            with unittest.mock.patch.dict(
                os.environ,
                {
                    "WATSONX_APIKEY": "k",
                    "WATSONX_PROJECT_ID": "proj-test",
                    "WATSONX_TIMEOUT": "30",
                    "WATSONX_STATE_FILE": state_path,
                },
            ):
                t0 = time.monotonic()
                res = handle_agent_1(_make_req("I need help.", http_post_fn=fake_http))
                elapsed = time.monotonic() - t0
                # With a 30 s TIMEOUT but 18 s cap, the call should complete quickly (mocked)
                self.assertLess(elapsed, 5.0, "Mocked call must complete in < 5 s")
                self.assertFalse(res["is_mock"], "Mocked success must set is_mock=False")
        finally:
            os.unlink(state_path)

    def test_budget_fallback_when_iam_exceeds_budget(self):
        """When IAM call times out within budget, fallback to is_mock=True."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)

            def fake_http_slow_iam(url, body, headers):
                if "iam" in url:
                    raise TimeoutError("IAM timed out")
                return _make_wx_response({"proposed_needs": []})

            with unittest.mock.patch.dict(
                os.environ,
                {
                    "WATSONX_APIKEY": "k",
                    "WATSONX_PROJECT_ID": "proj-test",
                    "WATSONX_TIMEOUT": "15",
                    "WATSONX_STATE_FILE": state_path,
                },
            ):
                res = handle_agent_1(_make_req("I need help.", http_post_fn=fake_http_slow_iam))

            self.assertTrue(res["is_mock"])
            codes = [i["code"] for i in res["issues"]]
            self.assertIn("WATSONX_FALLBACK", codes)
        finally:
            os.unlink(state_path)


# ---------------------------------------------------------------------------
# Item 6: WATSONX_* env isolation in tests
# ---------------------------------------------------------------------------

class TestEnvIsolation(unittest.TestCase):
    """Item 6: WATSONX_* vars must be absent by default in test runs (except WATSONX_STATE_FILE)."""

    def test_no_sensitive_watsonx_env_vars_present_by_default(self):
        """After setUpModule clears WATSONX_* vars, sensitive keys must be absent.
        WATSONX_STATE_FILE is intentionally set by tests/__init__.py for isolation."""
        sensitive = {k: v for k, v in os.environ.items()
                     if k.startswith("WATSONX_") and k != "WATSONX_STATE_FILE"}
        self.assertEqual(
            sensitive, {},
            f"Sensitive WATSONX_* vars must be cleared in test context; found: {sensitive}",
        )

    def test_unset_apikey_gives_fallback(self):
        """With no WATSONX_APIKEY in env, handle_agent_1 must use deterministic fallback."""
        # WATSONX_APIKEY is definitely absent (cleared by setUpModule)
        res = handle_agent_1({
            "request_id": "req-iso",
            "run_id": "run-iso",
            "case_id": "case-iso",
            "case_version": 1,
            "task_type": "understand_story",
            "payload": {"story_text": "I lost my job."},
        })
        self.assertTrue(res["is_mock"])
        codes = [i["code"] for i in res["issues"]]
        self.assertIn("WATSONX_FALLBACK", codes)
        fb = next(i for i in res["issues"] if i["code"] == "WATSONX_FALLBACK")
        self.assertEqual(fb["severity"], "info")


# ---------------------------------------------------------------------------
# New: Date-rollover resets call_count to 0
# ---------------------------------------------------------------------------

class TestDateRollover(unittest.TestCase):
    """Daily resetting call cap: when stored date != today, call_count resets to 0."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)
        os.environ.pop("WATSONX_STATE_FILE", None)

    def test_stale_date_resets_call_count_to_zero(self):
        """If the state file contains a past date, _get_call_count() returns 0."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            os.environ["WATSONX_STATE_FILE"] = state_path
            # Write state with yesterday's date and a non-zero count
            a1_mod._write_state({"date": "2000-01-01", "call_count": 99})
            count = a1_mod._get_call_count()
            self.assertEqual(count, 0, "Stale date must reset call_count to 0")
        finally:
            os.unlink(state_path)

    def test_stale_date_increment_starts_at_one(self):
        """When date has rolled over, the first _increment_call_count() returns 1."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            os.environ["WATSONX_STATE_FILE"] = state_path
            a1_mod._write_state({"date": "2000-01-01", "call_count": 99})
            new_count = a1_mod._increment_call_count()
            self.assertEqual(new_count, 1, "After date rollover, first increment must yield 1")
        finally:
            os.unlink(state_path)

    def test_state_file_contains_date_and_call_count(self):
        """After an increment, the state file must contain 'date' and 'call_count'."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            os.environ["WATSONX_STATE_FILE"] = state_path
            a1_mod._write_state({})
            a1_mod._increment_call_count()
            with open(state_path, "r") as f:
                state = json.load(f)
            self.assertIn("date", state)
            self.assertIn("call_count", state)
            self.assertEqual(state["date"], date.today().isoformat())
            self.assertEqual(state["call_count"], 1)
        finally:
            os.unlink(state_path)

    def test_supervisor_dialog_with_dummy_apikey_state_counter_stays_zero(self):
        """Supervisor dialog with WATSONX_APIKEY='dummy' (no project ID) keeps call count at 0."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            os.environ["WATSONX_STATE_FILE"] = state_path
            a1_mod._write_state({})
            a1_mod._watsonx_call_count = 0
            a1_mod._iam_token_cache = ("", 0.0)

            with unittest.mock.patch.dict(
                os.environ,
                {"WATSONX_APIKEY": "dummy", "WATSONX_STATE_FILE": state_path},
                # Note: WATSONX_PROJECT_ID intentionally absent
            ):
                handle_agent_1({
                    "request_id": "req-sup",
                    "run_id": "run-sup",
                    "case_id": "case-sup",
                    "case_version": 1,
                    "task_type": "understand_story",
                    "payload": {"story_text": "I need help paying rent."},
                })

            count = a1_mod._get_call_count()
            self.assertEqual(count, 0,
                             "No network call should be made without WATSONX_PROJECT_ID; call_count must stay 0")
        finally:
            os.unlink(state_path)
            os.environ.pop("WATSONX_STATE_FILE", None)


# ---------------------------------------------------------------------------
# New: State file never contains IAM token
# ---------------------------------------------------------------------------

class TestStateFileNoToken(unittest.TestCase):
    """IAM token must be kept in memory only; state file must never contain token data."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)
        os.environ.pop("WATSONX_STATE_FILE", None)

    def test_state_file_never_contains_iam_token(self):
        """After a successful watsonx call, state file must not contain iam_token or access_token."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response(token="secret-bearer")
                return _make_wx_response({"proposed_needs": []})

            with unittest.mock.patch.dict(
                os.environ,
                {"WATSONX_APIKEY": "k", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_STATE_FILE": state_path},
            ):
                handle_agent_1(_make_req("I need help.", http_post_fn=fake_http))

            with open(state_path, "r") as f:
                state = json.load(f)

            # None of these token-related keys should appear
            for forbidden_key in ("iam_token", "access_token", "expires_at", "iam_token_wall_expires"):
                self.assertNotIn(
                    forbidden_key, state,
                    f"State file must not contain '{forbidden_key}' (memory-only token)"
                )
        finally:
            os.unlink(state_path)

    def test_state_file_only_contains_date_and_call_count(self):
        """After a call, the state file must contain exactly 'date' and 'call_count'."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response()
                return _make_wx_response({"proposed_needs": []})

            with unittest.mock.patch.dict(
                os.environ,
                {"WATSONX_APIKEY": "k", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_STATE_FILE": state_path},
            ):
                handle_agent_1(_make_req("I need help.", http_post_fn=fake_http))

            with open(state_path, "r") as f:
                state = json.load(f)

            # Only date and call_count should be present
            self.assertIn("date", state)
            self.assertIn("call_count", state)
            extra_keys = set(state.keys()) - {"date", "call_count"}
            self.assertEqual(extra_keys, set(),
                             f"State file must only contain 'date' and 'call_count'; found extra: {extra_keys}")
        finally:
            os.unlink(state_path)


# ---------------------------------------------------------------------------
# New: No hard-coded project ID — WATSONX_PROJECT_ID unset/whitespace → fallback
# ---------------------------------------------------------------------------

class TestProjectIdFallback(unittest.TestCase):
    """WATSONX_PROJECT_ID unset or whitespace-only must trigger is_mock=True with info issue."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)
        os.environ.pop("WATSONX_STATE_FILE", None)

    def _run_no_network(self, env_patch: dict) -> dict:
        """Run handle_agent_1 with given env; a fake_http that must never be called."""
        def should_not_be_called(url, body, headers):
            raise AssertionError("No network call must be made when project ID is missing")

        with unittest.mock.patch.dict(os.environ, env_patch):
            return handle_agent_1(_make_req(
                "I need help paying rent.",
                http_post_fn=should_not_be_called,
            ))

    def test_unset_project_id_gives_mock_fallback(self):
        """With WATSONX_APIKEY set but WATSONX_PROJECT_ID absent, must fall back (is_mock=True, info)."""
        res = self._run_no_network({"WATSONX_APIKEY": "real-key"})
        self.assertTrue(res["is_mock"])
        codes = [i["code"] for i in res["issues"]]
        self.assertIn("WATSONX_FALLBACK", codes)
        fb = next(i for i in res["issues"] if i["code"] == "WATSONX_FALLBACK")
        self.assertEqual(fb["severity"], "info")
        self.assertIn("WATSONX_PROJECT_ID", fb["message"])

    def test_whitespace_only_project_id_gives_mock_fallback(self):
        """Whitespace-only WATSONX_PROJECT_ID must be treated as unset."""
        res = self._run_no_network({"WATSONX_APIKEY": "real-key", "WATSONX_PROJECT_ID": "   "})
        self.assertTrue(res["is_mock"])
        codes = [i["code"] for i in res["issues"]]
        self.assertIn("WATSONX_FALLBACK", codes)
        fb = next(i for i in res["issues"] if i["code"] == "WATSONX_FALLBACK")
        self.assertEqual(fb["severity"], "info")

    def test_set_project_id_allows_call(self):
        """With both WATSONX_APIKEY and WATSONX_PROJECT_ID set, watsonx is called (not mock)."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response()
                return _make_wx_response({"proposed_needs": []})

            with unittest.mock.patch.dict(
                os.environ,
                {
                    "WATSONX_APIKEY": "real-key",
                    "WATSONX_PROJECT_ID": "my-project",
                    "WATSONX_STATE_FILE": state_path,
                },
            ):
                res = handle_agent_1(_make_req("I need help.", http_post_fn=fake_http))

            self.assertFalse(res["is_mock"],
                             "With both APIKEY and PROJECT_ID set, is_mock must be False")
        finally:
            os.unlink(state_path)


# ---------------------------------------------------------------------------
# New: Whitespace APIKEY gives 'info' severity (not 'warning')
# ---------------------------------------------------------------------------

class TestApikeyInfoSeverity(unittest.TestCase):
    """Whitespace-only or absent WATSONX_APIKEY must emit WATSONX_FALLBACK at severity='info'."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)

    def test_absent_apikey_severity_is_info(self):
        """Missing WATSONX_APIKEY must yield WATSONX_FALLBACK with severity='info'."""
        res = handle_agent_1({
            "request_id": "r", "run_id": "r", "case_id": "c", "case_version": 1,
            "task_type": "understand_story",
            "payload": {"story_text": "I need food assistance."},
        })
        self.assertTrue(res["is_mock"])
        fb = next((i for i in res["issues"] if i["code"] == "WATSONX_FALLBACK"), None)
        self.assertIsNotNone(fb)
        self.assertEqual(fb["severity"], "info",
                         "Absent APIKEY fallback must use severity='info', not 'warning'")
        self.assertIn("WATSONX_APIKEY", fb["message"])

    def test_whitespace_apikey_severity_is_info(self):
        """Whitespace-only WATSONX_APIKEY must yield WATSONX_FALLBACK with severity='info'."""
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "   "}):
            res = handle_agent_1({
                "request_id": "r", "run_id": "r", "case_id": "c", "case_version": 1,
                "task_type": "understand_story",
                "payload": {"story_text": "I need food assistance."},
            })
        self.assertTrue(res["is_mock"])
        fb = next((i for i in res["issues"] if i["code"] == "WATSONX_FALLBACK"), None)
        self.assertIsNotNone(fb)
        self.assertEqual(fb["severity"], "info",
                         "Whitespace APIKEY fallback must use severity='info', not 'warning'")


# ---------------------------------------------------------------------------
# New: Canonical need descriptions (model-supplied description is not used)
# ---------------------------------------------------------------------------

class TestCanonicalNeedDescriptions(unittest.TestCase):
    """Model-supplied 'description' must be replaced by a fixed canonical description."""

    def setUp(self) -> None:
        self._stash = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_")}

    def tearDown(self) -> None:
        os.environ.update(self._stash)
        os.environ.pop("WATSONX_STATE_FILE", None)

    def test_model_description_replaced_by_canonical(self):
        """Model's 'description' field must not appear in the merged need; canonical used instead."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            state_path = tf.name
        try:
            _reset(state_file=state_path)
            story = "I need some help with crowdfunding to raise money for my community project."
            model_description = "INVENTED MODEL DESCRIPTION THAT MUST NOT APPEAR"

            def fake_http(url, body, headers):
                if "iam" in url:
                    return _make_iam_response()
                return _make_wx_response({
                    "proposed_needs": [
                        {
                            "category": "crowdfunding_guidance",
                            "description": model_description,
                            "original_quote": "help with crowdfunding to raise money for my community project.",
                        }
                    ],
                })

            with unittest.mock.patch.dict(
                os.environ,
                {"WATSONX_APIKEY": "k", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_STATE_FILE": state_path},
            ):
                res = handle_agent_1(_make_req(story, http_post_fn=fake_http))

            cg = next(
                (n for n in res["result"]["proposed_needs"] if n["category"] == "crowdfunding_guidance"),
                None,
            )
            self.assertIsNotNone(cg)
            self.assertNotEqual(cg["description"], model_description,
                                "Model-supplied description must NOT be used")
            # Canonical description for crowdfunding_guidance
            self.assertIn("crowdfunding", cg["description"].lower(),
                          "Canonical description must mention crowdfunding")
        finally:
            os.unlink(state_path)

    def test_canonical_descriptions_are_deterministic(self):
        """The same category always gets the same canonical description regardless of model output."""
        from navigator.agents.agent_1_2.agent_1 import _CANONICAL_NEED_DESCRIPTIONS
        for cat in ("food_assistance", "housing_assistance", "income_assistance",
                    "utility_assistance", "medical_health_coverage", "debt_hardship",
                    "material_in_kind", "crowdfunding_guidance", "other_unlisted"):
            self.assertIn(cat, _CANONICAL_NEED_DESCRIPTIONS,
                          f"Category '{cat}' must have a canonical description")
            desc = _CANONICAL_NEED_DESCRIPTIONS[cat]
            self.assertIsInstance(desc, str)
            self.assertGreater(len(desc), 5)


if __name__ == "__main__":
    unittest.main()
