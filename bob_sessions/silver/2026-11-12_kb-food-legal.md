# Bob session — KB Nov 12: food pantries, Salvation Army rent help, LSNC tenant legal help
**Date:** 2026-11-12  
**Branch:** silver/kb-food-legal  
**Owner:** Silver Sanchez Cardenas

---

## What was done

### 1. Branch setup
- Pulled `main` (fast-forwarded to include the ZIP-list PR).
- Created branch `silver/kb-food-legal` from the updated `main`.

### 2. Copy records_nov12.py
- Copied `records_nov12.py` from `<repo>/../navigator/kb/tools/` (Silverwork folder) to `<repo>/navigator/kb/tools/records_nov12.py`.
- File was already present in the Silverwork workspace folder (authored by Silver, Nov 12, 2026).

### 3. Edit build_kb.py
Added 4 lines immediately before `out = {"schema_version"` in `<repo>/navigator/kb/tools/build_kb.py`:

```python
import sys as _sys; _sys.path.insert(0, HERE)
from records_nov12 import build as build_nov12
_p, _e = build_nov12(ev_row, assemble)
programs += _p; evidence += _e
```

### 4. Build and validate
```
python3 navigator/kb/tools/build_kb.py
→ 11 programs, 200 evidence records -> navigator/kb/kb_sacramento.json

python3 navigator/kb/tools/validate_kb.py
→ ERRORS: none
  prog_food_calfresh_sac_001: 55 evidence | conflicting=0, needs_review=3, unverified=0, verified=52
  prog_income_edd_ui_ca_001: 29 evidence | conflicting=0, needs_review=0, unverified=0, verified=29
  prog_housing_saintjohns_sac_001: 17 evidence | conflicting=0, needs_review=0, unverified=0, verified=17
  prog_housing_coordaccess_sac_001: 12 evidence | conflicting=0, needs_review=0, unverified=0, verified=12
  prog_food_rivercity_midtown_sac_001: 17 evidence | conflicting=1, needs_review=0, unverified=0, verified=16
  prog_food_rivercity_arden_sac_001: 17 evidence | conflicting=1, needs_review=0, unverified=0, verified=16
  prog_food_salvationarmy_pantry_sac_001: 10 evidence | conflicting=0, needs_review=0, unverified=0, verified=10
  prog_housing_salvationarmy_rent_sac_001: 12 evidence | conflicting=0, needs_review=1, unverified=0, verified=11
  prog_food_sfbfs_foodfinder_sac_001: 9 evidence | conflicting=0, needs_review=0, unverified=0, verified=9
  prog_food_elkgrove_foodbank_sac_001: 10 evidence | conflicting=0, needs_review=0, unverified=0, verified=10
  prog_housing_lsnc_sac_001: 12 evidence | conflicting=0, needs_review=1, unverified=0, verified=11
```

### 5. SOURCES.md
Updated `<repo>/navigator/kb/SOURCES.md`:
- Count line updated: **21 → 32 source links, 9 → 15 sites, 8 → 13 owners**.
- 6 new rows added: `rivercityfoodbank.org`, `www.salvationarmyusa.org`, `sacramento.salvationarmy.org`, `www.sacramentofoodbank.org`, `elkgrovefoodbank.org`, `lsnc.net`.
- Footer note updated: "7 of the 9" → "12 of the 15 sites have no confirmed terms page".

### 6. Agent 4 rule — EDD + reduced_hours
No code change needed: Agent 4 does not evaluate `employment_status` at all, so `reduced_hours` already produces `potential_match`. Added **T11** to document and guard the rule.

### 7. New tests (T11, T12) in test_agents_3_4_5.py

**T11 — EDD reduced_hours:**
```python
class T11_EddReducedHours(unittest.TestCase):
    def test_reduced_hours_is_potential_match_not_mismatch(self):
        # employment_status=reduced_hours + confirmed Sacramento County location
        # → potential_match for EDD UI, never confirmed_mismatch
```

**T12 — Nov 12 programs:**
```python
class T12_Nov12Programs(unittest.TestCase):
    def test_zip_95660_food_need_returns_food_pantry_programs(self):
        # ZIP 95660 + food need → all 6 food programs returned

    def test_salvation_army_rent_help_stays_potential_match_eviction_unknown(self):
        # Unknown eviction notice → never mismatch for Salvation Army rent help

    def test_river_city_nov20_availability_is_conflicting(self):
        # Agent 5: ev_rcfbmt_014 / ev_rcfbar_014 → conflicting for both sites
```

### 8. Silver's existing tests updated (counts/lists only)
All changes are in `<repo>/tests/agent_3_4_5/test_agents_3_4_5.py`.

| Test | Change |
|---|---|
| T1 `test_all_three_needs_covered` | `assertEqual(by, {4 programs})` → per-program `assertIn` loop (KB now returns 11) |
| T6 `test_zip_only_still_works_locally` | `4` → `11` |
| T6 `test_subcategory_orders_but_does_not_filter` | `assertEqual(ids, [SJ, CAS])` → `assertIn` + ordering check |
| T7 `test_1_unknown_category_is_input_error_not_gap` | `assertEqual(candidates, [CALFRESH])` → `assertIn(CALFRESH)` + all-food loop |
| T9 `test_3_1_truncation_is_reported` | `"2 candidate(s) found, 1 returned"` → `"4 candidate(s) found, 1 returned"` |

No tests owned by other team members were changed.

### 9. Full test run
```
python3 -m unittest discover tests -v
Ran 225 tests in 3.748s
OK
```

### 10. Example run — ZIP 95660 + reduced_hours
Script: `<repo>/navigator/samples/demo_95660_reduced_hours.py`

Input:
```
Story:             'I have problems with housing and food. I need help.'
ZIP:               95660
Employment status: reduced_hours  (partially unemployed)
```

Agent 3 retrieved 11 programs (4 housing, 6 food, 1 income).  
Agent 4: all 11 → `potential_match` (EDD is `potential_match`, not mismatch).  
Agent 5 highlights:
- River City Midtown + Arden: `availability: [conflicting]` (Nov 20 conflict)
- Salvation Army rent help: `availability: [needs_review]` (funding availability unknown)
- All others: `availability: [verified]`

### 11. README updated
Added:
- Build/test commands under Quick Start.
- KB table (11 programs, availability, category).
- Source count reference.

### 12. Commits on silver/kb-food-legal
| SHA | Message |
|---|---|
| 324e9f3 | KB Nov 12: food pantries, Salvation Army rent help, LSNC tenant legal help |
| 05bbff9 | T9: use exact count '4 candidate(s) found, 1 returned' in truncation test |
| 3dabd33 | Demo: show all 11 programs in Agent 5 (remove [:6] cap) |

---

## Files changed

| File | Change |
|---|---|
| `navigator/kb/tools/records_nov12.py` | new — 7 programs, 200 evidence records total |
| `navigator/kb/tools/build_kb.py` | +4 lines before `out = {"schema_version"` |
| `navigator/kb/kb_sacramento.json` | rebuilt: 11 programs, 200 evidence records |
| `navigator/kb/history/superseded_evidence.json` | rebuilt (no new superseded rows) |
| `navigator/kb/SOURCES.md` | +6 source rows, counts updated |
| `tests/agent_3_4_5/test_agents_3_4_5.py` | T11 + T12 added; T1/T6/T7/T9 updated for expanded KB |
| `navigator/samples/demo_95660_reduced_hours.py` | new demo script |
| `navigator/samples/demo_95660_reduced_hours.txt` | story text file |
| `README.md` | KB table + build/test commands added |
