import hashlib
import re
import unittest
import unicodedata
from pathlib import Path
from tempfile import TemporaryDirectory


class PresetContractTests(unittest.TestCase):
    repo_root = Path(__file__).resolve().parents[1]

    def read(self, relative_path):
        return (self.repo_root / relative_path).read_text(encoding="utf-8")

    def markdown_section(self, text, heading):
        match = re.search(
            rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, f"missing markdown section: {heading}")
        return match.group(1)

    def markdown_table_rows(self, text, heading):
        section = self.markdown_section(text, heading)
        rows = []
        data_started = False
        for line in section.splitlines():
            if not line.startswith("|"):
                continue
            if line.startswith("| ---"):
                data_started = True
                continue
            if not data_started:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            rows.append(cells)
        return rows

    @staticmethod
    def canonicalize_criterion(text):
        normalized = unicodedata.normalize("NFC", text)
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
        normalized = normalized.strip()
        return re.sub(r"\s+", " ", normalized)

    @classmethod
    def criterion_fingerprint(cls, text):
        canonical = cls.canonicalize_criterion(text).encode("utf-8")
        return "sha256:" + hashlib.sha256(canonical).hexdigest()

    @classmethod
    def simulation_row_authenticates(
        cls,
        source_key,
        source_text,
        row_key,
        row_text,
        row_fingerprint,
    ):
        if not source_key or source_key != row_key or not source_text or not row_text:
            return False
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", row_fingerprint or ""):
            return False
        return (
            cls.canonicalize_criterion(source_text) == cls.canonicalize_criterion(row_text)
            and cls.criterion_fingerprint(source_text) == row_fingerprint
        )

    def legacy_directory_aliases(self):
        return ("." + "prepared", "." + "prepare")

    def find_legacy_alias_matches(self, root=None):
        scan_root = Path(root) if root is not None else self.repo_root
        binary_suffixes = {
            ".7z",
            ".bmp",
            ".class",
            ".db",
            ".dll",
            ".dylib",
            ".exe",
            ".gif",
            ".gz",
            ".ico",
            ".jar",
            ".jpeg",
            ".jpg",
            ".mov",
            ".mp3",
            ".mp4",
            ".o",
            ".otf",
            ".pdf",
            ".png",
            ".so",
            ".sqlite",
            ".sqlite3",
            ".tar",
            ".tgz",
            ".ttf",
            ".wav",
            ".webm",
            ".webp",
            ".woff",
            ".woff2",
            ".xls",
            ".xlsx",
            ".zip",
        }
        ignored_directories = {".git", ".superpowers", "__pycache__"}
        matches = []

        for path in scan_root.rglob("*"):
            if not path.is_file():
                continue
            if ignored_directories.intersection(path.parts):
                continue
            if path.suffix.lower() in binary_suffixes:
                continue

            relative_path = path.relative_to(scan_root).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                self.fail(f"non-binary source file is not UTF-8: {relative_path}: {exc}")

            for alias in self.legacy_directory_aliases():
                if alias in text:
                    matches.append(f"{relative_path}: {alias}")

        return matches

    def test_repository_alias_scan_checks_extensionless_and_unknown_text(self):
        alias = self.legacy_directory_aliases()[1]

        for filename in ("NOTICE", "notes.rst"):
            with self.subTest(filename=filename):
                with TemporaryDirectory(
                    prefix=".alias-scan-fixture-",
                ) as temp_dir:
                    fixture = Path(temp_dir) / filename
                    fixture.write_text(f"prefix {alias} suffix", encoding="utf-8")

                    matches = self.find_legacy_alias_matches(temp_dir)
                    self.assertEqual(1, len(matches))
                    self.assertIn(filename, matches[0])

    def test_repository_alias_scan_skips_known_binary_formats(self):
        alias = self.legacy_directory_aliases()[1]

        with TemporaryDirectory(prefix=".alias-scan-fixture-") as temp_dir:
            fixture = Path(temp_dir) / "image.png"
            fixture.write_bytes(alias.encode("utf-8"))

            self.assertEqual([], self.find_legacy_alias_matches(temp_dir))

    def test_repository_alias_scan_fails_on_undecodable_unknown_file(self):
        with TemporaryDirectory(
            prefix=".alias-scan-fixture-",
        ) as temp_dir:
            fixture = Path(temp_dir) / "opaque.asset"
            fixture.write_bytes(b"\xff\xfe\xfa")

            with self.assertRaisesRegex(AssertionError, "not UTF-8"):
                self.find_legacy_alias_matches(temp_dir)

    def test_release_metadata_and_default_directory(self):
        manifest = self.read("preset.yml")
        readme_en = self.read("README.md")
        readme_zh = self.read("README.zh-CN.md")

        self.assertIn('version: "1.6.0"', manifest)
        self.assertIn('speckit_version: ">=1.0.9"', manifest)
        self.assertIn(".auxiliary/docs/specs-analysis-repo/", manifest)
        self.assertEqual(manifest.count('type: "command"'), 15)
        self.assertEqual(manifest.count('type: "template"'), 11)
        self.assertIn('name: "speckit.simulate-acceptance"', manifest)
        self.assertIn('name: "acceptance-simulation-template"', manifest)
        for text in (readme_en, readme_zh):
            self.assertIn("v1.6.0", text)
            self.assertIn("/speckit.converge", text)
            self.assertIn("/speckit.simulate-acceptance", text)
            self.assertIn(".auxiliary", text)
            self.assertIn("analysis_report_dir: <path>", text)
            self.assertIn("[spec-dir]-analysis.md", text)

        acceptance_entry = re.search(
            r'- type: "command"\s+'
            r'name: "speckit\.acceptance"\s+'
            r'file: "[^"]+"\s+'
            r'description: "([^"]+)"',
            manifest,
        )
        self.assertIsNotNone(acceptance_entry, "acceptance command metadata is missing")
        acceptance_description = acceptance_entry.group(1)
        for term in (
            "converge gate",
            "simulation import",
            "stale fallback",
            "AI_FAIL blocks acceptance",
        ):
            self.assertIn(term, acceptance_description)

    def test_repository_has_no_legacy_auxiliary_directory_alias(self):
        matches = self.find_legacy_alias_matches()
        self.assertEqual([], matches, "legacy auxiliary directory aliases remain")

    def test_analyze_report_has_severity_sections_and_routes(self):
        command = self.read("commands/speckit.analyze.md")
        text = self.read("templates/analysis-report-template.md")
        report_path = "./.auxiliary/docs/specs-analysis-repo/[spec-dir]-analysis.md"
        for source in (command, text):
            for alias in self.legacy_directory_aliases():
                self.assertNotIn(alias, source)
            self.assertIn(report_path, source)
        for heading in ("Critical", "High", "Medium", "Low"):
            self.assertIn(heading, text)
        for field in ("问题键", "证据", "影响", "修复入口命令", "具体修改建议", "验证判据"):
            self.assertIn(field, text)
        for route in ("speckit.clarify", "speckit.plan", "speckit.tasks"):
            self.assertIn(route, text)

    def test_rectify_uses_strict_phase_order_and_regression(self):
        text = self.read("commands/speckit.rectify.md")
        algorithm = self.markdown_section(text, "执行算法")
        clarify = algorithm.index("speckit.clarify 阶段")
        plan = algorithm.index("speckit.plan 阶段")
        tasks = algorithm.index("speckit.tasks 阶段")
        self.assertLess(clarify, plan)
        self.assertLess(plan, tasks)
        self.assertIn("按 Critical → High → Medium → Low", algorithm)
        self.assertIn("回到最早受影响阶段", algorithm)
        self.assertIn("同一稳定问题键连续两轮", algorithm)
        self.assertIn(
            "不是恰好 `speckit.clarify`、`speckit.plan`、`speckit.tasks` 中的一个",
            algorithm,
        )
        self.assertIn("请求用户重跑 `speckit.analyze`", algorithm)
        self.assertIn("不得自行映射或忽略该问题", algorithm)

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

        with self.subTest("criterion fingerprint authentication"):
            for text in (command, template, acceptance, implementation_report):
                self.assertIn("判据指纹", text)
                self.assertIn("sha256:<hex>", text)
            for text in (command, acceptance):
                for phrase in (
                    "Unicode NFC",
                    "行尾统一为 LF",
                    "去掉首尾空白",
                    "内部连续空白折叠为一个空格",
                    "UTF-8",
                ):
                    self.assertIn(phrase, text)
            self.assertIn("来源键与判据指纹", acceptance)
            self.assertIn("判据文本缺失、被替换或无法解析", acceptance)
            self.assertIn("整个模拟失效", acceptance)
            self.assertIn("即使 baseline 已过期", acceptance)

            source_text = "  Accept the file\r\n  only after validation.  "
            correct_fingerprint = self.criterion_fingerprint(source_text)
            source_key = "spec:AC-01"
            row_key = source_key
            self.assertEqual(
                "sha256:20bbd5fabd1a397ffa8e0e316930c4ef2986cd5288ee237c71cfd361698bfa6e",
                correct_fingerprint,
            )
            self.assertTrue(
                self.simulation_row_authenticates(
                    source_key,
                    source_text,
                    row_key,
                    "Accept the file only after validation.",
                    correct_fingerprint,
                )
            )
            self.assertFalse(
                self.simulation_row_authenticates(
                    source_key,
                    source_text,
                    row_key,
                    "Accept any file without validation.",
                    correct_fingerprint,
                ),
                "a correct stable key and stale fingerprint must not authenticate altered text",
            )
            for malformed_fingerprint in ("", "sha256:", "sha256:not-hex", "sha256:" + "A" * 64):
                self.assertFalse(
                    self.simulation_row_authenticates(
                        source_key,
                        source_text,
                        row_key,
                        "Accept the file only after validation.",
                        malformed_fingerprint,
                    )
                )

        with self.subTest("simulation rerun lifecycle"):
            self.assertIn("现有 `implementation-report.md`", command)
            self.assertIn("未提交", command)
            self.assertIn("提交或移除", command)
            self.assertIn("重新运行模拟", command)

    def test_analysis_report_directory_resolution_is_shared(self):
        files = (
            "commands/speckit.analyze.md",
            "commands/speckit.rectify.md",
            "commands/speckit.implement.md",
            "commands/speckit.acceptance.md",
            "templates/analysis-report-template.md",
            "templates/implementation-report-template.md",
            "preset.yml",
            "README.md",
            "README.zh-CN.md",
            "docs/superpowers/specs/2026-11-18-auxiliary-rectify-converge-design.md",
            "docs/superpowers/plans/2026-11-18-auxiliary-rectify-converge.md",
        )
        default_directory = "./.auxiliary/docs/specs-analysis-repo/"

        for relative_path in files:
            with self.subTest(path=relative_path):
                text = self.read(relative_path)
                self.assertIn("analysis_report_dir: <path>", text)
                self.assertIn(default_directory, text)
                self.assertIn("[spec-dir]-analysis.md", text)

        for relative_path in files[:6]:
            with self.subTest(parser_contract=relative_path):
                text = self.read(relative_path)
                self.assertIn("唯一一行", text)
                self.assertIn("重复", text)
                self.assertIn("空", text)

    def test_readmes_number_all_twelve_command_stages_in_flow_order(self):
        expected_commands = [
            "prototype",
            "specify",
            "clarify",
            "plan",
            "tasks",
            "analyze",
            "rectify",
            "implement",
            "converge",
            "simulate-acceptance (optional)",
            "acceptance",
            "release",
        ]

        for relative_path, heading in (
            ("README.md", "The Milestone Loop (Twelve Steps per Mx)"),
            ("README.zh-CN.md", "里程碑开发循环（每个 Mx 的十二步）"),
        ):
            with self.subTest(path=relative_path):
                rows = self.markdown_table_rows(self.read(relative_path), heading)
                self.assertEqual(13, len(rows), "expected one branch row plus twelve numbered stages")
                self.assertEqual("", rows[0][0], "the branch action must remain unnumbered")
                branch_row = " ".join(rows[0]).lower()
                self.assertTrue(
                    "branch" in branch_row or "分支" in branch_row,
                    "the unnumbered row must identify the branch action",
                )
                command_rows = rows[1:]
                self.assertEqual(
                    [str(index) for index in range(1, 13)],
                    [row[0] for row in command_rows],
                )
                actual_commands = []
                for row in command_rows:
                    command = re.sub(r"^speckit\.", "", row[1])
                    command = command.replace("（可选）", " (optional)")
                    actual_commands.append(command)
                self.assertEqual(expected_commands, actual_commands)
                implement_row = next(row for row in command_rows if row[1] == "speckit.implement")
                converge_row = next(row for row in command_rows if row[1] == "speckit.converge")
                self.assertIn("converge", " ".join(implement_row).lower())
                self.assertIn("implement", " ".join(converge_row).lower())

    def test_acceptance_snapshots_before_and_rechecks_after_verification(self):
        acceptance = self.read("commands/speckit.acceptance.md")
        implementation_report = self.read("templates/implementation-report-template.md")
        steps = self.markdown_section(acceptance, "执行步骤")
        preconditions = steps.split("2. **校验可选验收模拟**", maxsplit=1)[0]

        for marker in (
            "正式验收前置检查",
            "先扫描 `AI_FAIL`",
            "当前会话最近一次 `speckit.converge`",
            "来源键与判据指纹",
            "验证前快照",
        ):
            self.assertIn(marker, preconditions)
        for first, second in (
            (
                "当前会话最近一次 `speckit.converge`",
                "先扫描 `AI_FAIL`",
            ),
            (
                "先扫描 `AI_FAIL`",
                "来源键与判据指纹",
            ),
            (
                "来源键与判据指纹",
                "验证前快照",
            ),
        ):
            self.assertLess(preconditions.index(first), preconditions.index(second))

        verification_snapshot = steps.index("验证前快照")
        run_verification = steps.index("运行或引用自动化验证")
        post_check = steps.index("验证后复检")
        write_report = steps.index("写入报告")
        self.assertLess(verification_snapshot, run_verification)
        self.assertLess(run_verification, post_check)
        self.assertLess(post_check, write_report)

        snapshot_section = steps[
            verification_snapshot:
            steps.index("3. **采集实现事实**")
        ]
        recheck_section = steps[
            steps.index("5. **验证后复检"):
            write_report
        ]
        for text in (snapshot_section, recheck_section):
            self.assertIn("`git rev-parse HEAD`", text)
            self.assertIn("`git status --porcelain=v1 --untracked-files=all`", text)
            for artifact in ("spec.md", "plan.md", "tasks.md"):
                self.assertIn(artifact, text)
            self.assertIn("SHA-256", text)
        for phrase in ("任一项不同", "模拟失效", "不得写入", "重新 converge"):
            self.assertIn(phrase, recheck_section)
        self.assertIn("验证前快照", implementation_report)
        self.assertIn("验证后复检", implementation_report)

    def test_docs_name_stale_ai_fail_exception_and_navigator_evidence_scope(self):
        readme_en = self.read("README.md")
        readme_zh = self.read("README.zh-CN.md")
        design = self.read(
            "docs/superpowers/specs/2026-11-18-auxiliary-rectify-converge-design.md"
        )
        navigator = self.read("templates/agents-reminder-template.md")

        self.assertIn(
            "A visible `AI_FAIL` blocks acceptance even when the baseline is stale.",
            readme_en,
        )
        self.assertIn(
            "只要存在可见的 `AI_FAIL`，即使 baseline 已过期，也阻止验收。",
            readme_zh,
        )
        self.assertIn("存档验收判据指纹", design)
        self.assertIn("可见的 `AI_FAIL`", design)
        self.assertIn("即使 baseline 已过期", design)
        self.assertIn("证据（文件系统/当前会话）", navigator)
        self.assertNotIn("证据（文件系统）", navigator)

    def test_workflow_hands_off_through_converge(self):
        implement = self.read("commands/speckit.implement.md")
        acceptance = self.read("commands/speckit.acceptance.md")
        navigator = self.read("templates/agents-reminder-template.md")

        self.assertIn("agent: speckit.converge", implement)
        self.assertNotIn("agent: speckit.acceptance", implement)
        self.assertIn("Agent 可执行", implement)
        self.assertIn("需人工", implement)
        self.assertIn("analysis_report_dir: <path>", implement)
        self.assertIn("./.auxiliary/docs/specs-analysis-repo/", implement)
        self.assertIn("[spec-dir]-analysis.md", implement)
        for alias in self.legacy_directory_aliases():
            self.assertNotIn(alias, implement)
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

        acceptance_steps = self.markdown_section(acceptance, "执行步骤")
        acceptance_preconditions = acceptance_steps.split(
            "2. **校验可选验收模拟**",
            maxsplit=1,
        )[0]
        self.assertIn("speckit.converge", acceptance_preconditions)
        self.assertIn("无法确认", acceptance_preconditions)
        self.assertIn("先运行 `/speckit.converge`", acceptance_preconditions)
        self.assertIn("不得生成验收报告", acceptance_preconditions)
        self.assertIn("先扫描 `AI_FAIL`", acceptance_preconditions)
        self.assertLess(
            acceptance_preconditions.index("/speckit.converge"),
            acceptance_preconditions.index("先扫描 `AI_FAIL`"),
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

    def test_navigator_prioritizes_simulation_failures(self):
        navigator = self.read("templates/agents-reminder-template.md")
        failure_rows = [
            line
            for line in navigator.splitlines()
            if "acceptance-simulation.md" in line and "AI_FAIL" in line
        ]

        self.assertEqual(1, len(failure_rows), "navigator needs one AI_FAIL priority row")
        failure_row = failure_rows[0]
        for route in (
            "/speckit.clarify",
            "/speckit.plan",
            "/speckit.tasks",
            "/speckit.implement",
        ):
            self.assertIn(route, failure_row)
        self.assertIn("恰好一个", failure_row)
        self.assertIn("/speckit.converge", failure_row)
        self.assertIn("/speckit.simulate-acceptance", failure_row)
        self.assertIn("/speckit.acceptance", failure_row)

        general_converged_row = "| converge 已报告 `Converged`"
        self.assertLess(
            navigator.index(failure_row),
            navigator.index(general_converged_row),
        )
