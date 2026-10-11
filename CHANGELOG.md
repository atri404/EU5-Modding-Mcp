# Changelog

所有项目的重要更改都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
此项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [2.3.1] - 2026-10-11

### Added - Token 极致优化与极速工具搜索升级
- ⚡ **全库一站式智能统一检索 (`eu5_omni_search`)**：单次调用跨 10 大系统（修改器、效果、触发器、事件目标、原生挂钩点、开发者Readme、字段规范、原版机制、Defines常量与双语术语）检索相关条目，输出高密度摘要卡片，节约 70% Token 与 4 倍多轮尝试耗时。
- 📦 **紧凑 JSON 序列化 (`serialize_response`)**：工具与资源响应默认去除冗余缩进空格与换行，上下文 Token 消耗直降 30%~50%。
- 📑 **按小节精简分段读取 (`section`)**：`get_field_definition`、`get_vanilla_mechanic` 与 `get_guide` 增加可选 `section` 参数（如 `section="补缺"`、`section="可改"`），按需提取目标段落，避免单次塞入 30KB+ 大文档导致上下文挤爆。
- ⌨️ **5 条 Claude Code 快捷斜杠指令 (`commands/`)**：新增 `/eu5-search` (跨库检索), `/eu5-lint` (代码静态诊断), `/eu5-arch` (三层架构与工坊规范), `/eu5-readme` (官方开发者规范全文), `/eu5-error` (报错日志解码)。
- 🔍 **超级静态诊断校验器规则扩充至 15+ 项**：
  - 自动拦截全角中文标点符号（如 `：`、`，`、`“”`，防止 Jomini `lexer.cpp` 词法器未知字符崩溃）；
  - 自动拦截在只读判断条件块 (`trigger = { ... }`) 内误写状态修改效果 (`add_treasury`, `set_variable` 等)；
  - 自动提示事件文件顶部缺少 `namespace = xxx` 声明。
- 🛡️ **Defines 源码脱敏与系统地图分组概览**：`search_defines` 块列表自动脱敏长源码并保留 `content_length` 与提取提示；`get_systems_map` 默认返回功能分组紧凑概览，节约 86% Token。
- 🔧 **工具集扩充至 36 个**：纳入 `eu5_omni_search`、`ping` 与 `get_server_info`，与 FastMCP 服务端注册完全同步。

---

## [2.3.0] - 2026-10-11

### Added - 原版游戏本体与 1.4 工坊深度融合
- ⚙️ **Defines 体系本体全量对齐**：提取 `loading_screen/common/defines/00_defines.txt` 与 `00_gfx.txt` 全量 **38 个 N 块与 1,430 个常量**（含 Faster Universalis 性能调优说明与行号索引）。
- 📖 **游戏本体 74 份开发者 Readme 全文收录 (`vanilla_readmes.json`)**：涵盖 advances, building_types, laws, generic_actions 等所有原版核心类目。
- 🔄 **原版 216 条 on_actions 挂钩点全量解析 (`on_actions.json`)**：包含原版全部 131 个底层 hardcoded 挂钩点及各类周期脉冲与触发事件。
- 🏛️ **EU5 三层生命周期架构指南 (`mod_architecture_guide.json`)**：深入指导 `loading_screen/`、`main_menu/`、`in_game/` 三层物理隔离规则、无冲突 Sub-on-action 链式挂载与 CMF 虚拟存储国机制。
- 🩺 **真实 C++ 引擎报错诊断库扩充至 23 组 (`error_log_decoder.json`)**：提取实机运行捕获的 `pdx_localize.cpp`, `pdx_gui_layout.cpp`, `interaction_target.cpp`, `lexer.cpp` 等源码签名。
- 🔍 **超级静态诊断校验器升级**：新增拦截自动布局容器内 `position` 布局冲突 (`pdx_gui_layout.cpp:201`)、根挂钩点破坏性覆盖、select_trigger 重复标记与 EU4 废弃修改器。
- 📊 **全库条目扩充至 30,907 条**，唯一索引键达 28,643 个。

---

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

---

## [1.0.0] - 2025-11-06

### Added
- ✨ 初始发布
- 📚 基础 EU5 Modifier MCP 服务器实现
- 🔍 搜索工具：修改器、效果、事件目标
- 📊 基础数据类型检索
