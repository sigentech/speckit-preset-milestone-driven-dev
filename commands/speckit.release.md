---
description: 里程碑发布——验收全过后，feature/Mx 并入 develop 与 main、打 tag、推送远程、回写里程碑状态，并列出新解锁的可并行里程碑。
handoffs:
  - label: 规划下一迭代
    agent: speckit.milestones
    prompt: 回顾评审本里程碑，规划下一迭代
---

## 目的

把"验收通过的里程碑"安全地合流：feature/Mx → develop → main，留下可回滚的发布点（tag），并把项目状态推进到下一迭代。对应 DevOps 循环中"可工作的软件 → 发布"的一步。

## 用户输入

~~~text
$ARGUMENTS
~~~

可指定里程碑号；缺省取当前 feature/Mx 分支。

## 前置门禁（全部满足方可发布）

1. `implementation-report.md` §四全部验收项标记"通过"（有不通过/待验收项 → 停止）
2. 报告已提交入库且 feature/Mx 已推送远程（`git status` 干净）
3. 最新分析报告状态"已清零"

## 执行步骤（每步先说明后执行）

1. **同步确认**：`git fetch origin`；若 develop 在本里程碑开发期间有新合并，先把 develop 合入 feature/Mx 并跑一次冒烟验证（构建+主测试），冲突停下请用户处理
2. **并入 develop**：
   ~~~bash
   git checkout develop && git pull origin develop
   git merge --no-ff feature/Mx -m "merge: Mx [里程碑名] 并入 develop"
   ~~~
3. **并入 main**：
   ~~~bash
   git checkout main && git pull origin main
   git merge --no-ff develop -m "release: Mx [里程碑名]"
   git tag -a "v0.Mx.0" -m "里程碑 Mx 发布"   # 版本号规则：v0.[里程碑号].[该里程碑内修订序号]
   ~~~
4. **推送远程**：
   ~~~bash
   git push origin develop main --tags
   ~~~
5. **回写状态**：milestones.md 该里程碑状态 → `done`，填完成日期；变更日志记一行
6. **Demo 归档**：prototype 存在的里程碑——将真实实现的关键界面截图回灌 `prototype/screenshots/`，prototype.md 状态置"已归档（已被实现取代）"，填归档记录。此后 UI 的真相源是真实实现，Demo 仅作历史凭证；后续 UI 调整走 speckit.hotfix 或新里程碑。
7. **清理建议**：提示用户可删除已合流的 feature/Mx（本地与远程）；若该里程碑后续可能有 bug，保留分支亦可，规则见 speckit.hotfix
8. **报告**：
   - 发布结果（合并提交、tag、推送状态）
   - **新解锁里程碑**：依赖本里程碑且其余依赖均已 done 的里程碑清单（可立即 `speckit.specify`）
   - 建议下一步：回顾评审（DevOps 迭代循环）→ `speckit.milestones status` / `add` / `revise`

## 约束

- 全部合并用 `--no-ff` 保留里程碑边界；禁止 force-push 到 main/develop
- 冒烟验证失败不得并入 main；develop 上修复（或走 hotfix）后再发
- 发布是单向动作：tag 打后不移动；出问题走 hotfix，不回滚 tag
