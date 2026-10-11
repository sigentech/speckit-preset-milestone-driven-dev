---
description: 【可选命令，默认不启用】生成产品需求文档（PRD）——仅当功能愿景来源缺失时启用（无任何既有规范/愿景文档的全新项目），产出作为 speckit.milestones init 的直接输入。
handoffs:
  - label: 规划里程碑
    agent: speckit.milestones
    prompt: 以这份 PRD 为功能愿景来源，规划项目里程碑
    send: true
---

## 启用判据（先判后做）

判定规则：

1. 检测功能愿景来源是否已存在（既有规范文档、既有 PRD、或用户明确指定的愿景文件）：
   - 存在 → **停止**，提示："检测到功能愿景来源已存在，PRD 无必要——它会与既有文档形成双真相源。请直接运行 speckit.milestones init 并以该文档为愿景输入。"
   - 不存在（全新项目）→ 继续以下流程
2. PRD 是一次性产物，生成后不再维护——后续需求演进走 milestones add/revise，不回头改 PRD（防双真相源）。

## 目的（启用时）

把用户的初步设想转化为一份产品级需求文档 `.specify/memory/prd.md`，回答"为什么做、为谁做、做什么、不做什么、怎么算成"，作为 `speckit.milestones init` 的功能愿景输入。

## 用户输入与模式

~~~text
$ARGUMENTS
~~~

| 模式 | 用途 |
| --- | --- |
| `gen` | 访谈式生成 PRD 首稿 |
| `update` | 里程碑规划前的有限修订（规划启动后冻结） |

## 模式：gen

1. 按 prd-template 逐节访谈填充（每次最多 5 个问题，先问价值与边界，再问功能与度量）：
   - 背景与目标：解决谁的什么问题；为什么现在做
   - 用户画像与用户旅程：1~3 个核心画像，各一条主旅程
   - 功能需求：MoSCoW 分级（Must/Should/Could/Won't）——Won't 必填，边界比功能更重要
   - 成功度量：可量化的"成了"判据
   - 范围外与约束：明确排除项；技术/合规/资源约束
2. 一致性自检：Must 项与成功度量可互相支撑；用户旅程每步有功能承接
3. 用户确认后写入 `.specify/memory/prd.md`（与 constitution、milestones 同级）

## 约束

- PRD 只描述 what/why，禁止技术选型（栈归 constitution 与 plan）
- PRD 生成后如遇愿景变化：先改 PRD（update 模式）再 milestones——但里程碑规划一旦启动，PRD 冻结，变更走 milestones
