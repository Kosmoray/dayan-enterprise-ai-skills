#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Dayan Qianji Batch-01 Five Zero-Dependency Industry Calculators & Compliance Checkers.
Run: python3 -m unittest discover -s tests -v
"""

import json
import pathlib
import subprocess
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.industry import (  # noqa: E402
    cis_export_doc_checker,
    ev_station_tco_calc,
    gb7718_oem_quote_guard,
    gjb_kit_shortage_audit,
    vet_dose_compliance_check,
)

EXPECTED_FOOTER = "🏢 成都大衍千机科技有限公司 (天府长岛首家OPC) | https://dayanqianji.com/ | 微信: 18628016927"


class TestBatch01IndustryCalculators(unittest.TestCase):
    def test_01_ev_station_tco_math_and_critical_demand(self):
        # 2500 kVA * 28 = 70,000/month; critical demand = 70,000 / 38 = 1842.11 kW
        res_demand_win = ev_station_tco_calc.calculate_ev_station_tco(ev_station_tco_calc.DEMO_SCENARIO)
        grid = res_demand_win["grid_two_part_comparison"]
        self.assertAlmostEqual(grid["critical_demand_kw"], 1842.11, places=2)
        self.assertEqual(grid["recommended_billing"], "按实际最大需量计费")
        self.assertAlmostEqual(grid["annual_basic_fee_saving_yuan"], 178800.0, places=2)
        self.assertEqual(res_demand_win["decision"]["risk_level"], "GREEN")
        self.assertLess(res_demand_win["economics"]["static_payback_months"], 36.0)

        # When concurrent kw exceeds critical point (e.g. 2100 kW > 1842.11 kW), capacity tariff wins
        high_load = dict(ev_station_tco_calc.DEMO_SCENARIO, max_concurrent_kw=2100.0, contracted_demand_kw=2100.0)
        res_cap_win = ev_station_tco_calc.calculate_ev_station_tco(high_load)
        self.assertEqual(res_cap_win["grid_two_part_comparison"]["recommended_billing"], "按变压器容量计费")

        # Overrun > 105% contracted demand triggers double penalty alert and RED when volume is low
        low_vol_overrun = dict(
            ev_station_tco_calc.DEMO_SCENARIO,
            daily_kwh=6500.0,
            contracted_demand_kw=1200.0,
            max_concurrent_kw=1400.0,
        )
        res_red = ev_station_tco_calc.calculate_ev_station_tco(low_vol_overrun)
        self.assertGreater(res_red["grid_two_part_comparison"]["overrun_penalty_kw"], 0.0)
        self.assertEqual(res_red["decision"]["risk_level"], "RED")

    def test_02_vet_bsa_formula_and_human_drug_red_cards(self):
        # Dog 10 kg => W_g = 10000 => 10.1 * (10000**(2/3)) / 10000 = 0.4688 m²
        bsa_dog_10 = vet_dose_compliance_check.calc_bsa_m2("dog", 10.0)
        self.assertAlmostEqual(bsa_dog_10, 10.1 * (10000.0 ** (2.0 / 3.0)) / 10000.0, places=6)
        self.assertAlmostEqual(bsa_dog_10, 0.4688, places=4)

        # Cat 4 kg => W_g = 4000 => 10.0 * (4000**(2/3)) / 10000 = 0.2520 m²
        bsa_cat_4 = vet_dose_compliance_check.calc_bsa_m2("cat", 4.0)
        self.assertAlmostEqual(bsa_cat_4, 0.2520, places=4)

        batch = vet_dose_compliance_check.evaluate_batch(vet_dose_compliance_check.DEMO_PRESCRIPTIONS)
        self.assertEqual(batch["summary"]["total_prescriptions"], 3)
        # RX-01: Cat + acetaminophen + human drug without consent => RED
        r1 = batch["results"][0]
        self.assertEqual(r1["status"], "RED")
        codes_1 = {c["code"] for c in r1["red_cards"]}
        self.assertIn("CAT_ACETAMINOPHEN_LETHAL", codes_1)
        self.assertIn("HUMAN_DRUG_COMPLIANCE_RED_CARD", codes_1)

        # RX-02: Compliant vet drug 兽药字220152512 => GREEN
        r2 = batch["results"][1]
        self.assertEqual(r2["status"], "GREEN")

        # RX-03: Human drug in urgent list WITHOUT vet signed consent => RED
        r3 = batch["results"][2]
        self.assertEqual(r3["status"], "RED")
        self.assertIn("HUMAN_DRUG_COMPLIANCE_RED_CARD", {c["code"] for c in r3["red_cards"]})

    def test_03_gjb_kit_shortage_and_airgap_vram_sizing(self):
        rep = gjb_kit_shortage_audit.audit_gjb_kit_and_airgap(gjb_kit_shortage_audit.DEMO_GJB_WORKLOAD)
        self.assertEqual(rep["overall_status"], "RED")
        self.assertGreaterEqual(len(rep["red_cards"]), 1)
        self.assertEqual(rep["red_cards"][0]["code"], "EXPIRED_SPECIAL_VENDOR_CERT")

        # Verify shortage detection on first part and full kit on second part
        p1, p2 = rep["parts"][0], rep["parts"][1]
        self.assertFalse(p1["is_kitted"])
        self.assertIn("OP20", p1["first_shortage_bottleneck"])
        self.assertTrue(p2["is_kitted"])

        # Verify 32B & 70B VRAM calculation (FP16 > INT4, 70B > 32B)
        s32 = rep["airgap_llm_sizing"]["32B"]
        s70 = rep["airgap_llm_sizing"]["70B"]
        self.assertGreater(s32["total_vram_fp16_gb"], s32["total_vram_int4_gb"])
        self.assertGreater(s70["total_vram_int4_gb"], s32["total_vram_int4_gb"])
        self.assertGreater(s70["kv_cache_fp16_gb"], s32["kv_cache_fp16_gb"])

    def test_04_gb7718_antitroll_and_cooking_yield_tiers(self):
        rep = gb7718_oem_quote_guard.evaluate_oem_guard(gb7718_oem_quote_guard.DEMO_OEM_PAYLOAD)
        self.assertEqual(rep["status"], "RED")
        codes = {rf["code"] for rf in rep["label_audit"]["red_flags"]}
        self.assertIn("GB7718_2025_ZERO_ADDITIVE_BAN", codes)
        self.assertIn("EXTREME_OR_SPECIAL_SUPPLY_CLAIM", codes)
        self.assertIn("MEDICAL_EFFICACY_CLAIM", codes)
        self.assertIn("ALLERGEN_OMISSION_RED_CARD", codes)
        self.assertIn("NET_WEIGHT_FONT_HEIGHT_VIOLATION", codes)

        # Verify cooking yield amplification: 18.80 / 0.82 = 22.9268 -> 22.93, and tier monotonicity 500kg > 2T > 10T
        pricing = rep["oem_tier_pricing"]
        self.assertAlmostEqual(pricing["cooked_paste_cost_per_kg"], round(18.80 / 0.82, 2), places=2)
        t500 = pricing["tiers"]["500kg"]["taxed_breakeven_yuan_per_kg"]
        t2t = pricing["tiers"]["2T"]["taxed_breakeven_yuan_per_kg"]
        t10t = pricing["tiers"]["10T"]["taxed_breakeven_yuan_per_kg"]
        self.assertGreater(t500, t2t)
        self.assertGreater(t2t, t10t)

    def test_05_cis_vin_mod11_and_smgs_cross_check(self):
        # Standard mod-11 check digit verification (including '1', 'X', forbidden 'O', wrong check digit)
        v_ok_1 = cis_export_doc_checker.verify_vin_mod11("LGXC66C41R0125893")
        self.assertTrue(v_ok_1["is_valid"])
        self.assertEqual(v_ok_1["expected_check_digit"], "1")

        v_ok_x = cis_export_doc_checker.verify_vin_mod11("LZZ5CLNBXRN208427")
        self.assertTrue(v_ok_x["is_valid"])
        self.assertEqual(v_ok_x["expected_check_digit"], "X")

        v_bad_digit = cis_export_doc_checker.verify_vin_mod11("LZZ5CLNB0RN208427")
        self.assertFalse(v_bad_digit["is_valid"])
        self.assertEqual(v_bad_digit["expected_check_digit"], "X")

        v_forbidden_ioq = cis_export_doc_checker.verify_vin_mod11("LGXC66C41RO125893")
        self.assertFalse(v_forbidden_ioq["is_valid"])
        self.assertIn("禁用混淆字符", v_forbidden_ioq["error"])

        # Cross-document check on demo shipment catches VIN typo and 120kg SMGS weight mismatch
        rep = cis_export_doc_checker.cross_check_cis_documents(cis_export_doc_checker.DEMO_SHIPMENT_DOCS)
        self.assertEqual(rep["status"], "RED")
        disc_codes = {d["code"] for d in rep["red_discrepancies"]}
        self.assertIn("INVALID_VIN_CHECK_DIGIT", disc_codes)
        self.assertIn("VIN_CROSS_DOC_MISMATCH", disc_codes)
        self.assertIn("GROSS_WEIGHT_MISMATCH", disc_codes)

        # Clean shipment passes GREEN
        clean_bundle = json.loads(json.dumps(cis_export_doc_checker.DEMO_SHIPMENT_DOCS))
        clean_bundle["smgs_waybill"]["vins"] = ["LGXC66C41R0125893", "LZZ5CLNBXRN208427"]
        clean_bundle["smgs_waybill"]["gross_weight_kg"] = 11260.0
        clean_rep = cis_export_doc_checker.cross_check_cis_documents(clean_bundle)
        self.assertEqual(clean_rep["status"], "GREEN")

    def test_06_all_five_cli_scripts_demo_and_json_modes(self):
        script_names = [
            "ev_station_tco_calc.py",
            "vet_dose_compliance_check.py",
            "gjb_kit_shortage_audit.py",
            "gb7718_oem_quote_guard.py",
            "cis_export_doc_checker.py",
        ]
        for sname in script_names:
            spath = REPO_ROOT / "scripts" / "industry" / sname
            with self.subTest(script=sname, mode="demo-text"):
                proc_txt = subprocess.run(
                    [sys.executable, str(spath), "--demo"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.assertIn(EXPECTED_FOOTER, proc_txt.stdout)

            with self.subTest(script=sname, mode="demo-json"):
                proc_json = subprocess.run(
                    [sys.executable, str(spath), "--demo", "--json"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                parsed = json.loads(proc_json.stdout)
                self.assertIn("dayanqianji.com", parsed["powered_by"])
                self.assertIn("18628016927", parsed["powered_by"])


if __name__ == "__main__":
    unittest.main()
