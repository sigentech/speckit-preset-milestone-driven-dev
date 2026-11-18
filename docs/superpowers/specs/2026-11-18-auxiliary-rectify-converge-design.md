# `.auxiliary`、分级分析与收敛闭环设计

| 项目 | 值 |
| --- | --- |
| 日期 | 2026-11-18 |
| 目标版本 | preset `1.6.0` |
| 选定方案 | 直接复用核心 `speckit.converge`，只调整 preset 编排与文档 |
| 最低 spec-kit | `>=1.0.9` |

## 1. 意图与范围

本轮把 preset 从“规格体系分析消除后直接实现、验收”升级为完整闭环：

```text
analyze/rectify 清零
-> implement
-> converge
-> 有追加任务则 implement -> converge
-> Converged
-> 可选 simulate-acceptance
-> acceptance
-> release
```

同时完成四项局部改造：

1. 分析报告目录统一为 `.auxiliary/`。
2. `speckit.analyze` 为每个问题输出完整证据、影响、修复建议和唯一上游命令。
3. `speckit.rectify` 严格按 clarify、plan、tasks 三个层级依次清空问题，再进入实现。
4. 新增可选命令 `speckit.simulate-acceptance`，让 Agent 基于真实实现证据代替用户完成可自动验证的验收项，并把无法可靠模拟的项目交给人工。

## 2. 非目标

- 不新增或覆盖 `commands/speckit.converge.md`。
- 不改变上游 converge 的意图源、append-only、无缺口零写入和 hook 契约。
- 不让 converge 修改 spec、plan、代码或分析报告。
- 不允许模拟验收伪造运行结果、截图、外部系统状态或人工体验结论。
- 不改变里程碑、prototype、hotfix 的既有业务规则。
- 不新增需要人工维护的 convergence 状态文件。

## 3. 方案取舍

### 方案 A：直接复用核心命令并调整本地编排（已选）

- 不复制上游命令正文，自动继承后续修复。
- 修改 implement 的交接、acceptance 前置门禁、navigator 和双 README。
- 版本门槛设为 `>=1.0.9`，确保“任务勾选不是完成证据”的语义可用。
- 维护成本最低，语义漂移风险最小。

### 方案 B：本地 override converge

- 可在命令内部记录收敛状态并自动交接。
- 需要复制上游完整命令并长期跟踪 hooks、脚本和语义变化。
- 本轮收益不足以抵消维护成本，不采用。

### 方案 C：仅文档推荐

- 不把 converge 设为验收门禁，容易漏跑或生成过期验收报告。
- 无法保证每个里程碑真正收敛，不采用。

## 4. 目录统一

所有活动命令、模板、manifest、README、CHANGELOG 和研究记录中的分析报告目录统一为：

```text
./.auxiliary/docs/specs-analysis-repo/[spec-dir]-analysis.md
```

`.auxiliary` 是默认目录，不是强制唯一目录。所有命令、模板和文档使用同一条机器可读解析规则：

1. 在 constitution 中查找唯一一行 `analysis_report_dir: <path>`。
2. 存在时使用 `<path>` 作为分析报告目录，路径相对项目根解析。
3. 不存在时使用默认目录 `./.auxiliary/docs/specs-analysis-repo/`。
4. 报告文件名固定为 `[spec-dir]-analysis.md`，完整路径为 `<analysis-report-dir>/[spec-dir]-analysis.md`。
5. 重复键、空路径、含通配符或无法唯一解析的登记必须停止流程，不得猜测自定义路径。

验收条件：仓库中不再存在旧目录名的引用。历史 changelog 也直接使用统一后的名称，并在 `1.6.0` 记录本轮目录迁移。preset 不自动移动用户项目中的既有报告；中文和英文 README 的升级说明要求曾固定旧默认路径的项目同步修改 constitution 和目录。

## 5. `speckit.analyze` 报告合同

每轮报告必须包含：

1. 状态、轮次、输入基线和各级问题计数。
2. Critical、High、Medium、Low 四个独立分区；某级无问题也必须明确写“无”。
3. 每个问题使用独立问题卡，至少包含：
   - 问题 ID；
   - 稳定问题键；
   - 严重级；
   - 分析维度；
   - 来源位置；
   - 证据；
   - 详细问题描述；
   - 影响；
   - 修复入口命令；
   - 具体修改建议；
   - 消除后的验证判据。
4. 修复入口必须且只能是以下一个命令：
   - `speckit.clarify`：规格目标、范围、歧义、验收标准等规格层问题；
   - `speckit.plan`：架构、技术选择、契约、数据与依赖设计等方案层问题；
   - `speckit.tasks`：任务缺口、顺序、依赖或文件范围等任务层问题。
