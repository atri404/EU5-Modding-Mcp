---
name: eu5-mod-lookup
description: EU5（Jomini 引擎）机制规范与 API 智能查表技能：查 1.4-beta 变更、类目字段白名单（103 篇）、原版机制深度拆解（24 篇，含硬编码边界）、中英双语术语对照，调用绑定的 EU5 Modding MCP 工具即时检索。
whenToUse: 用户询问某个机制怎么运作、某字段是否存在、有哪些可改动点或硬编码限制、1.4 测试版改了什么、或查询中英专业术语时使用
disable-model-invocation: false
---

# EU5 Mod Lookup（机制与 API 智能查表）

本技能为 **EU5 (Europa Universalis V / Jomini 引擎)** 提供快速精准的机制规则、字段规格与引擎 API 查询服务。
全面融合本插件绑定的 **`eu5-modding-mcp`** 实时工具与 `kb/` 全量文档。

---

## 🛠️ MCP 核心查表工具

查阅时根据用户问题类型直接调用对应工具：

| 查询场景 | 推荐 MCP 工具 | 示例参数 |
| :--- | :--- | :--- |
| **查询 1.4 Beta 变更** | `get_1_4_beta_summary` | 无参数 |
| **查类目有哪些字段** | `get_field_definition` | `category: "expedition_types"` / `"estates"` / `"building_types"` |
| **搜索包含某属性的类目** | `search_field_definitions` | `query: "ai_chance"` / `"goods"` |
| **查底层机制与硬编码边界** | `get_vanilla_mechanic` | `system: "army_movement"` / `"production_and_buildings"` / `"pop"` |
| **查修改器名字与格式** | `search_modifiers` | `query: "discipline"`, `category: "country"` |
| **查触发器或效果语法** | `search_triggers` / `search_effects` | `query: "has_building"`, `scope: "location"` |
| **查挂钩点 on_actions** | `search_on_actions` | `query: "yearly_country_pulse"` |
| **查中英双语官方术语** | `search_glossary` | `query: "市场接入度"` 或 `"market_access"` |
| **查避坑与经验** | `get_modding_pitfalls` | `topic: "scope"` / `"merging"` / `"BOM"` |

---

## 一、高频查询指南

### 1. 类目字段白名单查询
- 当需要知道 `common/` 目录下某一类目（如新加建筑、新加政策、新加远征）支持哪些字段时：
  - 调用 `get_field_definition("类目名")`；
  - 关注返回结果中的 `summary` 与 `本体实测补缺` 小节，特别注意官方 readme 漏写的实际生效字段。

### 2. 原版机制与硬编码边界查询
- 当玩家或作者问“这个机制能不能改”、“怎么实现 X”时：
  - 调用 `get_vanilla_mechanic("系统名")`；
  - 重点阅读文档末尾的 **「可改点 vs 引擎硬编码边界」**（例如：天气的风暴效果是引擎硬编码，只能改生成与 `on_storm_reached_location`；时代的年份推进全局有效等）。

### 3. 术语对齐与汉化
- 严禁凭主观臆造译名，调用 `search_glossary` 查对齐官方本体文件的标准译法（如 `merchant_power` 应为“贸易优势”而非“商人力量”；`market_access` 为“市场接入度”）。
