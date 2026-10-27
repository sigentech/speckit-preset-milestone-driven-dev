<!-- BEGIN speckit-preset:milestone-driven-dev v1.4.0 -->
## 工作流领航提醒（milestone-driven-dev preset）

本项目使用 milestone-driven-dev speckit-preset 管理开发流程。**每次完成用户请求、输出最终回复前**，在回复末尾附上"下一步"提醒（与本项目开发无关的纯闲聊可省略）：

1. 用下方状态表判定当前环节（自上而下，取首个命中的行；"当前 spec" = `specs/` 下最新且对应里程碑未 done 的目录）。
2. 输出三部分，总计不超过 8 行：
   - **当前环节**：一句话
   - **主线下一步**：1~2 条，给出确切命令
   - **可选项**：0~4 条旁路操作（无则省略此行）
3. 只提醒，不擅自执行。用户表示"别再提醒"时当次跳过，并告知可用 `/speckit.setup remove` 永久关闭本提醒。

### 状态检测表

| 证据（文件系统） | 当前环节 | 主线下一步 | 可选项 |
| --- | --- | --- | --- |
| 无 `.specify/memory/constitution.md` | 未立项目宪法 | `/speckit.constitution` | — |
| 无 `.specify/memory/milestones.md` | 未规划里程碑 | `/speckit.milestones init` | `/speckit.prd`（愿景缺失的全新项目） |
| 无当前 spec（无 `specs/` 或里程碑全 done） | 待启动下一里程碑 | 从 develop 开 `feature/Mx` → `/speckit.prototype gen Mx` | `/speckit.milestones status` / `add` / `revise` |
| 当前 spec 的 prototype.md 未冻结且未 skip | UI Demo 未冻结 | 迭代 Demo → `/speckit.prototype freeze` | `/speckit.prototype status`；引擎型可 `skip` |
| 当前 spec 无 `spec.md` | 待建功能规格 | `/speckit.specify` | — |
| 有 spec.md、无 `plan.md` | 待技术计划 | `/speckit.plan` | `/speckit.clarify`（规格有歧义先消歧） |
| 有 plan.md、无 `tasks.md` | 待任务分解 | `/speckit.tasks` | `/speckit.analyze` |
| 最新一轮分析报告存在未清零问题 | 待消除问题 | `/speckit.rectify` | `/speckit.analyze`（消除后重跑） |
| 报告已清零、实现未完成 | 待编码实现 | `/speckit.implement` | `/speckit.analyze` |
| 实现完成、无 `implementation-report.md` | 待生成验收报告 | `/speckit.acceptance` | — |
| 验收清单未全部"通过" | 待人工逐项验收 | 按报告中的操作指南逐项验收并记录 | — |
| 验收全过、里程碑未置 done | 待发布合流 | `/speckit.release` | — |

任意状态下，若用户报告 bug，"可选项"追加 `/speckit.hotfix`。
任意状态下，若用户想深挖某个决定或做头脑风暴，"可选项"追加 `/speckit.grill`（拷问式深挖）/ `/speckit.brainstorm`（对话式头脑风暴）；二者为旁路技能，结论沉淀到当前环节产物，不改变主线状态。
<!-- END speckit-preset:milestone-driven-dev -->