5. 跨层问题路由到能消除根因的最上游命令，不得并列多个入口。
6. 修改建议必须说明改哪份产物的哪一节、改成什么以及如何验证，不能只写“补充”“优化”“调整”。
7. 对话输出除计数外，应展示全部问题摘要；报告落盘保存全部详细问题卡。
8. 稳定问题键用于跨轮识别同一根因。重跑 analyze 时，若入口命令、根因与来源锚点未发生实质变化，必须沿用原问题键和原 ID，并记录首次出现轮次；措辞或严重级变化不产生新键。根因实质变化或发现独立新问题时才分配新键，并可用“关联问题”字段指向旧问题。

模板会从“简表 + 路由标签”升级为“汇总表 + 分级详细问题卡 + 消除记录”。为兼容用户措辞，`critic` 统一规范为 `Critical`。

## 6. `speckit.rectify` 三阶段闭环

### 6.1 阶段顺序

固定顺序为：

```text
clarify 阶段 -> plan 阶段 -> tasks 阶段
```

每个阶段执行同一个循环：

1. 读取最新分析轮次。
2. 筛出当前阶段唯一入口命令对应的问题。
3. 按 Critical -> High -> Medium -> Low 排序；同级按报告编号升序。
4. 在会话中先输出本轮问题表，包含编号、严重级、来源、描述、建议动作。
5. 一次性调用当前阶段的 `speckit.clarify`、`speckit.plan` 或 `speckit.tasks` 处理全部已列出问题。
6. 将处置结果写回当前分析轮次的消除记录。
7. 调用一次 `speckit.analyze` 生成新轮次。
8. 重新读取新轮次；若当前入口仍存在问题，重复本阶段。

### 6.2 阶段推进与跨层回归

- clarify 阶段只在最新报告没有 `speckit.clarify` 问题时进入 plan 阶段。
- plan 阶段只在最新报告没有 `speckit.plan` 问题时进入 tasks 阶段。
- tasks 阶段只在最新报告没有 `speckit.tasks` 问题时结束整个 rectify。
- 下游修改若重新引入上游问题，必须回到最早受影响阶段。例如 tasks 修改产生新的 clarify 问题，则回到 clarify 阶段；plan 修改产生新的 clarify 问题同理。
- 只有最新一轮四类问题全部为零，才报告闭环完成并允许 implement。

### 6.3 安全护栏

- 不提供 Low 豁免；Critical、High、Medium、Low 全部消除。
- 同一稳定问题键连续两轮仍未消除时停止自动循环，交用户裁决，避免无限循环。
- 每次只处理当前阶段列出的全部问题，不跨阶段混排。
- rectify 仍只修改 spec、plan、tasks 与分析报告，不修改代码。

稳定问题键由 analyze 维护，至少由“路由命令 + 来源锚点 + 根因类别”组成。rectify 不自行改写问题键；若认为 analyze 的合并或拆分有误，先请用户裁决并记入报告附注。

## 7. converge 编排

### 7.1 命令复用

- 直接使用核心 `speckit.converge`，本地不新增同名命令。
- 保持其 `spec.md`、`plan.md`、`tasks.md` 唯一意图源地位。
- 保持 `missing / partial / contradicts / unrequested` 分类和 `CRITICAL / HIGH / MEDIUM / LOW` 严重度。
- 保持 `tasks_appended` 后重新 implement、`Converged` 后才可验收的循环。

### 7.2 本地交接

- `speckit.implement` 完成全部 Agent 可执行任务后，handoff 到 `speckit.converge`，不再直接进入 acceptance。
- 标记为“需人工”的任务不等待人工执行；它们不是 Agent 可执行实现任务。implement 完成后即进入 converge，这些任务最终展开为 acceptance 的人工验收项。
- converge 若指出人工任务背后仍缺少代码实现，应补充实现任务并回到 implement；不得为了绕过 converge 把人工任务直接勾选完成。
- converge 追加任务时，用户或 agent 回到 `speckit.implement`；完成后再 converge。
- converge 输出 `Converged` 后才可进入可选的 `speckit.simulate-acceptance`，再由 `speckit.acceptance` 生成正式报告。
- `speckit.acceptance` 增加门禁：tasks 全部完成；当前会话能确认最近一次 converge 为 `Converged`。无法确认时必须先运行 converge；若追加任务则停止验收并回到 implement。
- implementation report 记录 converge 已收敛及分析报告轮次，确保验收基于已收敛范围。

### 7.3 navigator

状态表增加收敛环节：

- 分析未清零：`/speckit.rectify`；
- 报告清零但任务未完成：`/speckit.implement`；
- 实现任务完成且尚无验收报告：先 `/speckit.converge`；确认 `Converged` 后可运行 `/speckit.simulate-acceptance`，最后运行 `/speckit.acceptance`。

tasks 中因 converge 追加的未完成任务会使状态自然回到 implement，形成可检测的循环。

