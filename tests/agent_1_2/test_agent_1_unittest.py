"""
Standard-Library Unittest Suite for Agent 1 (v6.1)
Zero external dependencies (Runs via `python -m unittest discover -s tests -t .`).
"""
from datetime import date
import os
import unittest
import unittest.mock

from navigator.agents.agent_1_2.agent_1 import handle_agent_1

class TestAgent1(unittest.TestCase):

    def test_sacramento_benchmark(self):
        req = {
            "request_id": "req-0001",
            "run_id": "run-0001",
            "case_id": "case-demo-001",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {
                "story_text": (
                    "I'm a single mom in Sacramento, ZIP 95823, with two kids, 6 and 9. "
                    "I was laid off from my warehouse job last Friday. Rent of $1,450 is due on "
                    "November 1 and I only have about $300 left. We're also running low on food "
                    "this week. I don't know where to start."
                ),
                "locale": "en-US",
            },
        }
        res = handle_agent_1(req, ref_date=date(2026, 10, 23))
        self.assertEqual(res["status"], "completed")
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("zip_code"), "95823")
        self.assertEqual(facts.get("household_size"), 3)
        self.assertEqual(facts.get("children_ages"), [6, 9])
        self.assertEqual(facts.get("rent_amount_monthly"), 1450)
        self.assertEqual(facts.get("cash_on_hand_approx"), 300)
        self.assertEqual(facts.get("rent_due_date"), "2026-11-01")

    def test_overdue_rent_date_stays_in_past(self):
        req = {
            "request_id": "req-overdue",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {
                "story_text": "Rent of $1,450 was due on November 1. ZIP 95823."
            },
        }
        res = handle_agent_1(req, ref_date=date(2026, 11, 3))
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("rent_due_date"), "2026-11-01")
        needs = res["result"]["proposed_needs"]
        housing = [n for n in needs if n["category"] == "housing_assistance"][0]
        self.assertEqual(housing["urgency"], "immediate")
        self.assertEqual(housing["urgency_reason"], "Rent is overdue")

    def test_broadened_life_safety_signals(self):
        phrases = [
            "I'm thinking about ending it all",
            "I can't go on like this",
            "I'm scared he will come back and hurt us",
            "I'm scared she will come back and hurt us",
            "He will come back and hurt us",
            "She will come back and hurt us",
            "I might hurt someone",
            "I want to kill myself",
            "My partner hits me",
            "I feel unsafe at home",
            "He said he will hurt us if we don't leave.",
            "He said he will hurt us if we don\u2019t leave.",
            "The landlord threatened to attack us.",
            "My husband threatened to kill himself.",
            "He threatened to hurt my son.",
            "He will hurt my daughter.",
            "She said she would hurt the children.",
            "He is going to hurt my baby.",
            "He threatened to kill my children.",
            "They threatened to kill my dog.",
            "My boyfriend will hurt me.",
            "My girlfriend is going to hurt the kids.",
            "My boyfriend said he would kill us.",
        ]
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                req = {
                    "request_id": "req-safe",
                    "run_id": "run-001",
                    "case_id": "case-001",
                    "case_version": 1,
                    "role_id": "agent_1",
                    "task_type": "understand_story",
                    "payload": {"story_text": phrase},
                }
                res = handle_agent_1(req)
                flags = res["result"].get("safety_or_official_deadline_flags", [])
                self.assertGreaterEqual(len(flags), 1, f"Failed to flag: {phrase}")
                self.assertEqual(flags[0]["type"], "safety")
                self.assertNotIn("safety_or_deadline_flags", res["result"])

    def test_safety_signals_negative_everyday_sentences(self):
        benign_phrases = [
            "my landlord said he will come back to fix the heater",
            "my landlord said she will come back to fix the heater",
            "the contractor will come back tomorrow morning",
            "they will come back next week to inspect the property",
            "he will come back from work at 5pm",
            "They might harm my credit score if I miss rent.",
            "They will kill my hours at work.",
            "They are going to beat the deadline.",
            "The headache will kill me.",
            "This toothache will kill me.",
            "My backache is going to kill me.",
        ]
        for phrase in benign_phrases:
            with self.subTest(phrase=phrase):
                req = {
                    "request_id": "req-safe-neg",
                    "run_id": "run-001",
                    "case_id": "case-001",
                    "case_version": 1,
                    "role_id": "agent_1",
                    "task_type": "understand_story",
                    "payload": {"story_text": phrase},
                }
                res = handle_agent_1(req)
                flags = res["result"].get("safety_or_official_deadline_flags", [])
                safety_flags = [f for f in flags if f.get("type") == "safety"]
                self.assertEqual(
                    len(safety_flags),
                    0,
                    f"Unexpected safety flag on benign phrase: {phrase}",
                )

    def test_monthly_household_income_extraction(self):
        req_approx = {
            "request_id": "req-inc-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "I make about $1,200 a month in 95823."},
        }
        res_approx = handle_agent_1(req_approx)
        facts_approx = {f["field"]: f for f in res_approx["result"]["factual_claims"]}
        self.assertIn("household_gross_monthly_income", facts_approx)
        self.assertEqual(facts_approx["household_gross_monthly_income"]["value"], 1200)
        self.assertTrue(facts_approx["household_gross_monthly_income"]["is_approximate"])

        req_zero = {
            "request_id": "req-inc-2",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "I have no income right now."},
        }
        res_zero = handle_agent_1(req_zero)
        facts_zero = {f["field"]: f for f in res_zero["result"]["factual_claims"]}
        self.assertIn("household_gross_monthly_income", facts_zero)
        self.assertEqual(facts_zero["household_gross_monthly_income"]["value"], 0)

        req_none = {
            "request_id": "req-inc-3",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "I need help paying rent in 95823."},
        }
        res_none = handle_agent_1(req_none)
        fields = [f["field"] for f in res_none["result"]["factual_claims"]]
        self.assertNotIn("household_gross_monthly_income", fields)

    def test_sleeping_in_car_housing_need(self):
        req = {
            "request_id": "req-car",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "We are sleeping in our car tonight in 95823."},
        }
        res = handle_agent_1(req)
        needs = [n for n in res["result"]["proposed_needs"] if n["category"] == "housing_assistance"]
        self.assertGreaterEqual(len(needs), 1)
        self.assertEqual(needs[0]["subcategory"], "emergency_shelter")
        self.assertEqual(needs[0]["urgency"], "immediate")

    def test_housing_and_food_both_detected(self):
        """Housing Need Regex + Contract 4.1: 'housing and food' produces both needs,
        ambiguity_flags is an array of objects with field/quote/note."""
        req = {
            "request_id": "req-hf-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "I have problems with housing and food. I need help."},
        }
        res = handle_agent_1(req)
        self.assertEqual(res["status"], "completed")
        categories = [n["category"] for n in res["result"]["proposed_needs"]]
        self.assertIn("housing_assistance", categories)
        self.assertIn("food_assistance", categories)
        # Contract 4.1: ambiguity_flags must be an array of objects
        af = res["result"]["ambiguity_flags"]
        self.assertIsInstance(af, list)
        self.assertGreater(len(af), 0)
        self.assertIsInstance(af[0], dict)
        self.assertIn("field", af[0])
        self.assertIn("quote", af[0])
        self.assertIn("note", af[0])
        self.assertEqual(af[0]["note"], "unspecified_hardship_cause")

    def test_passive_hours_cut_clears_unspecified_hardship(self):
        """Passive hours-cut phrasing ('My hours were cut at work') must be recognized
        as a root cause, so unspecified_hardship_cause is NOT flagged."""
        req = {
            "request_id": "req-hc-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "My hours were cut at work and I can't pay rent."},
        }
        res = handle_agent_1(req)
        self.assertEqual(res["status"], "completed")
        af_notes = [
            (f["note"] if isinstance(f, dict) else f)
            for f in res["result"]["ambiguity_flags"]
        ]
        self.assertNotIn("unspecified_hardship_cause", af_notes)

    def test_zip_code_answer_during_income_clarification(self):
        """Income Sanity Guard: answer '95660' when income is pending sets
        zip_code='95660' and does NOT set household_gross_monthly_income."""
        req = {
            "request_id": "req-zip-income-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "parse_clarification_answer",
            "payload": {
                "answer_text": "95660",
                "pending_fact_keys": ["household_gross_monthly_income"],
            },
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("zip_code"), "95660")
        self.assertNotIn("household_gross_monthly_income", facts)

    def test_bad_input_handling(self):
        res_null = handle_agent_1({
            "request_id": "req-1", "run_id": "r-1", "case_id": "c-1", "case_version": 1,
            "role_id": "agent_1", "task_type": "understand_story", "payload": {"story_text": None}
        })
        self.assertEqual(res_null["status"], "failed")
        self.assertEqual(res_null["issues"][0]["code"], "EMPTY_STORY")

        res_no_pl = handle_agent_1({
            "request_id": "req-2", "run_id": "r-1", "case_id": "c-1", "case_version": 1,
            "role_id": "agent_1", "task_type": "understand_story"
        })
        self.assertEqual(res_no_pl["status"], "failed")
        self.assertEqual(res_no_pl["issues"][0]["code"], "MISSING_PAYLOAD")

        res_bad_date = handle_agent_1({
            "request_id": "req-3", "run_id": "r-1", "case_id": "c-1", "case_version": 1,
            "role_id": "agent_1", "task_type": "understand_story",
            "payload": {"story_text": "Laid off in 95823", "ref_date": "not-a-date"}
        })
        self.assertEqual(res_bad_date["status"], "failed")
        self.assertEqual(res_bad_date["issues"][0]["code"], "INVALID_REF_DATE")

    def test_3_day_notice_extracts_eviction_notice_type(self):
        """Defect fix: '3-day notice to pay or quit' must extract both
        has_written_eviction_notice=True and eviction_notice_type='3_day_pay_or_quit'."""
        req = {
            "request_id": "req-evict-type-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {
                "story_text": (
                    "My landlord gave me a 3-day notice to pay or quit yesterday "
                    "and threatened to lock us out if we don't pay."
                )
            },
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertTrue(facts.get("has_written_eviction_notice"))
        self.assertEqual(facts.get("eviction_notice_type"), "3_day_pay_or_quit")

    def test_arrears_amount_not_rent_amount_monthly(self):
        """Defect fix: 'the amount due is $1,600' in a clarification answer must extract
        rent_arrears_amount and leave rent_amount_monthly untouched."""
        req = {
            "request_id": "req-arrears-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "parse_clarification_answer",
            "payload": {
                "answer_text": "The notice date is November 6, 2026, and the amount due is $1,600.",
                "pending_fact_keys": ["eviction_notice_type"],
            },
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("rent_arrears_amount"), 1600)
        self.assertNotIn("rent_amount_monthly", facts)

    def test_clarification_food_keywords_add_food_assistance_need(self):
        """Defect fix: clarification answer with 'groceries' / 'food' / 'hungry'
        must append food_assistance to proposed_needs."""
        for phrase in [
            "we have no groceries left for the kids",
            "we don't have food at home",
            "the kids are hungry",
        ]:
            with self.subTest(phrase=phrase):
                req = {
                    "request_id": "req-food-claric",
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
                needs = res["result"].get("proposed_needs", [])
                cats = [n["category"] for n in needs]
                self.assertIn(
                    "food_assistance", cats,
                    f"Expected food_assistance in proposed_needs for: {phrase}",
                )
    def test_lockout_threat_is_housing_not_safety_flag(self):
        req = {
            "request_id": "req-lockout-threat",
            "run_id": "run-001",
            "case_id": "case-lockout-001",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {
                "story_text": "My landlord threatened to lock us out",
                "locale": "en-US",
            },
        }
        res = handle_agent_1(req)
        self.assertEqual(res["status"], "completed")
        self.assertEqual(res["result"]["safety_or_official_deadline_flags"], [])
        needs = res["result"]["proposed_needs"]
        self.assertTrue(any(n["category"] == "housing_assistance" for n in needs))

    def test_physical_harm_threat_still_raises_safety_flag(self):
        req = {
            "request_id": "req-harm-threat",
            "run_id": "run-001",
            "case_id": "case-harm-001",
            "case_version": 1,
            "schema_version": "1.0",
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {
                "story_text": "My landlord threatened to hurt us",
                "locale": "en-US",
            },
        }
        res = handle_agent_1(req)
        self.assertEqual(res["status"], "completed")
        flags = res["result"]["safety_or_official_deadline_flags"]
        self.assertTrue(any(f.get("type") == "safety" for f in flags))


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

    # -----------------------------------------------------------------------
    # Item a — Step 4b: both reduced_hours + reduced_pay flagged simultaneously
    # -----------------------------------------------------------------------

    def test_both_reduced_hours_and_pay_in_story(self):
        """When BOTH hours-cut and pay-reduction appear, triggering_events must
        contain 'reduced_hours' AND 'reduced_pay', and the income_assistance
        need description must be 'Work hours and pay reduced'."""
        req = {
            "request_id": "req-rh-rp-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {
                "story_text": "My hours were cut and my pay was reduced.",
            },
        }
        res = handle_agent_1(req)
        self.assertEqual(res["status"], "completed")
        tevents = res["result"].get("triggering_events", [])
        self.assertIn("reduced_hours", tevents)
        self.assertIn("reduced_pay", tevents)
        needs = {n["category"]: n for n in res["result"]["proposed_needs"]}
        self.assertIn("income_assistance", needs)
        self.assertEqual(needs["income_assistance"]["description"], "Work hours and pay reduced")

    def test_only_reduced_hours_no_pay(self):
        """Only hours-cut phrasing → triggering_events has 'reduced_hours' only."""
        req = {
            "request_id": "req-rh-only",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "My hours were cut at work."},
        }
        res = handle_agent_1(req)
        tevents = res["result"].get("triggering_events", [])
        self.assertIn("reduced_hours", tevents)
        self.assertNotIn("reduced_pay", tevents)

    # -----------------------------------------------------------------------
    # Item b — Expanded RE_REDUCED_PAY patterns
    # -----------------------------------------------------------------------

    def test_reduced_pay_they_reduced_my_pay(self):
        """'They reduced my pay.' must flag reduced_pay in triggering_events,
        set employment_status='reduced_pay', and propose income_assistance."""
        req = {
            "request_id": "req-rp-b1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "They reduced my pay."},
        }
        res = handle_agent_1(req)
        self.assertEqual(res["status"], "completed")
        tevents = res["result"].get("triggering_events", [])
        self.assertIn("reduced_pay", tevents)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("employment_status"), "reduced_pay")
        needs_cats = [n["category"] for n in res["result"]["proposed_needs"]]
        self.assertIn("income_assistance", needs_cats)

    def test_reduced_pay_paycheck_dropped(self):
        """'My paycheck dropped a lot this month.' must flag reduced_pay,
        set employment_status='reduced_pay', and propose income_assistance."""
        req = {
            "request_id": "req-rp-b2",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "My paycheck dropped a lot this month."},
        }
        res = handle_agent_1(req)
        self.assertEqual(res["status"], "completed")
        tevents = res["result"].get("triggering_events", [])
        self.assertIn("reduced_pay", tevents)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("employment_status"), "reduced_pay")
        needs_cats = [n["category"] for n in res["result"]["proposed_needs"]]
        self.assertIn("income_assistance", needs_cats)

    # -----------------------------------------------------------------------
    # Item d — $800/month slash phrasing for household_gross_monthly_income
    # -----------------------------------------------------------------------

    def test_income_slash_monthly_story(self):
        """'$800/month' in a story must set household_gross_monthly_income=800."""
        req = {
            "request_id": "req-slash-1",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "We bring in $800/month total."},
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("household_gross_monthly_income"), 800)

    def test_income_slash_mo_story(self):
        """'800/mo' in a story must set household_gross_monthly_income=800."""
        req = {
            "request_id": "req-slash-2",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "My income is about 800/mo."},
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("household_gross_monthly_income"), 800)

    def test_income_slash_monthly_clarification(self):
        """'$800/month' in a clarification answer must set
        household_gross_monthly_income=800."""
        req = {
            "request_id": "req-slash-claric",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "parse_clarification_answer",
            "payload": {
                "answer_text": "$800/month",
                "pending_fact_keys": ["household_gross_monthly_income"],
            },
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("household_gross_monthly_income"), 800)

    # -----------------------------------------------------------------------
    # Item e — income + rent in the same clarification answer
    # -----------------------------------------------------------------------

    def test_income_and_rent_same_answer_story(self):
        """'We get 800 a month, rent is 1400' in a story must extract BOTH
        household_gross_monthly_income=800 AND rent_amount_monthly=1400."""
        req = {
            "request_id": "req-inc-rent-s",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "We get 800 a month, rent is 1400."},
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("household_gross_monthly_income"), 800)
        self.assertEqual(facts.get("rent_amount_monthly"), 1400)

    def test_income_and_rent_same_clarification_answer(self):
        """'We get 800 a month, rent is 1400' as a clarification answer must
        extract BOTH household_gross_monthly_income=800 AND rent_amount_monthly=1400."""
        req = {
            "request_id": "req-inc-rent-c",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "parse_clarification_answer",
            "payload": {
                "answer_text": "We get 800 a month, rent is 1400",
                "pending_fact_keys": ["household_gross_monthly_income"],
            },
        }
        res = handle_agent_1(req)
        facts = {f["field"]: f["value"] for f in res["result"]["factual_claims"]}
        self.assertEqual(facts.get("household_gross_monthly_income"), 800)
        self.assertEqual(facts.get("rent_amount_monthly"), 1400)

    # -----------------------------------------------------------------------
    # Item f — Expanded safety threat patterns
    # -----------------------------------------------------------------------

    def test_safety_not_safe_at_home(self):
        """'I'm not safe at home.' / 'not safe at home' must raise a safety flag."""
        for phrase in [
            "I'm not safe at home.",
            "not safe at home",
        ]:
            with self.subTest(phrase=phrase):
                req = {
                    "request_id": "req-safe-f1",
                    "run_id": "run-001",
                    "case_id": "case-001",
                    "case_version": 1,
                    "role_id": "agent_1",
                    "task_type": "understand_story",
                    "payload": {"story_text": phrase},
                }
                res = handle_agent_1(req)
                flags = res["result"].get("safety_or_official_deadline_flags", [])
                safety = [f for f in flags if f.get("type") == "safety"]
                self.assertGreaterEqual(len(safety), 1, f"No safety flag for: {phrase}")

    def test_safety_ex_threatening(self):
        """'My ex is threatening me.' must raise a safety flag."""
        req = {
            "request_id": "req-safe-f2",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "My ex is threatening me."},
        }
        res = handle_agent_1(req)
        flags = res["result"].get("safety_or_official_deadline_flags", [])
        safety = [f for f in flags if f.get("type") == "safety"]
        self.assertGreaterEqual(len(safety), 1)

    def test_safety_scared_for_my_life(self):
        """'I am scared for my life.' must raise a safety flag."""
        req = {
            "request_id": "req-safe-f3",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "I am scared for my life."},
        }
        res = handle_agent_1(req)
        flags = res["result"].get("safety_or_official_deadline_flags", [])
        safety = [f for f in flags if f.get("type") == "safety"]
        self.assertGreaterEqual(len(safety), 1)

    def test_safety_fear_for_my_life(self):
        """'I fear for my life.' must raise a safety flag."""
        req = {
            "request_id": "req-safe-f4",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "I fear for my life."},
        }
        res = handle_agent_1(req)
        flags = res["result"].get("safety_or_official_deadline_flags", [])
        safety = [f for f in flags if f.get("type") == "safety"]
        self.assertGreaterEqual(len(safety), 1)

    def test_safety_partner_hits_me(self):
        """'I don't feel safe, my partner hits me.' must raise a safety flag
        (hits word-boundary match)."""
        req = {
            "request_id": "req-safe-f5",
            "run_id": "run-001",
            "case_id": "case-001",
            "case_version": 1,
            "role_id": "agent_1",
            "task_type": "understand_story",
            "payload": {"story_text": "I don't feel safe, my partner hits me."},
        }
        res = handle_agent_1(req)
        flags = res["result"].get("safety_or_official_deadline_flags", [])
        safety = [f for f in flags if f.get("type") == "safety"]
        self.assertGreaterEqual(len(safety), 1)


