---
description: 在 converge 报告 Converged 后生成《实现与验收报告》implementation-report.md；校验来源键与判据指纹后消费当前有效模拟，缺失或过期时退回全人工验收，可见 AI_FAIL 即使 baseline 过期也阻止验收。
handoffs:
  - label: 发布里程碑
    agent: speckit.release
    prompt: 人工验收全部通过，发布本里程碑
---

## 目的

在 spec 的编码实现完成且核心 `speckit.converge` 报告 `Converged` 后，于该 spec 目录下生成正式《实现与验收报告》（`implementation-report.md`）。它是用户人工验收的操作手册，也是里程碑能否 release 的判定依据。

可选的 `speckit.simulate-acceptance` 可以预填有当前证据的 `AI_PASS` 项并复制人工指南；正式验收必须重新校验模拟 `baseline`，不能把模拟当成最终验收。

必须遵守命令顺序：`/speckit.implement` → `/speckit.converge` → 可选 `/speckit.simulate-acceptance` → `/speckit.acceptance`。

可见的 `AI_FAIL` 是独立失败信号：即使模拟 `baseline` 已过期、格式不完整或不能导入任何 `AI_PASS`，它仍阻止正式验收。

## 用户输入

~~~text
$ARGUMENTS
~~~

可指定 spec 目录；缺省取当前 feature/Mx 分支对应的活跃 spec。

## 执行步骤

1. **正式验收前置检查（必须按此顺序）**
   - 确认 `tasks.md` 中全部 Agent 可执行任务已勾选；标记“需人工”的任务保留为正式验收中的待验项。当前分支必须为 `feature/Mx`。
   - 确认当前会话最近一次 `speckit.converge` 明确报告 `Converged`。无法确认时停止，不得生成验收报告，要求先运行 `/speckit.converge`；若 converge 追加了任务，停止并回到 `speckit.implement`，完成后再 converge。
   - 先扫描 `AI_FAIL`，包括 `acceptance-simulation.md` 的总表与明细。只要存在任何可见 `AI_FAIL`，即使 baseline 已过期，也立即停止且不得生成正式验收报告；按记录根因路由到 `speckit.clarify`、`speckit.plan`、`speckit.tasks` 或 `speckit.implement`。
   - 按唯一规则解析分析报告目录：读取 `.specify/memory/constitution.md`；若存在唯一一行 `analysis_report_dir: <path>`，使用该目录，否则使用 `./.auxiliary/docs/specs-analysis-repo/`。报告文件名固定为 `[spec-dir]-analysis.md`。重复、空或不可解析的路径登记必须停止。
   - 从当前 `spec.md`、`.specify/memory/milestones.md` 和 `tasks.md` 独立重算期望来源键，并逐个提取当前来源条目的完整验收判据正文。去除列表标记、checkbox、稳定来源键及其后的分隔冒号后，判据正文必须唯一解析为一段非空文本。
   - 每个来源条目按下述算法计算当前判据指纹；模拟每个来源行必须同时记录相同来源键、`判据指纹: sha256:<hex>`，且其“验收判据”经同一算法得到的文本必须与当前来源判据一致。来源键与判据指纹必须精确匹配，不能只校验来源键。
   - 判据指纹固定算法：先做 Unicode NFC 规范化；行尾统一为 LF；去掉首尾空白；把内部连续空白折叠为一个空格；再以 UTF-8 编码该规范文本并计算 SHA-256，输出 64 位小写十六进制，写作 `sha256:<hex>`。
   - 判据文本缺失、被替换或无法解析（包括同键解析出多段），或任一指纹不匹配时，整个模拟失效；不得导入其中任何 `AI_PASS`，只能退回全人工验收。该失败不是 `AI_FAIL`，但仍不得复用旧证据。
   - 在运行任何正式验证命令前建立**验证前快照**：记录 `git rev-parse HEAD` 的输出、`git status --porcelain=v1 --untracked-files=all` 的原样输出，以及 `spec.md`、`plan.md`、`tasks.md` 各自的 SHA-256 摘要指纹。快照缺失或不完整时停止。

2. **校验可选验收模拟**
   - 无可见 `AI_FAIL` 时运行 `git status --porcelain=v1 --untracked-files=all`。除目标 `acceptance-simulation.md` 外，只要存在任一已跟踪或未跟踪变更，baseline 即视为**过期**，不得导入任何 AI 结果。
   - 模拟总表的来源键必须与当前期望集合恰好一次一一对应；存在缺失、额外或重复来源键、无法识别的来源键或重复验收编号，均不得导入 AI 结果。模拟自报的覆盖结果不能代替本次重算。
   - 记录的工作区清洁基线必须为 `PASS`，且当前分支、commit、`spec.md`/`plan.md`/`tasks.md` SHA-256 摘要指纹和 converge 结果均匹配；状态数量与逐项状态一致；结论与逐项状态一致；每个 `HUMAN_REQUIRED`/`BLOCKED` 有完整人工指南。
   - 每个 `AI_PASS` 必须有实际执行的完整命令、关键输出和证据路径，并且退出码必须为 0。若声明“预期非零成功契约”，必须同时记录契约来源、精确预期退出码、为何非零代表成功和可复核输出证明；缺少任一项都不得作为 `AI_PASS` 导入。
   - 模拟报告的 commit 或任一摘要指纹变化、分支不符、converge 结果不是 `Converged`，均视为**过期**。缺失、格式不可解析、工作区不干净、来源或判据认证失败、状态或结论不一致、成功证据/人工指南不完整、baseline 无效时，同样不得导入 AI 结果。
   - 当前有效且不存在 `AI_FAIL`：可导入 `AI_PASS` 与 `HUMAN_REQUIRED`/`BLOCKED` 人工项。
   - 缺失、过期或无效：退回**全人工验收**，将当前期望验收集全部展开为待人工项；提示用户可先运行 `/speckit.simulate-acceptance`，但不得等待它而阻塞现有流程。

