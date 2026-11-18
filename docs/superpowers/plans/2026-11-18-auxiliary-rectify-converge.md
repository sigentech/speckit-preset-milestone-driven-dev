# `.auxiliary`、分级分析与收敛闭环 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 preset 升级到 `1.6.0`，统一分析目录、强化分级分析、实现三阶段 rectify 闭环、接入核心 converge，并增加可选的 Agent 预验收。

**Architecture:** 用标准库 Python 合同测试固定 manifest、命令、模板和双 README 的关键行为；随后按 analyze、rectify、simulate-acceptance、converge/navigator、目录与发布文档五个边界修改文件。上游 converge 保持原文，不在 preset 中 override。

**Tech Stack:** Markdown command templates、YAML manifest、Python 3 `unittest`、spec-kit CLI。

**Spec:** `docs/superpowers/specs/2026-11-18-auxiliary-rectify-converge-design.md`

## Global Constraints

- preset 版本必须为 `1.6.0`。
- `requires.speckit_version` 必须为 `>=1.0.9`。
- 不新增 `commands/speckit.converge.md`，直接复用核心 converge。
- 分析报告目录使用唯一规则：constitution 存在唯一一行 `analysis_report_dir: <path>` 时使用该目录，否则使用 `./.auxiliary/docs/specs-analysis-repo/`；文件名固定为 `[spec-dir]-analysis.md`。重复、空或不可解析的登记必须停止。
- analyze 的每条修复入口只能是一个：`speckit.clarify`、`speckit.plan`、`speckit.tasks`。
- rectify 顺序固定为 clarify 阶段 -> plan 阶段 -> tasks 阶段；下游引入上游问题时必须回退。
- simulate-acceptance 是验收前可选命令，状态固定为 `AI_PASS`、`AI_FAIL`、`HUMAN_REQUIRED`、`BLOCKED`。
- 每个模拟来源行同时记录稳定来源键和 `判据指纹: sha256:<hex>`；判据指纹使用 NFC、LF、去首尾空白、折叠内部空白后的 UTF-8 SHA-256。
- acceptance 必须独立认证来源键和判据指纹；任一文本缺失、替换、不可解析或指纹不匹配时，整个模拟回退全人工验收。
- 正式验证前建立 HEAD、工作区状态和 spec/plan/tasks 指纹快照，验证后、报告写入前复检；任一变化停止报告并要求重新 converge。
- Agent 不得伪造运行结果、截图、外部系统状态或人工体验结论。
- 所有改动同步英文 `README.md` 与中文 `README.zh-CN.md`。
- commands 数量为 15，templates 数量为 11。

## Review Focus

- 过期的 `acceptance-simulation.md` 被 acceptance 误用：baseline 不一致时必须重新模拟或全部转人工。
- 人工任务被误当成 Agent 实现未完成：implement 完成 Agent 任务后仍必须能进入 converge。
- tasks 阶段修改重新引入 clarify/plan 问题时仍继续前进：rectify 必须回到最早受影响阶段。
- 旧目录别名残留导致运行时路径分裂：仓库内所有内建引用必须统一为 `.auxiliary`。
- 中英文 README 流程漂移：两版必须显示相同的 converge、可选模拟验收和 acceptance 顺序。

---

### Task 1: 固定并实现 analyze 报告合同

**Files:**
- Create: `tests/test_preset_contract.py`
- Modify: `commands/speckit.analyze.md`
- Modify: `templates/analysis-report-template.md`

**Interfaces:**
- Consumes: 设计稿 §5 的问题卡字段与唯一路由规则。
- Produces: `unittest` 类 `PresetContractTests`，供后续任务继续增加合同测试；分析模板中的固定四级分区和路由命令名称。

- [ ] **Step 1: 写失败测试，固定 analyze 合同**

在 `tests/test_preset_contract.py` 创建标准库测试：

