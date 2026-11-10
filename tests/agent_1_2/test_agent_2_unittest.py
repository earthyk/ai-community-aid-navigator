"""
Standard-Library Unittest Suite for Agent 2 (v6.1)
Zero external dependencies (Runs via `python -m unittest discover -s tests -t .`).
"""
import unittest

from navigator.agents.agent_1_2.agent_1 import handle_agent_1
from navigator.agents.agent_1_2.agent_2 import handle_agent_2

class TestAgent2(unittest.TestCase):

    def test_deduplication_and_filtering(self):
        req = {
            "request_id": "req-0002",
            "run_id": "run-0001",
            "case_id": "case-demo-001",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_2",
            "task_type": "clarify_case",
            "payload": {
                "needs": [
                    {"need_id": "need_003", "category": "food_assistance", "description": "Food"}
                ],
                "case_facts": [
                    {"field": "zip_code", "value": "95823"},
                    {"field": "employment_status", "value": "laid_off"},
                    {"field": "household_gross_monthly_income", "value": 1200},
                ],
                "already_asked": ["rent_amount_monthly"],
                "candidate_requirements": [
                    {"program_id": "prog_rent", "fact_key": "zip_code", "verified_rule_ref": "rule_geo"},
                    {"program_id": "prog_aid", "fact_key": "has_written_eviction_notice", "verified_rule_ref": "rule_evict"},
                ],
            },
        }
        res = handle_agent_2(req)
        self.assertEqual(res["status"], "needs_clarification")
        self.assertEqual(len(res["clarification_requests"]), 1)
        self.assertEqual(res["clarification_requests"][0]["fact_key"], "has_written_eviction_notice")
        self.assertFalse(res["result"]["optional_food_check"])

    def test_missing_income_question_generation(self):
        req = {
            "request_id": "req-income-q",
            "run_id": "run-0001",
            "case_id": "case-demo-001",
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
        self.assertEqual(len(res["clarification_requests"]), 1)
        self.assertEqual(res["clarification_requests"][0]["fact_key"], "household_gross_monthly_income")
        self.assertFalse(res["clarification_requests"][0]["can_skip"])

    def test_unspecified_hardship_circumstance_clarification(self):
        """Multi-turn: vague story → Agent 1 flags unspecified_hardship_cause →
        Agent 2 asks for circumstances first, NOT income."""
        story = (
            "Hi, I need help with food and rent. "
            "I'm having financial problems and I'm worried about how my family will get through next month."
        )
        a1_req = {
            "request_id": "req-a1-circ",
            "run_id": "run-0001",
            "case_id": "case-circ-001",
            "case_version": 1,
            "task_type": "understand_story",
            "payload": {"story_text": story},
        }
        a1_res = handle_agent_1(a1_req)
        self.assertEqual(a1_res["status"], "completed")
        ambiguity_flags = a1_res["result"]["ambiguity_flags"]
        self.assertIn("unspecified_hardship_cause", ambiguity_flags)

        a2_req = {
            "request_id": "req-a2-circ",
            "run_id": "run-0001",
            "case_id": "case-circ-001",
            "case_version": 1,
            "task_type": "clarify_case",
            "payload": {
                "needs": a1_res["result"]["proposed_needs"],
                "case_facts": a1_res["result"]["factual_claims"],
                "already_asked": [],
                "candidate_requirements": [],
                "ambiguity_flags": ambiguity_flags,
            },
        }
        a2_res = handle_agent_2(a2_req)
        self.assertEqual(a2_res["status"], "needs_clarification")
        self.assertEqual(len(a2_res["clarification_requests"]), 1)

        first_q = a2_res["clarification_requests"][0]
        self.assertEqual(first_q["fact_key"], "triggering_circumstances")
        self.assertEqual(
            first_q["user_facing_question"],
            "I'm sorry your family is going through a difficult time. "
            "Could you tell me a little more about what happened that led to these financial difficulties?",
        )

        asked_keys = [r["fact_key"] for r in a2_res["clarification_requests"]]
        self.assertNotIn("household_gross_monthly_income", asked_keys)


    def test_missing_zip_code_question_generated_on_turn_1(self):
        """Item 2: Agent 2 must emit a zip_code clarification (can_skip=False) when
        zip_code is absent from case_facts and has not been asked yet."""
        req = {
            "request_id": "req-zip-q",
            "run_id": "run-0001",
            "case_id": "case-zip-001",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_2",
            "task_type": "clarify_case",
            "payload": {
                "needs": [{"need_id": "need_001", "category": "housing_assistance"}],
                "case_facts": [
                    {"field": "employment_status", "value": "laid_off"},
                    {"field": "household_gross_monthly_income", "value": 1500},
                ],
                "already_asked": [],
                "candidate_requirements": [],
                "ambiguity_flags": [],
            },
        }
        res = handle_agent_2(req)
        self.assertEqual(res["status"], "needs_clarification")
        asked_keys = [r["fact_key"] for r in res["clarification_requests"]]
        self.assertIn("zip_code", asked_keys)
        zip_q = next(r for r in res["clarification_requests"] if r["fact_key"] == "zip_code")
        self.assertFalse(zip_q["can_skip"])

    def test_missing_household_size_question_when_needed(self):
        """Item 3: Agent 2 must emit a household_size clarification (can_skip=True) when
        household_size is absent and candidate_requirements reference it."""
        req = {
            "request_id": "req-hh-q",
            "run_id": "run-0001",
            "case_id": "case-hh-001",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_2",
            "task_type": "clarify_case",
            "payload": {
                "needs": [{"need_id": "need_001", "category": "food_assistance"}],
                "case_facts": [
                    {"field": "zip_code", "value": "95823"},
                    {"field": "household_gross_monthly_income", "value": 1200},
                ],
                "already_asked": ["zip_code"],
                "candidate_requirements": [
                    {
                        "program_id": "prog_food",
                        "fact_key": "household_size",
                        "verified_rule_ref": "rule_hh_size",
                    }
                ],
                "ambiguity_flags": [],
            },
        }
        res = handle_agent_2(req)
        self.assertEqual(res["status"], "needs_clarification")
        asked_keys = [r["fact_key"] for r in res["clarification_requests"]]
        self.assertIn("household_size", asked_keys)
        hh_q = next(r for r in res["clarification_requests"] if r["fact_key"] == "household_size")
        self.assertTrue(hh_q["can_skip"])
        # Pacing ceiling: never more than 2 questions per turn
        self.assertLessEqual(len(res["clarification_requests"]), 2)


if __name__ == "__main__":
    unittest.main()
