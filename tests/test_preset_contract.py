import unittest
from pathlib import Path


class PresetContractTests(unittest.TestCase):
    repo_root = Path(__file__).resolve().parents[1]

    def read(self, relative_path):
        return (self.repo_root / relative_path).read_text(encoding="utf-8")

    def test_analyze_report_has_severity_sections_and_routes(self):
        command = self.read("commands/speckit.analyze.md")
        text = self.read("templates/analysis-report-template.md")
        report_path = "./.auxiliary/docs/specs-analysis-repo/[spec-dir]-analysis.md"
        for source in (command, text):
            self.assertNotIn(".prepare", source)
            self.assertIn(report_path, source)
        for heading in ("Critical", "High", "Medium", "Low"):
            self.assertIn(heading, text)
        for field in ("问题键", "证据", "影响", "修复入口命令", "具体修改建议", "验证判据"):
            self.assertIn(field, text)
        for route in ("speckit.clarify", "speckit.plan", "speckit.tasks"):
            self.assertIn(route, text)