```python
class PresetContractTests(unittest.TestCase):
    def test_analyze_report_has_severity_sections_and_routes(self):
        text = self.read("templates/analysis-report-template.md")
        for heading in ("Critical", "High", "Medium", "Low"):
            self.assertIn(heading, text)
        for field in ("问题键", "证据", "影响", "修复入口命令", "具体修改建议", "验证判据"):
            self.assertIn(field, text)
        for route in ("speckit.clarify", "speckit.plan", "speckit.tasks"):
            self.assertIn(route, text)
```

测试辅助方法使用 `pathlib.Path(__file__).resolve().parents[1]` 定位仓库根并读取 UTF-8 文件。

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_analyze_report_has_severity_sections_and_routes -v`

Expected: FAIL，缺少固定字段或分区。

- [ ] **Step 3: 重写 analyze 规则与模板**

在 `commands/speckit.analyze.md` 明确：

- 四个严重级必须各有独立分区，无问题写“无”；
- 每个问题必须有稳定问题键、证据、详细描述、影响、唯一入口命令、具体修改建议、验证判据；
- 跨层问题只路由到最上游命令；
- 修改建议必须具体到产物章节和改法；
- 所有问题摘要进入会话输出，详细问题卡进入报告。

在 `templates/analysis-report-template.md` 增加汇总表、Critical/High/Medium/Low 详细问题卡、问题键/首次出现轮次、消除记录和阶段化 rectification 记录。

- [ ] **Step 4: 运行 analyze 合同测试**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_analyze_report_has_severity_sections_and_routes -v`

Expected: PASS。

- [ ] **Step 5: 提交本任务**

```bash
git add tests/test_preset_contract.py commands/speckit.analyze.md templates/analysis-report-template.md
git commit -m "feat: strengthen analysis report contract"
```

### Task 2: 实现 rectify 三阶段闭环

**Files:**
- Modify: `commands/speckit.rectify.md`
- Test: `tests/test_preset_contract.py`

**Interfaces:**
- Consumes: analyze 报告中的稳定问题键和唯一入口命令。
- Produces: clarify、plan、tasks 三个固定阶段及其循环/回退语义，供 implement 前置门禁使用。

- [ ] **Step 1: 新增失败测试，固定阶段顺序和回归规则**

增加：

```python
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_rectify_uses_strict_phase_order_and_regression -v`

Expected: FAIL，当前命令使用混排路由。

- [ ] **Step 3: 重写 rectify 执行算法**

在 `commands/speckit.rectify.md` 固化：

1. clarify 阶段处理全部 clarify 问题并 analyze，直到为零；
2. plan 阶段处理全部 plan 问题并 analyze，直到为零；
3. tasks 阶段处理全部 tasks 问题并 analyze，直到为零；
4. 新 analyze 轮次出现更早阶段问题时回退；
5. 同键连续两轮未消除则停止；
6. 不提供 Low 豁免，不改代码。

同时在命令描述中写明分阶段循环，不保留“同级按路由分组”的旧表述。

