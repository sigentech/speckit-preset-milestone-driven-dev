---
description: 在 converge 报告 Converged 后执行可选 AI 辅助验收模拟，生成带证据和人工待验指南的 acceptance-simulation.md。
---

## 目的

在核心 `speckit.converge` 报告 `Converged` 后、正式 `speckit.acceptance` 前，对当前实现做一次**可选**预验收。它是 AI 辅助验收模拟，不是正式验收，也不能替代用户对真人体验、真实设备、外部系统和最终发布的确认。

输出固定为：`specs/[NNN-mX-slug]/acceptance-simulation.md`

## 用户输入

~~~text
$ARGUMENTS
~~~

可指定 spec 目录；缺省取当前 feature/Mx 分支对应的活跃 spec。

## 前置检查

1. 当前分支必须是 `feature/Mx`，并选定唯一活跃 spec 目录。
2. `tasks.md` 中全部 Agent 可执行任务必须已完成；标记“需人工”的任务不要求 Agent 代为完成。
3. 当前会话最近一次 `speckit.converge` 必须明确报告 `Converged`，且没有待回到 `speckit.implement` 的新增任务。无法确认时停止，先运行 `/speckit.converge`。
4. 不读取尚待 acceptance 生成的当前 `implementation-report.md` 作为验收事实。历史报告只有 baseline 与当前实现一致时才能作为背景线索，不能代替当前证据。
5. 在收集运行证据前执行 `git status --porcelain=v1 --untracked-files=all`。输出必须为空，或只包含目标 `acceptance-simulation.md`；任何其他已跟踪或未跟踪变更都表示实现基线不干净，必须停止，先提交或清理实现变更后重新 converge，不得生成可用于正式验收的模拟。
6. 重新运行模拟时，若现有 `implementation-report.md` 未提交，不得把它当作任意生成文件静默豁免。必须明确提示用户先提交或移除该未提交报告，再重新运行模拟；目标 `acceptance-simulation.md` 是唯一允许存在于清洁基线中的未提交生成文件。

## 执行步骤

1. **采集验收事实**
   - 读取 `spec.md` 的需求与验收标准、`plan.md` 的技术/验证决策、`tasks.md` 的实现结果与“需人工”任务。
   - 读取 `.specify/memory/milestones.md` 中本里程碑的“用户验收指导”。
   - 查看当前代码、测试、已有截图/日志及其他实现证据，并记录本轮 converge 的 `Converged` 结果。
   - 在分类任何验收项之前，从当前源文件独立构建**期望验收集**，并为每个来源项分配稳定来源键：
     - spec 验收标准使用 `spec:AC-01`（有既有稳定标识时使用 `spec:[既有标识]`）。
     - 里程碑“用户验收指导”的编号条目使用 `milestone:Mx-UA-01`。
     - tasks 中标记“需人工”的任务使用 `tasks:T012-manual`。
   - 对每个来源条目，按固定算法计算 `判据指纹: sha256:<hex>`：去除列表标记、checkbox、稳定来源键及其后的分隔冒号后，取完整验收判据正文；先做 Unicode NFC 规范化，行尾统一为 LF，去掉首尾空白，把内部连续空白折叠为一个空格，再以 UTF-8 编码并计算 SHA-256，输出 64 位小写十六进制。
   - 每个模拟来源行必须同时记录稳定来源键与 `判据指纹: sha256:<hex>`，并在“验收判据”列保留当前来源的完整判据正文。
   - “来源覆盖校验”必须列出当前期望来源键、当前判据指纹、模拟中的来源键、模拟判据指纹，以及缺失、额外或重复的来源键。每个期望来源键在总表中必须恰好出现一次且判据指纹精确匹配；任何缺失、额外、重复或指纹不匹配都使模拟不可导入。
   - 同一验收判据被多个来源提及时分别保留稳定来源键；不能为了凑数把一个来源键分配给多项。

