---
name: eu5-mod-lookup
description: EU5（Jomini 引擎）机制规范与 API 智能查表技能：查 1.4-beta 变更、类目字段白名单（103 篇）、原版机制深度拆解（24 篇）、制作指南与端到端教程（12 篇）、Defines 引擎常量索引、ID 族引用规范、中英双语术语对照，调用绑定的 EU5 Modding MCP 工具即时检索。
whenToUse: 用户询问某个机制怎么运作、某字段是否存在、有哪些可改动点或硬编码限制、1.4 测试版改了什么、Defines 常量在哪、制作教程怎么写、或查询中英专业术语时使用
disable-model-invocation: false
---

# EU5 Mod Lookup（机制与 API 智能查表）

本技能为 **EU5 (Europa Universalis V / Jomini 引擎)** 提供快速精准的机制规则、字段规格、制作指南与引擎 API 查询服务。
全面融合本插件绑定的 **`eu5-modding-mcp`** 实时工具与 `kb/` 全量文档。

---

## 🛠️ MCP 核心查表工具速查

查阅时根据用户问题类型直接调用对应工具：

| 查询场景 | 推荐 MCP 工具 | 示例参数 / 说明 |
| :--- | :--- | :--- |
| **查询 1.4 Beta 变更** | `get_1_4_beta_summary` | 无参数，查看 1.4 Open Beta 权威变更与新增机制 |
| **查三层生命周期与工坊规范** | `get_mod_architecture_guide` | `topic: "lifecycle"` (三层隔离) / `"sub_on_action"` (无冲突挂载) / `"performance"` (性能调优) |
| **查原版 74 份开发者 Readme** | `get_vanilla_readme` / `search_vanilla_readmes` | `category: "building_types"` / `"cabinet_actions"` / `"laws"` (官方设计规范全文) |
| **查制作教程与实战手册** | `get_guide` / `search_guides` | `guide_name: "new-country-tutorial"` / `"new-mission-pack-tutorial"` / `"merging"` |
| **查 error.log 日志报错** | `decode_error_log` | `log_text: "Failed to fetch variable ..."` 智能给出病因与首查点 (含 C++ 引擎报错特征) |
| **查 ID 族写法（前缀 vs 裸写）** | `get_id_rule` / `search_id_rules` | `family: "building_type"`（前缀）/ `"advance"`（裸写） |
| **查 00_defines.txt 常量数值** | `search_defines` / `get_define_block` | `query: "COMBAT_BASE"` / `block_name: "NAI"` (全量 38 块与 1,430 常量) |
| **查 common 160+ 类目地图** | `get_systems_map` | `category: "building"` 查看入口文件与 readme 状态 |
| **查类目有哪些字段** | `get_field_definition` | `category: "expedition_types"` / `"estates"` / `"laws"` |
| **查底层机制与硬编码边界** | `get_vanilla_mechanic` | `system: "army_movement"` / `"production_and_buildings"` / `"pop"` |
| **查本地化键固定命名格式** | `get_loc_key_rules` | `category: "event"` / `"mission"` / `"modifier"` |
| **查结构化审查清单** | `get_review_checklist` | `section: "文件"` / `"作用域"` / `"白名单"` |
| **查修改器名字与格式** | `search_modifiers` | `query: "discipline"`, `category: "country"` |
| **查触发器或效果语法** | `search_triggers` / `search_effects` | `query: "has_building"`, `scope: "location"` |
| **查挂钩点 on_actions** | `search_on_actions` | `query: "yearly_country_pulse"` (含原版全部 206 挂钩点) |
| **查中英双语官方术语** | `search_glossary` | `query: "市场接入度"` 或 `"market_access"` |
| **查避坑经验与 EU4 对照** | `get_modding_pitfalls` | `topic: "scope"` / `"merging"` / `"BOM"` |
| **抢救 A 类中文乱码** | `recover_corrupted_encoding` | `text: "鍚堝悓"` 自动还原为 `"合同"` |

---

## 一、高频查询指南

### 1. 制作教程与实战手册查询
- 遇到新国家制作、新任务链编写、文件合并（INJECT/REPLACE 规则）、法律设计时，直接调用 `get_guide` 查阅端到端完整教程。

### 2. 类目字段白名单查询
- 当需要知道 `common/` 目录下某一类目（如新加建筑、新加政策、新加远征）支持哪些字段时：
  - 调用 `get_field_definition("类目名")`；
  - 关注返回结果中的 `summary` 与 `本体实测补缺` 小节，特别注意官方 readme 漏写的实际生效字段。

### 3. 原版机制与硬编码边界查询
- 当玩家或作者问“这个机制能不能改”、“怎么实现 X”时：
  - 调用 `get_vanilla_mechanic("系统名")`；
  - 重点阅读文档末尾的 **「可改点 vs 引擎硬编码边界」**（例如：天气的风暴效果是引擎硬编码，只能改生成与 `on_storm_reached_location`；时代的年份推进全局有效等）。

### 4. ID 族与静默失效排查
- 严禁猜测 ID 前缀！调用 `get_id_rule` 确认该类目属于前缀族（如 `building_type:`）还是裸写族（如 `has_advance = <id>`）。写反不会在 error.log 报错，而是静默永不命中。
