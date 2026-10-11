# EU5 Modding Plugin & MCP Server (v2.2.0)

![Version](https://img.shields.io/badge/version-2.2.0-blue)
![Plugin Spec](https://img.shields.io/badge/Claude%20Plugin-compatible-purple)
![EU5 Version](https://img.shields.io/badge/EU5-1.3.x%20%2F%201.4%20Beta-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Entries](https://img.shields.io/badge/data%20entries-30%2C775-orange)
![License](https://img.shields.io/badge/license-MIT-green)

一个专为 **Europa Universalis V (欧陆风云 5 / Jomini 引擎)** 模组开发打造的 **Claude Code 一体化插件与 Model Context Protocol (MCP) 服务器**。

本项目仿照 Google 官方的 `chrome-devtools-mcp` 架构设计，**将 MCP 服务器、智能体技能 (Skills) 与 1.4-beta 全量权威知识库无缝绑定打包**：
- 🔌 **插件级生命周期管理**：在 `/plugin` 中启用此插件时，MCP 服务与全部开发技能**同时开启**；在 `/plugin` 中关闭时，二者**同时安全关闭**。
- 📚 **100% 全量深度整合 `eu5-modding-kb` (1.4open_beta)**：内置全部 156 篇权威文档（103 篇字段规范、24 篇机制拆解、12 篇实操教程、4 篇实测案例、5 篇查表工具、18 篇避坑专题与 167 条中英双语术语表）。
- 🎯 **深度对齐 1.4.0 Open Beta**：包含新版远征系统（`expedition_types`）、独立阶层（`estates`）、军队战术机动与行军规则（`army-movement`）。
- 🛠️ **修复历史缺陷**：彻底修复原版事件目标解析 Bug（由 1 条恢复为 299 条），并将游戏修改器扩充至 **2,497 条**（融合拜占庭 DLC 与游戏本体实查）。
- 🔍 **超级静态诊断校验器**：自动拦截花括号不平衡、EU4 风格大写作用域（`ROOT`/`PREV`）、废弃 `event_target`、本地化 `:0` 后缀、错误 building:/unit_category: 前缀、法规 potential 周期撤销陷阱、灾难无限重入死循环。
- 🩺 **error.log 智能解码器**：输入报错日志行自动分析典型病因、首查点与解决建议。
- 🚑 **GBK/UTF-8 乱码智能抢救器**：基于实测 A 类乱码回环算法自动抢救因 ANSI/GBK 误读导致的损坏中文（如 `鍚堝悓` -> `合同`）。

---

## 🌟 核心特性概览

| 模块 | 规模 / 状态 | 特性说明 |
| :--- | :--- | :--- |
| **MCP 工具集** | **30 个工具** | 覆盖全库检索、修改器、效果、触发器、事件目标、挂钩点、教程、案例、error.log解码、ID族规则、本地化规范、系统地图、Defines索引、静态诊断与乱码抢救 |
| **MCP 只读资源** | **23 项资源 (`eu5://`)** | 提供 index, modifiers, effects, triggers, event_targets, fields, mechanics, guides, cases, error_decoder, id_rules, loc_rules, checklist, systems_map, defines 等只读资源 |
| **智能体技能 (Skills)** | 3 个打包技能 | `eu5-mod-dev` (开发制作)、`eu5-mod-review` (代码审查与排错)、`eu5-mod-lookup` (机制查表) |
| **知识库文档 (kb/)** | **156 篇全量文档** | 103 篇字段白名单、24 篇机制深度解析、12 篇实战教程、4 篇真实案例、5 篇查表工具、18 个避坑专题、167 条标准术语 |
| **游戏修改器** | 2,497 条 | 包含本体所有分类、布尔/百分比属性、颜色及适用范围 (Country/Location等) |
| **事件目标 (修复)** | 299 条 | 修复旧版单条压缩 Bug，完整提供 Input/Output Scopes |
| **on_actions** | 159 条 | 脉冲与事件挂钩点及执行作用域定义 |
| **自定义本地化** | 413 条 | 动态本地化函数及其候选条目列表 |
| **common 系统地图** | 137 个类目 | 涵盖 in_game/common 全部类目的入口文件、官方 readme 状态与功能分组 |
| **00_defines 常量** | 17 块 / 77 常量 | 覆盖 NAI, NCombat, NUnit, NPop, NEstate, NColony 等关键常量数值与行区间 |
| **全库总条目** | **30,775 条** | 全局唯一索引键 28,555 个 |

---

## 🚀 快速安装与配置

### 方式一：作为 Claude Code 插件加载 (推荐，Skills + MCP 强绑定)

在启动 Claude Code 时直接挂载本仓库目录：

```bash
# 启动时直接挂载本插件目录
claude --plugin-dir "D:\eu5mods\EU5-Modding-Mcp"
```

加载后，Claude Code 会自动：
1. 启动并连接 `.claude-plugin/plugin.json` 中配置的 `eu5-modding-mcp` 服务（30 个工具与 23 项资源即开即用）；
2. 激活 `skills/` 中的 `eu5-mod-dev`、`eu5-mod-review`、`eu5-mod-lookup` 技能；
3. 当你在终端中输入 `/plugin disable eu5-modding` 关闭插件时，MCP 服务与全部技能将**同时安全卸载**。

---

### 方式二：单独作为 MCP 服务器配置

如果你需要在其它环境（如 Claude Desktop、Cursor 或 Windsurf）中作为独立 MCP 服务器使用：

#### 在 Claude Code 中注册：
```bash
claude mcp add eu5-modding-mcp "C:\Users\杨洋\AppData\Local\Programs\Python\Python312\python.exe" -- "D:\eu5mods\EU5-Modding-Mcp\server.py"
```

#### 在 Claude Desktop / Cursor 配置文件 (`claude_desktop_config.json`) 中：
```json
{
  "mcpServers": {
    "eu5-modding-mcp": {
      "command": "C:\\Users\\杨洋\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": ["D:\\eu5mods\\EU5-Modding-Mcp\\server.py"]
    }
  }
}
```

---

## 🛠️ 打包技能 (Skills)

| 技能名称 | 对应文件 | 作用说明 |
| :--- | :--- | :--- |
| **`eu5-mod-dev`** | `skills/eu5-mod-dev/SKILL.md` | **Mod 制作全流程**：骨架搭建、加国家、任务树、法律政策、建筑商品、本地化 UTF-8 BOM 规范、合并策略及 Defines 常量配置 |
| **`eu5-mod-review`** | `skills/eu5-mod-review/SKILL.md` | **代码审查与排错**：7 级结构化代码审查、error.log 日志诊断、ID 族引用核查、法规撤销陷阱、乱码抢救与白名单排除 |
| **`eu5-mod-lookup`** | `skills/eu5-mod-lookup/SKILL.md` | **机制与 API 智能查表**：快速检索 1.4 beta 变更、类目字段白名单、机制硬编码边界、制作教程与官方中英术语 |

---

## 🔧 MCP 工具清单 (共 30 个)

### 1. 基础与综合检索
- `search_by_name`：全库 30,775 条目综合模糊/精确搜索；
- `search_modifiers`：搜索 2,497 条修改器（支持 `category` 过滤）；
- `search_effects`：搜索 1,323 条游戏效果（支持 `scope` 过滤）；
- `search_triggers`：搜索 1,499 条触发条件（支持 `scope` 过滤）；
- `search_event_targets`：搜索 299 条事件目标（带完整作用域）；
- `search_on_actions`：搜索 159 条 on_actions 挂钩点；
- `search_custom_localization`：搜索 413 条动态文本函数；

### 2. 字段规范与机制拆解
- `search_field_definitions`：搜索 103 篇类目字段规范；
- `get_field_definition`：获取指定类目完整规范全文（如 `expedition_types`, `estates`, `laws`）；
- `search_vanilla_mechanics`：搜索 24 篇原版机制深度拆解；
- `get_vanilla_mechanic`：获取指定机制系统的深度解析（如 `army_movement`, `production_and_buildings`）；

### 3. 指南、教程与实战复盘
- `search_guides`：搜索 12 篇制作指南与端到端实操教程；
- `get_guide`：获取指定制作指南或教程全文（如 `new-country-tutorial`, `new-mission-pack-tutorial`, `merging`, `law-design`）；
- `search_modding_cases`：搜索 4 篇实操排错案例复盘；
- `get_modding_case`：获取指定案例全文（如 `encoding-corruption-2026-10`, `laws-events-and-estates-2026-09`）；

### 4. 诊断、查表与实用工具箱
- `decode_error_log`：error.log 智能解码器（输入报错行自动匹配病因与首查点）；
- `search_id_rules`：查询全游戏 ID 族引用规则（前缀族 vs 裸写族）；
- `get_id_rule`：获取特定 ID 族的权威写法（避免静默失效）；
- `get_loc_key_rules`：查询事件、任务、修正等本地化键形态表与缺键排查原则；
- `get_review_checklist`：获取 7 维度结构化审查清单与防误报白名单；
- `get_systems_map`：查询 137 个 common 类目入口地图与 readme 状态；
- `search_defines`：检索 00_defines.txt 常量索引与数值；
- `get_define_block`：获取指定 N 块的行区间与主要常量；
- `get_newbie_guide`：获取从零开始新手路线与按任务速查表；
- `recover_corrupted_encoding`：GBK/UTF-8 A 类乱码智能回环抢救器；

### 5. 校验、术语与版本
- `validate_mod_snippet`：超级模组脚本静态诊断校验器；
- `get_modding_pitfalls`：查询避坑指南与 EU4 对照全集；
- `search_glossary`：查询 167 条中英双语标准术语表；
- `get_1_4_beta_summary`：获取 1.4.0 公测版关键变更速览；
- `get_statistics`：获取全库统计明细与知识库覆盖率。

---

## 📚 目录结构

```
EU5-Modding-Mcp/
├── .claude-plugin/        Claude Code 插件配置 (plugin.json)
├── .cursor-plugin/        Cursor 插件配置 (plugin.json)
├── plugin.json            Agent Plugins 国际标准清单
├── skills/                随插件绑定的三大智能体技能
│   ├── eu5-mod-dev/       模组制作全流程技能
│   ├── eu5-mod-review/    模组代码审查与排错技能
│   └── eu5-mod-lookup/    机制与 API 智能查表技能
├── kb/                    内置 1.4-beta 全量 156 篇知识库
│   ├── fields/            103 篇类目字段白名单
│   ├── vanilla/           24 篇原版机制深度拆解
│   ├── guides/            12 篇教程与指南 (含新国家/任务链 E2E)
│   ├── cases/             4 篇实测排错案例
│   ├── tools/             5 篇查表工具
│   ├── pitfalls.md        实战避坑与 EU4 差异速查 (52KB)
│   ├── glossary.md        双语对照术语表 (167 条)
│   └── START-HERE.md      新手路线指引
├── mcp-data/              处理好的全量 JSON 数据文件 (30,775 条)
├── src/                   MCP 服务器核心源码 (data_handler, tools, resources)
├── scripts/               数据抽取与重建转换脚本 (convert_data.py, extract_kb_extensions.py)
├── tests/                 完整功能测试套件 (test_implementation.py)
├── server.py              MCP 服务器入口
├── pyproject.toml         包与依赖配置
└── README.md              项目说明文档
```

---

## 🤝 致谢与致敬

- 原版 MCP 服务实现架构：[@GlossMod](https://github.com/GlossMod/EU5-Modding-Mcp)
- 权威 EU5 知识库与 1.4 测试版实证数据：[@mrjiaobai-glitch/eu5-modding-kb](https://github.com/mrjiaobai-glitch/eu5-modding-kb)
- 游戏本体数据：Paradox Tinto & Paradox Interactive (Europa Universalis V)

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。
