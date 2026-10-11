---
description: 问题消除编排——依据最新一轮分析报告，依次调用 clarify→plan→tasks 消除问题（Critical/High/Medium/Low 全部立即消除），记录消除结果，防引入新问题，随后重跑 analyze 验证。
handoffs:
  - label: 重新分析
    agent: speckit.analyze
    prompt: 问题已消除，重新分析验证
    send: true
---

## 目的

把"分析报告里的问题"变成"已消除的问题"。按报告中的消除建议，依次用 `speckit.clarify`、`speckit.plan`、`speckit.tasks` 三个技能消除存在的问题；消除后更新分析报告记录消除结果；然后重跑 `speckit.analyze` 验证清零。

## 用户输入

~~~text
$ARGUMENTS
~~~

可指定 spec 目录；缺省取当前分支对应的活跃 spec（feature/Mx → specs/NNN-mX-…/）。

## 执行步骤

1. **加载报告**：`.prepare/docs/specs-analysis-repo/[spec目录名]-analysis.md`，取最新一轮中"待处置"的问题。无待处置项 → 提示直接重跑 analyze 或进入 implement，退出。
2. **排序**：按 Critical → High → Medium → Low 处理；同级按消除建议的路由分组（先 clarify 层、再 plan 层、后 tasks 层——上游修改可能引起下游连锁更新）。
3. **逐条消除**：
   - **路由到 clarify 的**：执行 speckit.clarify 流程，按消除建议改写 spec.md 对应位置（歧义消解、验收标准可测化、范围边界明确）
   - **路由到 plan 的**：执行 speckit.plan 的修订流程，调整 plan.md（结构调整、技术选型修正、契约补全）
   - **路由到 tasks 的**：执行 speckit.tasks 的修订/重生成，对齐 tasks.md（补缺口、修顺序、标依赖）
   - 每条处理遵循**最小改动**原则：只改消除该问题所必需的内容
4. **防引入新问题护栏**（每条消除后自查）：
   - 改动不得与 constitution 条款冲突
   - 改动不得推翻已冻结产物（spec 已冻结则需用户显式解冻确认并记录）
   - 改动不得使其他已无问题的条目重新失效（如同名实体两处定义改了一处）——发现连锁必须同轮处理，记入"消除过程附注"
   - 拿不准的（建议本身可能有误）：呈现建议与风险，请用户裁决后记入附注，**不得自作主张偏离建议**
5. **记录消除结果**：在分析报告当前轮次的"消除结果"表逐条填写（处置方式/结果/日期/验证）；连锁处理与用户裁决记入"消除过程附注"。
6. **重跑 analyze**：调用 `speckit.analyze` 追加新一轮次。判定：
   - 新一轮 Critical/High/Medium/Low 均为 0 → 状态"已清零"，报告闭环，提示进入 `speckit.implement`
   - 仍有遗留（含新引入）→ 回到第 1 步循环；同一问题连续两轮未消除 → 停下请用户介入（可能建议本身需要人工改判）

## 约束

- **Critical/High/Medium/Low 全部必须立即消除**——没有"暂不处理"选项；确需豁免的由用户显式裁决并记入附注（仅 Low 可豁免，且需理由）
- 本命令只改 spec/plan/tasks 与分析报告，不改代码
- 每个问题消除后立即可追溯：报告中必须有对应记录
