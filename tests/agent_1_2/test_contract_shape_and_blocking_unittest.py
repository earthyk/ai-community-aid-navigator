"""
AI Community Aid Navigator — Contract Shape & 9-Blocking-Items Test Suite
Covers all 9 PR #6 blocking review items:
  1. proposed_needs contract shape (need_id, description, original_quote, user_reported,
     confirmation_status, urgency — never "priority").
  2. factual_claims contract shape (fact_id, field, value, confirmation_status, time_context).
  3. result top-level keys (narrative_summary, factual_claims, proposed_needs,
     safety_or_official_deadline_flags, triggering_events, ambiguity_flags).
  4. safety flags correct format ({type, quote, note} — not {type, reason, action_required}).
  5. Job loss emits employment_status fact + "job_loss" in triggering_events.
  6. Bereavement emits employment_status fact + "bereavement" in triggering_events.
  7. Urgency escalation: rent_due_date before ref_date → housing urgency="immediate".
  8. Eviction threat phrase → housing_assistance with urgency="immediate".
  9. Unemployment income ("I get $800 a month in unemployment") extracts income.
 10. Agent 2 Julia Requirement: missing income triggers question with can_skip=False.
 11. Agent 2 eviction clarification has can_skip=False.

Pure standard library. Zero external dependencies.
Run: python -m unittest discover -s tests -t .
"""
from datetime import date
import unittest
from navigator.agents.agent_1_2.agent_1 import handle_agent_1
from navigator.agents.agent_1_2.agent_2 import handle_agent_2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_story(story: str, ref_date: date = date(2026, 11, 4)) -> dict:
    """Run Agent 1 understand_story and return the full envelope."""
    return handle_agent_1(
        {
            "request_id": "req-block-test",
            "run_id": "run-block",
            "case_id": "case-block",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": story},
        },
        ref_date=ref_date,
    )


