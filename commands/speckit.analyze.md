---
description: （定制覆盖）跨产物一致性分析——报告输出至 ./.prepare/docs/specs-analysis-repo/，每 spec 一份按轮次追加；问题分 Critical/High/Medium/Low 并附消除建议。
handoffs:
  - label: 消除问题
    agent: speckit.rectify
    prompt: 依据最新一轮分析报告消除问题
    send: true
---

## 与核心命令的关系

先按核心 `speckit.analyze` 完整流程执行跨产物只读分析（spec↔plan↔tasks 覆盖、宪法合规等）；本文件定义**报告的落盘格式、位置与严重级体系**。核心流程的分析发现原样保留，按下述结构重组输出。

## 定制输出规则

1. **报告位置**：`./.prepare/docs/specs-analysis-repo/[spec目录名]-analysis.md`（默认输出目录，目录不存在则创建；如需改配，在 constitution 中登记自定义路径并保持全项目一致）。**每个 spec 一份报告，按轮次依次追加，只增不删。**
2. **轮次编号**：扫描该 spec 报告已有"轮次 N"节，取 N+1；首次分析则创建文件（从 analysis-report-template 生成骨架）并写"轮次 1"。
3. **严重级体系**（替代/映射核心的 CRITICAL/WARNING）：

| 级别 | 定义 | 典型情形 | 处置要求 |
| --- | --- | --- | --- |
| Critical | 阻塞级：规格自相矛盾、违反宪法、不可实现 | spec 与 plan 冲突；宪法条款违反 | 立即消除，不消除不得 implement |
| High | 返工级：覆盖缺口、依赖错误、契约不清 | 需求无任务承接；验收标准不可测 | 立即消除 |
| Medium | 风险级：歧义、含糊、假设未声明 | 模糊词；隐式前提 | 立即消除 |
| Low | 打磨级：表述、格式、一致性瑕疵 | 术语不统一；编号断档 | 立即消除 |

4. **每条问题必须附"消除建议"**，格式：`路由（clarify/plan/tasks 之一）+ 具体做法`。路由规则：
   - 规格层问题（歧义、范围、验收标准）→ clarify
   - 结构/技术方案层问题 → plan
   - 任务层问题（缺口、顺序、依赖标注）→ tasks
   - 跨层问题路由到最上游产物
5. **里程碑维度**：除核心维度外，追加检查——spec 范围是否越出里程碑边界、spec 验收标准能否支撑里程碑用户验收指导、当前 spec 与已 done 里程碑的接口假设是否仍成立。
6. **Demo 一致性维度**（prototype 存在时）：spec "UI 契约"节引用的 SCR-nn 全部可在 prototype.md 屏清单解析（无悬空引用、无缺失屏）；plan 的"Demo 屏 → 真实组件映射表"覆盖全部 SCR-nn（缺失判 High）。
7. **更新文件头**：当前轮次、状态（存在未消除问题/已清零）、输入基线版本。

## 输出

- 对话内：分级汇总（各级数量）+ Critical/High 问题全文 + 报告路径
- 落盘：完整轮次记录（问题清单、维度小结、轮次结论）
- 若全部维度无问题：状态置"已清零"，提示可进入 `speckit.implement`

## 约束

- 分析本身**严格只读**（不改 spec/plan/tasks）；唯一的写操作是分析报告文件
- 轮次只增不删；历史轮次是迭代凭证
