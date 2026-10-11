---
name: eu5-mod-review
description: EU5（Jomini 引擎）模组全流程审查与排错技能：对标原版规范、6 级结构化代码审查、检查小写作用域（root/prev/this）、具名 scope 链断裂、变量体系初始化、本地化键前缀与 UTF-8 BOM，结合绑定的 EU5 Modding MCP 诊断工具输出分级结构化自检报告。
whenToUse: 用户要求审查、检查、自检、验证、排错 EU5 模组代码或提供 mod 目录要求审计时使用
disable-model-invocation: false
---

# EU5 Mod Review（模组代码审查流程）

本技能为 **EU5 (Europa Universalis V / Jomini 引擎)** 模组提供结构化审查和排错支持。
与绑定的 **`eu5-modding-mcp`** 服务深度结合，实现自动化规则检查与 API 存在性核验。

---

## 🛠️ MCP 审查工具联动

审查过程中优先调用以下绑定的 MCP 工具进行快速比对：
- `validate_mod_snippet`：对目标代码段执行底层规则离线诊断（大写 ROOT、废弃语法、变量守卫误用等）；
- `get_modding_pitfalls`：查询特定模块的踩坑记录（输入 'scope', 'variable', 'merging', 'BOM', '1.4' 等）；
- `get_field_definition`：核对被审类目（如 `laws`, `estates`, `expedition_types`）是否使用了未支持的字段；
- `search_modifiers` / `search_effects` / `search_triggers`：验证代码中调用的语法词条在 1.3/1.4 版本中是否存在。

---

## 一、审查准备与文件发现

1. **定位 Mod 目录**：`Documents\Paradox Interactive\Europa Universalis V\mod\<mod>\` 或 Steam 工坊目录。
2. **扫描文件树**：
   - 脚本：`**/*.txt`, `**/*.gui`, `**/*.info`
   - 本地化：`**/*.yml`
   - 模组配置：`.metadata/metadata.json`
3. **定位知识库**：参考本插件根目录 `kb/` 下的 `fields/` 对应类目文档及 `pitfalls.md`。

---

## 二、六级结构化检查清单

### 1. 结构与格式（致命缺陷）
- [ ] **括号配对**：花括号 `{}` 严格平衡，防止跨块穿透；
- [ ] **注释吞行**：检查 `#` 是否误注释了换行后的核心逻辑代码；
- [ ] **UTF-8 BOM**：所有 `.yml` 必须具备 UTF-8 BOM 签名（EF BB BF）。普通无 BOM 文件将被游戏直接略过；
- [ ] **本地化缩进**：`.yml` 内部键名必须缩进 1 级，严禁顶格书写。

### 2. 作用域与具名 Scope
- [ ] **小写作用域**：严格禁止 `ROOT`/`PREV`/`FROM`/`THIS`，必须为小写 `root`/`prev`/`this`；
- [ ] **禁止 event_target**：严禁使用 `event_target:xxx`，必须先 `save_scope_as = xxx` 并在后续使用 `scope:xxx`；
- [ ] **具名 Scope 嵌套限制**：`save_scope_as` 保存的具名 scope **不跨嵌套 effect 调用**，跨层使用须在 effect 开头防御性重存：`scope:actor = { save_scope_as = xxx }`；
- [ ] **作用域实体匹配**：佣兵不能直接取 `unit_location`，必须经 sub_unit 遍历位置。

### 3. 变量体系与守卫
- [ ] **变量初始化**：变量使用前必须初始化，避免报 `Failed to fetch variable`；
- [ ] **数值变量守卫**：**检查数值变量是否存在必须使用 `has_variable = X`**；禁止使用 `exists = var:X`（后者仅用于国家/实体引用变量，用于数值变量会导致 trigger 守卫穿透并报数百次错误）。

### 4. 合并体系与加载顺序
- [ ] **顺序敏感块**：`levies` 特化单位、`country_name_construction` 是按第一个匹配生效的块，**绝不能使用 `INJECT:`**，必须整体文件覆盖并置顶新条目；
- [ ] **REPLACE 完整性**：使用 `REPLACE:` 时必须保留原版同名块内的全部非修改字段。

### 5. 事件结构规范
- [ ] **事件 Type**：必须五选一（`country_event`, `location_event`, `unit_event`, `exploration_event`, `age_event`），严禁 EU4 的 `province_event`；
- [ ] **选项权重**：严禁 `weight = N`，必须使用 `ai_chance = { base = N modifier = {...} }`；
- [ ] **事件 ID 格式**：严格遵循 `<namespace>.<1~9999>`。

### 6. AI 生态与防死循环
- [ ] **门槛防死**：事件若带 `is_human = yes` 门槛，AI 永远不会触发；
- [ ] **灾难防重入**：灾难的结束 effect **绝不能在 on_end 移除解决标记**，否则会导致灾难无限重入并重复叠加永久修正。

---

## 三、审查输出报告标准格式

```markdown
## 审查报告：<mod 目录/名称>

### 🚨 阻塞级缺陷 (Blockers / Errors)
- `path/to/file.txt:行号`：[错误类型] 具体问题阐述与正确写法对比。

### ⚠️ 潜在隐患 (Warnings / High Risk)
- `path/to/file.yml:行号`：[BOM/作用域警告] 潜在风险与改进建议。

### 💡 规范与优化建议 (Suggestions)
- [数值吸附/命名建议] ...

### 📋 校验总结
- 检查文件数：N
- 发现错误：N 处 | 警告：N 处 | 建议：N 处
- 评估结论：[通过 / 需修复后部署]
```
