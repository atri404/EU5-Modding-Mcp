---
name: eu5-mod-review
description: EU5（Jomini 引擎）模组全流程审查与排错技能：对标原版规范、8 级结构化代码审查、error.log 日志诊断、ID 族引用校验、三层生命周期存放检查、GUI 自动布局约束、乱码抢救与防误报白名单，结合绑定的 EU5 Modding MCP 诊断工具输出分级结构化自检报告。
whenToUse: 用户要求审查、检查、自检、验证、排错 EU5 模组代码或提供 mod 目录要求审计时使用
disable-model-invocation: false
---

# EU5 Mod Review（模组代码审查与排错流程）

本技能为 **EU5 (Europa Universalis V / Jomini 引擎)** 模组提供结构化审查和排错支持。
与绑定的 **`eu5-modding-mcp`** 服务深度结合，实现自动化规则检查与 API 存在性核验。

---

## 🛠️ MCP 审查与排错工具联动

审查与排错过程中优先调用以下绑定的 MCP 工具：
- `validate_mod_snippet`：对目标代码段执行底层规则离线诊断（大写 ROOT、废弃语法、错误 building:/unit_category: 前缀、花括号平衡、法规撤销陷阱、变量守卫误用、根挂钩点 effect 破坏性覆写、vbox 内 position 布局冲突、重复 target_flag 等 11+ 项规则）；
- `decode_error_log`：当提供 `error.log` 日志行时，自动解码报错病因、首查点与解决建议（集成 23 条包含真实 C++ 引擎签名的规则）；
- `get_mod_architecture_guide`：核对文件是否放在正确的生命周期层级（`loading_screen/`, `main_menu/`, `in_game/`）；
- `search_vanilla_readmes` / `get_vanilla_readme`：调阅对应类目的原版开发者官方规范；
- `search_id_rules` / `get_id_rule`：核对代码中引用的 ID 属于带前缀族（`building_type:`, `sub_unit_category:`）还是裸写族（`advance`, `trait` 查询），排查静默失效；
- `get_loc_key_rules`：核对事件、任务、修正等本地化键命名及缺键排查原则；
- `get_review_checklist`：获取 7 维度机械审查项与防误报白名单（白名单内容不得误报为错误）；
- `search_modding_cases` / `get_modding_case`：参考真实案例复盘（BOM损坏、法律撤销机制等）；
- `recover_corrupted_encoding`：若遇到注释或本地化出现中文乱码（如 `鍚堝悓`），尝试自动回环抢救还原。

---

## 一、审查准备与文件发现

1. **定位 Mod 目录**：`Documents\Paradox Interactive\Europa Universalis V\mod\<mod>\` 或 Steam 工坊目录。
2. **扫描文件树**：
   - 脚本：`**/*.txt`, `**/*.gui`, `**/*.info`
   - 本地化：`**/*.yml`
   - 模组配置：`.metadata/metadata.json`
3. **定位知识库**：参考本插件根目录 `kb/` 下的 `fields/` 对应类目文档及 `pitfalls.md`。

---

## 二、八级结构化检查清单

### 1. 结构与格式（致命缺陷）
- [ ] **括号配对**：花括号 `{}` 严格平衡，防止跨块穿透（可用 `validate_mod_snippet` 自动测定）；
- [ ] **注释吞行**：检查 `#` 是否误注释了换行后的核心逻辑代码；
- [ ] **UTF-8 BOM**：所有 `.yml` 和脚本必须具备 UTF-8 BOM 签名（EF BB BF）。普通无 BOM 文件将被游戏直接略过；
- [ ] **本地化缩进**：`.yml` 内部键名必须缩进 1 级，严禁顶格书写。

### 2. ID 族引用规范（静默失效杀手）
- [ ] **前缀族检查**：
  - 建筑：必须 `building_type:<id>`（⚠️ **严禁 `building:<id>`**，原版 0 处）；
  - 单位类别：必须 `sub_unit_category:<id>`（⚠️ **严禁 `unit_category:<id>`**，原版 0 处）；
  - 灾难：必须 `disaster_type:<id>`；
