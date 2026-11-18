# spec-kit `/speckit.converge` 一手来源研究

| 项目 | 值 |
| --- | --- |
| 调研日期 | 2026-11-18 |
| 上游仓库 | <https://github.com/github/spec-kit> |
| 默认分支 | `main` |
| 调研时默认分支 commit | `59d61c59630c3bd5a294f4c23e43a60d8ab98d02` |
| 调研时最新正式 release | `v1.4.2`，发布于 2026-11-17 |
| 本地 preset 基线 | `main@39dd5f795e6a04d0e02efb5c40790467fa71bad0`，preset `v1.5.0` |

本文只保留官方源码、官方文档、commit 和 release notes 可以直接支持的一手结论。除特别标注为“工程判断”的内容外，不把博客、二手总结或推测当作事实。

## 结论摘要

1. `/speckit.converge` 是**实现后的完整性收敛门禁**。它读取当前 `spec.md`、`plan.md`、`tasks.md` 和 constitution，检查当前代码是否实现这些意图，并把仍未完成的工作追加为新任务。
2. 它必须在完整 `tasks.md` 已生成且 `implement` 已对当前任务集执行之后运行。若 converge 追加任务，必须再次 `implement`，然后再次 `converge`，直到结果为 converged。
3. converge 不是 Git diff、分支比较或历史比较工具，也不持续监控 artifact/code 漂移。它只回答“当前代码是否满足当前意图”。
4. converge 的唯一写入是向 `tasks.md` 尾部追加 `Convergence` 阶段；它不修改代码、`spec.md` 或 `plan.md`，不删除或重排旧任务，无缺口时连一个字节都不写。
5. converge 首次出现于 `v0.11.2`；若依赖当前“勾选状态不是完成证据、所有旧任务都要重查”的语义，推荐最低版本是 `v1.0.9`，而不是仅满足 `v0.11.2`。
6. 本地 preset 不应覆盖上游 converge 的核心正文。推荐采用“直接复用上游命令 + 调整本地编排”的混合方案，把严格顺序定义为：

   ```text
   analyze/rectify 清零 -> implement -> converge
   -> 若追加任务：implement -> converge
   -> acceptance -> release
   ```

## 1. 版本、引用与引入时间

### 1.1 当前固定引用

| 项目 | 固定引用 |
| --- | --- |
| 默认分支 | `main` |
| 当前默认分支 commit | `59d61c59630c3bd5a294f4c23e43a60d8ab98d02` |
| 当前最新正式 release | `v1.4.2` |
| `v1.4.2` 中 converge 文件 blob | `f6a44c3e91b3c0100aa4553d498e758b1125b9a5` |
| 当前 `main` 中 converge 文件 blob | `f6a44c3e91b3c0100aa4553d498e758b1125b9a5` |

当前 `main` 与 `v1.4.2` 的 converge 命令定义内容相同。本文的命令语义固定引用当前 `main` commit，同时也给出 `v1.4.2` tag 链接。

来源：

