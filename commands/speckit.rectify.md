---
description: 分阶段问题消除闭环——按 speckit.clarify 阶段 → speckit.plan 阶段 → speckit.tasks 阶段固定顺序循环，逐阶段 analyze 清零，并在下游引入上游问题时回退。
handoffs:
  - label: 重新分析
    agent: speckit.analyze
    prompt: 当前阶段问题已消除，重新分析验证
    send: true
---

## 目的

严格按分析报告中的唯一修复入口命令分阶段消除问题，直到最新一轮 analyze 的 Critical、High、Medium、Low 全部为零。每个问题只进入其修复入口对应的一个阶段；阶段推进和回退均以最新 analyze 轮次为准。

## 用户输入

~~~text
$ARGUMENTS
~~~

可指定 spec 目录；缺省取当前分支对应的活跃 spec（feature/Mx → specs/NNN-mX-…/）。

## 执行算法

1. **加载并校验报告**：读取 `./.auxiliary/docs/specs-analysis-repo/[spec-dir]-analysis.md` 的最新轮次，取得全部“未消除”问题及其问题 ID、稳定问题键、严重级、修复入口命令、具体修改建议和验证判据。
   - 若“修复入口命令”缺失或包含多个命令，停止并提示重跑 `speckit.analyze`，不得自行猜测路由。
   - 若没有未消除问题，提示直接重跑 analyze 或进入 `speckit.implement`，退出。
   - 仅处理下列三个修复入口：`speckit.clarify`、`speckit.plan`、`speckit.tasks`。

2. **按严重级排序**：每个阶段内按 Critical → High → Medium → Low 排序并全部处理，不提供 Low 豁免。

3. **speckit.clarify 阶段**：
   - 处理最新报告中全部修复入口为 `speckit.clarify` 的问题，按具体修改建议和验证判据最小化修改 `spec.md`。
   - 本批全部处理完并记录后，调用 `speckit.analyze` 追加新一轮。
   - 若新一轮仍有 `speckit.clarify` 问题，继续本阶段；直到该入口问题为零，才进入 plan 阶段。

4. **speckit.plan 阶段**：
   - 处理最新报告中全部修复入口为 `speckit.plan` 的问题，按具体修改建议和验证判据最小化修改 `plan.md`。
   - 本批全部处理完并记录后，调用 `speckit.analyze` 追加新一轮。
   - 若新一轮出现 `speckit.clarify` 问题，立即停止 plan 阶段并**回到最早受影响阶段**，先重新执行 clarify 阶段；若只有 `speckit.plan` 问题，继续本阶段，直到该入口问题为零。

5. **speckit.tasks 阶段**：
   - 处理最新报告中全部修复入口为 `speckit.tasks` 的问题，按具体修改建议和验证判据最小化修改 `tasks.md`。
   - 本批全部处理完并记录后，调用 `speckit.analyze` 追加新一轮。
   - 若新一轮出现 `speckit.clarify` 或 `speckit.plan` 问题，**回到最早受影响阶段**并重新执行对应阶段及其后的顺序；若只有 `speckit.tasks` 问题，继续本阶段，直到该入口问题为零。

6. **阶段推进与收敛**：
   - 每次 analyze 后先检查更早阶段的问题，再决定重复当前阶段或推进；下游问题不得越过未清零的上游阶段。
   - clarify、plan、tasks 三个入口在最新一轮同时为零时，将报告状态记为“已清零”并提示进入 `speckit.implement`。
   - 每次回退都要在“阶段化 rectification 记录”中写明触发问题 ID、稳定问题键、目标阶段和回退原因。

7. **用户介入停止条件**：
   - 跟踪稳定问题键在连续 analyze 轮次中的状态。同一稳定问题键连续两轮仍未消除时，立即停止自动消除，保留当前报告与修改记录，并向用户说明问题、已尝试的修改和阻塞点。
   - 措辞或严重级变化但稳定问题键不变，仍视为同一问题。等待用户裁决后，才可继续。

## 记录要求

- 每个问题处理后，在最新轮次的“消除记录”中填写处置方式、结果、验证和日期。
- 每次 analyze 后，在“阶段化 rectification 记录”中按固定顺序追加阶段、问题 ID、analyze 轮次、阶段结果与回退记录。
- 连锁处理、人工裁决及回退原因写入“消除过程附注”。
- 修改必须可追溯到具体问题；不得只记录“已处理”而缺少对应验证判据。

## 约束

- **Critical/High/Medium/Low 全部必须消除，不提供 Low 豁免。**
- 本命令只修改 spec/plan/tasks 与分析报告，不改代码。
- 不得绕过尚未清零的上游阶段，也不得在同一阶段内跨入口混排问题。
- 不得推翻已冻结产物；需要解冻时先取得用户显式确认并记录。
- 修改不得与 constitution 冲突，不得引入新的上游问题；一旦引入，按回退规则处理。
