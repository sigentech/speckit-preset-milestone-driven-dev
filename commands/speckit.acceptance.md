---
description: 生成《实现与验收报告》implementation-report.md——实现概述、自动化验证结果、关键技术决策、待人工验收项清单及逐项操作指南、产物速查；随 docs 提交并推送远程。
handoffs:
  - label: 发布里程碑
    agent: speckit.release
    prompt: 人工验收全部通过，发布本里程碑
---

## 目的

在 spec 的编码实现完成后（tasks.md 中 Agent 可执行任务全部执行完毕），于该 spec 目录下生成《实现与验收报告》（`implementation-report.md`）。它是用户人工验收的操作手册，也是里程碑能否 release 的判定依据。

## 用户输入

~~~text
$ARGUMENTS
~~~

可指定 spec 目录；缺省取当前 feature/Mx 分支对应的活跃 spec。

## 执行步骤

1. **前置检查**：tasks.md 全部 Agent 可执行任务已勾选；当前分支 feature/Mx。未满足则停止。
2. **采集实现事实**：
   - 读 spec.md（需求点/验收标准）、plan.md（技术决策）、tasks.md（已完成任务与"需人工"任务）
   - `git log develop..HEAD --oneline` 汇总本轮提交
3. **运行自动化验证**：按 plan.md 技术上下文中的验证命令逐项执行（单测/集成测试/构建/lint/type；缺失的命令标注"未配置"），结果填入报告 §二（命令/结果/输出摘要）。任一失败 → 停止，先修复（代码问题直接修，规格问题走 rectify）再重新生成。
4. **生成待人工验收项清单**（§四）：
   - 来源：spec 验收标准 + 里程碑"用户验收指导" + tasks 中标记"需人工"的任务
   - 逐项给出：**操作步骤**（具体到点击/命令/输入数据）、**预期结果**（可观察的确切现象）、**结果记录位置**（表内"验收结果"列）
   - 每项可独立执行、无需读代码
5. **填产物位置速查**（§六）：spec/plan/tasks/分析报告/源码入口/测试/文档的实际路径。
6. **写入报告**：`specs/[NNN-mX-短名]/implementation-report.md`（从 implementation-report-template 生成）。
7. **提交并推送**（向用户说明后执行）：
   ~~~bash
   git add -A
   git commit -m "docs: Mx 实现与验收报告"
   git push origin feature/Mx
   ~~~
8. **报告**：报告路径、自动化验证汇总、待人工验收项数量，提示用户逐项验收（结果填在报告 §四表内）；全部通过后运行 `speckit.release`。

## 约束

- 报告中的验收项必须"可操作、可预期、可记录"三要素齐全；抽象表述（"功能正常"）一律改写为可观察判据
- 自动化验证失败时不得生成"待验收"假象——先修复再出报告
- 报告随 docs 提交入库并推送远程是铁律（spec 目录与文档一并入库）
