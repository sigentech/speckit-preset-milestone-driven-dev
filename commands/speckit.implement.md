---
description: （定制覆盖）编码实现——核心流程之上：执行前确认分析报告已清零、全程在 feature/Mx 分支、全部 Agent 可执行任务完成后自动接续 speckit.acceptance 生成《实现与验收报告》。
handoffs:
  - label: 生成实现与验收报告
    agent: speckit.acceptance
    prompt: 实现完成，生成实现与验收报告
    send: true
---

## 与核心命令的关系

先按核心 `speckit.implement` 完整流程执行（按 tasks.md 逐任务实现代码）；本文件定义**前置门禁与收尾动作**。

## 前置门禁

1. 当前分支为 `feature/Mx` 且与 spec 目录的里程碑号一致；不一致则停止并提示切换。
2. `.prepare/docs/specs-analysis-repo/[spec目录名]-analysis.md` 最新状态为"已清零"；否则停止并提示先走 `speckit.rectify` → `speckit.analyze`。
3. 工作区无未提交的非本里程碑改动（防串味；有则提示先提交或 stash）。

## 执行中的定制要求

- 提交粒度：按 tasks.md 阶段分批提交，提交信息格式 `feat(Mx): [任务摘要]`（docs 用 `docs(Mx):`，测试用 `test(Mx):`）
- 遇到 spec/plan 未覆盖的实现歧义：**停下**，按 speckit.rectify 的路由逻辑回补规格（clarify/plan/tasks），再继续——禁止在代码里静默发明规格
- 每完成一个任务勾选 tasks.md；标记为"需人工"的任务不强行实现，记入验收报告待人工验收项

## 收尾动作（核心流程执行完毕后）

1. 确认 tasks.md 中全部 **Agent 可执行**任务已完成
2. 自动接续 `speckit.acceptance`：生成 `specs/[NNN-mX-短名]/implementation-report.md`
3. 更新 milestones.md：该里程碑状态 `in-progress → acceptance`

## 约束

- 里程碑范围外的功能不得在本文实现（发现"顺手能做"的相邻功能 → 记入 milestones 变更候选，不在本分支做）
- 验收报告生成前不得并入 develop/main