- [ ] **Step 4: 运行 rectify 合同测试**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_rectify_uses_strict_phase_order_and_regression -v`

Expected: PASS。

- [ ] **Step 5: 提交本任务**

```bash
git add commands/speckit.rectify.md tests/test_preset_contract.py
git commit -m "feat: enforce phased rectify loops"
```

### Task 3: 新增可选验收模拟并接入 acceptance

**Files:**
- Create: `commands/speckit.simulate-acceptance.md`
- Create: `templates/acceptance-simulation-template.md`
- Modify: `commands/speckit.acceptance.md`
- Modify: `templates/implementation-report-template.md`
- Test: `tests/test_preset_contract.py`

**Interfaces:**
- Consumes: spec、plan、tasks、里程碑用户验收指导、converge 结果和实现证据。
- Produces: `specs/[NNN-mX-slug]/acceptance-simulation.md`；acceptance 可消费的四种状态及逐项人工指南。

- [ ] **Step 1: 写失败测试，固定命令、状态和人工指南**

增加：

```python
def test_acceptance_simulation_contract(self):
    command = self.read("commands/speckit.simulate-acceptance.md")
    template = self.read("templates/acceptance-simulation-template.md")
    acceptance = self.read("commands/speckit.acceptance.md")
    for status in ("AI_PASS", "AI_FAIL", "HUMAN_REQUIRED", "BLOCKED"):
        self.assertIn(status, command)
        self.assertIn(status, template)
    for field in ("前置条件", "操作步骤", "预期结果", "判定标准", "记录位置"):
        self.assertIn(field, template)
    self.assertIn("acceptance-simulation.md", acceptance)
    self.assertIn("AI_PASS", acceptance)
    self.assertIn("baseline", acceptance)
    self.assertIn("过期", acceptance)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_acceptance_simulation_contract -v`

Expected: FAIL，文件和命令尚不存在。

- [ ] **Step 3: 创建模拟验收命令**

`commands/speckit.simulate-acceptance.md` 必须：

- 在 converge `Converged` 后运行；
- 汇总 spec 验收标准、里程碑验收指导、tasks 人工项和当前实现证据；
- 实际执行可行测试；禁止无证据标记通过；
- 对 `AI_FAIL` 路由回 clarify/plan/tasks/implement；
- 对 `HUMAN_REQUIRED`/`BLOCKED` 输出完整人工指南；
- 生成 baseline、汇总、总表、AI 结果明细、人工待验区和结论。

- [ ] **Step 4: 创建模拟验收模板**

`templates/acceptance-simulation-template.md` 使用固定四种状态，并为每个剩余人工项提供独立小节模板，字段覆盖设计稿 §8.3。

- [ ] **Step 5: 接入正式验收报告**

修改 `commands/speckit.acceptance.md`：

- 前置检查 converge 结果；
- 若模拟报告 baseline 当前有效，导入 `AI_PASS` 与人工项；
- `AI_FAIL` 禁止出报告；
- 缺失或过期时退回全人工验收；
- 正式报告记录模拟报告路径、baseline 和证据。

更新 `templates/implementation-report-template.md` 的验收状态、证据列、模拟结果来源与人工指南。

- [ ] **Step 6: 运行模拟验收合同测试**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_acceptance_simulation_contract -v`

Expected: PASS。

- [ ] **Step 7: 提交本任务**

```bash
git add commands/speckit.simulate-acceptance.md templates/acceptance-simulation-template.md commands/speckit.acceptance.md templates/implementation-report-template.md tests/test_preset_contract.py
git commit -m "feat: add optional acceptance simulation"
```

### Task 4: 接入核心 converge 并更新 navigator

**Files:**
- Modify: `commands/speckit.implement.md`
- Modify: `commands/speckit.acceptance.md`
- Modify: `templates/agents-reminder-template.md`
- Test: `tests/test_preset_contract.py`

**Interfaces:**
- Consumes: 核心 `speckit.converge`；Task 3 的模拟验收入口。
- Produces: `implement -> converge -> optional simulate-acceptance -> acceptance` 的本地交接与状态提醒。

- [ ] **Step 1: 新增失败测试，固定 converge 编排**

增加：

```python
def test_workflow_hands_off_through_converge(self):
    implement = self.read("commands/speckit.implement.md")
    acceptance = self.read("commands/speckit.acceptance.md")
    navigator = self.read("templates/agents-reminder-template.md")
    self.assertIn("agent: speckit.converge", implement)
    self.assertNotIn("agent: speckit.acceptance", implement)
    self.assertIn("Agent 可执行", implement)
    self.assertIn("需人工", implement)
    self.assertIn("speckit.converge", acceptance)
    self.assertIn("/speckit.converge", navigator)
    self.assertIn("/speckit.simulate-acceptance", navigator)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_workflow_hands_off_through_converge -v`

