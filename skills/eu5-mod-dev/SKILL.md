---
name: eu5-mod-dev
description: EU5（Jomini 引擎）模组开发制作全流程技能：搭建 Mod 骨架（metadata.json 与四区目录）、制作事件/国家/任务树/法律/建筑/商品脚本、本地化 UTF-8 BOM 规范、合并策略（INJECT/REPLACE），结合绑定的 EU5 Modding MCP 工具进行实时语法与修改器校验。
whenToUse: 用户要求新建、制作、编写、扩展 EU5 模组内容（新国家、新任务链、新事件、新建筑、新法律政策、本地化等），或询问"怎么在 EU5 做 X"时使用
disable-model-invocation: false
---

# EU5 Mod Development（模组制作工作流）

本技能为 **EU5 (Europa Universalis V / Jomini 引擎)** 模组开发制作提供全流程工程化指导。
知识库位于本插件根目录的 `kb/` 下，底层 API 与语法可通过绑定的 **`eu5-modding-mcp`** 工具实时查询。

> ⚠️ **核心铁律：EU5 ≠ EU4**
> 1. 无 `ROOT` / `PREV`，作用域一律小写：`root`, `prev`, `this`。
> 2. 无 `event_target` / `global_event_target`，使用 `save_scope_as = xxx` 并在后续通过 `scope:xxx` 引用。
> 3. 本地化词条无 `:0` 后缀，且所有 `.yml` 与脚本必须带 **UTF-8 BOM**（无 BOM 会被引擎忽略或乱码）。
> 4. 事件选项无 EU4 式 `weight = N`，改用 `ai_chance = { base = N modifier = {...} }`。
> 5. 编写任何条目随时调用 MCP 工具 `validate_mod_snippet` 静态校验。

---

## 🛠️ MCP 协同工具（即开即用）

当本插件启用时，以下 MCP 工具随技能一同生效，编写过程中优先调用：
- `search_modifiers`：查询 2,497 条修改器属性（包含是否百分比、布尔及适用范围）。
- `search_effects`：查询游戏效果语法签名与适用作用域。
- `search_triggers`：查询触发条件语法与适用作用域。
- `get_field_definition`：获取指定类目（如 `building_types`, `laws`, `expedition_types`）的完整字段白名单与 1.4 beta 变更。
- `get_vanilla_mechanic`：查询机制深度解析（可改点与硬编码边界）。
- `validate_mod_snippet`：对你生成的脚本片段进行离线语法诊断。

---

## 一、搭建 Mod 骨架

1. **模组路径**：`Documents\Paradox Interactive\Europa Universalis V\mod\<your_mod>\`
2. **注册清单**：新建 `.metadata\metadata.json`：
```json
{
  "name": "My Mod Name",
  "id": "my_mod_unique_id",
  "version": "1.0.0",
  "supported_game_version": "1.4.*",
  "short_description": "A mod for Europa Universalis V",
  "tags": ["Gameplay", "Historical"]
}
```
3. **四区分离机制**：
   - `in_game\common\`：主体逻辑（事件、科技、建筑、单位、法律、阶层等）
   - `loading_screen\common\defines\`：数值常量（`00_defines.txt`）
   - `main_menu\common\`：修正类型注册（`modifier_type_definitions\`）、静态修正（`static_modifiers\`）、旗帜纹章等
   - `main_menu\localization\<lang>\`：主本地化文件（带 UTF-8 BOM）

---

## 二、合并策略选择（冲突防范）

- **新增独立内容**：新建文件，使用大数字或 `zzz_` 前缀（如 `zzz_my_events.txt`）保证加载后置。
- **修改原版条目**：
  - `INJECT:` 追加到同名块末尾（⚠️ **征召兵 levies 特化单位与国名构建等顺序敏感块绝不可用**，必须整体覆盖并在 fallback 前插入）。
  - `REPLACE:` 整块替换（必须逐字段保留原版属性，否则会丢失关联机制）。
  - `on_action`：直接书写同名块即为合并追加语义，无需加 REPLACE。
  - **事件不能 REPLACE/INJECT**：修改原版事件应新建文件并在同名 namespace 下重新定义同名 ID。

---

## 三、标准脚本模式

### 1. 事件制作 (`in_game/events/`)
- 必须声明 `namespace = <ns>`，事件 ID 格式为 `<ns>.<int>`（1~9999）。
- `type` 必须五选一：`country_event`, `location_event`, `unit_event`, `exploration_event`, `age_event`。
- 本地化键名规则：`<ns>.<id>.title`, `<ns>.<id>.desc`, `<ns>.<id>.a`（选项文本）。

### 2. 国家新增端到端（详见 `kb/guides/new-country-tutorial.md`）
- 步骤 0：确认 TAG（3 个大写字母）未被占用；
- 步骤 1：国家定义在 `in_game/setup/countries/<region>.txt`，字段带 `culture_definition` 与 `religion_definition`；
- 步骤 2：注册旗帜与本地化。

### 3. 本地化规范
- 文件名：`main_menu\localization\<lang>\<topic>_l_<lang>.yml`
- 第一行顶格 `l_simp_chinese:`，内部条目缩进 1 级。
- 保存必须为 **UTF-8 with BOM**（前三字节 `EF BB BF`）。

---

## 四、自检与测试收尾

编写完成后，执行以下步骤：
1. 将编写的脚本段传入 MCP 工具 `validate_mod_snippet`，检查是否存在 EU4 遗留语法或作用域陷阱；
2. 检查括号闭合与 `#` 注释吞行；
3. 使用 `kb/tools/error-log-decoder.md` 解读游戏 `error.log` 中的报错行。
