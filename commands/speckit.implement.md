---
description: （定制覆盖）编码实现——核心流程之上：执行前确认分析报告已清零、全程在 feature/Mx 分支、全部 Agent 可执行任务完成后自动接续核心 speckit.converge 收敛检查。
handoffs:
  - label: 运行 converge 收敛检查
    agent: speckit.converge
    prompt: 全部 Agent 可执行任务已完成，运行 converge 收敛检查
    send: true
---

## 与核心命令的关系

先按核心 `speckit.implement` 完整流程执行（按 tasks.md 逐任务实现代码）；本文件定义**前置门禁与收尾动作**。

## 前置门禁

1. 当前分支为 `feature/Mx` 且与 spec 目录的里程碑号一致；不一致则停止并提示切换。
2. 按唯一规则解析分析报告路径：读取 `.specify/memory/constitution.md`；存在唯一一行 `analysis_report_dir: <path>` 时使用该目录，否则使用 `./.auxiliary/docs/specs-analysis-repo/`；文件名固定为 `[spec-dir]-analysis.md`。重复、空或不可解析的路径登记必须停止并要求修正 constitution。
3. 解析后的分析报告最新状态为"已清零"；否则停止并提示先走 `speckit.rectify` → `speckit.analyze`。
4. 工作区无未提交的非本里程碑改动（防串味；有则提示先提交或 stash）。

## 执行中的定制要求

- 提交粒度：按 tasks.md 阶段分批提交，提交信息格式 `feat(Mx): [任务摘要]`（docs 用 `docs(Mx):`，测试用 `test(Mx):`）
- 遇到 spec/plan 未覆盖的实现歧义：**停下**，按 speckit.rectify 的路由逻辑回补规格（clarify/plan/tasks），再继续——禁止在代码里静默发明规格
- 每完成一个任务勾选 tasks.md；标记为"需人工"的任务不强行实现，保留为验收报告中的待人工验收项

## 收尾动作（核心流程执行完毕后）

1. 确认 tasks.md 中全部 **Agent 可执行**任务已完成；标记“需人工”的任务不视为未完成的 Agent 实现，不得因此停留在 implement。
2. 自动接续核心 `speckit.converge`，不得直接交接 `speckit.acceptance`。
3. 按 converge 结果继续：
   - 报告 `Converged`：可先运行可选的 `/speckit.simulate-acceptance`，再运行 `/speckit.acceptance`。
   - 追加任务：回到 `speckit.implement` 完成新增任务；完成后仍然运行 `speckit.converge`，直到 `Converged`。
4. 仅当 converge 报告 `Converged` 且没有追加任务时，才允许进入正式验收；全体 Agent 可执行任务完成但仍有“需人工”项时，仍然运行 `speckit.converge`，人工项的最终确认留给 acceptance。
5. 正式 acceptance 生成验收报告时，再将 milestones.md 中该里程碑状态从 `in-progress` 更新为 `acceptance`。

## 约束

- 里程碑范围外的功能不得在本文实现（发现"顺手能做"的相邻功能 → 记入 milestones 变更候选，不在本分支做）
- converge 未报告 `Converged` 时不得进入正式验收
- 验收报告生成前不得并入 develop/main
