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
> 4. 事件选项无 EU4 式 `weight = N`，改用 `ai_chance = { base = N modifier = {...} }`。
> 5. **ID 引用必须遵循前缀族与裸写族规范**（如 `building_type:xxx` 绝不能写成 `building:xxx`；`has_advance = xxx` 绝不能带前缀）。
> 6. 编写任何条目随时调用 MCP 工具 `validate_mod_snippet` 静态校验。

---

## 🛠️ MCP 协同工具（即开即用）

当本插件启用时，以下 MCP 工具随技能一同生效，编写过程中优先调用：
- `get_mod_architecture_guide`：查询 EU5 三层生命周期架构规范、无冲突 Sub-on-action 链式挂载、CMF 虚拟存储国机制与 Faster Universalis 性能调优常量。
- `search_vanilla_readmes` / `get_vanilla_readme`：调阅游戏本体 74 份官方开发者 readme.txt 规范（涵盖 advances, building_types, laws, generic_actions 等）。
- `search_guides` / `get_guide`：调阅 12 篇制作指南与端到端教程（如 `new-country-tutorial` 新国家、`new-mission-pack-tutorial` 新任务链、`mod-skeleton` 骨架、`merging` 合并规则、`law-design` 法律、`defines` 常量）。
- `search_modifiers`：查询 2,497 条修改器属性（包含是否百分比、布尔及适用范围）。
- `search_effects` / `search_triggers`：查询游戏效果与触发条件语法签名及适用作用域。
- `search_id_rules` / `get_id_rule`：核对某个类目引用必须带前缀（如 `building_type:`）还是裸写（如 `advance`）。
- `get_loc_key_rules`：查询事件、任务、修正、概念等类目的固定本地化键命名规范。
- `get_systems_map`：定位 160+ 类目的原版入口文件与 readme 状态。
- `search_defines` / `get_define_block`：查询 00_defines.txt 常量数值与行范围（聚合本体 38 个 N 块与 1,430 个常量）。
- `get_field_definition`：获取指定类目（如 `building_types`, `laws`, `expedition_types`）的完整字段白名单与 1.4 beta 变更。
- `validate_mod_snippet`：对生成的脚本片段执行离线语法诊断与高危陷阱排查。

---

## 一、EU5 三层生命周期架构 (3-Tier Lifecycle Architecture)

EU5 相比旧代引擎的核心差异在于将所有数据、界面与脚本严格解耦为**三个生命周期层级**，放错目录会导致静默忽略或直接崩溃：

### 1. 引导启动层 (`loading_screen/`)
- **职能**：引擎冷启动与全局常量初始化。
- **核心路径**：
  - `loading_screen/common/defines/00_defines.txt`：**所有全局 Defines 常量必须放这里**（⚠️ 严禁直接放 `common/defines/`，会被引擎静默略过！）。
  - `loading_screen/gfx/defines/00_gfx.txt`：摄像机 `NCamera` 参数。
  - `loading_screen/data_binding/`：跨界面全局数据绑定宏。
  - `loading_screen/input_profile/*.profile`：全局按键映射。

### 2. 前端界面与全局静态层 (`main_menu/`)
- **职能**：游戏进入主菜单、选国界面与游戏大厅。
- **核心路径**：
  - `main_menu/common/static_modifiers/`：全局静态修正。
  - `main_menu/common/modifier_type_definitions/`：自定修改器类型注册。
  - `main_menu/gui/`：主菜单与选国 HUD。
  - `main_menu/localization/<lang>/`：前端与全局通用词条。
  - `main_menu/setup/start/`：开局启动序列脚本。
- **禁忌**：严禁调用依赖运行中国家的数据绑定（如 `GetPlayer`, `ShowDBDefinitionName`），会触发 `Trying to use ... when there is no game state`。