class TestContractShapeAndBlocking(unittest.TestCase):
    """9 blocking PR review items — all must pass for 100% gate."""

    # -------------------------------------------------------------------
    # BLOCKING ITEM 1 — proposed_needs contract shape §3.1
    # -------------------------------------------------------------------

    def test_block_1_proposed_needs_required_fields(self):
        """Every proposed_need must have all §3.1 required fields; 'priority' must never appear."""
        res = _run_story(
            "I was laid off last week. Rent of $1,200 is due November 15 and I need food. ZIP 95823."
        )
        self.assertEqual(res["status"], "completed")
        needs = res["result"]["proposed_needs"]
        self.assertGreater(len(needs), 0, "Expected at least one proposed need")

        required_fields = {"need_id", "category", "description", "original_quote",
                           "user_reported", "confirmation_status", "urgency"}
        for need in needs:
            missing = required_fields - set(need.keys())
            self.assertEqual(
                missing, set(),
                f"Need '{need.get('category')}' missing fields: {missing}"
            )
            # urgency must be one of the allowed values
            self.assertIn(
                need["urgency"],
                {"immediate", "high", "normal", "unknown"},
                f"Invalid urgency value '{need['urgency']}' in need '{need.get('category')}'"
            )
            # user_reported must be True
            self.assertIs(need["user_reported"], True,
                          f"user_reported must be True, got {need['user_reported']}")
            # confirmation_status must be "proposed"
            self.assertEqual(need["confirmation_status"], "proposed",
                             f"confirmation_status must be 'proposed', got {need['confirmation_status']}")
            # 'priority' must never appear (use 'urgency' instead)
            self.assertNotIn("priority", need,
                             f"Field 'priority' must not appear in proposed_needs (use 'urgency')")

    # -------------------------------------------------------------------
    # BLOCKING ITEM 2 — factual_claims contract shape §3.2
    # -------------------------------------------------------------------

    def test_block_2_factual_claims_required_fields(self):
        """Every factual_claim must have all §3.2 required fields: fact_id, field, value,
        confirmation_status, time_context."""
        res = _run_story(
            "I'm a single mom in Sacramento, ZIP 95823, with two kids, 6 and 9. "
            "I was laid off from my warehouse job. Rent of $1,450 is due on November 1."
        )
        self.assertEqual(res["status"], "completed")
        facts = res["result"]["factual_claims"]
        self.assertGreater(len(facts), 0, "Expected at least one factual claim")

        required_fields = {"fact_id", "field", "value", "confirmation_status"}
        for fact in facts:
            missing = required_fields - set(fact.keys())
            self.assertEqual(
                missing, set(),
                f"Fact '{fact.get('field')}' missing fields: {missing}"
            )
            # confirmation_status must be "proposed"
            self.assertEqual(
                fact["confirmation_status"], "proposed",
                f"Fact '{fact.get('field')}' has confirmation_status '{fact['confirmation_status']}'"
            )
            # fact_id must be non-empty string
            self.assertIsInstance(fact["fact_id"], str)
            self.assertGreater(len(fact["fact_id"]), 0)
            # time_context key must be present (may be None)
            self.assertIn("time_context", fact,
                          f"Fact '{fact.get('field')}' missing 'time_context' key")

    # -------------------------------------------------------------------
    # BLOCKING ITEM 3 — result top-level keys §4.1
    # -------------------------------------------------------------------

    def test_block_3_result_top_level_keys(self):
        """result must always contain all 6 required top-level keys."""
        res = _run_story("I need help paying rent in ZIP 95823.")
        self.assertEqual(res["status"], "completed")
        result = res["result"]

        required_top_keys = {
            "narrative_summary",
            "factual_claims",
            "proposed_needs",
            "safety_or_official_deadline_flags",
            "triggering_events",
            "ambiguity_flags",
        }
        missing = required_top_keys - set(result.keys())
        self.assertEqual(
            missing, set(),
            f"result is missing required top-level keys: {missing}"
        )
        # ambiguity_flags must be a list (may be empty)
        self.assertIsInstance(result["ambiguity_flags"], list)
        # triggering_events must be a list (may be empty)
        self.assertIsInstance(result["triggering_events"], list)
        # narrative_summary must be a non-empty string
        self.assertIsInstance(result["narrative_summary"], str)
        self.assertGreater(len(result["narrative_summary"]), 0)

    # -------------------------------------------------------------------
    # BLOCKING ITEM 4 — safety flag format §4.1 / §5.2 S9
    # -------------------------------------------------------------------

    def test_block_4_safety_flag_format_type_quote_note(self):
        """Safety flags must use {type, quote, note} — never {type, reason, action_required}."""
        res = _run_story("I can't go on like this anymore.")
        self.assertEqual(res["status"], "completed")
        flags = res["result"]["safety_or_official_deadline_flags"]
        self.assertGreater(len(flags), 0, "Expected at least one safety flag")

        flag = flags[0]
        self.assertEqual(flag.get("type"), "safety")
        # Required keys
        self.assertIn("quote", flag, "Safety flag must have 'quote' key")
        self.assertIn("note", flag, "Safety flag must have 'note' key")
        # Forbidden keys
        self.assertNotIn("reason", flag,
                         "Safety flag must NOT have 'reason' key (use 'note')")
        self.assertNotIn("action_required", flag,
                         "Safety flag must NOT have 'action_required' key (use 'note')")
        # quote must be a non-empty string containing the triggering text
        self.assertIsInstance(flag["quote"], str)
        self.assertGreater(len(flag["quote"]), 0)

    def test_block_4b_multiple_safety_phrases(self):
        """All safety phrase variants must produce {type, quote, note} flags."""
        phrases = [
            "I want to kill myself",
            "I don't want to be alive anymore",
            "everyone would be better off without me",
            "I'm ending it all tonight",
            "I have no reason to live",
            "I can't go on like this",
            "My husband hits me every night",
            "I'm afraid my boyfriend will hurt the kids",
        ]
        for phrase in phrases:
            res = _run_story(phrase)
            flags = res["result"].get("safety_or_official_deadline_flags", [])
            self.assertGreater(len(flags), 0, f"No safety flag for: {phrase!r}")
            flag = flags[0]
            self.assertIn("quote", flag, f"Missing 'quote' for: {phrase!r}")
            self.assertIn("note", flag, f"Missing 'note' for: {phrase!r}")
            self.assertNotIn("reason", flag, f"'reason' must not appear for: {phrase!r}")
            self.assertNotIn("action_required", flag, f"'action_required' must not appear for: {phrase!r}")

    # -------------------------------------------------------------------
    # BLOCKING ITEM 5 — Job loss: employment_status + triggering_events
    # -------------------------------------------------------------------

    def test_block_5_job_loss_emits_employment_status_and_triggering_event(self):
        """Job loss must emit employment_status in factual_claims and 'job_loss' in triggering_events."""
        stories = [
            "I was laid off from my warehouse job last Friday. ZIP 95823.",
            "I lost my job at the factory two days ago in 95814.",
            "I am unemployed and cannot pay rent. ZIP 95823.",
            "I got fired last week. Need help with food. ZIP 95823.",
        ]
        for story in stories:
            res = _run_story(story)
            self.assertEqual(res["status"], "completed", f"Failed for: {story!r}")

            # triggering_events must contain "job_loss"
            triggering = res["result"]["triggering_events"]
            self.assertIn(
                "job_loss", triggering,
                f"'job_loss' not in triggering_events for: {story!r}\ngot: {triggering}"
            )

            # factual_claims must contain employment_status
            facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
            self.assertIn(
                "employment_status", facts,
                f"'employment_status' missing from factual_claims for: {story!r}"
            )

    # -------------------------------------------------------------------
    # BLOCKING ITEM 6 — Bereavement: employment_status + triggering_events
    # -------------------------------------------------------------------

    def test_block_6_bereavement_emits_employment_status_and_triggering_event(self):
        """Bereavement must emit employment_status + 'bereavement' in triggering_events."""
        story = (
            "My husband passed away last week. He was our sole earner and I need "
            "survivor benefits in 95823."
        )
        res = _run_story(story)
        self.assertEqual(res["status"], "completed")

        triggering = res["result"]["triggering_events"]
        self.assertIn(
            "bereavement", triggering,
            f"'bereavement' not in triggering_events; got: {triggering}"
        )

        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertIn(
            "employment_status", facts,
            "employment_status must be in factual_claims for bereavement case"
        )

    # -------------------------------------------------------------------
    # BLOCKING ITEM 7 — Urgency escalation: rent overdue by date
    # -------------------------------------------------------------------

    def test_block_7_rent_overdue_by_date_escalates_to_immediate(self):
        """If rent_due_date is before ref_date, housing urgency must be 'immediate'
        with urgency_reason='Rent is overdue'."""
        # ref_date = Nov 4; rent due = Nov 1 → overdue
        res = _run_story(
            "Rent of $1,450 is due on November 1. I only have $50 left. ZIP 95823.",
            ref_date=date(2026, 11, 4),
        )
        self.assertEqual(res["status"], "completed")

        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("rent_due_date"), "2026-11-01",
                         "rent_due_date must be 2026-11-01")

        housing_needs = [
            n for n in res["result"]["proposed_needs"]
            if n.get("category") == "housing_assistance"
        ]
        self.assertGreater(len(housing_needs), 0, "Expected housing_assistance need")
        hn = housing_needs[0]
        self.assertEqual(
            hn["urgency"], "immediate",
            f"housing urgency must be 'immediate' when rent is overdue, got '{hn['urgency']}'"
        )
        self.assertEqual(
            hn.get("urgency_reason"), "Rent is overdue",
            f"urgency_reason must be 'Rent is overdue', got '{hn.get('urgency_reason')}'"
        )

    def test_block_7b_rent_not_yet_due_is_high_not_immediate(self):
        """Rent due in the future must NOT be immediate (just 'high')."""
        # ref_date = Oct 23; rent due = Nov 1 → not overdue
        res = _run_story(
            "Rent of $1,450 is due on November 1. ZIP 95823.",
            ref_date=date(2026, 10, 23),
        )
        housing_needs = [
            n for n in res["result"]["proposed_needs"]
            if n.get("category") == "housing_assistance"
        ]
        self.assertGreater(len(housing_needs), 0)
        hn = housing_needs[0]
        # Not yet overdue: urgency should be high (not immediate)
        self.assertNotEqual(
            hn["urgency"], "immediate",
            "Rent not yet due must not escalate to 'immediate'"
        )

    # -------------------------------------------------------------------
    # BLOCKING ITEM 8 — Eviction threat → housing_assistance immediate
    # -------------------------------------------------------------------

    def test_block_8_eviction_threat_generates_immediate_housing_need(self):
        """'Landlord said he will evict us' must generate housing_assistance with urgency=immediate."""
        stories = [
            "My landlord said he will evict us if we don't pay by Friday. ZIP 95823.",
            "The landlord is going to evict me next week. I have two kids. ZIP 95823.",
            "I am facing eviction and don't know what to do. ZIP 95823.",
        ]
        for story in stories:
            res = _run_story(story)
            self.assertEqual(res["status"], "completed", f"Failed for: {story!r}")

            housing_needs = [
                n for n in res["result"]["proposed_needs"]
                if n.get("category") == "housing_assistance"
            ]
            self.assertGreater(
                len(housing_needs), 0,
                f"No housing_assistance need for eviction threat: {story!r}"
            )
            self.assertEqual(
                housing_needs[0]["urgency"], "immediate",
                f"Eviction threat must set urgency='immediate' for: {story!r}"
            )

    # -------------------------------------------------------------------
    # BLOCKING ITEM 9 — Unemployment income extraction
    # -------------------------------------------------------------------

    def test_block_9_unemployment_income_extracted(self):
        """'I get $800 a month in unemployment' must extract household_gross_monthly_income=800."""
        stories_and_expected = [
            ("I get $800 a month in unemployment. ZIP 95823.", 800),
            ("I receive $1,200 a month from unemployment benefits. ZIP 95823.", 1200),
            ("I collect $650 per month in disability benefits. ZIP 95823.", 650),
        ]
        for story, expected in stories_and_expected:
            res = _run_story(story)
            self.assertEqual(res["status"], "completed", f"Failed for: {story!r}")

            facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
            self.assertIn(
                "household_gross_monthly_income", facts,
                f"household_gross_monthly_income missing for: {story!r}"
            )
            self.assertEqual(
                facts["household_gross_monthly_income"], expected,
                f"Expected {expected}, got {facts['household_gross_monthly_income']} for: {story!r}"
            )

    # -------------------------------------------------------------------
    # BLOCKING ITEM 10 — Agent 2 Julia Requirement: missing income question
    # with can_skip=False, regardless of candidate_requirements
    # -------------------------------------------------------------------

    def test_block_10_agent2_missing_income_asks_with_can_skip_false_no_candidates(self):
        """Agent 2 must ask income question (can_skip=False) when income unknown,
        even with empty candidate_requirements."""
        req = {
            "request_id": "req-julia-1",
            "run_id": "run-block",
            "case_id": "case-block",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_2",
            "task_type": "clarify_case",
            "payload": {
                "needs": [{"need_id": "need_001", "category": "income_assistance"}],
                "case_facts": [{"field": "zip_code", "value": "95823"}],
                "already_asked": [],
                "candidate_requirements": [],
            },
        }
        res = handle_agent_2(req)
        self.assertEqual(res["status"], "needs_clarification")
        income_qs = [
            r for r in res["clarification_requests"]
            if r["fact_key"] == "household_gross_monthly_income"
        ]
        self.assertGreater(len(income_qs), 0, "Income question must be generated")
        self.assertFalse(income_qs[0]["can_skip"],
                         "Income question must have can_skip=False")

    def test_block_10b_agent2_missing_income_not_asked_when_already_known(self):
        """Agent 2 must NOT ask income when it is already in case_facts."""
        req = {
            "request_id": "req-julia-2",
            "run_id": "run-block",
            "case_id": "case-block",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_2",
            "task_type": "clarify_case",
            "payload": {
                "needs": [{"need_id": "need_001", "category": "income_assistance"}],
                "case_facts": [
                    {"field": "household_gross_monthly_income", "value": 800}
                ],
                "already_asked": [],
                "candidate_requirements": [],
            },
        }
        res = handle_agent_2(req)
        income_qs = [
            r for r in res["clarification_requests"]
            if r["fact_key"] == "household_gross_monthly_income"
        ]
        self.assertEqual(len(income_qs), 0,
                         "Income question must NOT be generated when income is already known")

    def test_block_10c_agent2_missing_income_not_asked_when_already_asked(self):
        """Agent 2 must NOT re-ask income when it's in already_asked."""
        req = {
            "request_id": "req-julia-3",
            "run_id": "run-block",
            "case_id": "case-block",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_2",
            "task_type": "clarify_case",
            "payload": {
                "needs": [{"need_id": "need_001", "category": "income_assistance"}],
                "case_facts": [],
                "already_asked": ["household_gross_monthly_income"],
                "candidate_requirements": [],
            },
        }
        res = handle_agent_2(req)
        income_qs = [
            r for r in res["clarification_requests"]
            if r["fact_key"] == "household_gross_monthly_income"
        ]
        self.assertEqual(len(income_qs), 0,
                         "Income question must NOT be re-asked when in already_asked")

    # -------------------------------------------------------------------
    # BLOCKING ITEM 11 — Agent 2 eviction clarification has can_skip=False
    # -------------------------------------------------------------------

    def test_block_11_agent2_eviction_question_can_skip_false(self):
        """has_written_eviction_notice clarification must have can_skip=False."""
        req = {
            "request_id": "req-evict-cs",
            "run_id": "run-block",
            "case_id": "case-block",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_2",
            "task_type": "clarify_case",
            "payload": {
                "needs": [],
                "case_facts": [],
                "already_asked": [],
                "candidate_requirements": [
                    {
                        "program_id": "prog_evict",
                        "fact_key": "has_written_eviction_notice",
                        "verified_rule_ref": "rule_eviction_doc",
                    }
                ],
            },
        }
        res = handle_agent_2(req)
        eviction_qs = [
            r for r in res["clarification_requests"]
            if r["fact_key"] == "has_written_eviction_notice"
        ]
        self.assertGreater(len(eviction_qs), 0, "Eviction question must be generated")
        self.assertFalse(
            eviction_qs[0]["can_skip"],
            "Eviction clarification must have can_skip=False"
        )
        # Must ask for document type and date (per blocking rule)
        question_text = eviction_qs[0]["user_facing_question"]
        self.assertTrue(
            any(kw in question_text.lower() for kw in ["type", "document", "date"]),
            f"Eviction question must ask for document type and date; got: {question_text!r}"
        )


