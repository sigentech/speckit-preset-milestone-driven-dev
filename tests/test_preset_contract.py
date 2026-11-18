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

    def test_rectify_uses_strict_phase_order_and_regression(self):
        text = self.read("commands/speckit.rectify.md")
        clarify = text.index("speckit.clarify 阶段")
        plan = text.index("speckit.plan 阶段")
        tasks = text.index("speckit.tasks 阶段")
        self.assertLess(clarify, plan)
        self.assertLess(plan, tasks)
        self.assertIn("按 Critical → High → Medium → Low", text)
        self.assertIn("回到最早受影响阶段", text)
        self.assertIn("同一稳定问题键连续两轮", text)
        self.assertIn(
            "不是恰好 `speckit.clarify`、`speckit.plan`、`speckit.tasks` 中的一个",
            text,
        )
        self.assertIn("请求用户重跑 `speckit.analyze`", text)
        self.assertIn("不得自行映射或忽略该问题", text)

    def test_acceptance_simulation_contract(self):
        command_path = self.repo_root / "commands/speckit.simulate-acceptance.md"
        template_path = self.repo_root / "templates/acceptance-simulation-template.md"
        self.assertTrue(command_path.is_file(), "acceptance simulation command is missing")
        self.assertTrue(template_path.is_file(), "acceptance simulation template is missing")

        command = self.read("commands/speckit.simulate-acceptance.md")
        template = self.read("templates/acceptance-simulation-template.md")
        acceptance = self.read("commands/speckit.acceptance.md")
        implementation_report = self.read("templates/implementation-report-template.md")

        for status in ("AI_PASS", "AI_FAIL", "HUMAN_REQUIRED", "BLOCKED"):
            self.assertIn(status, command)
            self.assertIn(status, template)
        for field in ("前置条件", "操作步骤", "预期结果", "判定标准", "记录位置"):
            self.assertIn(field, template)

        self.assertIn("specs/[NNN-mX-slug]/acceptance-simulation.md", command)
        self.assertIn("Converged", command)
        self.assertIn("不得伪造", command)
        self.assertIn("实际执行", command)
        for route in ("speckit.clarify", "speckit.plan", "speckit.tasks", "speckit.implement"):
            self.assertIn(route, command)
        for section in ("基线", "汇总", "全部验收项结果", "AI_PASS 明细", "AI_FAIL 明细", "人工待验", "结论"):
            self.assertIn(section, template)
        for field in (
            "验收目标",
            "前置条件与环境",
            "测试数据/输入",
            "可观察的预期结果",
            "通过/不通过/阻塞",
            "为什么 Agent 不能可靠完成",
        ):
            self.assertIn(field, template)

        self.assertIn("speckit.converge", acceptance)
        self.assertIn("Converged", acceptance)
        self.assertIn("acceptance-simulation.md", acceptance)
        self.assertIn("AI_PASS", acceptance)
        self.assertIn("AI_FAIL", acceptance)
        self.assertIn("baseline", acceptance)
        self.assertIn("过期", acceptance)
        self.assertIn("全人工验收", acceptance)
        self.assertIn("不得生成", acceptance)
        self.assertIn("即使 baseline 已过期", acceptance)
        self.assertIn("状态数量", acceptance)
        self.assertIn("结论与逐项状态一致", acceptance)

        for field in ("验收状态", "证据", "模拟结果来源", "模拟 baseline", "人工指南"):
            self.assertIn(field, implementation_report)
        self.assertIn(
            "./.auxiliary/docs/specs-analysis-repo/[spec-dir]-analysis.md",
            implementation_report,
        )

        with self.subTest("source-to-simulation coverage"):
            for source_key in ("spec:AC-01", "milestone:Mx-UA-01", "tasks:T012-manual"):
                self.assertIn(source_key, command)
                self.assertIn(source_key, template)
            self.assertIn("期望验收集", command)
            self.assertIn("来源覆盖校验", template)
            self.assertIn("来源键", template)
            self.assertIn("恰好一次", acceptance)
            self.assertIn("独立重算", acceptance)
            self.assertIn("缺失、额外或重复", acceptance)
            self.assertIn("来源覆盖", implementation_report)

        with self.subTest("clean worktree freshness"):
            status_command = "git status --porcelain=v1 --untracked-files=all"
            self.assertIn(status_command, command)
            self.assertIn(status_command, acceptance)
            self.assertIn("工作区清洁基线", command)
            self.assertIn("工作区清洁基线", template)
            self.assertIn("已跟踪或未跟踪", acceptance)
            self.assertIn("过期", acceptance)
            self.assertIn("工作区清洁基线", implementation_report)

        with self.subTest("successful command evidence"):
            self.assertIn("退出码必须为 0", command)
            self.assertIn("退出码必须为 0", acceptance)
            self.assertIn("预期非零成功契约", command)
            self.assertIn("预期非零成功契约", template)
            self.assertIn("预期非零成功契约", acceptance)
            self.assertNotIn("[0 或其他]", template)
            self.assertIn("AI_PASS 成功证据", implementation_report)

    def test_workflow_hands_off_through_converge(self):
        implement = self.read("commands/speckit.implement.md")
        acceptance = self.read("commands/speckit.acceptance.md")
        navigator = self.read("templates/agents-reminder-template.md")

        self.assertIn("agent: speckit.converge", implement)
        self.assertNotIn("agent: speckit.acceptance", implement)
        self.assertIn("Agent 可执行", implement)
        self.assertIn("需人工", implement)
        self.assertIn("./.auxiliary/docs/specs-analysis-repo/[spec-dir]-analysis.md", implement)
        self.assertNotIn(".prepare", implement)
        self.assertIn("追加任务", implement)
        self.assertIn("回到 `speckit.implement`", implement)
        self.assertIn("仍然运行 `speckit.converge`", implement)
        self.assertLess(
            implement.index("agent: speckit.converge"),
            implement.index("/speckit.simulate-acceptance"),
        )
        self.assertLess(
            implement.index("/speckit.simulate-acceptance"),
            implement.index("/speckit.acceptance"),
        )

        self.assertIn("speckit.converge", acceptance)
        self.assertIn("无法确认", acceptance)
        self.assertIn("先运行 `/speckit.converge`", acceptance)
        self.assertIn("不得生成验收报告", acceptance)
        self.assertLess(
            acceptance.index("/speckit.converge"),
            acceptance.index("/speckit.simulate-acceptance"),
        )
        self.assertLess(
            acceptance.index("/speckit.simulate-acceptance"),
            acceptance.index("/speckit.acceptance"),
        )

        self.assertIn("speckit-preset:milestone-driven-dev v1.6.0", navigator)
        self.assertIn("/speckit.converge", navigator)
        self.assertIn("/speckit.simulate-acceptance", navigator)
        self.assertIn("需人工", navigator)
        self.assertLess(navigator.index("/speckit.converge"), navigator.index("/speckit.simulate-acceptance"))
        self.assertLess(
            navigator.index("/speckit.simulate-acceptance"),
            navigator.index("/speckit.acceptance"),
        )
        self.assertFalse(
            (self.repo_root / "commands/speckit.converge.md").exists(),
            "the preset must reuse core speckit.converge",
        )