# ---------------------------------------------------------------------------
# Item 6: Module-level WATSONX_* env isolation
# ---------------------------------------------------------------------------
_WATSONX_ENV_KEYS = [k for k in os.environ if k.startswith("WATSONX_") and k != "WATSONX_STATE_FILE"]
_SAVED_WATSONX_ENV: dict = {}


def setUpModule():
    """Remove all WATSONX_* env vars before any test in this module runs."""
    global _SAVED_WATSONX_ENV
    _SAVED_WATSONX_ENV = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_") and k != "WATSONX_STATE_FILE"}


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
        self._stashed = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("WATSONX_") and k != "WATSONX_STATE_FILE"}

    def tearDown(self):
        """Restore any WATSONX_* vars stashed during setUp."""
        os.environ.update(self._stashed)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    _STORY = (
        "I lost my job last month and can't pay rent in 95823. "
        "We also need help with crowdfunding to get back on our feet."
    )

    @staticmethod
    def _reset_module():
        """Reset module-level watsonx state before a test (in-process + persisted)."""
        import navigator.agents.agent_1_2.agent_1 as a1_mod
        a1_mod._watsonx_call_count = 0
        a1_mod._iam_token_cache = ("", 0.0)
        # Also clear the cross-process persistent state file
        a1_mod._write_state({})

    def _make_req(self, story=None, http_post_fn=None):
        payload = {
            "story_text": story or self._STORY,
        }
        if http_post_fn is not None:
            payload["_http_post_fn"] = http_post_fn
        return {
            "request_id": "req-wx-test",
            "run_id": "run-wx-test",
            "case_id": "case-wx-test",
            "case_version": 1,
            "task_type": "understand_story",
            "payload": payload,
        }

    @staticmethod
    def _make_iam_response(token="tok-abc", expires_in=3600):
        import json
        return json.dumps({
            "access_token": token,
            "expires_in": expires_in,
            "token_type": "Bearer",
        }).encode()

    @staticmethod
    def _make_wx_response(content_dict):
        import json
        content_json = json.dumps(content_dict)
        outer = {
            "choices": [
                {"message": {"role": "assistant", "content": content_json}}
            ]
        }
        return json.dumps(outer).encode()

    # ------------------------------------------------------------------
    # Test 1: mocked success + WATSONX_USED issue appended
    # ------------------------------------------------------------------
    def test_mocked_success_watsonx_used_issue(self):
        from navigator.agents.agent_1_2.agent_1 import handle_agent_1

        wx_payload = {
            "proposed_needs": [
                {
                    "category": "crowdfunding_guidance",
                    "description": "Help with crowdfunding",
                    "original_quote": "We also need help with crowdfunding to get back on our feet.",
                }
            ],
            "factual_claims": [],
        }

        calls = []

        def fake_http(url, body, headers):
            calls.append(url)
            if "iam.cloud.ibm.com" in url:
                return self._make_iam_response()
            return self._make_wx_response(wx_payload)

        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-123", "WATSONX_PROJECT_ID": "proj-test"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))

        self.assertEqual(res["status"], "completed")
        self.assertFalse(res["is_mock"])

        issue_codes = [i["code"] for i in res["issues"]]
        self.assertIn("WATSONX_USED", issue_codes)
        wx_issue = next(i for i in res["issues"] if i["code"] == "WATSONX_USED")
        self.assertIn("call_count", wx_issue)
        self.assertIn("latency_ms", wx_issue)
        # Privacy: no story text, no prompt, no model output in issues
        self.assertNotIn(self._STORY, str(res["issues"]))

        # crowdfunding_guidance should have been merged
        cats = [n["category"] for n in res["result"]["proposed_needs"]]
        self.assertIn("crowdfunding_guidance", cats)

        # Urgency must come from rules (not model): rule default = "high"
        cg_need = next(n for n in res["result"]["proposed_needs"] if n["category"] == "crowdfunding_guidance")
        self.assertEqual(cg_need["urgency"], "high")

        # IAM + watsonx calls both made
        self.assertTrue(any("iam.cloud.ibm.com" in c for c in calls))
        self.assertTrue(any("ml/v1/text/chat" in c for c in calls))

    # ------------------------------------------------------------------
    # Test 2: IAM token is reused across two calls (only one IAM request)
    # ------------------------------------------------------------------
    def test_iam_token_reused_across_two_calls(self):
        from navigator.agents.agent_1_2.agent_1 import handle_agent_1

        iam_call_count = []

        def fake_http(url, body, headers):
            if "iam.cloud.ibm.com" in url:
                iam_call_count.append(1)
                return self._make_iam_response(expires_in=3600)
            return self._make_wx_response({"proposed_needs": [], "factual_claims": []})

        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-reuse", "WATSONX_PROJECT_ID": "proj-test"}):
            handle_agent_1(self._make_req(http_post_fn=fake_http))
            # Second call — must reuse cached token (do NOT reset module state here)
            handle_agent_1(self._make_req(http_post_fn=fake_http))

        self.assertEqual(len(iam_call_count), 1, "IAM token should be fetched only once")

    # ------------------------------------------------------------------
    # Test 3: WATSONX_APIKEY unset → is_mock=True, WATSONX_FALLBACK info
    # ------------------------------------------------------------------
    def test_unset_apikey_fallback(self):
        from navigator.agents.agent_1_2.agent_1 import handle_agent_1

        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {}, clear=True):
            res = handle_agent_1(self._make_req())

        self.assertTrue(res["is_mock"])
        issue_codes = [i["code"] for i in res["issues"]]
        self.assertIn("WATSONX_FALLBACK", issue_codes)
        fb_issue = next(i for i in res["issues"] if i["code"] == "WATSONX_FALLBACK")
        self.assertEqual(fb_issue["severity"], "info")
        # Deterministic result still populated
        self.assertIsNotNone(res["result"].get("proposed_needs"))

    # ------------------------------------------------------------------
    # Test 4: invalid JSON from model → warning WATSONX_FALLBACK
    # ------------------------------------------------------------------
    def test_invalid_json_fallback(self):
        import json as _json
        from navigator.agents.agent_1_2.agent_1 import handle_agent_1

        def fake_http(url, body, headers):
            if "iam.cloud.ibm.com" in url:
                return self._make_iam_response()
            # Return outer valid JSON but content is not JSON
            outer = {
                "choices": [
                    {"message": {"role": "assistant", "content": "not valid json }{{"}}
                ]
            }
            return _json.dumps(outer).encode()

        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-badjson", "WATSONX_PROJECT_ID": "proj-test"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))

        self.assertTrue(res["is_mock"])
        issue_codes = [i["code"] for i in res["issues"]]
        self.assertIn("WATSONX_FALLBACK", issue_codes)
        fb_issue = next(i for i in res["issues"] if i["code"] == "WATSONX_FALLBACK")
        self.assertEqual(fb_issue["severity"], "warning")

    # ------------------------------------------------------------------
    # Test 5: timeout/HTTP exception → warning WATSONX_FALLBACK
    # ------------------------------------------------------------------
    def test_http_exception_fallback(self):
        from navigator.agents.agent_1_2.agent_1 import handle_agent_1

        def fake_http(url, body, headers):
            if "iam.cloud.ibm.com" in url:
                return self._make_iam_response()
            raise TimeoutError("Connection timed out")

        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-timeout", "WATSONX_PROJECT_ID": "proj-test"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))

        self.assertTrue(res["is_mock"])
        issue_codes = [i["code"] for i in res["issues"]]
        self.assertIn("WATSONX_FALLBACK", issue_codes)
        fb_issue = next(i for i in res["issues"] if i["code"] == "WATSONX_FALLBACK")
        self.assertEqual(fb_issue["severity"], "warning")

    # ------------------------------------------------------------------
    # Test 6: ungrounded quote (not in story) must be rejected
    # ------------------------------------------------------------------
    def test_ungrounded_quote_rejected(self):
        from navigator.agents.agent_1_2.agent_1 import handle_agent_1

        wx_payload = {
            "proposed_needs": [
                {
                    "category": "crowdfunding_guidance",
                    "description": "Crowdfunding help",
                    "original_quote": "This text does not appear in the story at all.",
                }
            ],
            "factual_claims": [],
        }

        def fake_http(url, body, headers):
            if "iam.cloud.ibm.com" in url:
                return self._make_iam_response()
            return self._make_wx_response(wx_payload)

        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-ungrounded"}):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))

        cats = [n["category"] for n in res["result"]["proposed_needs"]]
        self.assertNotIn("crowdfunding_guidance", cats,
                         "Ungrounded quote must be rejected from merge")

    # ------------------------------------------------------------------
    # Test 7: invalid category / invalid enum value rejected
    # ------------------------------------------------------------------
    def test_invalid_category_and_enum_rejected(self):
        from navigator.agents.agent_1_2.agent_1 import handle_agent_1

        story = "I lost my job last month and can't pay rent in 95823."
        wx_payload = {
            "proposed_needs": [
                {
                    "category": "totally_made_up_category",
                    "description": "Whatever",
                    "original_quote": "I lost my job last month",
                }
            ],
            "factual_claims": [
                {
                    "field": "employment_status",
                    "value": "not_a_real_enum_value",
                },
                {
                    "field": "eviction_notice_type",
                    "value": "banana",
                },
            ],
        }

        def fake_http(url, body, headers):
            if "iam.cloud.ibm.com" in url:
                return self._make_iam_response()
            return self._make_wx_response(wx_payload)

        self._reset_module()
        with unittest.mock.patch.dict(os.environ, {"WATSONX_APIKEY": "test-key-invalid-cat"}):
            res = handle_agent_1(self._make_req(story=story, http_post_fn=fake_http))

        cats = [n["category"] for n in res["result"]["proposed_needs"]]
        self.assertNotIn("totally_made_up_category", cats)
        fact_fields = [f["field"] for f in res["result"]["factual_claims"]]
        # employment_status is already set by rules, so the invalid model value would
        # be blocked either by existing-field guard or enum guard.
        # eviction_notice_type with "banana" must never appear.
        for f in res["result"]["factual_claims"]:
            if f["field"] == "eviction_notice_type":
                self.assertNotEqual(f["value"], "banana")

    # ------------------------------------------------------------------
    # Test 8: WATSONX_MAX_CALLS cap enforcement
    # ------------------------------------------------------------------
    def test_max_calls_cap_enforced(self):
        import navigator.agents.agent_1_2.agent_1 as a1_mod
        from navigator.agents.agent_1_2.agent_1 import handle_agent_1

        wx_calls = []

        def fake_http(url, body, headers):
            if "iam.cloud.ibm.com" in url:
                return self._make_iam_response()
            wx_calls.append(1)
            return self._make_wx_response({"proposed_needs": [], "factual_claims": []})

        self._reset_module()
        with unittest.mock.patch.dict(
            os.environ,
            {"WATSONX_APIKEY": "test-key-cap", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_MAX_CALLS": "2"},
        ):
            # 3 calls, cap is 2
            for i in range(3):
                handle_agent_1(self._make_req(http_post_fn=fake_http))

        self.assertEqual(len(wx_calls), 2, "watsonx endpoint must not be called more than MAX_CALLS times")

        # The third call (index 2) should have been a cap-triggered fallback.
        # _watsonx_call_count is now 2, which equals MAX_CALLS=2, so next call → fallback.
        with unittest.mock.patch.dict(
            os.environ,
            {"WATSONX_APIKEY": "test-key-cap", "WATSONX_PROJECT_ID": "proj-test", "WATSONX_MAX_CALLS": "2"},
        ):
            res = handle_agent_1(self._make_req(http_post_fn=fake_http))

        self.assertTrue(res["is_mock"])
        issue_codes = [i["code"] for i in res["issues"]]
        self.assertIn("WATSONX_FALLBACK", issue_codes)


if __name__ == "__main__":
    unittest.main()
