# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

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
