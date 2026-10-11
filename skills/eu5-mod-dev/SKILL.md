---
name: eu5-mod-dev
description: EU5（Jomini 引擎）模组开发制作全流程技能：搭建 Mod 骨架（metadata.json 与四区目录）、端到端制作新国家/新任务链/事件/法律/建筑/商品脚本、本地化 UTF-8 BOM 规范、合并策略（INJECT/REPLACE）、Defines 常量修改，结合绑定的 EU5 Modding MCP 工具进行实时语法与修改器校验。
whenToUse: 用户要求新建、制作、编写、扩展 EU5 模组内容（新国家、新任务链、新事件、新建筑、新法律政策、本地化等），或询问"怎么在 EU5 做 X"时使用
disable-model-invocation: false
---

# EU5 Mod Development（模组制作工作流）

本技能为 **EU5 (Europa Universalis V / Jomini 引擎)** 模组开发制作提供全流程工程化指导。
知识库位于本插件根目录的 `kb/` 下，底层 API 与权威规格可通过绑定的 **`eu5-modding-mcp`** 工具实时查询。

> ⚠️ **核心铁律：EU5 ≠ EU4**
> 1. 无 `ROOT` / `PREV`，作用域一律小写：`root`, `prev`, `this`。
> 2. 无 `event_target` / `global_event_target`，使用 `save_scope_as = xxx` 并在后续通过 `scope:xxx` 引用。
> 3. 本地化词条无 `:0` 后缀，且所有 `.yml` 与脚本必须带 **UTF-8 BOM**（无 BOM 会被引擎忽略或乱码）。
> 4. 严禁使用全角标点符号（如 `：`、`，`、`“”`），词法器 `lexer.cpp` 会直接中断解析报错。
> 5. `trigger = { ... }` 块内绝对只读，严禁混入 `add_treasury` 等状态修改指令。
> 6. 事件选项无 EU4 式 `weight = N`，改用 `ai_chance = { base = N modifier = {...} }`。
> 7. **ID 引用必须遵循前缀族与裸写族规范**（如 `building_type:xxx` 绝不能写成 `building:xxx`；`has_advance = xxx` 绝不能带前缀）。
> 8. 编写任何条目随时调用 MCP 工具 `validate_mod_snippet` 静态校验。

---

## 🛠️ MCP 协同工具与快捷指令（即开即用）

当本插件启用时，随附 36 个专业 MCP 工具与 5 条快捷斜杠指令：
- **快捷指令**：
  - `/eu5-search <关键词>`：快速跨库综合检索
  - `/eu5-lint <代码段>`：静态代码语法诊断
  - `/eu5-arch [主题]`：三层架构与工坊规范速查
  - `/eu5-readme <类目>`：官方开发者规范全文速查
  - `/eu5-error <报错>`：error.log 智能解码

- **核心 MCP 工具**：
  - `eu5_omni_search`：**【优先推荐】** 一站式跨库综合检索，单次请求同时返回最匹配的修改器、效果、触发条件、原生挂钩点、Readme 与常量卡片，节约 70% Token。
  - `get_mod_architecture_guide`：查询 EU5 三层生命周期架构规范、无冲突 Sub-on-action 链式挂载、CMF 虚拟存储国机制与 Faster Universalis 性能调优常量。
  - `search_vanilla_readmes` / `get_vanilla_readme`：调阅游戏本体 74 份官方开发者 readme.txt 规范（涵盖 advances, building_types, laws, generic_actions 等）。
  - `search_guides` / `get_guide`：调阅 12 篇制作指南与端到端教程（支持按 `section` 精简读取）。
  - `search_modifiers`：查询 2,497 条修改器属性（包含是否百分比、布尔及适用范围）。
  - `search_effects` / `search_triggers`：查询游戏效果与触发条件语法签名及适用作用域。
  - `search_id_rules` / `get_id_rule`：核对某个类目引用必须带前缀（如 `building_type:`）还是裸写（如 `advance`）。
  - `get_loc_key_rules`：查询事件、任务、修正、概念等类目的固定本地化键命名规范。
  - `get_systems_map`：定位 137+ 类目的原版入口文件、分组概览与 readme 状态。
  - `search_defines` / `get_define_block`：查询 00_defines.txt 常量数值与行范围（聚合本体 38 个 N 块与 1,430 个常量，搜索结果已脱敏长源码）。
  - `get_field_definition`：获取指定类目（如 `building_types`, `laws`, `expedition_types`）的完整字段白名单与 1.4 beta 变更（支持按 `section="补缺"` 提取）。
  - `validate_mod_snippet`：对生成的脚本片段执行离线语法诊断与高危陷阱排查。

