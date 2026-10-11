# Changelog

所有项目的重要更改都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
此项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [2.1.0] - 2026-10-11

### Added - 核心新增
- 🚀 **全面适配 EU5 1.3.x (Pavia) 与 1.4.0 Open Beta**：基于 `eu5-modding-kb` 1.4open_beta 分支与游戏本地安装文件完成数据重构。
- 📚 **整合 103 篇类目字段规范 (`field_definitions.json`)**：收录官方 readme 与本体全量实查字段（含 1.4 新增 `common/expedition_types`、`common/estates`）。
- 🛠️ **整合 24 篇原版机制深度拆解 (`vanilla_mechanics.json`)**：解析文件组成、数值位置、挂钩点与引擎硬编码边界（含 1.4 新增 `vanilla-army-movement.md` 军队移动机制）。
- ⚠️ **整合 18 个实测避坑专题 (`modding_pitfalls.json`)**：系统收录 EU4 vs EU5 语法对照、作用域失效、变量守卫规则、BOM 规范及 1.4 废弃接口。
- 📖 **标准中英双语术语表 (`glossary.json`)**：收录 167 条已对齐官方汉化的权威术语。
- 🔄 **支持 on_actions 挂钩点 (`on_actions.json`)**：新增 159 条官方 on_actions 检索及执行作用域验证。
- 🌐 **支持自定义本地化 (`custom_localization.json`)**：新增 413 条动态文本函数及候选条目检索。
- 🔍 **脚本离线静态诊断校验器 (`validate_mod_snippet`)**：自动排查大写 `ROOT`、废弃 `event_target`、`:0` 本地化后缀、顺序敏感块合并误用等典型语法 Bug。
- 📦 **1.4 Beta 变更速查工具 (`get_1_4_beta_summary`)**。

### Fixed - 重大修复
- 🐛 **修复 `event_targets` 解析 Bug**：原版转换脚本使用二级标题正则分割，导致 `###` 开头的条目全部合并为 1 条；已修复并成功提取全部 299 条事件目标（Input/Output Scopes、Requires Data）。
- 🐛 **修改器数量大幅补齐**：结合游戏本体 `main_menu/common/modifier_type_definitions/`（含 DLC 01_byz 等），修改器条目从 1,855 条扩充至 **2,497 条**，并完整补全布尔/百分比与颜色属性。
- 🐛 **移除硬编码绝对路径**：原版脚本中的作者本地路径已全部改为动态相对路径。
- 🐛 **兼容 MCP 1.x / 2.x SDK**：支持 `FastMCP` 与 `MCPServer` 双向兼容导入。

### Changed
- 📊 全库数据总条目从 29,122 扩充至 **30,759 条**，唯一索引键达 **28,539 个**。
- 🔄 更新 `src/data_handler.py`、`src/tools.py` 与 `src/resources.py`，新增 10+ 项检索与规范查阅工具。

---

## [1.0.0] - 2025-11-06

### Added
- ✨ 初始发布
- 📚 基础 EU5 Modifier MCP 服务器实现
- 🔍 搜索工具：修改器、效果、事件目标 (存在解析Bug)
- 📊 基础数据类型检索
