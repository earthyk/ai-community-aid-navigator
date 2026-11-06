"""
PR #2 audit regression tests (A6-01, A6-02, A6-03, A6-04,
A7-01, A7-02, A7-03, A10-02, C-OD2).

One test per audit item.  All tests are self-contained (no fixtures loaded
from disk) so they run independently.

Run:
    python3 -m unittest tests/agent_6_7_8_10/test_pr2_regression.py
    python3 -m unittest discover -s tests -t .
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from navigator.agents.agent_6_7_8_10.agent_6_7_8_10 import handle, TASK_TYPES

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_BASE = {
    "request_id": "req_pr2_test",
    "run_id": "run-pr2",
    "case_id": "case-pr2",
    "case_version": 1,
    "schema_version": "1.0",
    "correlation_id": "corr-pr2",
    "allowed_case_facts": [],
    "upstream_result_refs": [],
}


def _req(role, payload):
    r = dict(_BASE)
    r["role_id"] = role
    r["task_type"] = TASK_TYPES[role]
    r["payload"] = payload
    return r


def _need(need_id, category="food_assistance", subcategory="food_pantry",
          urgency="high"):
    return {
        "need_id": need_id,
        "category": category,
        "subcategory": subcategory,
        "description": need_id,
        "original_quote": need_id,
        "confirmation_status": "confirmed",
        "user_reported": True,
        "urgency": urgency,
        "urgency_reason": "test",
        "user_priority": None,
    }


def _match(program_id, need_ids, subcategory="food_pantry"):
    return {
        "program_id": program_id,
        "need_ids": list(need_ids),
        "match_status": "supported_match",
        "matched_criteria": [],
        "missing_case_facts": [],
        "mismatch_criteria": [],
        "evidence_refs": [],
        "subcategory": subcategory,
    }


def _open_avail(program_id):
    return {"program_id": program_id, "availability": "confirmed_open",
            "evidence_refs": []}


def _run6(needs, matches, checked_claims=None, program_availability=None,
          evidence_records=None, timing=None):
    payload = {
        "needs": needs,
        "matches": matches,
        "checked_claims": checked_claims or [],
        "program_availability": program_availability or [
            _open_avail(m["program_id"]) for m in matches],
        "evidence_records": evidence_records or [],
        "timing": timing or [],
    }
    return handle(_req("agent_6", payload))["result"]["proposed_actions"]


def _run7(stage_result, needs, evidence_records=None):
    payload = {
        "stage": "verification",
        "stage_result": stage_result,
        "needs": needs,
    }
    if evidence_records is not None:
        payload["evidence_records"] = evidence_records
    return handle(_req("agent_7", payload))["result"]["findings"]


def _run10(plan, needs, matches, checked_claims=None, evidence_records=None,
           availability=None):
    payload = {
        "plan": plan,
        "needs": needs,
        "matches": matches,
        "checked_claims": checked_claims or [],
        "availability": availability or {},
        "evidence_records": evidence_records or [],
    }
    return handle(_req("agent_10", payload))["result"]


# ---------------------------------------------------------------------------
# A6-01: Multiple needs – one resource serves several need_ids
# ---------------------------------------------------------------------------

class TestA601MultipleNeeds(unittest.TestCase):
    """A resource serving need_A and need_B must not leave either in coverage_gaps,
    regardless of the order in which need_ids appear in the match."""

    def _run(self, need_ids_order):
        needs = [
            _need("need_A", category="food_assistance", subcategory="food_pantry"),
            _need("need_B", category="food_assistance", subcategory="calfresh_benefits"),
        ]
        matches = [_match("PROG-MULTI", need_ids_order, subcategory="food_pantry")]
        # The action need_id is always the first in need_ids_order, but coverage
        # must include ALL need_ids.
        acts = _run6(needs, matches)
        covered = {nid for a in acts for nid in a.get("need_ids", [a["need_id"]])}
        gaps_from_issues = None  # agent_6 issues are separate; check covered set
        return covered

    def test_forward_order_covers_both_needs(self):
        covered = self._run(["need_A", "need_B"])
        self.assertIn("need_A", covered)
        self.assertIn("need_B", covered)

    def test_reversed_order_covers_both_needs(self):
        covered = self._run(["need_B", "need_A"])
        self.assertIn("need_A", covered)
        self.assertIn("need_B", covered)

    def test_same_coverage_regardless_of_order(self):
        covered_fwd = self._run(["need_A", "need_B"])
        covered_rev = self._run(["need_B", "need_A"])
        self.assertEqual(covered_fwd, covered_rev,
                         "Coverage must not change when need_ids order is reversed")


# ---------------------------------------------------------------------------
# A6-02: Conflicting deadlines
# ---------------------------------------------------------------------------

class TestA602ConflictingDeadlines(unittest.TestCase):
    """Two different verified deadlines or claim_value=None must produce a
    'confirm' action with both evidence refs and no empty () or None in text."""

    def _claims_two_verified(self, pid):
        return [
            {"program_id": pid, "field_path": "deadlines[0]",
             "claim_value": "2026-11-04",
             "verification_status": "verified",
             "evidence_refs": ["EV-A1"], "checked_at": "2026-10-21T15:00:00Z",
             "issue": None},
            {"program_id": pid, "field_path": "deadlines[0]",
             "claim_value": "2026-12-10",
             "verification_status": "verified",
             "evidence_refs": ["EV-A2"], "checked_at": "2026-10-21T15:00:00Z",
             "issue": None},
        ]

    def _claims_none_value(self, pid):
        return [
            {"program_id": pid, "field_path": "deadlines[0]",
             "claim_value": None,
             "verification_status": "verified",
             "evidence_refs": ["EV-B1"], "checked_at": "2026-10-21T15:00:00Z",
             "issue": None},
        ]

    def _run_with_claims(self, claims):
        pid = "PROG-DL"
        needs = [_need("need_001", category="housing_assistance",
                        subcategory="rental_assistance")]
        matches = [_match(pid, ["need_001"], subcategory="rental_assistance")]
        ev_records = [{"evidence_id": r, "program_id": pid,
                       "field_path": "deadlines[0]", "claim_value": "x",
                       "source_url": "", "checked_at": "2026-10-21T15:00:00Z",
                       "verification_status": "verified"}
                      for r in ["EV-A1", "EV-A2", "EV-B1"]]
        acts = _run6(needs, matches, checked_claims=claims,
                     evidence_records=ev_records)
        return acts

    def test_two_verified_deadlines_produce_confirm_action(self):
        """Two verified deadlines must produce a 'confirm deadline' action."""
        acts = self._run_with_claims(self._claims_two_verified("PROG-DL"))
        confirm = next((a for a in acts
                        if "Official sources disagree" in a["rationale"]
                        or "confirm" in a["rationale"].lower()), None)
        self.assertIsNotNone(confirm,
                             "Expected a confirm-deadline action for two verified deadlines")

    def test_two_verified_deadlines_no_empty_parens_or_none(self):
        """The confirm action must not contain '()' or 'None' in user-visible text."""
        acts = self._run_with_claims(self._claims_two_verified("PROG-DL"))
        for a in acts:
            for field in ("rationale", "uncertainty_notes"):
                text = str(a.get(field, ""))
                self.assertNotIn("()", text,
                                 f"Empty () found in action field {field!r}: {text!r}")
                self.assertNotIn("None", text,
                                 f"'None' found in action field {field!r}: {text!r}")

    def test_claim_value_none_produces_confirm_action(self):
        """A verified claim with claim_value=None must produce a confirm action."""
        acts = self._run_with_claims(self._claims_none_value("PROG-DL"))
        confirm = next((a for a in acts
                        if "confirm" in a["rationale"].lower()
                        or "unknown" in a["rationale"].lower()), None)
        self.assertIsNotNone(confirm,
                             "Expected a confirm action when deadline claim_value is None")

    def test_claim_value_none_no_empty_parens_or_none(self):
        """The confirm action for a None-value claim must not show () or None."""
        acts = self._run_with_claims(self._claims_none_value("PROG-DL"))
        for a in acts:
            for field in ("rationale",):
                text = str(a.get(field, ""))
                self.assertNotIn("()", text,
                                 f"Empty () found in rationale: {text!r}")
                self.assertNotIn("None", text,
                                 f"'None' found in rationale: {text!r}")


# ---------------------------------------------------------------------------
# A6-03: Time-based ordering
# ---------------------------------------------------------------------------

class TestA603TimeBasedOrdering(unittest.TestCase):
    """With equal urgency, Nov 4 deadline sorts before Dec 10, regardless of
    input order."""

    def _run(self, matches_order):
        needs = [
            _need("need_A", category="housing_assistance",
                  subcategory="rental_assistance", urgency="high"),
            _need("need_B", category="housing_assistance",
                  subcategory="rental_assistance", urgency="high"),
        ]
        timing = [
            {"program_id": "PROG-NOV4", "need_id": "need_A",
             "official_deadline": "2026-11-04",
             "user_target_date": None,
             "estimated_processing_time": None},
            {"program_id": "PROG-DEC10", "need_id": "need_B",
             "official_deadline": "2026-12-10",
             "user_target_date": None,
             "estimated_processing_time": None},
        ]
        verified_claims = [
            {"program_id": "PROG-NOV4", "field_path": "deadlines[0]",
             "claim_value": "2026-11-04", "verification_status": "verified",
             "evidence_refs": ["EV-N4"], "checked_at": "2026-10-21T15:00:00Z",
             "issue": None},
            {"program_id": "PROG-DEC10", "field_path": "deadlines[0]",
             "claim_value": "2026-12-10", "verification_status": "verified",
             "evidence_refs": ["EV-D10"], "checked_at": "2026-10-21T15:00:00Z",
             "issue": None},
        ]
        avail = [_open_avail("PROG-NOV4"), _open_avail("PROG-DEC10")]
        ev = [{"evidence_id": r, "program_id": p,
               "field_path": "deadlines[0]", "claim_value": d,
               "source_url": "", "checked_at": "2026-10-21T15:00:00Z",
               "verification_status": "verified"}
              for (r, p, d) in [("EV-N4", "PROG-NOV4", "2026-11-04"),
                                 ("EV-D10", "PROG-DEC10", "2026-12-10")]]
        acts = _run6(needs, matches_order, checked_claims=verified_claims,
                     program_availability=avail, evidence_records=ev,
                     timing=timing)
        return acts

    def test_nov4_before_dec10_natural_order(self):
        matches = [
            _match("PROG-NOV4", ["need_A"], subcategory="rental_assistance"),
            _match("PROG-DEC10", ["need_B"], subcategory="rental_assistance"),
        ]
        acts = self._run(matches)
        pids = [a["program_id"] for a in acts if a["program_id"]]
        nov4_idx = pids.index("PROG-NOV4")
        dec10_idx = pids.index("PROG-DEC10")
        self.assertLess(nov4_idx, dec10_idx,
                        f"PROG-NOV4 must come before PROG-DEC10; got order {pids}")

    def test_nov4_before_dec10_reversed_input(self):
        """Nov 4 deadline sorts before Dec 10 even when matches are given reversed."""
        matches = [
            _match("PROG-DEC10", ["need_B"], subcategory="rental_assistance"),
            _match("PROG-NOV4", ["need_A"], subcategory="rental_assistance"),
        ]
        acts = self._run(matches)
        pids = [a["program_id"] for a in acts if a["program_id"]]
        nov4_idx = pids.index("PROG-NOV4")
        dec10_idx = pids.index("PROG-DEC10")
        self.assertLess(nov4_idx, dec10_idx,
                        f"Nov 4 deadline must sort before Dec 10 regardless of input order; got {pids}")


# ---------------------------------------------------------------------------
# A6-04: Unsupported urgency – no dates in, no urgency words out
# ---------------------------------------------------------------------------

class TestA604UnsupportedUrgency(unittest.TestCase):
    """If no deadline or target date is present, the rationale must not say
    'approaching', 'is close', or 'deadline' in a time-pressuring way."""

    _URGENCY_WORDS = ("approaching", "is close", "is near", "running out",
                      "before the deadline")

    def test_no_dates_means_no_urgency_wording(self):
        needs = [_need("need_001", category="housing_assistance",
                        subcategory="rental_assistance", urgency="high")]
        matches = [_match("PROG-RA", ["need_001"], subcategory="rental_assistance")]
        # No timing, no facts with dates, no deadline claims.
        acts = _run6(needs, matches, checked_claims=[], evidence_records=[],
                     timing=[])
        for a in acts:
            rationale = (a.get("rationale") or "").lower()
            for word in self._URGENCY_WORDS:
                self.assertNotIn(
                    word, rationale,
                    f"Urgency word {word!r} found in rationale without any date: "
                    f"{rationale!r}",
                )


# ---------------------------------------------------------------------------
# A7-01: Empty matches → every need flagged as uncovered
# ---------------------------------------------------------------------------

class TestA701EmptyMatches(unittest.TestCase):
    """With matches: [], every need must produce a Q8 finding."""

    def test_empty_matches_flags_all_needs_as_uncovered(self):
        needs = [
            _need("need_001"),
            _need("need_002"),
            _need("need_003"),
        ]
        stage_result = {"matches": [], "checked_claims": []}
        findings = _run7(stage_result, needs)
        q8_needs = {f["need_id"] for f in findings if f["rule_id"] == "Q8"}
        self.assertIn("need_001", q8_needs)
        self.assertIn("need_002", q8_needs)
        self.assertIn("need_003", q8_needs)


# ---------------------------------------------------------------------------
# A7-02: Every evidence_ref must exist in evidence_records; empty list ≠ pass
# ---------------------------------------------------------------------------

class TestA702EvidenceRefs(unittest.TestCase):
    """An empty evidence_records list must NOT pass a verified claim that cites
    an evidence_ref."""

    def test_empty_evidence_records_fails_verified_claim_with_ref(self):
        needs = [_need("need_001")]
        claims = [{
            "program_id": "PROG-X",
            "field_path": "contact[0]",
            "claim_value": "Call 555-0100",
            "verification_status": "verified",
            "evidence_refs": ["EV-DOES-NOT-EXIST"],
            "checked_at": "2026-10-21T15:00:00Z",
            "issue": None,
        }]
        matches = [_match("PROG-X", ["need_001"])]
        stage_result = {"matches": matches, "checked_claims": claims}
        # Pass an EMPTY evidence_records list (not absent — present but empty).
        findings = _run7(stage_result, needs, evidence_records=[])
        q1_rules = [f["rule_id"] for f in findings if f["rule_id"] == "Q1"]
        self.assertGreater(
            len(q1_rules), 0,
            "Q1 must fire when evidence_records is empty and a claim cites a ref",
        )


# ---------------------------------------------------------------------------
# A7-03: claim_value None + contradictory evidence → severity from SEVERITY table
# ---------------------------------------------------------------------------

class TestA703NoneValueConflict(unittest.TestCase):
    """A conflicting claim with claim_value=None must produce Q2 (not Q3).
    The severity must match the current table in the code (critical for
    deadline/contact/availability fields, warning for others)."""

    def test_none_value_conflict_on_deadline_gives_q2_critical(self):
        """Deadline field with conflicting + claim_value=None → Q2 critical."""
        needs = [_need("need_001")]
        claims = [{
            "program_id": "PROG-Y",
            "field_path": "deadlines[0]",
            "claim_value": None,
            "verification_status": "conflicting",
            "evidence_refs": ["EV-C1"],
            "checked_at": "2026-10-21T15:00:00Z",
            "issue": "Deadline not published on any source",
        }]
        matches = [_match("PROG-Y", ["need_001"])]
        stage_result = {"matches": matches, "checked_claims": claims}
        findings = _run7(stage_result, needs)
        non_info = [f for f in findings if f["severity"] != "info"]
        rule_ids = [f["rule_id"] for f in non_info]
        self.assertIn("Q2", rule_ids, f"Expected Q2 for None-value conflict; got {rule_ids}")
        self.assertNotIn("Q3", rule_ids, f"Q3 must not fire for None-value conflict")
        q2 = next(f for f in non_info if f["rule_id"] == "Q2")
        self.assertEqual(
            q2["severity"], "critical",
            f"Q2 on a deadline field must be critical per the SEVERITY table; got {q2['severity']}",
        )

    def test_none_value_conflict_on_non_critical_field_gives_q2_warning(self):
        """Non-critical field with conflicting + claim_value=None → Q2 warning."""
        needs = [_need("need_001")]
        claims = [{
            "program_id": "PROG-Z",
            "field_path": "income_limit[0]",
            "claim_value": None,
            "verification_status": "conflicting",
            "evidence_refs": ["EV-D1"],
            "checked_at": "2026-10-21T15:00:00Z",
            "issue": None,
        }]
        matches = [_match("PROG-Z", ["need_001"])]
        stage_result = {"matches": matches, "checked_claims": claims}
        findings = _run7(stage_result, needs)
        non_info = [f for f in findings if f["severity"] != "info"]
        rule_ids = [f["rule_id"] for f in non_info]
        self.assertIn("Q2", rule_ids, f"Expected Q2 for None-value conflict on non-critical field; got {rule_ids}")
        q2 = next(f for f in non_info if f["rule_id"] == "Q2")
        self.assertEqual(
            q2["severity"], "warning",
            f"Q2 on a non-critical field must be warning; got {q2['severity']}",
        )


# ---------------------------------------------------------------------------
# A10-02: False coverage – related_need_ids must match the original match's need_ids
# ---------------------------------------------------------------------------

class TestA1002FalseCoverage(unittest.TestCase):
    """A food card claiming need_housing in related_need_ids must flag V12."""

    def test_food_card_claiming_housing_need_fails(self):
        needs = [
            _need("need_food", category="food_assistance", subcategory="food_pantry"),
            _need("need_housing", category="housing_assistance",
                  subcategory="rental_assistance"),
        ]
        matches = [_match("PROG-FOOD", ["need_food"], subcategory="food_pantry")]
        # Card incorrectly claims need_housing (which the food program does not serve).
        cards = [{
            "card_id": "CARD-001",
            "program_id": "PROG-FOOD",
            "action_title": "Visit a food pantry",
            "reason": "Food help",
            "next_step": "Visit during open hours.",
            "priority_reason": "Food is needed.",
            "order_group": "parallel",
            "dependency_card_ids": [],
            "source_refs": [],
            "uncertainty_notes": [],
            "official_deadline": None,
            "user_target_date": None,
            "processing_estimate": None,
            "progress_status": "not_started",
            "related_need_ids": ["need_food", "need_housing"],  # need_housing is wrong
            "contacts": [],
        }]
        plan = {"action_cards": cards, "potential_options": [], "coverage_gaps": []}
        result = _run10(plan, needs, matches,
                        availability={"PROG-FOOD": "confirmed_open"})
        v12_flags = [f for f in result["flags"] if f["rule_id"] == "V12"]
        self.assertGreater(len(v12_flags), 0,
                           "V12 must fire when a card's related_need_ids includes "
                           "a need the program does not match")
        self.assertFalse(result["verdict"] == "PASS",
                         "Verdict must not be PASS when false coverage is present")


# ---------------------------------------------------------------------------
# C-OD2: Overdue rent + food need → housing action first
# ---------------------------------------------------------------------------

class TestCOD2OverdueRentFoodOrdering(unittest.TestCase):
    """Overdue rent (immediate urgency, housing) with a food need:
    housing action must come before food action."""

    def test_housing_before_food_with_overdue_rent(self):
        needs = [
            _need("need_housing", category="housing_assistance",
                  subcategory="rental_assistance", urgency="immediate"),
            _need("need_food", category="food_assistance",
                  subcategory="food_pantry", urgency="immediate"),
        ]
        matches = [
            _match("PROG-HOUSING", ["need_housing"],
                   subcategory="rental_assistance"),
            _match("PROG-FOOD", ["need_food"], subcategory="food_pantry"),
        ]
        avail = [_open_avail("PROG-HOUSING"), _open_avail("PROG-FOOD")]
        # Supply matches in food-first order to prove sorting overrides input order.
        acts = _run6(
            needs,
            [matches[1], matches[0]],  # food first in input
            program_availability=avail,
        )
        pids = [a["program_id"] for a in acts if a["program_id"]]
        housing_idx = pids.index("PROG-HOUSING")
        food_idx = pids.index("PROG-FOOD")
        self.assertLess(
            housing_idx, food_idx,
            f"Housing action must come before food when rent is overdue; got {pids}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
