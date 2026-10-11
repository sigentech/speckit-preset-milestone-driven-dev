---
description: （定制覆盖）技术计划——核心流程之上：prototype 存在的里程碑必须包含"Demo 屏 → 真实组件映射表"，禁止设计出 Demo 没有的交互。
handoffs:
  - label: 分解任务
    agent: speckit.tasks
    prompt: 技术计划已完成，分解实现任务
    send: true
---

## 与核心命令的关系

先按核心 `speckit.plan` 完整流程执行（技术选型、架构设计、数据模型、实施阶段）；本文件只追加**两节强制内容**。

## 追加内容一：Demo 屏 → 真实组件映射表（prototype 存在时必填）

在 plan.md 中增加一节，逐屏建立映射：

| 屏ID | 屏名 | 真实组件/路由 | 数据源（API/本地） | 交互逻辑归属 | 备注 |
| --- | --- | --- | --- | --- | --- |
| SCR-01 | | [组件路径/路由] | [端点或本地数据] | [前端状态/后端服务] | |

规则：
- **禁止设计出冻结 Demo 没有的交互**——确需新增的，先回 `speckit.prototype` 迭代 Demo 并走变更分级协议，再补进 plan
- Demo 中的 mock 数据逐一标注真实数据源；标注"暂无来源"的必须在 tasks 中有对应任务
- 冻结 Demo 后发生过"交互变更"的屏，映射表以变更记录中的最新版为准

## 追加内容二：无 Demo 里程碑的 UI 契约说明（prototype 已降级时必填）

若本里程碑经 `speckit.prototype skip` 降级：plan.md 须说明 UI 契约来源（如"沿用 M1 壳层导航，仅新增设置页两个配置项，配置项清单见下"），不允许 UI 要求悬空。

## 约束

- 映射表缺失或屏覆盖不全（SCR-nn 无映射）时，`speckit.analyze` 将判 High 级问题
