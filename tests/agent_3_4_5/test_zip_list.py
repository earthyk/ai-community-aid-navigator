"""Tests for the Sacramento County ZIP list (v1.8). Run from repo root:
python -I -m unittest discover -s tests -t ."""
import copy, json, os, unittest
from navigator.agents.agent_3_4_5 import agent_3
from navigator.agents.agent_3_4_5.common import SAC_COUNTY_ZIPS

BASE = {"request_id": "req-zip-test", "run_id": "run-zip", "case_id": "case-zip-001", "case_version": 1,
        "correlation_id": "corr-zip", "schema_version": "1.0", "allowed_case_facts": [], "upstream_result_refs": []}

NEEDS_THREE = [
    {"need_id": "need_f", "category": "food_assistance",   "subcategory": None, "description": "Food", "urgency": "high"},
    {"need_id": "need_h", "category": "housing_assistance","subcategory": None, "description": "Housing", "urgency": "high"},
    {"need_id": "need_i", "category": "income_assistance", "subcategory": None, "description": "Income", "urgency": "high"},
]


def retrieve(zip_code):
    r = copy.deepcopy(BASE)
    r.update(role_id="agent_3", task_type="retrieve_candidates",
             payload={"needs": NEEDS_THREE, "geography": [zip_code], "retrieval_constraints": []})
    return agent_3.handle(r)


class T11_ZipListMapping(unittest.TestCase):
    """ZIPs on the saccounty.gov list map to Sacramento County with COUNTY_FROM_ZIP_FALLBACK warning."""

    def _assert_sac_warning(self, out, zip_code):
        warns = [i for i in out["issues"] if i["code"] == "COUNTY_FROM_ZIP_FALLBACK"]
        self.assertEqual(len(warns), 1, f"Expected 1 COUNTY_FROM_ZIP_FALLBACK for {zip_code}, got {warns}")
        self.assertEqual(warns[0]["severity"], "warning")
        self.assertIn("saccounty.gov", warns[0]["message"])
        self.assertEqual(warns[0]["related_ref"], zip_code)

    def _assert_has_sac_programs(self, out):
        pids = {c["program_id"] for c in out["result"]["candidate_programs"]}
        self.assertTrue(pids, "Expected at least one candidate program for a Sacramento ZIP")

    def test_95660_maps_to_sacramento(self):
        """95660 (North Highlands area) is on the county map → Sacramento County programs found."""
        out = retrieve("95660")
        self._assert_sac_warning(out, "95660")
        self._assert_has_sac_programs(out)

    def test_95757_maps_to_sacramento(self):
        """95757 (Elk Grove area) is on the county map → Sacramento County programs found."""
        out = retrieve("95757")
        self._assert_sac_warning(out, "95757")
        self._assert_has_sac_programs(out)

    def test_95670_maps_to_sacramento(self):
        """95670 (Rancho Cordova area) is on the county map → Sacramento County programs found."""
        out = retrieve("95670")
        self._assert_sac_warning(out, "95670")
        self._assert_has_sac_programs(out)


class T12_ZipListNonMatch(unittest.TestCase):
    """ZIPs not on the list produce unresolved geography (partial), not a coverage gap."""

    def _assert_unresolved(self, out, zip_code):
        codes = {i["code"] for i in out["issues"]}
        self.assertIn("GEOGRAPHY_UNRESOLVED", codes, f"Expected GEOGRAPHY_UNRESOLVED for {zip_code}")
        self.assertNotIn("COVERAGE_GAP", codes, f"Should not see COVERAGE_GAP for unresolved ZIP {zip_code}")
        self.assertEqual(out["status"], "partial", f"Expected partial status for unresolved ZIP {zip_code}")
        self.assertEqual(out["result"]["candidate_programs"], [],
                         f"Should return no programs for unresolved ZIP {zip_code}")

    def test_95812_not_on_list_is_unresolved(self):
        """95812 is a PO-box-only ZIP not on the county map → unresolved geography, not 'no programs'."""
        out = retrieve("95812")
        self._assert_unresolved(out, "95812")

    def test_90210_not_on_list_is_unresolved(self):
        """90210 is a Beverly Hills ZIP → unresolved geography, not 'no programs'."""
        out = retrieve("90210")
        self._assert_unresolved(out, "90210")


class T13_ZipFileStructure(unittest.TestCase):
    """The ZIP file itself has the expected shape: 61 unique 5-digit ZIPs plus source_url and checked_at."""

    def test_zip_file_shape(self):
        path = os.path.join(os.path.dirname(__file__), "..", "..", "navigator", "kb", "sacramento_county_zips.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("source_url", data, "Missing source_url")
        self.assertIn("checked_at", data, "Missing checked_at")
        zips = data["zips"]
        unique = set(zips)
        self.assertEqual(len(unique), 61, f"Expected 61 unique ZIPs, got {len(unique)}")
        for z in zips:
            self.assertRegex(z, r"^\d{5}$", f"Not a 5-digit string: {z!r}")
        # SAC_COUNTY_ZIPS loaded at import time should equal the file's unique ZIP set
        self.assertEqual(SAC_COUNTY_ZIPS, unique)


if __name__ == "__main__":
    unittest.main()