---

## 一、EU5 三层生命周期架构 (3-Tier Lifecycle Architecture)

EU5 相比旧代引擎的核心差异在于将所有数据、界面与脚本严格解耦为**三个生命周期层级**，放错目录会导致静默忽略或直接崩溃：

### 1. 引导启动层 (`loading_screen/`)
- **职能**：引擎冷启动与全局常量初始化。
- **包含内容**：
  - `common/defines/00_defines.txt`（**所有 defines 必须放置在此目录！放到根目录 common/defines/ 会被引擎静默略过**）；
  - `gfx/defines/00_gfx.txt`（摄像机 `NCamera` 参数）；
  - `data_binding/`（底层 UI 数据绑定宏）；
  - `input_profile/*.profile`（键位映射）；
  - `fonts/`（全局字体定义）。

### 2. 前端数据库层 (`main_menu/`)
- **职能**：主菜单界面展示与跨局静态元数据注册。
- **包含内容**：
  - `common/static_modifiers/`（难度修正 `difficulty.txt`、国家/地点默认基础属性）；
  - `common/modifier_type_definitions/`（修改器类型注册表）；
  - `gui/`（主菜单 HUD、单人/多人大厅选国面板）；
  - `localization/`（全局元数据本地化）；
  - `setup/start/`（剧本起始年份定义，如 1337.1.1）。
- **避坑红线**：此阶段无存档态与推演状态，**严禁调用游戏内数据函数**（如 `GetPlayer`、`ShowDBDefinitionName` 等），否则引发 `Trying to use ... when there is no game state` 引擎崩溃。

### 3. 玩法模拟层 (`in_game/`)
- **职能**：战局运行、动态事件推演与游戏内交互。
- **包含内容**：
  - `common/` 下的 124 类核心玩法类目（`advances`, `building_types`, `laws`, `generic_actions`, `country_interactions`, `on_action` 等）；
  - `events/`（各类脚本事件）；
  - `gui/`（游戏内 lateralviews 侧边面板、hud 主界面）；
  - `localization/`（具体玩法本地化文本）；
  - `map_data/`（地图省份、航路、地形定义）；
  - `setup/`（历史国家、领地、人物剧本数据）。

---

## 二、工坊 1.4 模组架构模式与性能优化

### 1. 无冲突 Sub-on-action 链式挂载
- **规则**：严禁在 `on_game_start = { effect = { ... } }` 等根挂钩点直接写 `effect`（会覆盖原版与其他模组）；
- **正确做法**：
  ```pdx
  on_game_start = {
      on_actions = {
          mymod_init_hook
      }
  }
  mymod_init_hook = {
      effect = {
          # 你的模组初始化逻辑
      }
  }
  ```

### 2. 虚拟存储国机制 (CMF Storage Country)
- **原理**：为避免联机同步漂移与 `global_variable_list` 跨层穿透问题，在 `in_game/setup/countries/..._storage_country.txt` 注册一个无地虚拟国（如 `c:CMF` / `c:MYMOD`）；
- **数据访问**：
  ```pdx
  c:MYMOD = {
      set_variable = { name = my_setting_var value = 1 }
  }
  ```

### 3. Defines 性能优化调优常量 (Faster Universalis 经验)
- **AI 市场评估与内阁动作步长**：
  ```pdx
  NAI = {
      AI_PERFORMANCE_EVALUATE_MARKET_RATIO_PER_BUILDING = 0.5  # 原版 0.1，步长增大降低运算频率
      AI_PERFORMANCE_CABINET_ACTION_MONTHS_BETWEEN_UPDATES = 6 # 延长内阁检查周期
      AI_CONSTRUCTION_QUEUE_PARALLEL_CHECK_MAX = 5             # 限制单月并行建筑检查
  }
  ```
- **战斗缩放倍率**：
  ```pdx
  NCombat = {
      COMBAT_SPEED_SCALE = 1.0
      COMBAT_DAMAGE_MULT = 1.0
  }
  ```

---

## 三、模组标准骨架与制作四区

```text
<mod_root>/
├── .metadata/
│   └── metadata.json          # 模组元数据
├── loading_screen/            # 引导层
│   └── common/defines/
│       └── mymod_defines.txt  # N 块重载
├── main_menu/                 # 前端层
│   └── common/static_modifiers/
├── in_game/                   # 玩法层
│   ├── common/
│   │   ├── advances/
│   │   ├── building_types/
│   │   ├── laws/
│   │   └── on_action/
│   ├── events/
│   ├── gui/
│   └── localization/
│       └── simp_chinese/     # 必须带 UTF-8 BOM
```