Expected: FAIL，当前 implement 直接 handoff acceptance。

- [ ] **Step 3: 修改 implement 交接**

将 implement 的 completion handoff 改为 `speckit.converge`，明确 converge 追加任务时回到 implement，`Converged` 后才允许可选 simulate-acceptance 和 acceptance。保留“需人工”任务的验收语义。

- [ ] **Step 4: 更新 acceptance 与 navigator**

acceptance 当前会话无法确认 `Converged` 时要求先运行 converge；navigator 增加 converge、可选模拟验收和 acceptance 顺序，版本标记同步 `v1.6.0`。

- [ ] **Step 5: 运行 converge 编排合同测试**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_workflow_hands_off_through_converge -v`

Expected: PASS。

- [ ] **Step 6: 提交本任务**

```bash
git add commands/speckit.implement.md commands/speckit.acceptance.md templates/agents-reminder-template.md tests/test_preset_contract.py
git commit -m "feat: wire workflow through converge"
```

### Task 5: 统一 `.auxiliary`、manifest 与双 README

**Files:**
- Modify: `preset.yml`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `CHANGELOG.md`
- Modify: `templates/implementation-report-template.md`
- Modify: `commands/speckit.implement.md`
- Modify: `commands/speckit.rectify.md` if any path remains
- Modify: `docs/research/2026-11-18-speckit-converge.md`
- Test: `tests/test_preset_contract.py`

**Interfaces:**
- Consumes: 前面任务完成的命令与模板名称。
- Produces: 发布级 manifest、双语流程文档和新的默认目录。

- [ ] **Step 1: 新增失败测试，固定版本、计数和目录**

增加：

```python
def test_release_metadata_and_default_directory(self):
    manifest = self.read("preset.yml")
    readme_en = self.read("README.md")
    readme_zh = self.read("README.zh-CN.md")
    self.assertIn('version: "1.6.0"', manifest)
    self.assertIn('speckit_version: ">=1.0.9"', manifest)
    self.assertIn(".auxiliary/docs/specs-analysis-repo/", manifest)
    self.assertEqual(manifest.count('type: "command"'), 15)
    self.assertEqual(manifest.count('type: "template"'), 11)
    for text in (readme_en, readme_zh):
        self.assertIn("v1.6.0", text)
        self.assertIn("/speckit.converge", text)
        self.assertIn("/speckit.simulate-acceptance", text)
        self.assertIn(".auxiliary", text)
```

另加测试遍历仓库文本文件，拒绝两个旧目录别名；旧别名字符串在测试中用分片拼接，避免测试自己形成命中。

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_release_metadata_and_default_directory -v`

Expected: FAIL，版本、计数、README 和新目录尚未同步。

- [ ] **Step 3: 更新 manifest 与目录**

将 preset 版本改为 `1.6.0`，最低 spec-kit 改为 `>=1.0.9`，描述加入分阶段 rectify、converge 和模拟验收，注册 15 个 commands 与 11 个 templates，所有默认路径改为 `.auxiliary`。

- [ ] **Step 4: 更新双 README**

英文与中文同步：

- 标题、徽章、安装 tag、版本表；
- Mermaid 流程加入 converge 和可选 simulate-acceptance；
- 里程碑步骤表加入收敛与模拟验收；
- rectify 三阶段、analyze 问题卡、`.auxiliary` 默认路径；
- 文件清单更新 commands/templates 数量；
- 清理已存在的重复代码块和重复段落。

- [ ] **Step 5: 更新 CHANGELOG、研究记录与遗留路径**

新增 `1.6.0` 条目；研究记录中的活动路径统一为 `.auxiliary`；历史路径说明只保留“目录迁移”语义，不保留旧目录字面量。

