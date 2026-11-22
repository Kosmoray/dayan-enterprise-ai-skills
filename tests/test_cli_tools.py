#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Dayan Qianji Enterprise AI Skills CLI Tools & Skill Catalog.
Run: python3 -m unittest discover -s tests -v
"""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


class TestDayanEnterpriseSkills(unittest.TestCase):
    def test_all_66_skills_have_valid_frontmatter(self):
        skills = sorted((REPO_ROOT / "skills").glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skills), 66)
        for sf in skills:
            content = sf.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"), f"Missing frontmatter in {sf}")
            self.assertIn("name:", content)
            self.assertIn("description:", content)
            self.assertGreaterEqual(len(content), 800)

    def test_humanize_linter_detects_slop_and_meta_leaks(self):
        sample = REPO_ROOT / "examples" / "sample_ai_slop.md"
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "dayan_humanize_lint.py"), str(sample), "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(proc.stdout)
        self.assertGreaterEqual(data["ai_slop_score"], 50)
        severities = {f["severity"] for f in data["findings"]}
        self.assertIn("CRITICAL", severities)
        self.assertIn("WARN", severities)

    def test_contract_quickscan_detects_back_to_back_and_ip_traps(self):
        sample = REPO_ROOT / "examples" / "sample_b2b_contract.md"
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "dayan_contract_quickscan.py"), str(sample), "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(proc.stdout)
        self.assertIn("黑灯阻断", data["verdict"])
        levels = {h["level"] for h in data["clause_hits"]}
        self.assertIn("BLACK", levels)
        self.assertIn("RED", levels)

    def test_html_compiler_generates_executive_single_file_html(self):
        sample = REPO_ROOT / "examples" / "sample_ai_slop.md"
        with tempfile.TemporaryDirectory() as td:
            out_html = pathlib.Path(td) / "brief.html"
            subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "dayan_html_compiler.py"), str(sample), str(out_html)],
                capture_output=True,
                text=True,
                check=True,
            )
            rendered = out_html.read_text(encoding="utf-8")
            self.assertIn("#1B365D", rendered)
            self.assertIn("#D7263D", rendered)
            self.assertIn("dayanqianji.com", rendered)
            self.assertIn("18628016927", rendered)

    def test_skill_finder_matches_chinese_business_queries(self):
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "dayan_skill_finder.py"), "合同"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("dayan-contract-4way-audit", proc.stdout)


if __name__ == "__main__":
    unittest.main()
