# EU5 Modding MCP Server (v2.1.0)

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![EU5 Version](https://img.shields.io/badge/EU5-1.3.x%20%2F%201.4%20Beta-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Entries](https://img.shields.io/badge/data%20entries-30%2C759-orange)
![License](https://img.shields.io/badge/license-MIT-green)

一个专为 **Europa Universalis V (欧陆风云 5 / Jomini 引擎)** 模组开发打造的 Model Context Protocol (MCP) 服务器。

本项目基于发售初期的 `EU5-Modding-Mcp` 进行了**全面重构与现代化升级**，整合了：
1. **游戏本体最新数据**（EU5 1.3.x Pavia / 1.3.11 与本地安装文件实查）；
2. **`mrjiaobai-glitch/eu5-modding-kb`（1.4open_beta 分支）** 深度知识库；
3. **EU5 1.4.0 Open Beta** 新增语法（`common/expedition_types`、`common/estates`、`army movement` 等）；
4. 修复了旧版事件目标解析 Bug，并内置了针对 EU4 语法误用与常见引擎陷阱的**离线静态校验器**。

---

## 🌟 核心特性与主要更新 (v2.1.0)

- 🎯 **修复事件目标解析 Bug**：旧版将全量事件目标错误解析合并为 1 条，现已完全修复，提供 **299 条**完整的事件目标数据（输入/输出作用域、是否需数据）。
- 📊 **修改器全量补齐 (2,497 条)**：结合本体 `modifier_type_definitions/`（含拜占庭 DLC 与通用官僚补丁），条目数从 1,855 扩充至 **2,497 条**，附带 boolean、percent、color 与 game_data 类别。
- 🔄 **新增 on_actions 挂钩点 (159 条)**：查询脉冲事件触发点及其 expected_scope 作用域要求。
- 🌐 **新增自定义本地化函数 (413 条)**：查询动态文本函数与候选词条。
- 📚 **整合 103 篇类目权威字段规范**：收录各 common 类目的合法字段、官方 readme 漏写字段普查与取值白名单。
- 🛠️ **整合 24 篇原版机制深度拆解**：解析生产、POP、军事机动、天命、贸易、法律阶层等底层文件构成、数值位置及**引擎硬编码边界**。
- ⚠️ **整合 18 个避坑实战专题**：收录 EU4 vs EU5 语法对照、UTF-8 BOM 编码规范、`save_scope_as` 跨层失效规则、变量守卫等实测经验。
- 🔍 **静态脚本诊断校验器 (`validate_mod_snippet`)**：自动诊断大写 `ROOT/PREV`、废弃 `event_target`、本地化 `:0` 后缀、变量守卫误用等常见问题。
- 📦 **全库数据规模**：收录 **30,759 个条目**，索引键 **28,539 个**。

---

## 🚀 快速开始与配置

### 1. 安装依赖

```bash
git clone https://github.com/atri404/EU5-Modding-Mcp.git
cd EU5-Modding-Mcp
pip install -r requirements.txt
```

### 2. 配置 MCP 客户端

#### 在 Claude Code 中添加：
```bash
claude mcp add eu5-modding-mcp python -- /path/to/EU5-Modding-Mcp/server.py
```

#### 在 Claude Desktop / Cursor / Windsurf 的配置文件 (`claude_desktop_config.json`) 中：
```json
{
  "mcpServers": {
    "eu5-modding-mcp": {
      "command": "python",
      "args": ["<你的绝对路径>/EU5-Modding-Mcp/server.py"]
    }
  }
}
```

---

## 🛠️ MCP 工具列表 (16 个)

| 工具名称 | 作用说明 | 典型用途 |
| :--- | :--- | :--- |
| `search_by_name` | 全局跨库模糊/精确搜索 | 通配搜索任何名称、函数或关键词 |
| `search_modifiers` | 搜索修改器 (2,497 条) | 查 modifier 键名、作用范围 (category)、数值格式 |
| `search_effects` | 搜索游戏效果 (1,323 条) | 查 effect 语法签名及支持的 scopes |
| `search_triggers` | 搜索触发条件 (1,499 条) | 查 trigger 条件语法及支持的 scopes |
| `search_event_targets` | 搜索事件目标 (299 条，Bug已修) | 查作用域链链接（如 `capital`, `ruler`, `law_policy`） |
| `search_on_actions` | 搜索脉冲与事件挂钩 (159 条) | 查事件挂载点与期望执行的 scope |
| `search_custom_localization` | 搜索自定义本地化 (413 条) | 查动态文本替换函数及候选条目 |
| `search_field_definitions` | 搜索类目字段规范库 (103 篇) | 查指定类目的字段白名单及 1.4 更新 |
| `get_field_definition` | 获取单类目完整规范全文 | 如获取 `expedition_types`, `estates`, `building_types` |
| `search_vanilla_mechanics` | 搜索机制深度拆解 (24 篇) | 查各系统机制构成与硬编码边界 |
| `get_vanilla_mechanic` | 获取单机制系统深度解析 | 如获取 `army_movement`, `production_and_buildings` |
| `get_modding_pitfalls` | 查询实测避坑专题与 EU4 对照 | 查作用域坑、变量坑、BOM 规范、1.4 废弃接口 |
| `search_glossary` | 查标准中英双语术语表 (167 条) | 查对齐官方汉化的专业游戏术语 |
| `get_1_4_beta_summary` | 查询 1.4.0 公测版变更综述 | 快速获取测试版核心改动概览 |
| `validate_mod_snippet` | 离线静态诊断校验脚本片段 | 自动捕获 EU4 大写、废弃语法与隐藏 Bug |
| `get_statistics` | 查看全库数据统计明细 | 查询数据总览与分类分布 |

---

## 📚 MCP 资源列表 (14 个)

- `eu5://index` - 快速倒排定位索引
- `eu5://modifiers` - 全量修改器定义 (JSON)
- `eu5://effects` - 全量游戏效果 (JSON)
- `eu5://triggers` - 全量触发条件 (JSON)
- `eu5://event_targets` - 全量事件目标 (JSON)
- `eu5://on_actions` - 全量 on_actions 挂钩点 (JSON)
- `eu5://custom_loc` - 全量自定义本地化函数 (JSON)
- `eu5://fields` - 103 篇类目字段规范清单
- `eu5://mechanics` - 24 篇原版机制系统解析清单
- `eu5://pitfalls` - 实测避坑指南全文本
- `eu5://glossary` - 167 条标准中英术语表
- `eu5://1.4-beta/summary` - 1.4 测试版变更综述
- `eu5://statistics` - 全库详细统计报告
- `eu5://data_types/{category}` - Jomini 底层数据类型

---

## 🤝 致谢与数据来源

- 原版 MCP 服务实现架构：[@GlossMod](https://github.com/GlossMod/EU5-Modding-Mcp)
- 权威 EU5 知识库与 1.4 测试版实证数据：[@mrjiaobai-glitch/eu5-modding-kb](https://github.com/mrjiaobai-glitch/eu5-modding-kb)
- 游戏本体数据：Paradox Tinto & Paradox Interactive (Europa Universalis V)

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。