## 8. 可选验收模拟

### 8.1 定位与命名

新增可选命令：

```text
speckit.simulate-acceptance
```

它位于 converge 报告 `Converged` 之后、acceptance 生成正式验收报告之前。未运行该命令时，acceptance 保持现有行为。

该命令是“预验收”而不是正式验收报告：

- 读取 spec、plan、tasks、里程碑用户验收指导、当前代码、测试、截图、运行日志和其他实现证据；
- 对可自动观察的项目执行验证并记录证据；
- 对必须依赖真人、真实设备、外部账号、支付、隐私、触觉、主观体验或不可安全自动化操作的项目，明确标记为人工待验；
- 不把“代码看起来正确”当成运行证据，不允许猜测通过。

不读取尚由 acceptance 生成的 `implementation-report.md` 作为前置输入，避免循环依赖；若项目中已经存在旧报告，可作为背景参考，但必须校验 baseline，不能替代当前实现证据。

### 8.2 验收状态

模板中的每个验收项只能使用以下状态：

| 状态 | 含义 | 后续动作 |
| --- | --- | --- |
| `AI_PASS` | Agent 已执行检查并取得足以支持通过的证据 | acceptance 预填“通过”，保留证据链接/摘要 |
| `AI_FAIL` | Agent 已获得失败证据 | 阻止 acceptance；按根因回到 implement 或 rectify |
| `HUMAN_REQUIRED` | 无法由 Agent 可靠模拟，必须真人完成 | 保留“待验收”，输出逐项操作指南 |
| `BLOCKED` | 缺少凭证、设备、服务或环境，当前不能执行 | 视为人工待验，并说明解除阻塞所需条件 |

`AI_PASS`、`AI_FAIL`、`HUMAN_REQUIRED`、`BLOCKED` 均必须附原因；只有 `AI_PASS`/`AI_FAIL` 可以包含自动化执行证据。

### 8.3 模板合同

新增模板：

```text
templates/acceptance-simulation-template.md
```

输出文件：

```text
specs/[NNN-mX-slug]/acceptance-simulation.md
```

模板至少包含：

1. 基线：分支、commit、spec/plan/tasks 摘要指纹、converge 结果、生成日期。
2. 汇总：验收项总数、`AI_PASS`、`AI_FAIL`、`HUMAN_REQUIRED`、`BLOCKED` 数量。
3. 全部验收项结果表：编号、稳定来源键、判据指纹、来源、验收判据、状态、证据、置信度、后续动作。
4. `AI_PASS` 明细：实际执行的命令/检查、关键输出、证据路径。
5. `AI_FAIL` 明细：失败现象、证据、问题根因路由（`speckit.clarify` / `speckit.plan` / `speckit.tasks` / implement）。
6. 人工待验区：每个 `HUMAN_REQUIRED`/`BLOCKED` 项必须独立成节，包含：
   - 验收目标；
   - 前置条件与环境；
   - 编号操作步骤；
   - 测试数据/输入；
   - 可观察的预期结果；
   - 通过、不通过、阻塞的判定标准；
   - 结果记录位置；
   - 为什么 Agent 不能可靠完成。
7. 结论：`ready-for-acceptance`、`needs-implementation` 或 `needs-user-input`。

每个来源条目必须同时记录稳定来源键和 `判据指纹: sha256:<hex>`。判据指纹固定使用 SHA-256：先对当前来源的完整验收判据正文做 Unicode NFC 规范化，将行尾统一为 LF，去掉首尾空白，把内部连续空白折叠为一个空格，再以 UTF-8 编码规范文本并计算 SHA-256，输出 64 位小写十六进制。

### 8.4 acceptance 集成

- 若 `acceptance-simulation.md` 存在且 baseline 与当前代码/产物一致：
  - `AI_PASS` 项直接预填 implementation report 的验收结果并引用证据；
  - `HUMAN_REQUIRED`/`BLOCKED` 项保持“待验收”，复制逐项操作指南；
  - 存在 `AI_FAIL` 时禁止生成正式验收报告。
- 正式 acceptance 必须从当前每个来源条目独立提取验收判据正文，按同一算法重新计算判据指纹，并要求模拟来源行的来源键和判据指纹都精确匹配。仅验证稳定来源键不足以证明被验收的事实未被替换。
- 判据文本缺失、被替换、同键解析出多段、无法解析或任一判据指纹不匹配时，整个模拟失效并退回全人工验收，不得导入任何 `AI_PASS`；`AI_FAIL` 仍按失败优先处理。
- 先扫描可见 `AI_FAIL`。只要存在 `AI_FAIL`，即使 baseline 已过期，也阻止正式验收并路由到唯一上游命令。
- 若模拟报告缺失或已过期，acceptance 按现有流程生成全部待人工验收项，并可提示用户先运行模拟命令。
- 模拟不能降低安全门槛：凭证缺失、真实支付、生产数据、破坏性操作、真实设备、无障碍真人体验等默认留给用户。
- 正式验证前必须存档验收判据指纹，并建立包含 HEAD、`git status --porcelain=v1 --untracked-files=all` 和 spec/plan/tasks SHA-256 指纹的快照。验证命令执行后、写报告或更新里程碑前，必须逐项复检同一快照；任一项变化都证明仓库或验收意图被验证过程改变，模拟失效，停止报告生成并要求重新 converge。