2. **建立 baseline**
   - 记录当前分支、`git rev-parse HEAD`、生成日期、converge 结果，以及前置检查中 `git status --porcelain=v1 --untracked-files=all` 的原样输出。
   - 记录“工作区清洁基线”为 `PASS` 时必须证明除目标 `acceptance-simulation.md` 外没有任何已跟踪或未跟踪变更；否则不得生成有效模拟。
   - 对 `spec.md`、`plan.md`、`tasks.md` 分别计算 SHA-256 摘要指纹并记录，供 acceptance 判断是否过期。

3. **逐项执行可行检查**
   - 优先使用 plan、tasks 或项目配置中已经声明的测试、构建、lint、type、运行和接口检查命令。
   - 实际执行可安全运行的检查，记录工作目录、完整命令、退出码、关键输出、观察时间和证据路径/摘要。
   - 只有“已实际执行、证据直接支持该验收判据，且命令成功”才能标记 `AI_PASS`。退出码必须为 0；若命令确实以非零退出码表示成功，必须记录明确的“预期非零成功契约”，包括契约来源、精确预期退出码、为何非零代表成功，以及可复核输出证明，否则不得标记 `AI_PASS`。
   - 已执行并取得失败证据的标记 `AI_FAIL`，不得把失败改写为待人工验收。
   - 无法可靠自动化、需要真人主观判断、真实设备、外部账号、真实支付、生产数据、破坏性操作、无障碍真人体验或安全凭证的项目，标记 `HUMAN_REQUIRED` 或 `BLOCKED`，并写完整人工指南。
   - 不得伪造测试输出、退出码、截图、日志、接口响应、外部系统状态或人类体验结论；“查看代码后认为应该能通过”不是运行证据。

4. **固定状态与路由**
   - 每项只能使用 `AI_PASS`、`AI_FAIL`、`HUMAN_REQUIRED`、`BLOCKED` 之一，并写明原因。
   - `AI_FAIL` 必须定位根因并路由到恰好一个上游入口：
     - 需求/验收标准歧义或缺失：`speckit.clarify`
     - 技术方案、架构、依赖或数据模型缺陷：`speckit.plan`
     - 实现任务缺失、拆分或顺序错误：`speckit.tasks`
     - 现有任务内可修复的实现、回归或测试失败：`speckit.implement`
   - `HUMAN_REQUIRED` 与 `BLOCKED` 不视为通过；解除阻塞所需条件必须可执行、可观察。

5. **生成模拟报告**
   - 从 `templates/acceptance-simulation-template.md` 生成 `acceptance-simulation.md`。
   - 必须包含 baseline、来源覆盖校验（含判据指纹）、汇总、全部验收项结果表、`AI_PASS` 明细、`AI_FAIL` 明细、人工待验区和结论。
   - 每个仍待人工的项必须有独立小节，完整覆盖：验收目标、前置条件与环境、编号操作步骤、测试数据/输入、可观察的预期结果、通过/不通过/阻塞的判定标准、记录位置、为什么 Agent 不能可靠完成。
   - 结论只能是：
     - 无失败且无人工项：`ready-for-acceptance`
     - 存在任一 `AI_FAIL`：`needs-implementation`
     - 无 `AI_FAIL` 但存在 `HUMAN_REQUIRED`/`BLOCKED`：`needs-user-input`

6. **交接**
   - 汇总各状态数量、模拟报告路径、失败路由和待人工项数量。
   - 若结论为 `needs-implementation`，停止并执行对应上游路由；修复后重新 converge，必要时重新运行本命令。
   - 若 baseline 之后出现除目标 `acceptance-simulation.md` 外的任一已跟踪或未跟踪变更，或 spec、plan、tasks 发生变化，本报告立即过期，必须重跑。
   - 只有模拟报告 baseline 与当前产物一致、来源键与判据指纹均通过认证、来源覆盖恰好一一对应且不存在 `AI_FAIL` 时，才可进入 `/speckit.acceptance`。来源键正确但判据文本被替换、缺失或指纹不匹配时，整个模拟失效并退回全人工验收。

## 约束

- 本命令不修改正式 `implementation-report.md`，不把 `AI_PASS` 声明为最终验收。
- 最终验收与 release 确认始终由用户完成。
- 不能实际执行的检查不得标记 `AI_PASS`；缺少证据时降级为 `HUMAN_REQUIRED` 或 `BLOCKED`。