- [ ] **裸写族检查**：
  - 革新：必须 `has_advance = <id>`（严禁 `advance:<id>`）；
  - 道路：必须 `unlock_road_type = <id>`；
  - 生产方式：必须 `unlock_production_method = <id>`；
  - 特质查询：必须 `has_trait = <id>`（裸写）；仅添加特质时使用 `add_trait = trait:<id>`。

### 3. 作用域与具名 Scope
- [ ] **小写作用域**：严格禁止 `ROOT`/`PREV`/`FROM`/`THIS`，必须为小写 `root`/`prev`/`this`；
- [ ] **禁止 event_target**：严禁使用 `event_target:xxx`，必须先 `save_scope_as = xxx` 并在后续使用 `scope:xxx`；
- [ ] **具名 Scope 嵌套限制**：`save_scope_as` 保存的具名 scope **不跨嵌套 effect 调用**，跨层使用须在 effect 开头防御性重存：`scope:actor = { save_scope_as = xxx }`；
- [ ] **作用域实体匹配**：佣兵不能直接取 `unit_location`，必须经 sub_unit 遍历位置。

### 4. 变量体系与守卫
- [ ] **变量初始化**：变量使用前必须初始化，避免报 `Failed to fetch variable`；
- [ ] **数值变量守卫**：**检查数值变量是否存在必须使用 `has_variable = X`**；禁止使用 `exists = var:X`（后者仅用于国家/实体引用变量，用于数值变量会导致 trigger 守卫穿透并报数百次错误）。

### 5. 法律与灾难语义陷阱
- [ ] **法律/改革 potential 周期撤销**：`law` / `government_reform` 的 `potential` 绝不能包含兵力、阶层力量、金钱等波动性条件，否则条件一失效整条法律及政策会被引擎强制自动撤销！
- [ ] **灾难防重入**：灾难的结束 effect **绝不能在 on_end 移除解决标记**，否则会导致灾难无限重入并重复叠加永久修正。

### 6. 合并体系与加载顺序
- [ ] **顺序敏感块**：`levies` 特化单位、`country_name_construction` 是按第一个匹配生效的块，**绝不能使用 `INJECT:`**，必须整体文件覆盖并置顶新条目；
- [ ] **REPLACE 完整性**：使用 `REPLACE:` 时必须保留原版同名块内的全部非修改字段。

### 7. 生命周期层级与工坊规范
- [ ] **三层物理隔离**：
  - `00_defines.txt` 必须放 `loading_screen/common/defines/`，严禁放根 `common/`；
  - 玩法类目必须放 `in_game/common/`；
  - 静态修正放 `main_menu/common/static_modifiers/`；
- [ ] **无冲突 Sub-on-action 链**：根挂钩点（如 `on_game_start`, `on_new_ruler`）绝不能直接写 `effect = { ... }`，必须通过 `on_actions = { <sub_hook> }` 挂载！
- [ ] **GUI 自动布局约束**：`vbox`, `hbox`, `flowcontainer`, `dynamicgridbox` 内严禁给子元素写 `position = { ... }`，会引发 `pdx_gui_layout.cpp:201` 引擎报错；
- [ ] **交互动作 target_flags**：同一交互动作内多个 `select_trigger` 必须使用不同的 `target_flag` 命名；
- [ ] **废弃修改器**：禁止使用 EU4 废弃修改器（如 `great_power_score`, `army_reinforce_cost` 等）。

### 8. 防误报核对（白名单排除）
- 检查项是否属于 `review_checklist` 第七节白名单（如：空壳目录 `policies`/`mission_task_defs` 勿删、无脚本引用的 static_modifier 引擎按名生效、新教 `enable = 9999.1.1` 正常写法等），严禁误报！

---

## 三、审查输出报告标准格式

```markdown
## 审查报告：<mod 目录/名称>

### 🚨 阻塞级缺陷 (Blockers / Errors)
- `path/to/file.txt:行号`：[错误类型] 具体问题阐述与正确写法对比。

### ⚠️ 潜在隐患 (Warnings / High Risk)
- `path/to/file.yml:行号`：[BOM/作用域/法规撤销警告] 潜在风险与改进建议。

### 💡 规范与优化建议 (Suggestions)
- [数值吸附/命名建议] ...

### 📋 校验总结
- 检查文件数：N
- 发现错误：N 处 | 警告：N 处 | 建议：N 处
- 评估结论：[通过 / 需修复后部署]
```
