import unittest

from navigator.agents.agent_1_2 import agent_1 as A

STORY = ("I have a mortgage payment I cannot cover this month. "
         "My hours were cut and we have very little money left. We live in 95823.")
QUOTE = ("I have a mortgage payment I cannot cover this month. "
         "My hours were cut and we have very little money left.")


def _merge(wx_needs, existing=None):
    _, needs, _, _ = A._merge_watsonx_into_result(
        wx_result={"proposed_needs": wx_needs},
        story=STORY,
        facts=[],
        proposed_needs=list(existing or []),
        need_idx=1,
        fact_idx=1,
        urgency_fn=A._wx_urgency,
    )
    return [n["category"] for n in needs]


class WatsonxCategoryNormalizationTest(unittest.TestCase):
    def test_model_label_housing_is_merged(self):
        self.assertIn("housing_assistance",
                      _merge([{"category": "Housing", "description": "x", "original_quote": QUOTE}]))

    def test_contract_value_still_works(self):
        self.assertIn("housing_assistance",
                      _merge([{"category": "housing_assistance", "description": "x", "original_quote": QUOTE}]))

    def test_unknown_category_is_dropped(self):
        self.assertEqual(_merge([{"category": "Pets", "description": "x", "original_quote": QUOTE}]), [])

    def test_quote_not_in_story_is_dropped(self):
        self.assertEqual(_merge([{"category": "Housing", "description": "x",
                                  "original_quote": "We were evicted yesterday."}]), [])

    def test_no_duplicate_when_rules_already_found_it(self):
        cats = _merge([{"category": "Housing", "description": "x", "original_quote": QUOTE}],
                      existing=[{"category": "housing_assistance"}])
        self.assertEqual(cats.count("housing_assistance"), 1)


if __name__ == "__main__":
    unittest.main()
