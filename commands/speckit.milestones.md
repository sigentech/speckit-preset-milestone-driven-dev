---
description: 里程碑规划——init（生成里程碑文件）、add（迭代新增）、revise（调整/重排）、status。位于 constitution 之后、首个 specify 之前；一个里程碑=一个功能模块=一个 specify；依赖 DAG 支持并行开发。
handoffs:
  - label: 开始首个里程碑规格
    agent: speckit.specify
    prompt: 按里程碑 M1 创建功能规格
    send: true
---

## 目的

生成并维护 `.specify/memory/milestones.md`——项目级里程碑规划文件。它回答"整个系统分几步交付、每步是什么、谁先谁后、谁可并行"，是所有 `speckit.specify` 的前置门禁。

**流程定位（最佳实践）**：`constitution（项目宪法）→ milestones（里程碑规划）→ 逐里程碑 specify→…→implement→release`。理由：宪法固定不可变的质量原则与技术约束；里程碑在这些约束下把功能愿景（产品功能规范/PRD 等输入文档）分解为有序交付单元；此后每个里程碑走完整的 spec-kit 循环。里程碑文件在**每次迭代边界**（里程碑验收后的回顾评审）修订，是 DevOps 迭代开发的"计划板"。

## 用户输入与模式

~~~text
$ARGUMENTS
~~~

| 模式 | 何时用 | 写文件？ |
| --- | --- | --- |
| `init` | constitution 完成后、首个 specify 之前 | 是（创建 milestones.md） |
| `add` | 迭代扩展：新增里程碑 | 是 |
| `revise` | 调整范围/重排顺序/升降档位 | 是 |
| `status` 或无参 | 随时 | 否（只读仪表盘） |

## 模式：init

1. **前置检查**：`.specify/memory/constitution.md` 存在（无则提示先运行 speckit.constitution）；milestones.md 不存在（已存在则中止并提示用 add/revise）。
2. **采集功能愿景**，来源解析按优先级：
   1. `$ARGUMENTS` 显式指定（如 `--vision <路径>`）
   2. `.specify/memory/prd.md`（若存在）
   3. `docs/explore/` 下 frontmatter 为 `status: pending-absorb` 的前期探索产出（`/speckit.grill`、`/speckit.brainstorm` 生成）——全部通读，作为愿景素材
   4. 以上皆无 → 询问用户；若项目尚无任何愿景文档，提示可先运行 `speckit.prd` 生成，或直接以访谈形式现场采集
   愿景来源为 PRD 与探索产出的组合时，两者都要读；探索产出中与 PRD 冲突的点，向用户确认以哪份为准。
3. **划分里程碑**，密度原则（逐条向用户呈现划分结果与理由）：
   - **一个里程碑实现一个功能模块**：边界按"用户可感知的功能闭环"划，不按技术层切
   - **独立可验收**：每个里程碑交付物能被用户单独验收（有明确的操作路径与预期结果）
   - **规模适中**：S ≤1 周 / M 1~3 周 Agent 工作量；L 必须说明为何不可拆
   - **先地基后上层**：项目骨架、数据模型、核心引擎优先；集成、打磨、资产线靠后
4. **标注依赖关系**：每个里程碑填 依赖/被依赖/可并行；**DAG 校验**（不得有环）；按依赖分层得出并行组（A/B/…）。
5. **逐里程碑填六项**：目标与价值、实现功能（含/不含）、技术栈增量、依赖关系、用户验收指导（3~7 条要点）、规模档位与风险。
6. **用户确认**后写入 `.specify/memory/milestones.md`（从 milestones-template 生成），版本 v1.0。**回写吸收状态**：把本步吸收过的 `docs/explore/` 文件 frontmatter 更新为 `status: absorbed`、`absorbed_by: .specify/memory/milestones.md（YYYY-MM-DD）`；刻意未吸收的保持 `pending-absorb` 并向用户说明原因。
7. **报告**：里程碑总表、并行分组、建议的首个里程碑；提示下一步 `speckit.specify`。

## 模式：add

迭代新增里程碑：编号顺延（M(n+1)），同样过密度原则与 DAG 校验；写变更日志（v+MINOR，注明"第 n 轮迭代扩展"）。

## 模式：revise

调整既有里程碑：合并/拆分/重排/改范围/改依赖。
- 已 done 的里程碑不得修改（只可 add 新里程碑承载变更）
- in-progress 里程碑缩范围时，把移出部分转为新里程碑或 deferred，并提示检查对应 spec 是否需同步修改
- 每次修订写变更日志（含原因）

## 模式：status

只读输出：

~~~text
| 编号 | 名称 | 依赖 | 并行组 | 状态 | spec | 下一步 |
当前可启动（依赖已满足）：[Mx, My]
进行中：[Mx — 环节: tasks]
阻塞项：[用户待确认清单]
~~~

## 约束

- 一个里程碑只对应一个活跃 spec；spec 目录命名 `specs/NNN-mX-短名/`
- 依赖环是硬错误，必须现场解开
- 里程碑文件的任何修改都必须写变更日志——它是迭代历史的一部分
