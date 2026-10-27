# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [1.4.0] - 2026-10-27

### Added
- 新命令 `speckit.grill`：移植 grill-me / grilling 技能——设计树 + 逐轮前沿提问的拷问式深挖，可在流程任何环节调用；查事实由 Agent（或子代理）完成，决策留给用户；达成共识后按"环节落点表"沉淀到当前环节正式产物，不另起游离文件
- 新命令 `speckit.brainstorm`：移植 brainstorming 技能——先对话搞清楚要什么/为什么 → 摆出做法 → 设计文档（完整版含子代理建造者检查）→ 用户批准（HARD-GATE）→ 路由回当前环节主线命令；设计文档落点随环节（当前 spec 内 `design/` 或项目级 `docs/design/`）
- 新模板 `brainstorm-builder-check-prompt`、`brainstorm-visual-companion`：头脑风暴的建造者盲审提示词与浏览器可视化伴侣指南；可视化伴侣全套运行脚本（server.cjs/helper.js/frame-template.html/start-server.sh/stop-server.sh）随 preset 一并安装于 `templates/brainstorming/scripts/`
- AGENTS.md 领航提醒块升级至 v1.4.0：任意状态下"可选项"追加 `/speckit.grill` / `/speckit.brainstorm` 提示（已注入的项目重跑 `/speckit.setup` 即可升级）

## [1.3.1] - 2026-10-13

### Documentation
- README 双语化：`README.md` 改为英文（默认），中文内容移至 `README.zh-CN.md`，两版互链（English | 简体中文）
- 两版 README 增加徽章行（版本/spec-kit 要求/许可证）与一句话标语

## [1.3.0] - 2026-10-12

### Added
- 新命令 `speckit.setup`：向项目根 `AGENTS.md` 幂等注入"工作流领航提醒块"（inject/remove/status 三模式，BEGIN/END 标记包裹支持升级替换）；注入后 Agent 每次回复末尾自动提示当前环节与主线必选/旁路可选操作
- 新模板 `agents-reminder-template`：提醒块内容（13 态状态检测表 + 输出格式约束），单一维护源
- README 快速开始新增 `/speckit.setup` 步骤，流程图 INIT 子图同步

### Fixed
- **修复自 v1.0 起的潜在缺陷**：preset.yml 中命令原置于 `provides.commands` 独立键下，而 spec-kit CLI 仅识别 `provides.templates` 内的条目（type: command），导致全部命令从未注册到 Agent（安装不报错、静默忽略）。已将 12 个命令并入 `provides.templates` 列表，经 CLI v0.14.4 沙箱验证：8 个新命令注册为新技能、4 个覆盖命令正确接管

## [1.2.0] - 2026-10-11

### Changed
- 改写为独立自洽的 speckit-preset 项目：解除与源项目（Research-reports-writing-guru）的耦合，可在任意新项目中初始化使用
- UX 基线改为可配置（milestones §一 `ux_baseline` 路径），新增 `ux-baseline-template` 供新项目建立设计基线
- 功能愿景来源改为显式输入（`--vision` 或询问），不再默认指向特定项目的规范文档
- 分析报告输出目录保留默认 `./.prepare/docs/specs-analysis-repo/`，文档注明可在 constitution 中改配
- README 全面重写为 preset 使用文档（含安装命令与快速开始）

### Added
- LICENSE（MIT）、CHANGELOG.md

## [1.1.0] - 2026-10-11

### Added
- speckit.prototype（UI Demo 先行：gen/freeze/skip，UX 基线继承、变更分级协议、归档同步）
- speckit.prd（可选命令，愿景缺失的新项目才启用）
- speckit.plan 轻量覆盖（Demo 屏 → 真实组件映射表）
- milestones 模板新增优先级（MoSCoW）与用户旅程字段

## [1.0.0] - 2026-10-11

### Added
- 初版：里程碑驱动开发工作流（milestones/specify/analyze/rectify/implement/acceptance/release/hotfix 八命令 + 三模板）
