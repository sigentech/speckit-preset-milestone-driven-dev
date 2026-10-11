---
description: UI Demo 先行——gen（按里程碑生成轻量 HTML Demo）、freeze（用户确认冻结）、skip（引擎型里程碑降级）、status。位于 milestones 之后、specify 之前；Demo 冻结是 specify 的前置门禁。
handoffs:
  - label: 编写功能规格
    agent: speckit.specify
    prompt: Demo 已冻结，以它为首要证据编写功能规格
    send: true
---

## 目的

把"先 Demo 后编码"制度化：每个 UI 承载型里程碑在写规格之前，先生成一个可点击的轻量 HTML Demo，用户逐屏迭代细化、确认冻结后，specify 以它为首要证据编写 spec。视觉原型是最高效的消歧工具——文字规格里藏得住的歧义，界面上藏不住。

**流程定位**：`milestones → prototype（本命令）→ specify → clarify → …`

## 用户输入与模式

~~~text
$ARGUMENTS
~~~

| 模式 | 用途 | 写文件？ |
| --- | --- | --- |
| `gen Mx [短名]` | 生成首版 Demo | 是（specs/NNN-mX-短名/prototype/） |
| 迭代（对话中进行） | 用户逐屏反馈，就地修订 Demo 并记录 | 是 |
| `freeze` | 用户确认后冻结 | 是（prototype.md 冻结记录） |
| `skip Mx [理由]` | 引擎型里程碑降级跳过 | 是（降级说明） |
| `status` 或无参 | Demo 状态速览 | 否 |

## 模式：gen

1. **前置检查**：milestones.md 存在；目标里程碑状态 planned/specifying。
2. **分支准备**：若 `feature/Mx` 不存在，按 speckit.specify 同款规则从 develop 切出（先说明后执行）。
3. **目录分配**：扫描 specs/ 取下一 NNN，创建 `specs/NNN-mX-短名/prototype/`（注意：此时 spec.md 尚不存在，speckit.specify 将复用本目录）。
4. **读取 UX 基线**（解析顺序）：
   - ① `.specify/memory/milestones.md` §一 的 `ux_baseline` 字段登记的路径
   - ② 默认 `docs/ux-baseline/`（设计文档或基线 Demo）
   - 若均不存在：新项目提示先用 `ux-baseline-template` 建立基线（一次性，全项目共用）；用户选择跳过的，在 prototype.md 记"无基线，自立样式（理由）"
   - 基线确定后：导航结构、配色、组件样式、交互范式必须继承，禁止另起炉灶
5. **生成屏清单**：从该里程碑的"实现功能（含）+ 用户旅程"拆解出屏列表（SCR-01…SCR-nn），写入 `prototype/prototype.md`（从 prototype-template 生成）。
6. **生成 Demo**：轻量 HTML/CSS/JS（hash 路由单页或多页均可）、mock 数据、不绑定真实前端栈。迭代速度优先——改布局应是秒级成本。
7. **报告**：Demo 入口文件路径、屏清单，请用户在浏览器逐屏评审。

## 迭代（gen 之后、freeze 之前）

- 用户逐屏反馈 → 就地修改 HTML → 每轮在 prototype.md"迭代记录"追加一行（日期/反馈/改动）
- 反馈超出里程碑"实现功能"范围时：不加进 Demo，记入 milestones 变更候选（add 新里程碑的素材），并向用户说明

## 模式：freeze

1. 屏清单全部屏状态为"已确认"；遗留待办清零
2. 写冻结记录（版本/日期/确认人）；里程碑状态 → `specifying`
3. 提示下一步 `speckit.specify`——spec 的 UI 契约节将逐屏引用 SCR-nn

## 模式：skip

引擎型里程碑（UI 占比极低）可降级：记录理由（为什么不需要 Demo、UI 契约从何而来，如"沿用 M1 壳层，仅新增配置项"）。降级后 specify 不再要求 Demo 门禁。

## 开发期 UI 变更协议（speckit.implement 期间适用）

| 变更级别 | 例子 | 路径 |
| --- | --- | --- |
| 视觉微调 | 间距、配色、文案 | 实现者直接改，implementation-report §三记一笔 |
| 交互变更 | 流程、状态、导航变化 | **先改 Demo**（本命令迭代模式）→ clarify 回写 spec UI 契约 → plan 受影响则修 → tasks → implement。先改代码视为违例 |
| 范围变更 | 新增页面/功能 | 走 milestones 裁决（add 新里程碑或 revise 当前范围） |

## 约束

- Demo 必须继承 UX 基线；偏离基线的样式必须记录理由
- 未冻结（或未降级）的里程碑不得进入 specify
- Demo 与实现同步的终点在 release：真实界面截图回灌后，Demo 标"已被实现取代"归档（speckit.release 内建）