### 3. 游戏内玩法模拟层 (`in_game/`)
- **职能**：活动游戏会话（Active Game Session）的核心玩法逻辑。
- **核心路径**：
  - `in_game/common/`：124 个玩法类目（`advances`, `building_types`, `laws`, `generic_actions`, `country_interactions`, `on_action` 等）。
  - `in_game/events/`：事件体系。
  - `in_game/gui/`：游戏内 Lateralview、顶部栏与 Scripted Widgets。
  - `in_game/localization/<lang>/`：事件、任务、决议具体多语言文本。
  - `in_game/setup/`：国家、省份与角色历史数据。

---

## 二、工坊核心实践规范

### 1. 无冲突 Sub-on-action 链式挂载
严禁在根挂钩点（如 `on_game_start`, `on_new_ruler`）直接使用 `effect = { ... }`，否则会直接覆盖原版和其他模组的全部逻辑！
**唯一正确做法**：
```pdx
on_game_start = {
    on_actions = {
        mymod_on_game_start_hook
    }
}

mymod_on_game_start_hook = {
    effect = {
        # 自定义初始化逻辑
    }
}
```

### 2. CMF 虚拟存储国机制 (Storage Country)
跨多人会话或多脚本协同存储全局变量时，Jomini 的 `global_variable_list` 有概率遭遇 scope 寻址穿透。工坊主流实践在 `in_game/setup/countries/` 创建一个无地虚拟国（如 `c:CMF`），通过 `c:MYMOD = { set_variable = ... }` 稳定存取全局配置与异步队列。

### 3. GUI 布局黄金法则
在 `vbox`, `hbox`, `flowcontainer`, `dynamicgridbox` 等自动布局容器内**严禁包含 `position = { x y }`**，否则会触发 C++ 报错 `Widget cannot have a position in a layout (pdx_gui_layout.cpp:201)`。位置微调应使用 `margin`, `spacing` 或 `layoutpolicy_horizontal/vertical`。裸英文字符串在 GUI 中必须使用 `raw_text = "..."` 避免报缺词条警告。

---

## 二、端到端实战教程路由

遇到具体制作任务时，直接调阅对应的端到端实战手册：

1. **制作新国家**（调阅 `get_guide("new-country-tutorial")`）：
   - 开局三层数据：国家定义（`setup/countries/`）、开局模板（`common/country_creation/`，首选 `include = "<模板名>"`）、开局实体（`setup/start/`）。
   - 必备要素：Tag、政体、主要文化、宗教、首都位置、开局统治者与旗帜纹章。
2. **制作新任务链**（调阅 `get_guide("new-mission-pack-tutorial")`）：
   - 任务文件放 `common/missions/`；
   - 任务键 5 键套（`<链名>`, `_DESCRIPTION`, `_CRITERIA_DESCRIPTION`, `_BUTTON_TOOLTIP`, `_BUTTON_DETAILS`）；
   - 节点键 3 键套（`<节点名>`, `_desc`, `_tt`）；
   - 任务奖励必须区分一次性与持久奖励（`on_completion` vs `on_persistent_completion`）。
3. **设计新法律与政策**（调阅 `get_guide("law-design")`）：
   - `potential` 只能放恒定条件（政体/宗教/tag），**绝不放兵力/阶层力量/金钱等动态值**（否则引擎周期复查导致整条法律连同政策被自动撤销！）；
   - **必须查撞名**（显示名与键名都要查，防止覆盖本体）。
4. **修改引擎常量 Defines**（调阅 `get_guide("defines")` 或 `search_defines`）：
   - 优先在 `main_menu/common/game_rules/` 中通过游戏规则覆盖；
   - 直接覆盖修改 `loading_screen/common/defines/00_defines.txt` 的同名块。

---

## 三、合并策略选择（冲突防范）

- **新增独立内容**：新建文件，使用大数字或 `zzz_` 前缀（如 `zzz_my_events.txt`）保证加载后置。
- **修改原版条目**：
  - `INJECT:` 追加到同名块末尾（⚠️ **征召兵 levies 特化单位与国名构建等顺序敏感块绝不可用**，必须整体覆盖并在 fallback 前插入）。
  - `REPLACE:` 整块覆盖，**必须保留原版同块内未修改的全部字段**。
  - `EDIT:` 精细按键替换。