### 8.5 编排与回退

推荐流程：

```text
Converged
-> /speckit.simulate-acceptance（可选）
-> AI_FAIL：回到 implement 或 rectify，再 converge
-> AI_PASS / HUMAN_REQUIRED / BLOCKED 混合：/speckit.acceptance
-> 用户只处理剩余人工待验项
-> /speckit.release
```

若所有项目均为 `AI_PASS`，acceptance 报告中人工待验项为零，但仍保留最终 release 的人工确认。

`AI_FAIL` 是独立失败信号：即使 baseline 已过期、格式不完整或其余结果不能导入，可见的 `AI_FAIL` 仍然最先阻止 acceptance。

## 9. 版本与发布元数据

- preset 版本：`1.5.0 -> 1.6.0`，包含可选验收模拟。
- `requires.speckit_version`：`>=0.5.0 -> >=1.0.9`。
- README 徽章、安装 tag、版本表、快速开始同步到 `v1.6.0`。
- README 说明 converge 是核心命令，不在 preset 的 commands 清单中。
- CHANGELOG 新增 `1.6.0`，记录目录统一、analyze 合同、rectify 分阶段循环、converge 编排、可选验收模拟和文档双语同步。
- `agents-reminder-template` 标记版本升级为 `v1.6.0`。

## 10. 文档修改

英文和中文 README 必须同步：

- 标题下流程从“analyze/rectify -> implement -> acceptance”扩展到包含 converge；
- Mermaid 增加 converge 与条件回环；
- 里程碑循环表增加 converge 与可选 simulate-acceptance 步骤并更新步骤编号；
- Key Rules 说明 rectify 与 converge 的分工；
- 配置表的分析报告路径改为 `.auxiliary`；
- 文件清单明确 converge 来自 spec-kit 核心；
- 清理本次触及区域内既有的重复段落和重复代码块。

## 11. 文件影响

预计修改：

- `commands/speckit.analyze.md`
- `commands/speckit.rectify.md`
- `commands/speckit.implement.md`
- `commands/speckit.acceptance.md`
- `commands/speckit.simulate-acceptance.md`
- `templates/analysis-report-template.md`
- `templates/implementation-report-template.md`
- `templates/acceptance-simulation-template.md`
- `templates/agents-reminder-template.md`
- `preset.yml`
- `README.md`
- `README.zh-CN.md`
- `CHANGELOG.md`
- `docs/research/2026-11-18-speckit-converge.md`

不新增 `commands/speckit.converge.md`。commands 数量由 14 增至 15，templates 由 10 增至 11。

## 12. 验证

1. 搜索确认仓库不存在旧目录名。
2. 解析 `preset.yml`，确认版本、最低 spec-kit 版本、命令数为 15、模板数为 11。
3. 使用本机 `specify preset` 校验 preset manifest 与模板解析。
4. 检查 analyze 模板四个严重级和三个唯一入口命令均完整出现。
5. 检查 rectify 文档的阶段顺序、循环条件、回归规则和两轮停止护栏。
6. 检查 implement、acceptance、simulate-acceptance、navigator 均包含正确的 converge/模拟验收交接或门禁。
7. 检查英文与中文 README 的流程、命令顺序、路径和版本信息一致。
8. 检查 Mermaid 节点没有孤立步骤，converge 回环和 acceptance 分流清楚。
9. 检查验收模拟模板的每个 `HUMAN_REQUIRED`/`BLOCKED` 项都有完整操作步骤、预期结果、判定标准和记录位置。
10. 使用固定文本夹具验证正确来源键 + 被替换判据或错误指纹会被拒绝，并覆盖缺失、非十六进制和大小写不合规的指纹。
11. 检查 acceptance 在验证前建立快照，在验证后、报告/里程碑写入前复检 HEAD、工作区状态和 spec/plan/tasks 指纹。

## 13. 已知限制

- 上游 converge 在无缺口时按要求不写任何文件，因此没有持久“已收敛”标记；acceptance 需要依赖当前会话结果，若上下文丢失则重新运行 converge。
- 版本门槛选择 `>=1.0.9` 高于命令首次出现的版本，这是为了保证 preset 依赖的完整完成性语义。