- [ ] **Step 6: 运行发布元数据合同测试**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_release_metadata_and_default_directory -v`

Expected: PASS。

- [ ] **Step 7: 提交本任务**

```bash
git add preset.yml README.md README.zh-CN.md CHANGELOG.md templates/implementation-report-template.md commands/speckit.implement.md docs/research/2026-11-18-speckit-converge.md tests/test_preset_contract.py
git commit -m "docs: release preset 1.6 workflow"
```

---

### Final Review Correction Wave

**Interfaces:**
- Consumes: final whole-branch review findings and the controller ruling dated 2026-11-18.
- Produces: criterion-fingerprint authentication, one report-directory resolution rule, synchronized twelve-stage tables, and verified pre/post formal-verification snapshots.

- [x] Add RED contracts for correct-key/altered-criterion rejection, malformed fingerprints, shared `analysis_report_dir: <path>` parsing, twelve command stages, acceptance snapshot ordering, and navigator evidence scope.
- [x] Fix source authentication so every simulation row carries `判据指纹: sha256:<hex>` and acceptance independently extracts, canonicalizes, and fingerprints current criterion text before importing any simulation result.
- [x] Preserve `AI_FAIL` precedence even when the simulation baseline is stale; invalid criterion authentication otherwise falls back to full manual acceptance.
- [x] Apply the report-directory resolver to analyze, rectify, implement, acceptance, templates, README EN/ZH, manifest metadata, and research/configuration text.
- [x] Remove the numbered branch row, retain it as an unnumbered action, and number the twelve command stages through prototype, specify, clarify, plan, tasks, analyze, rectify, implement, converge, optional simulate-acceptance, acceptance, and release.
- [x] Require pre-verification and post-verification snapshots of HEAD, full porcelain status, and spec/plan/tasks SHA-256 fingerprints; any difference stops formal report and milestone writes and requires another converge.
- [x] Clarify simulation rerun lifecycle for an uncommitted existing `implementation-report.md`: commit or remove it, then rerun; only the target simulation report may be the otherwise-clean baseline exception.
- [x] Run focused tests, full unittest discovery, alias scan, manifest checks, isolated CLI smoke, and `git diff --check`.

### Task 6: 全量验证与安装冒烟

**Files:**
- Verify: `tests/test_preset_contract.py`
- Verify: `preset.yml`
- Verify: all modified Markdown files

**Interfaces:**
- Consumes: Tasks 1-5 的全部交付。
- Produces: 可安装、可解析、无旧路径残留的 `1.6.0` preset 验证结果。

- [ ] **Step 1: 运行全部合同测试**

Run: `python -m unittest discover -s tests -v`

Expected: 全部 PASS。

- [ ] **Step 2: 运行静态残留与结构检查**

Run:

```powershell
rg -n "speckit\.simulate-acceptance|speckit\.converge|\.auxiliary|AI_PASS|HUMAN_REQUIRED" commands templates README.md README.zh-CN.md preset.yml CHANGELOG.md
```

Expected: 各入口和状态均命中预期文件，无旧目录别名。

- [ ] **Step 3: 检查 manifest 注册数量与文件存在**

Run: `python -m unittest tests.test_preset_contract.PresetContractTests.test_release_metadata_and_default_directory -v`

Expected: PASS，manifest 中 15 个 command、11 个 template 均可解析，文件存在。

- [ ] **Step 4: 临时项目安装冒烟**

在系统临时目录创建 spec-kit 项目并执行：

```powershell
specify init --here --integration codex --ignore-agent-tools
specify preset add --dev D:\DevProj\AgentDev\speckit-preset-milestone-driven-dev
specify preset info milestone-driven-dev
specify preset resolve acceptance-simulation-template
```

Expected: preset 显示 `1.6.0`，新模板可解析，安装过程无 manifest/schema 错误。

- [ ] **Step 5: 检查最终 diff**

Run: `git diff --check; git status --short`

Expected: 无空白错误；仅包含设计、计划、研究、命令、模板、README、preset、changelog 和测试的预期改动。
