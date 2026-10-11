---
description: Bug 修复路径——里程碑内（fix/Mx-短名）与跨里程碑（fix/cross-短名）双路径：影响面评估、回归测试、向 develop/main 及全部活跃 feature 分支传播，修复记录留痕。
---

## 目的

给 bug 一条正规通道：不管在哪个里程碑发现、影响多少个里程碑，都按同一条路径修复、验证、传播、留痕——杜绝"随手在哪个分支上改一把"。

## 用户输入

~~~text
$ARGUMENTS
~~~

格式：`[bug 描述]`；可附 `M3`、`cross` 等范围线索。

## 第一步：影响面评估（必做）

1. 定位 bug 所在代码归属的里程碑（引入它的 feature/Mx）
2. 判定路径：

| 情形 | 路径 | 分支 |
| --- | --- | --- |
| 里程碑开发中（feature/Mx 未合流）发现的 bug | **里程碑内** | 直接在 feature/Mx 上修 |
| 已合流的单个里程碑范围内的 bug | **里程碑内（已发布）** | `fix/Mx-短名`，从 develop 切出 |
| 影响 ≥2 个里程碑、或位于共享层（数据模型/公共组件/配置）的 bug | **跨里程碑** | `fix/cross-短名`，从 develop 切出 |
| main 上影响使用的紧急 bug | **热修** | `hotfix/短名`，从 main 切出 |

3. 登记：跨里程碑 bug 必须先列出受影响里程碑清单与各自的表现，再动手。

## 第二步：修复

1. **先写回归测试**：能复现 bug 的测试先失败，修复后通过；无法自动测试的，在提交信息中说明人工验证步骤
2. 最小改动修复；修复中发现规格本身有错 → 按 speckit.rectify 路由回补对应 spec 的 spec/plan/tasks，并在对应分析报告"消除过程附注"记录
3. 提交信息：`fix(Mx): [摘要]` 或 `fix(cross): [摘要]`，正文写 bug 现象、根因、影响面

## 第三步：验证与传播

1. 修复分支上跑相关测试 + 受影响里程碑的验收关键项（implementation-report §四中的相关条目）
2. **合流**：
   - 里程碑内（已发布）：`fix/Mx-短名` → develop 与 main（--no-ff）
   - 跨里程碑：→ develop 与 main；**随后逐一合并到全部活跃 feature 分支**（feature/My…），每个分支合并后跑其冒烟验证
   - 热修：→ main 打修订 tag（v0.Mx.n+1），再合回 develop 与全部活跃 feature
3. 推送远程。

## 第四步：留痕

- 受影响里程碑的 implementation-report.md §三追加一行"发布后发现的问题与处理"
- 跨里程碑 bug 在 milestones.md 变更日志记一行（含根因分类：规格缺陷/实现缺陷/集成缺陷——回顾评审用）
- 若 bug 暴露出验收盲区：把对应验收项补进该里程碑 implementation-report.md §四（标注"后补"）

## 约束

- 跨里程碑修复未传播到全部活跃 feature 分支前，不得开始新的 milestone specify（防在旧代码上盖新楼）
- 禁止直接在 main/develop 上改 bug（紧急热修也走 hotfix 分支）
