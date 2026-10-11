---
description: （定制覆盖）创建功能规格——核心流程之上：强制关联里程碑、按 specs/NNN-mX-短名/ 建目录、创建并切换 feature/Mx 分支、回写里程碑状态。
handoffs:
  - label: 澄清规格
    agent: speckit.clarify
    prompt: 检测并消解这份规格的歧义
    send: true
---

## 与核心命令的关系

先按核心 `speckit.specify` 完整流程执行（从自然语言功能描述生成 spec.md）；本文件只定义**前置门禁、命名规则与附加步骤**。核心流程与本文件冲突处以本文件为准。

## 前置门禁

1. `.specify/memory/milestones.md` 必须存在——否则停止并提示：先运行 `speckit.milestones init`（里程碑是 specify 的前置规划层）。
2. 目标里程碑在 milestones.md 中状态为 `planned` 或 `specifying`；`done` 里程碑不得再开 spec（变更走 `speckit.milestones add`）。
3. **UI Demo 门禁**：UI 承载型里程碑（默认）须有 `specs/NNN-mX-短名/prototype/prototype.md` 且状态为"已冻结"；引擎型里程碑须为"已降级"。否则停止并提示先运行 `speckit.prototype`（gen/freeze 或 skip）。

## 定制步骤

1. **里程碑关联**：从 `$ARGUMENTS`（如 `M3 ……`）或 milestones.md status 建议中确定本 spec 属于哪个里程碑 Mx；一个里程碑只对应一个活跃 spec。若该里程碑已有 spec 目录，提示用户确认是修订旧 spec 还是里程碑范围已变（后者先走 milestones revise）。
2. **目录命名**：`specs/NNN-mX-短名/`——若 `speckit.prototype` 已创建该目录（含 prototype/），**复用之**（不重分配 NNN）；否则新建：NNN 全局递增（扫描 specs/ 取下一序号），X 为里程碑号，短名 2~4 词。示例：`specs/003-m2-retrieval-engine/`。
3. **分支准备**：
   - 若远程/本地尚无 `develop`：提示先按工作流文档完成 git 初始化（main/develop）
   - 若 `feature/Mx` 不存在：执行 `git checkout develop && git checkout -b feature/Mx`（执行前向用户说明，用户确认后执行）
   - 若 `feature/Mx` 已存在（恢复中断的里程碑）：`git checkout feature/Mx`，并同步一次 develop（`git merge develop` 或 rebase，冲突时停下请用户处理）
4. **执行核心 specify 流程**生成 spec.md，但 spec 内容必须满足里程碑约束：
   - 范围不得超出该里程碑"实现功能·包含"清单；超出部分列入"范围外（留待 M?）"
   - 验收标准须能支撑里程碑"用户验收指导"的逐条展开
   - 有冻结 Demo 时：spec 必须含"UI 契约"节，逐屏引用 SCR-nn（屏名、职责、关键交互、验收点），不得发明 Demo 没有的页面
5. **回写 milestones.md**：该里程碑状态 `planned → specifying`，登记 spec 目录路径。

## 报告

spec 路径、所属里程碑、当前分支、遗留 `[待澄清]` 项、下一步建议（clarify）。

## 约束

- 不得在没有里程碑关联的情况下创建 spec
- 分支操作全部先说明后执行；任何破坏性操作（强行切换、丢弃改动）禁止自动执行
