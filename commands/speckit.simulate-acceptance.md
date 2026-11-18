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

## 执行步骤

1. **采集验收事实**
   - 读取 `spec.md` 的需求与验收标准、`plan.md` 的技术/验证决策、`tasks.md` 的实现结果与“需人工”任务。
   - 读取 `.specify/memory/milestones.md` 中本里程碑的“用户验收指导”。
   - 查看当前代码、测试、已有截图/日志及其他实现证据，并记录本轮 converge 的 `Converged` 结果。
   - 为每个验收判据分配稳定编号并记录来源；同一判据被多个来源提及时合并去重。

2. **建立 baseline**
   - 记录当前分支、`git rev-parse HEAD`、生成日期和 converge 结果。
   - 对 `spec.md`、`plan.md`、`tasks.md` 分别计算 SHA-256 摘要指纹并记录，供 acceptance 判断是否过期。

3. **逐项执行可行检查**
   - 优先使用 plan、tasks 或项目配置中已经声明的测试、构建、lint、type、运行和接口检查命令。
   - 实际执行可安全运行的检查，记录工作目录、完整命令、退出码、关键输出、观察时间和证据路径/摘要。
   - 只有“已实际执行且证据直接支持该验收判据”才能标记 `AI_PASS`。
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
   - 必须包含 baseline、汇总、全部验收项结果表、`AI_PASS` 明细、`AI_FAIL` 明细、人工待验区和结论。
   - 每个仍待人工的项必须有独立小节，完整覆盖：验收目标、前置条件与环境、编号操作步骤、测试数据/输入、可观察的预期结果、通过/不通过/阻塞的判定标准、记录位置、为什么 Agent 不能可靠完成。
   - 结论只能是：
     - 无失败且无人工项：`ready-for-acceptance`
     - 存在任一 `AI_FAIL`：`needs-implementation`
     - 无 `AI_FAIL` 但存在 `HUMAN_REQUIRED`/`BLOCKED`：`needs-user-input`

6. **交接**
   - 汇总各状态数量、模拟报告路径、失败路由和待人工项数量。
   - 若结论为 `needs-implementation`，停止并执行对应上游路由；修复后重新 converge，必要时重新运行本命令。
   - 若 baseline 之后代码、spec、plan 或 tasks 发生变化，本报告立即过期，必须重跑。
   - 只有模拟报告 baseline 与当前产物一致且不存在 `AI_FAIL` 时，才可进入 `/speckit.acceptance`。

## 约束

- 本命令不修改正式 `implementation-report.md`，不把 `AI_PASS` 声明为最终验收。
- 最终验收与 release 确认始终由用户完成。
- 不能实际执行的检查不得标记 `AI_PASS`；缺少证据时降级为 `HUMAN_REQUIRED` 或 `BLOCKED`。