- 默认分支与仓库元数据：[GitHub API: repository](https://api.github.com/repos/github/spec-kit)
- 当前 `main` commit：[59d61c59630c3bd5a294f4c23e43a60d8ab98d02](https://github.com/github/spec-kit/commit/59d61c59630c3bd5a294f4c23e43a60d8ab98d02)
- 最新 release：[v1.4.2](https://github.com/github/spec-kit/releases/tag/v1.4.2)
- 当前 converge：[main@59d61c5: templates/commands/converge.md](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/converge.md)
- 发布版 converge：[v1.4.2: templates/commands/converge.md](https://github.com/github/spec-kit/blob/v1.4.2/templates/commands/converge.md)

### 1.2 最低版本要分两层

| 目标 | 最低版本 | 依据 |
| --- | --- | --- |
| 仅要求命令存在 | `>=0.11.2` | `v0.11.2` release notes 首次列出 `feat: add /speckit.converge command (#3001)` |
| 要求当前完成性判定语义 | `>=1.0.9` | `v1.0.9` release notes 包含 `fix: clarify converge assessment of completion claims (#4621)` |

时间线：

- 2026-06-17，converge 功能 commit `0c29d890abbdcda3acefab724e0b1bf05a52ddf8` 合入；commit message 明确说明它评估 spec/plan/tasks 对代码库的满足情况，并以 append-only 方式追加剩余任务。
- 2026-06-18，`v0.11.2` 发布，首次正式交付 `/speckit.converge`。
- 2026-09-18，commit `68b94af0079b48071a6596568190997836e1290e` 修正 completion claims 的判定，要求不能仅凭任务勾选状态判断实现是否完成。
- 2026-09-21，`v1.0.9` 发布，并明确列出上述修正。

来源：

- 首次引入 commit：[0c29d890abbdcda3acefab724e0b1bf05a52ddf8](https://github.com/github/spec-kit/commit/0c29d890abbdcda3acefab724e0b1bf05a52ddf8)
- 首次发布：[v0.11.2](https://github.com/github/spec-kit/releases/tag/v0.11.2)
- 完成性语义修正：[68b94af0079b48071a6596568190997836e1290e](https://github.com/github/spec-kit/commit/68b94af0079b48071a6596568190997836e1290e)
- 修正的发布版本：[v1.0.9](https://github.com/github/spec-kit/releases/tag/v1.0.9)

因此：

- `v0.14.4` 可以包含 converge 命令，因为 `v0.14.4 > v0.11.2`。
- 但 `v0.14.4` 不能证明具备 `v1.0.9` 才正式发布的 completion-claims 语义。
- 若 preset 只是把 converge 作为外部可选能力，可以分别声明“preset 基线版本”和“converge 可选能力最低版本”。
- 若 preset 的正式主流程承诺 converge，最低 spec-kit 版本不应继续停留在 `>=0.5.0`，而应至少是 `>=0.11.2`；要保证当前语义则应为 `>=1.0.9`。

## 2. 命令的确切作用

上游 converge 的目标是关闭以下二者之间的差距：

- 当前 feature 的 `spec.md`、`plan.md`、`tasks.md` 所表达的意图；
- 当前代码库实际提供的实现。

它把剩余工作追加到 `tasks.md`，再由 `implement` 完成。定义中明确写出：

- `spec.md`、`plan.md`、`tasks.md` 是**唯一意图来源**；
- constitution 是治理约束；
- 必须在 `implement` 已对当前 `tasks.md` 运行后使用；
- 必须在 `tasks` 已生成完整 `tasks.md` 后使用；
- 不追踪变更，不使用 git、branch comparison 或 history。

关键来源：[current converge command](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/converge.md)、[introducing commit](https://github.com/github/spec-kit/commit/0c29d890abbdcda3acefab724e0b1bf05a52ddf8)。

### 2.1 输入与前置条件

| 输入/条件 | 要求 |
| --- | --- |
| `spec.md` | 必需；缺失则停止并提示先运行 specify，不产生部分结果 |
| `plan.md` | 必需；缺失则停止并提示先运行 plan |
| `tasks.md` | 必需且应由 tasks 完整生成；缺失则停止并提示先运行 tasks |
| constitution | 若存在则作为最高约束；若仍是未填写模板则跳过 constitution 检查 |
| 当前任务集 | `implement` 必须已执行过当前 `tasks.md` |
| 用户参数 | `$ARGUMENTS` 非空时必须纳入处理，但不得改变命令的意图来源 |

命令先运行统一的 prerequisites script，取得 `FEATURE_DIR` 与 `AVAILABLE_DOCS`，然后推导：

- `SPEC = FEATURE_DIR/spec.md`
- `PLAN = FEATURE_DIR/plan.md`
- `TASKS = FEATURE_DIR/tasks.md`
- `CONSTITUTION = /memory/constitution.md`，若存在

来源：[converge execution step 1](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/converge.md#L77-L92)。

### 2.2 从每个 artifact 读取什么

| Artifact | converge 读取的意图 |
| --- | --- |
| `spec.md` | FR、SC、User Stories 的 Acceptance Scenarios、Edge Cases；SC 只纳入需要构建工作的项，不把发布后 outcome metrics 或业务 KPI 当作代码缺口 |
| `plan.md` | 架构/技术栈选择、技术决策、数据模型引用、计划阶段、文件/组件触点、技术约束 |
| `tasks.md` | 任务 ID、描述、阶段分组、引用路径；用于计算新任务 ID 和新阶段号 |
| constitution | Principle 名称、MUST/SHOULD 规范语句 |

这里采用 progressive disclosure，只加载评估所需的最小上下文。

来源：[load artifacts](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/converge.md#L93-L125)。

## 3. 执行步骤

上游命令的完整执行顺序如下：

1. **执行 before hooks**：读取 `.specify/extensions.yml` 的 `hooks.before_converge`。可解析、启用的 optional hook 给出运行提示；mandatory hook 必须实际执行并等待完成。
2. **初始化并校验前置条件**：运行 prerequisites script；缺少 spec、plan 或 tasks 时立即停止。
3. **渐进读取 artifacts**：从 spec、plan、tasks、constitution 提取上述最小必要意图。
4. **建立 Intent Inventory**：为每个 FR、可构建 SC、User Story acceptance scenario、plan decision、constitution obligation 建立稳定 key。
5. **建立 Code-scope Map**：根据 plan/tasks 指定路径及需求关键词，限定代码检查范围；不评估 artifact 未定义的更大范围。
6. **检查当前代码并分类**：逐个 intent item 检查当前行为，只记录缺口。所有已有任务都参与评估，无论 `[ ]`、`[x]`，还是来自旧 Convergence phase；任务勾选和完成声明都不是证据。
7. **分级**：为每个 finding 分配 gap type 和 severity。
8. **会话内汇报**：先输出 `Convergence Findings` 表，以及 requirements、plan decisions、constitution principles、gap types、severities 的计数；此时尚不写文件。
9. **两分支输出**：
   - 有 actionable findings：只向 `tasks.md` 尾部追加一个 `## Phase N: Convergence`。
   - 无 findings：不修改 `tasks.md`，报告 `Converged`。
10. **交付下一步**：`tasks_appended` 时建议再次 `implement`；`converged` 时表示当前 feature 的指定范围不再需要 implement pass，可进入 review/PR。
11. **执行 after hooks**：读取 `.specify/extensions.yml` 的 `hooks.after_converge`；mandatory hook 必须实际执行。

关键来源：

- [完整 converge 命令](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/converge.md)
- [completion claims 修正](https://github.com/github/spec-kit/commit/68b94af0079b48071a6596568190997836e1290e)
- [converge scaffold regression test](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/tests/test_converge_template_scaffold.py)
- [extension hook schema/API](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/docs/extensions/api.md)

## 4. 缺口分类、严重度与输出契约

### 4.1 gap type

| Gap type | 含义 |
| --- | --- |
| `missing` | 要求的工作在代码中完全不存在 |
| `partial` | 已有工作，但尚未满足完整 requirement、acceptance criterion 或 plan decision |
| `contradicts` | 代码与当前意图或 constitution MUST 冲突 |
| `unrequested` | 代码包含 spec、plan、tasks 未要求的实现；只用于提醒，converge 不删除代码，只追加 review/justify/remove 任务 |

### 4.2 severity

| Severity | 判定 |
| --- | --- |
| `CRITICAL` | 违反 constitution MUST，或 missing/contradicts 阻塞 P1 user story 的基础功能 |
| `HIGH` | 核心 FR 或 acceptance criterion 存在 missing/partial |
| `MEDIUM` | 次要要求 partial，或无法解释的 unrequested addition |
| `LOW` | 轻微 partial、打磨项或低风险 unrequested addition |

### 4.3 有缺口时的唯一写入

有 action findings 时，converge 只向 `tasks.md` 尾部写：

```markdown
## Phase N: Convergence

- [ ] T042 <imperative description> per <source-ref> (<gap-type>)
```

具体约束：

- `N` 是已有最大 phase 号加一；
- `M` 是已有最大 task ID，新 ID 从 `T{M+1:03d}` 连续编号；
- 每条 finding 对应一个 checklist task；
- 排序优先 `CRITICAL/HIGH`；
- constitution violation task 必须最先输出，并描述为 `CRITICAL`；
- `source-ref` 可以是 `FR-003`、`SC-002`、`US1/AC2`、`plan: storage decision`、`Constitution II` 等；
- `gap-type` 只能使用四种已定义值；
- 不修改、重编号、重排、删除、复用任何已有任务；
- 旧 Convergence phase 原样保留，新 phase 继续追加在其后。

### 4.4 无缺口时的输出

无 actionable findings 时：

- `tasks.md` 必须 byte-for-byte unchanged；
- 不添加空的 `Convergence` 标题；
- 报告 `Converged`；
- 输出检查计数；
- 推荐进入 review/PR，当前 feature 的指定范围不需要再跑一次 implement。

### 4.5 明确禁止的写入

converge 不得：

- 修改 `spec.md`；
- 修改 `plan.md`；
- 修改、创建或删除应用代码；
- 把自己发现的实现现状反写成新意图来接受代码；
- 删除或调整已有任务；
- 使用 Git diff、分支或历史推断缺口。

若实现暴露的是“意图变化”，正确路径是先修订 spec/plan/tasks，再走 `implement -> converge`。converge 不会把代码变成新的规格来源。

来源：[append contract](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/converge.md#L41-L61)、[task append step](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/converge.md#L201-L239)。

## 5. 与 tasks、analyze、implement 的关系

| 命令 | 检查对象 | 是否修改 artifact 或代码 | 与 converge 的关系 |
| --- | --- | --- | --- |
| `tasks` | spec + plan -> 初始任务分解 | 写 `tasks.md` | converge 消费已经完整的 `tasks.md`，不重新生成任务 |
| `analyze` | spec、plan、tasks 之间的一致性与覆盖 | 官方命令为只读分析 | 主要发生在实现前；不能检查代码是否实现意图，不能替代 converge |
| `implement` | 按 `tasks.md` 修改代码并执行任务 | 写代码，并更新任务执行状态 | converge 不相信任务勾选，而是直接验证真实代码行为 |
| `converge` | 当前代码 -> spec/plan/tasks/constitution | 通常零写入；有缺口时只追加 `tasks.md` | 将剩余工作交回 implement，形成实现后闭环 |

上游文档把交付循环明确写为：

```text
specify -> plan -> tasks -> implement -> converge
```

若 converge 追加任务，则重复：

```text
implement -> converge -> implement -> converge ...
```

直到 converge 报告 `Converged`。

来源：

- [How to evolve specifications](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/docs/how-to/evolving-specs.md)
- [Quickstart](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/docs/quickstart.md)
- [Agentic SDD reference](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/docs/reference/agentic-sdd.md)
- [Root README](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/README.md)
- [upstream analyze command](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/analyze.md)
- [upstream tasks command](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/tasks.md)
- [upstream implement command](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/implement.md)

需要特别区分：

- 上游内置 workflow 当前仍只自动执行 `specify -> plan -> tasks -> implement`；
- converge 是独立命令，文档要求用户或编排层在 implement 后调用；
- 因任务追加而再次 implement/converge 的循环，也属于工作流编排，不是 converge 自己修改代码或自动递归。

## 6. 它适用的阶段

### 适用

- 某个 feature 已经按当前 `tasks.md` 实现；
- spec/plan/tasks 已存在且是当前意图；
- 需要在人工验收、PR 或发布前确认代码没有遗漏、半实现或与意图冲突；
- converge 追加任务后，需要重复实现并再次收敛；
- 想以 append-only 方式保留剩余工作的可追溯来源。

### 不适用

- 在 implement 之前预检；这时绝大多数结果只会是 `missing`，应由 analyze/tasks/implement 处理；
- 持续监控长期 artifact/code drift；
- 双向同步 artifact 与代码；
- 自动决定保留哪些规格、改哪份规格或选择持久化策略；
- 处理需求变化本身。需求变化要先修订 spec/plan/tasks，再 implement/converge；
- 用 Git 分支或 commit 历史对账；
- 用当前代码反向生成或覆盖规格。

上游 evolving-specs 文档明确说明：converge 不重写 artifact 来接受代码，也不选择 persistence strategy；需求修订后仍需完成交付循环。

来源：[evolving specs: Deliver and Assess the Change](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/docs/how-to/evolving-specs.md#deliver-and-assess-the-change)。

## 7. 本地 preset 现状

本地基线为 `main@39dd5f795e6a04d0e02efb5c40790467fa71bad0`，`preset.yml` 中 preset 版本为 `1.5.0`。

| 本地项 | 当前事实 | 对 converge 的影响 |
| --- | --- | --- |
| [preset.yml](../../preset.yml) | `requires.speckit_version: ">=0.5.0"` | 不能保证 converge 命令存在，更不能保证 `v1.0.9` 语义 |
| `commands/` | 没有 `speckit.converge.md` | 当前完全依赖上游核心命令 |
| [speckit.analyze.md](../../commands/speckit.analyze.md) | 检查 spec/plan/tasks 跨产物一致性，报告落盘到 `.prepare/docs/specs-analysis-repo/` | 实现前门禁；报告不是 converge 的替代品，也不应升级成 converge 的唯一意图源 |
| [speckit.rectify.md](../../commands/speckit.rectify.md) | 按报告路由 clarify -> plan -> tasks，再重跑 analyze | 修复的是规格体系，不检查或不修改代码，发生阶段早于 converge |
| [speckit.implement.md](../../commands/speckit.implement.md) | 要求分析报告清零；完成后自动 handoff 到 `speckit.acceptance` | 当前没有 converge 拦截点；直接手动补跑容易与验收顺序冲突 |
| [speckit.acceptance.md](../../commands/speckit.acceptance.md) | 生成 `implementation-report.md` 并执行自动化验证 | converge 追加任务后，已有验收报告可能不再覆盖新的实现范围 |
| [speckit.release.md](../../commands/speckit.release.md) | 要求验收全通过、报告已提交且分析报告清零 | 当前 release 门禁不包含 implementation-to-intent convergence |
| [README.md](../../README.md) / [README.zh-CN.md](../../README.zh-CN.md) | 十步流程为 analyze/rectify -> implement -> acceptance -> release | 缺少实现后代码对意图的完整性收敛环节 |

本地现有主循环实际是：

```text
analyze/rectify 循环 -> implement -> acceptance -> release
```

上游 converge 与本地 rectify 是互补关系：

- `rectify`：实现前，让 spec/plan/tasks 自身闭合；
- `converge`：实现后，让当前代码对已闭合的意图闭合；
- `acceptance`：在实现和收敛完成后，生成人工验收依据。

基于本地源码的工程判断：

1. converge 不能紧跟在 rectify 后执行；这时代码还没有按最新任务实现，只会得到大量 missing。
2. 严格顺序应是 `analyze/rectify 清零 -> implement -> converge -> acceptance -> release`。
3. 若 converge 追加任务，应进入 `implement -> converge` 循环，循环完成后再生成 acceptance。
4. 当前 implement 自动 handoff 到 acceptance，因此“不调整本地编排、只让用户记得手跑 converge”是脆弱方案。
5. 若在 acceptance 后追加任务，旧 `implementation-report.md` 可能过期；这是由本地 acceptance 的生成时机推导出的风险，不是上游命令的额外能力。

## 8. 集成方案与推荐

### 方案 A：直接复用上游，人工可选收尾

做法：

- 不新增本地 `commands/speckit.converge.md`；
- 保持上游命令原文；
- 在文档和 navigator 中把 converge 标记为实现后可选的严格门；
- 用户必须在 acceptance 前手动插入。

优点：

- 零命令分叉；
- 自动继承上游修复；
- 改动成本最低。

风险：

- 本地 implement 会自动 handoff 到 acceptance，用户容易漏跑；
- 若在 acceptance 后才手跑，追加任务可能使验收报告过期；
- 无法形成稳定、可验证的 preset 门禁。

### 方案 B：直接复用上游命令，本地只调整编排，推荐

做法：

- 不 override converge 正文；
- 将来在本地的 implement handoff、workflow navigator、README 流程中把入口改为 converge；
- converge 结果为 `tasks_appended` 时回到 implement，结果为 `converged` 时进入 acceptance；
- 继续使用上游 `before_converge` / `after_converge` hooks。

目标流程：

```text
analyze/rectify 清零
-> implement
-> converge
-> tasks_appended: implement -> converge
-> converged
-> acceptance
-> release
```

优点：

- 保留上游全部语义、任务格式和 hook 契约；
- 补上本地当前缺失的实现后代码闭合；
- 不复制上游命令，未来升级时维护面最小；
- 能明确解决当前 implement 直接跳 acceptance 的顺序问题。

风险：

- 必须同步修改本地编排和相关文档，不能只写一句“建议运行”；
- 需要为循环设置交给用户的终止条件，例如 spec-kit 命令本身没有自动递归，外层编排应在无进展或达到人工设定上限时停下；
- 需要建立版本门槛：正式承诺当前语义时至少 `>=1.0.9`。

### 方案 C：薄 override，完全嵌入 preset 生命周期

做法：

- 新增本地 `commands/speckit.converge.md`；
- 尽量逐字保留上游正文；
- 只增加本地 feature/Mx 定位、analyze 清零门禁、handoff 和退出规则。

仅在以下条件下采用：

- preset 要求 `implement -> converge -> acceptance` 全自动；
- 上游 handoff/hook 无法表达本地里程碑状态机；
- 团队愿意持续跟随上游 diff 并维护 override。

风险：

- 命令正文复制后容易发生语义漂移；
- 每次上游修复或模板升级都需要人工同步；
- 很容易把本地 analyze 报告、acceptance 报告或里程碑文件错误提升为新的意图源。

### 推荐

采用**方案 B**：

- converge 定位为 `rectify` 前置闭环之后、`acceptance/release` 之前的实现后严格收尾门；
- 直接复用上游命令，不复制核心语义；
- 本地只编排 `implement -> converge -> conditional implement/converge -> acceptance`；
- 当前任务不修改这些文件，只把此方案记录为后续实施建议。

## 9. 如果 override，需要保留与可定制什么

### 必须原样保留

- `spec.md`、`plan.md`、`tasks.md` 的唯一意图源地位；
- constitution 的不可违背地位；
- 必需文件检查，缺任意一项停止；
- 不使用 Git diff、分支比较或历史；
- 所有已有任务都要验证实际代码，不信任 checkbox；
- 四种 gap type；
- 四级 severity；
- append-only；
- 无缺口时 byte-for-byte no-op；
- 新 task ID 从最大值续编、零填充、CRITICAL/HIGH 优先；
- `per <source-ref> (<gap-type>)` 的可追溯格式；
- 不修改 spec/plan、不修改代码、不删除或重排任务；
- `tasks_appended -> implement -> converge` 的循环；
- 上游 `$ARGUMENTS`、scripts frontmatter、before/after hooks。

### 可以增加，但不得改变上游意图模型

- 根据当前 `feature/Mx` 分支绑定 spec 目录；
- 运行前确认最新 analyze 报告已清零，作为本地前置门禁；
- 通过 handoff 把 `tasks_appended` 路由到 implement，把 `converged` 路由到 acceptance；
- 在 milestone/prototype/acceptance 与 spec/plan/tasks 已有明确引用时，把这些引用作为追踪上下文；
- 外层循环的终止规则，例如连续无进展或达到上限后交还用户；
- 对本地 SPEC、PLAN、TASKS、CONSTITUTION 路径常量做适配。

### 不得增加

- 不得让 converge 写分析报告、验收报告、`spec.md` 或 `plan.md`；
- 不得让 converge 修代码；
- 不得把当前实现反写为新规格；
- 不得用本地 analyze 报告替代 spec/plan/tasks 成为唯一意图源；
- 不得删除、重排、重编号或复用已有任务；
- 不得在 converged 时添加空 Convergence phase。

## 10. 最终建议

1. **现在不要 override converge。** 上游现有语义已经满足 preset 需要，复制正文的维护风险大于收益。
2. **把它作为 rectify 循环之后的实现后可选或严格收尾环节。** 推荐通过本地编排将它提升为严格门，但不要改变命令本身。
3. **不要把 converge 放在 implement 前。** 它对代码进行完成性评估，前置运行是阶段错误。
4. **把它纳入 `implement -> converge` 循环。** 追加任务后必须再次实现并再次收敛，直到 `Converged`。
5. **把它放在 acceptance 前。** 这样人工验收报告基于已经收敛的实现范围生成，避免 converge 追加任务后报告过期。
6. **版本策略分层。** 仅提供 converge 能力最低 `>=0.11.2`；若正式依赖当前“完成声明不是证据”的语义，最低 `>=1.0.9`。不能继续用 `>=0.5.0` 或仅凭 `v0.14.4` 声称完整兼容当前 converge 工作流。

## 11. 关键来源索引

| 关键结论 | 一手来源 | 固定 ref |
| --- | --- | --- |
| 默认分支为 `main`，当前 SHA | [GitHub API repository](https://api.github.com/repos/github/spec-kit) | 2026-11-18 查询 |
| 当前 `main` commit | [commit](https://github.com/github/spec-kit/commit/59d61c59630c3bd5a294f4c23e43a60d8ab98d02) | `59d61c59630c3bd5a294f4c23e43a60d8ab98d02` |
| converge 完整语义、前置、步骤、写入边界 | [converge.md](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/converge.md) | `main@59d61c5`，blob `f6a44c3...` |
| 最新发布中的 converge 与 main 相同 | [v1.4.2 converge.md](https://github.com/github/spec-kit/blob/v1.4.2/templates/commands/converge.md) | `v1.4.2`，blob `f6a44c3...` |
| converge 首次加入 | [commit 0c29d89](https://github.com/github/spec-kit/commit/0c29d890abbdcda3acefab724e0b1bf05a52ddf8) | `0c29d890abbdcda3acefab724e0b1bf05a52ddf8` |
| 首次正式发布 | [v0.11.2 release](https://github.com/github/spec-kit/releases/tag/v0.11.2) | `v0.11.2` |
| 勾选状态不是完成证据 | [commit 68b94af](https://github.com/github/spec-kit/commit/68b94af0079b48071a6596568190997836e1290e) | `68b94af0079b48071a6596568190997836e1290e` |
| 当前完成性语义首次发布 | [v1.0.9 release](https://github.com/github/spec-kit/releases/tag/v1.0.9) | `v1.0.9` |
| implement 后 converge，追加任务则循环 | [evolving-specs.md](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/docs/how-to/evolving-specs.md) | `main@59d61c5` |
| 交付循环与命令参考 | [agentic-sdd.md](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/docs/reference/agentic-sdd.md) | `main@59d61c5` |
| Quickstart 调用与流程 | [quickstart.md](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/docs/quickstart.md) | `main@59d61c5` |
| README 中的交付循环 | [README.md](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/README.md) | `main@59d61c5` |
| analyze/tasks/implement 的相邻职责 | [analyze.md](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/analyze.md)、[tasks.md](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/tasks.md)、[implement.md](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/templates/commands/implement.md) | `main@59d61c5` |
| converge 模板契约回归测试 | [test_converge_template_scaffold.py](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/tests/test_converge_template_scaffold.py) | `main@59d61c5` |
| before/after hooks | [extensions API](https://github.com/github/spec-kit/blob/59d61c59630c3bd5a294f4c23e43a60d8ab98d02/docs/extensions/api.md) | `main@59d61c5` |
| 本地无 converge、版本要求和现有循环 | [preset.yml](../../preset.yml)、[speckit.analyze.md](../../commands/speckit.analyze.md)、[speckit.rectify.md](../../commands/speckit.rectify.md)、[speckit.implement.md](../../commands/speckit.implement.md)、[speckit.acceptance.md](../../commands/speckit.acceptance.md)、[speckit.release.md](../../commands/speckit.release.md)、[README.md](../../README.md)、[README.zh-CN.md](../../README.zh-CN.md) | 本地 `main@39dd5f795e6a04d0e02efb5c40790467fa71bad0` |
