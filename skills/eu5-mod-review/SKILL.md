---
name: eu5-mod-review
description: EU5（Jomini 引擎）模组全流程审查与排错技能：对标原版规范、8 级结构化代码审查、error.log 日志诊断、ID 族引用校验、三层生命周期存放检查、GUI 自动布局约束、全角标点与只读条件冲突检查、乱码抢救与防误报白名单，结合绑定的 EU5 Modding MCP 诊断工具输出分级结构化自检报告。
whenToUse: 用户要求审查、检查、自检、验证、排错 EU5 模组代码或提供 mod 目录要求审计时使用
disable-model-invocation: false
---

# EU5 Mod Review（模组代码审查与排错流程）

本技能为 **EU5 (Europa Universalis V / Jomini 引擎)** 模组提供结构化审查和排错支持。
与绑定的 **`eu5-modding-mcp`** 服务（36 工具 & 25 资源）深度结合，实现自动化规则检查与 API 存在性核验。

---

## 🛠️ MCP 审查与排错工具联动

审查与排错过程中优先调用以下绑定的 MCP 工具：
- `validate_mod_snippet`：对目标代码段执行底层规则离线诊断（全角中文标点、trigger 只读条件块内误写修改效果、大写 ROOT、废弃语法、错误 building:/unit_category: 前缀、花括号平衡、法规撤销陷阱、变量守卫误用、根挂钩点 effect 破坏性覆写、vbox 内 position 布局冲突、重复 target_flag 等 15+ 项规则）；
- `decode_error_log`：当提供 `error.log` 日志行时，自动解码报错病因、首查点与解决建议（集成 23 条包含真实 C++ 引擎签名的规则）；
- `get_mod_architecture_guide`：核对文件是否放在正确的生命周期层级（`loading_screen/`, `main_menu/`, `in_game/`）；
- `search_vanilla_readmes` / `get_vanilla_readme`：调阅对应类目的原版开发者官方规范；
- `search_id_rules` / `get_id_rule`：核对代码中引用的 ID 属于带前缀族（`building_type:`, `sub_unit_category:`）还是裸写族（`advance`, `trait` 查询），排查静默失效；
- `get_loc_key_rules`：核对事件、任务、修正等本地化键命名及缺键排查原则；
- `get_review_checklist`：获取 8 维度机械审查项与防误报白名单（白名单内容不得误报为错误）；
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
- [ ] **全角标点符号**：严禁出现全角冒号 `：`、逗号 `，`、引号 `“”` 等中文符号，词法器 `lexer.cpp` 会直接抛出 `Unknown character` 中断解析；
- [ ] **注释吞行**：检查 `#` 是否误注释了换行后的核心逻辑代码；
- [ ] **UTF-8 BOM**：所有 `.yml` 和脚本必须具备 UTF-8 BOM 签名（EF BB BF）。普通无 BOM 文件将被游戏直接略过；
- [ ] **本地化缩进**：`.yml` 内部键名必须缩进 1 级，严禁顶格书写。

### 2. 作用域与条件隔离（逻辑安全）
- [ ] **小写作用域**：EU5 严格要求小写 `root`, `prev`, `this`，严禁大写 `ROOT`；
- [ ] **只读条件块安全**：`trigger = { ... }` 块内只读，严禁混入 `add_treasury`, `set_variable` 等修改状态指令；
- [ ] **事件目标语法**：EU5 弃用 `event_target:xxx`，必须改用 `save_scope_as = xxx`并在后续使用 `scope:xxx`；
- [ ] **事件命名空间**：独立事件文件必须在顶部声明 `namespace = xxx`。

### 3. ID 族引用规范（静默失效杀手）
- [ ] **前缀族检查**：
  - 建筑必须为 `building_type:<id>`（严禁 `building:<id>`，原版实查 0 处）；
  - 单位类别必须为 `sub_unit_category:<id>`（严禁 `unit_category:<id>`，原版实查 0 处）；
- [ ] **裸写族检查**：革新 `has_advance = <id>`、特质查询 `has_trait = <id>`、道路 `unlock_road_type = <id>` 严禁带任何前缀（加前缀反而静默失效）；
- [ ] **实体 vs 数值变量守卫**：国家等实体守卫用 `exists = var:x`，纯数值变量守卫用 `has_variable = x`。

### 4. 三层生命周期存放检查
- [ ] **loading_screen/**：`00_defines.txt`、`00_gfx.txt`（`NCamera`）、`data_binding/` 宏。严禁放根目录 `common/defines/`；
- [ ] **main_menu/**：静态修正 `main_menu/common/static_modifiers/` 与前端 GUI。严禁调用 `GetPlayer`、`ShowDBDefinitionName`；
- [ ] **in_game/**：124 类玩法类目、事件与 HUD。

### 5. 工坊无冲突架构模式
- [ ] **Sub-on-action 链式挂载**：严禁在 `on_game_start` 等根挂钩点直接写 `effect = { ... }`，必须使用子挂钩点链挂载；
- [ ] **虚拟存储国 (CMF)**：复杂模组跨层持久化全局变量，建议挂在无地虚拟国 `c:MYMOD` 作用域下。

### 6. GUI 自动布局约束
- [ ] **无 position 违规**：在 `vbox`, `hbox`, `flowcontainer`, `dynamicgridbox` 内部严禁使用 `position = { ... }`（防止 `pdx_gui_layout.cpp:201` 崩溃）。

### 7. 动态平衡与防死循环
- [ ] **法律 potential 恒定性**：法律与改革的 `potential` 只能放政体、宗教等恒定条件，严禁放阶层力量、兵力等波动条件（防止周期复查自动撤销）；
- [ ] **灾难防重入**：灾难完成标记绝不能在 `on_end` 移除。

### 8. 类目字段白名单
- [ ] **字段有效性**：严格比对 `fields/` 对应类目白名单，核验 1.4 测试版变更。

---

## 三、审查输出报告规范

执行审查后，按三级输出结构化结果：
1. **🚨 致命缺陷 (Critical)**：必崩、解析中断或整系统瘫痪项（附修复代码）；
2. **⚠️ 高危暗坑 (High/Warning)**：周期撤销、静默失效、污染其他模组等项；
3. **💡 架构与兼容性建议 (Suggestions)**：文件命名、目录分层、性能调优常量与本地化规范。
