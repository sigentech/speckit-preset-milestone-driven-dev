---
description: 项目初始化收尾——向项目根 AGENTS.md 幂等注入"工作流领航提醒块"（inject 默认 / remove / status）。注入后 Agent 每次回复末尾自动提示当前环节与主线/可选操作。preset add 之后、constitution 之前执行一次。
handoffs:
  - label: 立项目宪法
    agent: speckit.constitution
    prompt: AGENTS.md 提醒块已注入，接下来制定项目宪法
    send: true
---

## 目的

preset 安装（`specify preset add`）只复制命令与模板，无法自动改写项目文件。本命令完成初始化的最后一步：把"工作流领航提醒块"注入项目根 `AGENTS.md`，使 Agent 在每次回复末尾主动提醒用户当前可执行的操作（主线必选 + 旁路可选）。

**流程定位**：`specify init → preset add → speckit.setup（本命令）→ constitution → milestones init`

## 用户输入与模式

~~~text
$ARGUMENTS
~~~

| 模式 | 用途 | 写文件？ |
| --- | --- | --- |
| `inject` 或无参 | 注入/更新提醒块（幂等） | 是（AGENTS.md 标记块） |
| `remove` | 移除提醒块 | 是 |
| `status` | 报告注入状态 | 否 |

## 模式：inject（默认）

1. 读取提醒块内容：用 `specify preset resolve agents-reminder-template` 定位（通常为 `.specify/presets/milestone-driven-dev/templates/agents-reminder-template.md`）
2. 定位目标文件：项目根 `AGENTS.md`（大小写不敏感匹配已存在的 `agents.md`/`Agents.md` 等变体；均无则新建 `AGENTS.md`）
3. 幂等注入：
   - 文件中已存在 `<!-- BEGIN speckit-preset:milestone-driven-dev` 与 `<!-- END speckit-preset:milestone-driven-dev -->` 标记 → 用模板内容整体替换两标记之间（含标记）的块（preset 升级后重跑本命令即完成提醒块升级）
   - 不存在标记 → 在文件末尾追加提醒块（与前文空一行）
   - 文件不存在 → 创建，内容为提醒块
4. 除标记块外，不得改动 AGENTS.md 的任何既有内容
5. 完成后输出 status 信息（见下）

## 模式：remove

1. 找到 BEGIN/END 标记块并整块删除；清理因此产生的连续空行
2. 若删除后文件仅剩空白 → 询问用户后删除该文件
3. 无标记块 → 提示未注入，不做改动

## 模式：status

报告：是否已注入；注入块版本（BEGIN 标记中的 vX.Y.Z）；目标文件路径；preset 当前版本与注入块版本是否一致（不一致则提示重跑 `/speckit.setup` 升级）。

## 约束

- 提醒块内容由模板单一维护，注入时不得改写其内容
- 本命令只触碰 AGENTS.md 的标记块，不修改其他任何文件
