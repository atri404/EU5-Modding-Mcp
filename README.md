# EU5 Modding Plugin & MCP Server (v2.1.0)

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Plugin Spec](https://img.shields.io/badge/Claude%20Plugin-compatible-purple)
![EU5 Version](https://img.shields.io/badge/EU5-1.3.x%20%2F%201.4%20Beta-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Entries](https://img.shields.io/badge/data%20entries-30%2C759-orange)
![License](https://img.shields.io/badge/license-MIT-green)

一个专为 **Europa Universalis V (欧陆风云 5 / Jomini 引擎)** 模组开发打造的 **Claude Code 一体化插件与 Model Context Protocol (MCP) 服务器**。

本项目仿照 Google 的 `chrome-devtools-mcp` 架构设计，**将 MCP 服务器、智能体技能 (Skills) 与 1.4-beta 深度知识库无缝绑定打包**：
- 🔌 **插件级生命周期管理**：在 `/plugin` 中启用此插件时，MCP 服务与全部开发技能**同时开启**；在 `/plugin` 中关闭时，二者**同时关闭**。
- 📚 **全量整合 `eu5-modding-kb` (1.4open_beta)**：内置 103 篇类目字段权威、24 篇机制系统拆解、18 个避坑实战专题及 167 条中英双语术语表。
- 🎯 **深度对齐 1.4.0 Open Beta**：包含新版远征系统（`expedition_types`）、独立阶层（`estates`）、军队战术机动与行军规则（`army-movement`）。
- 🛠️ **修复历史缺陷**：彻底修复原版事件目标解析 Bug（由 1 条恢复为 299 条），并将游戏修改器扩充至 **2,497 条**（融合拜占庭 DLC 与游戏本体实查）。
- 🔍 **内置静态诊断器**：在写代码时自动拦截 EU4 风格大写作用域（`ROOT`/`PREV`）、废弃 `event_target`、本地化 `:0` 后缀与变量守卫穿透。

---

## 🌟 核心特性概览

| 模块 | 规模 / 状态 | 特性说明 |
| :--- | :--- | :--- |
| **MCP 工具集** | 16 个工具 | 覆盖全库模糊检索、修改器、效果、触发器、事件目标、挂钩点、静态校验等 |
| **智能体技能 (Skills)** | 3 个打包技能 | `eu5-mod-dev` (开发制作)、`eu5-mod-review` (代码审查)、`eu5-mod-lookup` (机制查表) |
| **知识库文档 (kb/)** | 150+ 篇文档 | 103 篇字段白名单、24 篇机制深度解析、18 个避坑专题、167 条标准术语 |
| **游戏修改器** | 2,497 条 | 包含本体所有分类、布尔/百分比属性、颜色及适用范围 (Country/Location等) |
| **事件目标 (修复)** | 299 条 | 修复旧版单条压缩 Bug，完整提供 Input/Output Scopes |
| **on_actions** | 159 条 | 脉冲与事件挂钩点及执行作用域定义 |
| **自定义本地化** | 413 条 | 动态本地化函数及其候选条目列表 |
| **全库总条目** | 30,759 条 | 全局唯一索引键 28,539 个 |

---

## 🚀 快速安装与配置

### 方式一：作为 Claude Code 插件加载 (推荐，Skills + MCP 绑定)

你可以直接以插件形式启动 Claude Code 或将其安装至插件目录：

```bash
# 启动时直接挂载本插件目录
claude --plugin-dir "/path/to/EU5-Modding-Mcp"
```

加载后，Claude Code 会自动：
1. 启动并连接 `.claude-plugin/plugin.json` 中配置的 `eu5-modding-mcp` 服务；
2. 激活 `skills/` 中的 `eu5-mod-dev`、`eu5-mod-review`、`eu5-mod-lookup` 技能；
3. 当你使用 `/plugin disable eu5-modding` 关闭插件时，MCP 服务与技能将**同时关闭**。

---

### 方式二：单独作为 MCP 服务器配置

如果你只需要在 Claude Code、Claude Desktop、Cursor 或 Windsurf 中作为通用 MCP 服务运行：

#### 在 Claude Code 中添加：
```bash
claude mcp add eu5-modding-mcp python -- "/path/to/EU5-Modding-Mcp/server.py"
```

#### 在 Claude Desktop / Cursor 配置文件 (`claude_desktop_config.json`) 中：
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

## 🛠️ 打包技能 (Skills)

| 技能名称 | 对应文件 | 作用说明 |
| :--- | :--- | :--- |
| **`eu5-mod-dev`** | `skills/eu5-mod-dev/SKILL.md` | **Mod 制作全流程**：骨架搭建、加国家、任务树、法律政策、建筑商品、本地化 UTF-8 BOM 规范及合并策略 |
| **`eu5-mod-review`** | `skills/eu5-mod-review/SKILL.md` | **代码审查与排错**：6 级结构化代码审查、作用域链断裂检测、变量守卫核对，生成分级审查报告 |
| **`eu5-mod-lookup`** | `skills/eu5-mod-lookup/SKILL.md` | **机制与 API 智能查表**：快速检索 1.4 beta 变更、类目字段白名单、机制硬编码边界与官方中英术语 |

---

## 🔧 MCP 工具清单 (16 个)

- `search_by_name`：全库 30,759 条目综合模糊/精确搜索；
- `search_modifiers`：搜索 2,497 条修改器（支持 `category` 过滤）；
- `search_effects`：搜索 1,323 条游戏效果（支持 `scope` 过滤）；
- `search_triggers`：搜索 1,499 条触发条件（支持 `scope` 过滤）；
- `search_event_targets`：搜索 299 条事件目标（彻底修复旧版无法查询的问题）；
- `search_on_actions`：搜索 159 条 on_actions 脉冲挂钩点与作用域；
- `search_custom_localization`：搜索 413 条动态文本替换函数与候选键；
- `search_field_definitions`：搜索 103 篇类目字段规范；
- `get_field_definition`：获取指定类目的完整规范全文（如 `expedition_types`, `estates`, `laws`）；
- `search_vanilla_mechanics`：搜索 24 篇原版机制深度拆解；
- `get_vanilla_mechanic`：获取指定系统的机制深度解析（如 `army_movement`, `production_and_buildings`）；
- `get_modding_pitfalls`：查询实测踩坑指南与 EU4 对照（支持按主题过滤）；
- `search_glossary`：查询 167 条标准中英双语术语表；
- `get_1_4_beta_summary`：查询 1.4.0 公测版关键变更速览；
- `validate_mod_snippet`：对传入的代码片段进行静态诊断与纠错；
- `get_statistics`：获取全库统计明细。

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
├── kb/                    内置 1.4-beta 全量知识库
│   ├── fields/            103 篇类目字段白名单
│   ├── vanilla/           24 篇原版机制深度拆解
│   ├── guides/            12 篇教程与指南 (含新国家/任务链 E2E)
│   ├── cases/             4 篇实测排错案例
│   ├── tools/             5 篇查表工具
│   ├── pitfalls.md        实战避坑与 EU4 差异速查 (52KB)
│   ├── glossary.md        双语对照术语表 (167 条)
│   └── START-HERE.md      新手路线指引
├── mcp-data/              处理好的全量 JSON 数据文件 (30,759 条)
├── src/                   MCP 服务器核心源码 (data_handler, tools, resources)
├── scripts/               数据抽取与重建转换脚本 (convert_data.py)
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