class TestContractShapeNegativeGuards(unittest.TestCase):
    """Negative guards — these cases must NOT produce false positives."""

    def test_no_safety_flag_for_show_about_violence(self):
        """'show about violence' must NOT trigger a safety flag."""
        res = _run_story("I was watching a show about violence last night. ZIP 95823.")
        flags = res["result"].get("safety_or_official_deadline_flags", [])
        safety_flags = [f for f in flags if f.get("type") == "safety"]
        self.assertEqual(len(safety_flags), 0, "False positive safety flag detected")

    def test_no_safety_flag_for_substance_abuse_program(self):
        """'substance abuse program years ago' must NOT trigger a safety flag."""
        res = _run_story(
            "I completed a substance abuse program years ago and I'm doing fine now. "
            "I just need help with rent. ZIP 95823."
        )
        flags = res["result"].get("safety_or_official_deadline_flags", [])
        safety_flags = [f for f in flags if f.get("type") == "safety"]
        self.assertEqual(len(safety_flags), 0, "False positive safety flag detected")

    def test_no_job_loss_triggering_event_without_job_loss(self):
        """Stories without job loss must NOT emit 'job_loss' in triggering_events."""
        res = _run_story("I need food assistance. My pantry is empty. ZIP 95820.")
        triggering = res["result"]["triggering_events"]
        self.assertNotIn("job_loss", triggering)

    def test_no_bereavement_event_without_death(self):
        """'sole earner' alone without death signal must NOT emit 'bereavement'."""
        res = _run_story(
            "I am the sole earner in my family and I need rental assistance. ZIP 95823."
        )
        triggering = res["result"]["triggering_events"]
        self.assertNotIn("bereavement", triggering)


if __name__ == "__main__":
    unittest.main()