3. **采集实现事实**
   - 读 `spec.md`（需求点/验收标准）、`plan.md`（技术决策/验证命令）、`tasks.md`（已完成任务与“需人工”任务）。
   - 读取 `.specify/memory/milestones.md` 中本里程碑的用户验收指导。
   - 运行 `git log develop..HEAD --oneline` 汇总本轮提交，并记录当前 commit。
   - 记录本次 converge 已收敛的证据/会话摘要与分析报告轮次。

4. **运行或引用自动化验证**
   - 按 `plan.md` 技术上下文中的验证命令逐项执行（单测/集成测试/构建/lint/type；缺失的命令标注“未配置”）。
   - 当前有效模拟中的 `AI_PASS` 可引用其命令、退出码、输出摘要和证据路径，但不得仅凭代码检查预填通过；必要时重跑关键命令并更新证据。
   - 任一正式验收阶段的自动化检查失败：不得生成“待验收”假象，停止并按根因修复后重新 converge；若有效模拟本应捕获该失败，将模拟标为过期并重跑。

5. **验证后复检**
   - 正式验证执行完毕后、写入任何正式报告或更新里程碑之前，重新读取并逐项比较验证前快照：`git rev-parse HEAD`、`git status --porcelain=v1 --untracked-files=all`，以及 `spec.md`、`plan.md`、`tasks.md` 的 SHA-256 摘要指纹。
   - 上述任一项不同，即证明验证过程改变了仓库状态或验收意图。此时模拟失效，立即停止正式报告生成，不得写入 `implementation-report.md`，不得更新里程碑状态，并要求重新 converge 后再验收。
   - 只有 HEAD、工作区状态和三项产物指纹全部与验证前快照一致，才可继续。

6. **生成正式验收项**
   - 每项至少包含：编号、来源键、判据指纹、来源、验收判据、验收状态、证据、人工指南、验收结果。
   - 当前有效模拟中的 `AI_PASS`：正式验收结果预填“通过”，保留模拟证据路径/摘要，并标记来源为“`AI_PASS` 导入”。
   - 当前有效模拟中的 `HUMAN_REQUIRED`/`BLOCKED`：正式验收结果保持“待验收”，复制对应独立人工指南。
   - 正式报告不得包含 `AI_FAIL` 项，也不得将 `HUMAN_REQUIRED`/`BLOCKED` 改写为通过。
   - 每个待人工项必须给出：**前置条件与环境、操作步骤、预期结果、判定标准、记录位置**，并补充测试数据/输入、为什么 Agent 不能可靠完成；每项可独立执行、无需读代码。

7. **填产物位置速查**
   - spec/plan/tasks/分析报告/converge 证据/验收模拟/源码入口/测试/文档使用实际路径。
   - 分析报告路径填写第 1 步按 `analysis_report_dir: <path>` 规则解析出的 `<analysis-report-dir>/[spec-dir]-analysis.md`。

8. **写入报告**
   - 从 `templates/implementation-report-template.md` 生成 `specs/[NNN-mX-短名]/implementation-report.md`。
   - 记录验证前快照、验证后复检结果、验收模拟来源、模拟 `baseline`、baseline 是否当前有效、导入的证据与全人工回退原因。
   - 将 `.specify/memory/milestones.md` 中本里程碑状态从 `in-progress` 更新为 `acceptance`。

9. **提交并推送（向用户说明后执行）**
   ~~~bash
   git add -A
   git commit -m "docs: Mx 实现与验收报告"
   git push origin feature/Mx
   ~~~

10. **报告**
   - 报告路径、自动化验证汇总、`AI_PASS`/人工项数量、模拟来源及是否回退全人工验收。
   - 提示用户逐项验收（结果填在报告 §四表内）；全部通过后运行 `speckit.release`。

## 约束

- 报告中的验收项必须“可操作、可预期、可记录”三要素齐全；抽象表述（“功能正常”）一律改写为可观察判据。
- converge 未确认 `Converged` 时不得验收。
- 当前有效模拟存在 `AI_FAIL` 时不得生成正式验收报告。
- 缺失、无效或过期模拟只能触发全人工验收，不得猜测或复用旧证据。
- 正式验收报告中的自动化证据必须来自实际执行，不得伪造命令输出、截图、外部系统状态或真人体验结论。
