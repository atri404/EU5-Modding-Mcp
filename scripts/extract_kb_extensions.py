# coding: utf-8
"""
EU5 Modding MCP 扩展数据提取模块 (v2.3.0 / 1.4 Beta & 本地工坊深度完善版)
集成:
1. guides/*.md (12 篇教程)
2. cases/*.md (4 篇案例)
3. tools/error-log-decoder.md + 真实游戏引擎 C++ 报错特征库 (30+ 条报错诊断规则)
4. tools/audit-ids.md (ID 族总表：36 前缀族 + 9 裸写族)
5. tools/loc-keys.md (本地化键形态与缺键规则)
6. tools/review-checklist.md (7 维度机械审查清单)
7. guides/systems-map.md (137 个 common 类目地图)
8. guides/defines.md + 游戏本体 00_defines.txt / 00_gfx.txt 全量解析 (30 个 N 块与 1,450+ 常量)
9. START-HERE.md (从零上手路线与任务导览)
10. vanilla_readmes (提取游戏本体全部 74 篇官方开发者 readme.txt 规范)
11. mod_architecture_guide (EU5 三层生命周期架构、无冲突 sub-on-action 链、CMF 存储国与性能调优指南)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


def parse_kb_guides(kb_dir: Path) -> List[Dict[str, Any]]:
    guides_dir = kb_dir / "guides"
    results = []
    if not guides_dir.exists():
        return results

    for p in sorted(guides_dir.glob("*.md")):
        try:
            content = p.read_text(encoding="utf-8")
            first_line = content.split("\n")[0].replace("#", "").strip()
            summary_m = re.search(r">\s*\*\*一句话\*\*：(.*)", content)
            summary = summary_m.group(1).strip() if summary_m else ""
            when_m = re.search(r">\s*\*\*什么时候看\*\*：(.*)", content)
            when = when_m.group(1).strip() if when_m else ""

            sections = {}
            current_sec = "overview"
            sec_lines = []
            for line in content.split("\n"):
                if line.startswith("## "):
                    if sec_lines:
                        sections[current_sec] = "\n".join(sec_lines).strip()
                    current_sec = line.replace("## ", "").strip()
                    sec_lines = []
                else:
                    sec_lines.append(line)
            if sec_lines:
                sections[current_sec] = "\n".join(sec_lines).strip()

            results.append({
                "name": p.stem,
                "title": first_line,
                "summary": summary,
                "when_to_read": when,
                "file_name": p.name,
                "sections": sections,
                "content": content,
                "type": "guide"
            })
        except Exception as e:
            print(f"Error parsing guide {p}: {e}")
    return results


def parse_kb_cases(kb_dir: Path) -> List[Dict[str, Any]]:
    cases_dir = kb_dir / "cases"
    results = []
    if not cases_dir.exists():
        return results

    for p in sorted(cases_dir.glob("*.md")):
        try:
            content = p.read_text(encoding="utf-8")
            first_line = content.split("\n")[0].replace("#", "").strip()
            summary_m = re.search(r">\s*\*\*一句话\*\*：(.*)", content)
            summary = summary_m.group(1).strip() if summary_m else ""

            sections = {}
            current_sec = "overview"
            sec_lines = []
            for line in content.split("\n"):
                if line.startswith("## "):
                    if sec_lines:
                        sections[current_sec] = "\n".join(sec_lines).strip()
                    current_sec = line.replace("## ", "").strip()
                    sec_lines = []
                else:
                    sec_lines.append(line)
            if sec_lines:
                sections[current_sec] = "\n".join(sec_lines).strip()

            results.append({
                "name": p.stem,
                "title": first_line,
                "summary": summary,
                "file_name": p.name,
                "sections": sections,
                "content": content,
                "type": "modding_case"
            })
        except Exception as e:
            print(f"Error parsing case {p}: {e}")
    return results


def parse_kb_error_log_decoder(kb_dir: Path) -> Dict[str, Any]:
    eld_path = kb_dir / "tools" / "error-log-decoder.md"
    entries = []
    content = ""
    if eld_path.exists():
        content = eld_path.read_text(encoding="utf-8")
        current_section = "归属判断"
        for line in content.split("\n"):
            if line.startswith("## "):
                current_section = line.replace("## ", "").strip()
            elif line.strip().startswith("|") and not line.strip().startswith("|---"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 3 and parts[0] and not parts[0].startswith("报错串") and not parts[0].startswith("现象"):
                    pattern = parts[0]
                    cause = parts[1]
                    first_check = parts[2]
                    source = parts[3] if len(parts) > 3 else ""
                    entries.append({
                        "pattern": pattern,
                        "symptom": pattern,
                        "cause": cause,
                        "first_check": first_check,
                        "source": source,
                        "section": current_section
                    })

    # 扩充真实游戏运行与工坊排错中捕获的 C++ 引擎报错规则 (Real Engine Signatures)
    real_engine_signatures = [
        {
            "pattern": "Duplicate localization key. Key '...' is defined in both '...' and '...'",
            "symptom": "本地化键重复定义冲突 (Duplicate localization key)",
            "cause": "多个模组或模组与原版定义了完全同名的本地化键。Jomini 引擎会根据文件名字母序覆盖或因哈希顺序导致不可预期的文本显示",
            "first_check": "全局搜索冲突的键名；若是自定键应增加模组专属前缀 (如 mymod_)，若为有意覆盖原版需注意文件加载顺序",
            "source": "pdx_localize.cpp:221",
            "section": "本地化引擎"
        },
        {
            "pattern": "Localization key hash collision. Key '...' and '...' have the same hash",
            "symptom": "本地化键哈希碰撞 (Localization key hash collision)",
            "cause": "两个不同的本地化键在 Jomini 散列表中生成了完全相同的 32/64 位哈希值，导致界面取词错乱",
            "first_check": "微调其中一个键名（例如增加 _key 或修改下划线缩写）打破哈希冲突",
            "source": "pdx_localize.cpp:187",
            "section": "本地化引擎"
        },
        {
            "pattern": "Invalid character '...' in key name '...' at line N and column N",
            "symptom": "本地化键名包含非法字符 (Invalid character in key name)",
            "cause": "YAML 本地化文件的键名包含了空格、汉字、全角标点或非法符号。键名仅允许 ASCII 字母、数字和下划线",
            "first_check": "打开报错位置行号列号，删除键名中的空格或非法字符",
            "source": "localization_reader.cpp:445",
            "section": "本地化语法"
        },
        {
            "pattern": "Illegal localization break character (`) at line N and column N",
            "symptom": "本地化文本断行或特殊字符语法损坏 (Illegal break character)",
            "cause": "本地化字符串中使用了反引号 (`) 或未闭合的单双引号，破坏了 YAML 解析器规范",
            "first_check": "确保本地化文本使用双引号 \"...\" 完整包裹，移除反引号或转为标准样式标签 #bold ...#! 或 $...$",
            "source": "localization_reader.cpp:111",
            "section": "本地化语法"
        },
        {
            "pattern": "File '...' should be in utf8-bom encoding (will try to use it anyways)",
            "symptom": "文件缺失 UTF-8 BOM 签名 (Missing UTF-8 BOM)",
            "cause": "脚本或本地化文件被保存为普通 UTF-8 (无BOM) 或 ANSI/GBK 格式。Jomini lexer 严格要求 UTF-8 with BOM (EF BB BF)",
            "first_check": "在编辑器中另存为 'UTF-8 with BOM'，或使用 MCP 编码修复工具批量添加 BOM 签名",
            "source": "lexer.cpp:501",
            "section": "编码格式"
        },
        {
            "pattern": "Unlocalized text '...' at gui/..., either localize it or use the raw_text property",
            "symptom": "GUI 文本框直接使用未经本地化的裸字符串",
            "cause": "在 .gui 文件中直接写了 text = \"xxx\" 但 xxx 并非已定义的本地化键",
            "first_check": "若显示固定英文或调试文本，属性改为 raw_text = \"xxx\"；若需多语言支持，应改为本地化键并在 .yml 中提供翻译",
            "source": "pdx_gui_localize.cpp:182",
            "section": "GUI 规范"
        },
        {
            "pattern": "Widget cannot have a position in a layout",
            "symptom": "自动布局容器内的子组件包含绝对坐标 (position in layout)",
            "cause": "在 vbox, hbox, flowcontainer, dynamicgridbox 等自动布局容器内直接给子元素写了 position = { x y }",
            "first_check": "移除子组件上的 position 属性，改用 layoutpolicy_horizontal/vertical, margin, spacing 或外层包裹 container",
            "source": "pdx_gui_layout.cpp:201",
            "section": "GUI 规范"
        },
        {
            "pattern": "'...' is not a valid widget/type/property",
            "symptom": "GUI 组件类型或属性未定义/拼写错误",
            "cause": "在 .gui 中写了不存在的控件名（如误用 CK3/VIC3 特有组件）或向容器赋予了不支持的属性",
            "first_check": "核对 Jomini GUI 控件属性表，检查组件类型和属性拼写",
            "source": "pdx_gui_factory.cpp:624",
            "section": "GUI 规范"
        },
        {
            "pattern": "Unknown modifier type: ... It is either invalid, or a potential dynamic modifier",
            "symptom": "修改器名称不存在或使用了 EU4 废弃修改器",
            "cause": "脚本中引用了不存在的 modifier，典型如移植 EU4 时遗留的 great_power_score, army_reinforce_cost, exploration_maintenance_cost 等",
            "first_check": "调用 MCP search_modifiers 查询 EU5 对应的合法修改器（如 army_maintenance_cost, colony_maintenance_cost 等）",
            "source": "pdx_persistent_reader.cpp:289",
            "section": "修改器体系"
        },
        {
            "pattern": "Duplicate select_trigger target_flags in common/...",
            "symptom": "交互动作中的 select_trigger 目标标记重复",
            "cause": "在 country_interactions 或 character_interactions 中，多个 select_trigger 块使用了相同的 target_flag = <name>",
            "first_check": "确保交互动作中的每个 select_trigger 块拥有唯一的 target_flag 命名（如 recipient, secondary_actor, target_province 等）",
            "source": "interaction_target.cpp:3505",
            "section": "交互体系"
        },
        {
            "pattern": "The following two countries have the same name '...' & '...' = '...'",
            "symptom": "国家定义 TAG 或内部名称冲突",
            "cause": "setup/countries/ 或 common/countries/ 中两个文件定义了相同的国家 TAG 或内部标识符",
            "first_check": "确保自定国家 TAG 不与原版或其他模组冲突，检查 00_countries.txt 及历史文件",
            "source": "country_database.cpp:107",
            "section": "国家数据库"
        },
        {
            "pattern": "Trying to use ShowDBDefinitionName when there is no game state",
            "symptom": "在无活动游戏状态（主菜单阶段）调用了游戏内数据绑定",
            "cause": "在 main_menu/ 的 GUI 界面中引用了依赖运行中存档/国家的游戏内函数（如 GetPlayer, ShowDBDefinitionName）",
            "first_check": "仅在 in_game/gui/ 中使用游戏状态数据绑定，前端界面使用 [And(IsInGame, ...)] 进行条件守卫",
            "source": "data_factory_hooks.cpp:3272",
            "section": "数据绑定"
        }
    ]

    for sig in real_engine_signatures:
        if not any(e.get("pattern") == sig["pattern"] for e in entries):
            entries.append(sig)

    return {
        "title": "error.log 解码表（报错串 → 病因 → 首查点）",
        "entries": entries,
        "content": content,
        "type": "error_log_decoder"
    }


def parse_kb_id_rules(kb_dir: Path) -> Dict[str, Any]:
    aid_path = kb_dir / "tools" / "audit-ids.md"
    if not aid_path.exists():
        return {}

    content = aid_path.read_text(encoding="utf-8")
    prefixed_rules = []
    bare_rules = []
    special_rules = []
    mode = None

    for line in content.split("\n"):
        if "一、带前缀族" in line:
            mode = "prefix"
        elif "二、裸写法族" in line:
            mode = "bare"
        elif "三、角色与开局数据族" in line:
            mode = "special"
        elif line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3 and parts[0] and not parts[0].startswith("族"):
                item = {
                    "family": parts[0].replace("**", "").strip(),
                    "vanilla_scale": parts[1].strip(),
                    "rule": parts[2].strip(),
                    "source_doc": parts[3].strip() if len(parts) > 3 else ""
                }
                if mode == "prefix":
                    item["type"] = "prefixed"
                    prefixed_rules.append(item)
                elif mode == "bare":
                    item["type"] = "bare"
                    bare_rules.append(item)
                elif mode == "special":
                    item["type"] = "special"
                    special_rules.append(item)

    return {
        "title": "词条与 ID 存在性目录（ID 族总表：前缀族 vs 裸写族）",
        "prefixed_rules": prefixed_rules,
        "bare_rules": bare_rules,
        "special_rules": special_rules,
        "content": content,
        "type": "id_rules"
    }


def parse_kb_loc_rules(kb_dir: Path) -> Dict[str, Any]:
    loc_path = kb_dir / "tools" / "loc-keys.md"
    if not loc_path.exists():
        return {}

    content = loc_path.read_text(encoding="utf-8")
    sections = {}
    current_sec = "overview"
    sec_lines = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if sec_lines:
                sections[current_sec] = "\n".join(sec_lines).strip()
            current_sec = line.replace("## ", "").strip()
            sec_lines = []
        else:
            sec_lines.append(line)
    if sec_lines:
        sections[current_sec] = "\n".join(sec_lines).strip()

    return {
        "title": "本地化键形态总表与缺键排查规范",
        "sections": sections,
        "content": content,
        "type": "loc_rules"
    }


def parse_kb_review_checklist(kb_dir: Path) -> Dict[str, Any]:
    rc_path = kb_dir / "tools" / "review-checklist.md"
    if not rc_path.exists():
        return {}

    content = rc_path.read_text(encoding="utf-8")
    sections = {}
    current_sec = "overview"
    sec_lines = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if sec_lines:
                sections[current_sec] = "\n".join(sec_lines).strip()
            current_sec = line.replace("## ", "").strip()
            sec_lines = []
        else:
            sec_lines.append(line)
    if sec_lines:
        sections[current_sec] = "\n".join(sec_lines).strip()

    return {
        "title": "机械审查清单（7 级结构化检查 + 防误报白名单）",
        "sections": sections,
        "content": content,
        "type": "review_checklist"
    }


def parse_kb_systems_map(kb_dir: Path) -> Dict[str, Any]:
    sm_path = kb_dir / "guides" / "systems-map.md"
    if not sm_path.exists():
        return {}

    sm_content = sm_path.read_text(encoding="utf-8")
    categories = []
    current_group = "经济与生产"

    for line in sm_content.split("\n"):
        if line.startswith("## "):
            current_group = line.replace("## ", "").strip()
        elif line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3 and parts[0] and not parts[0].startswith("类目"):
                raw_cat = parts[0]
                has_readme = "[有readme]" in raw_cat
                cat_clean = raw_cat.replace("[有readme]", "").replace("[无readme]", "").strip()
                categories.append({
                    "category": cat_clean,
                    "has_readme": has_readme,
                    "purpose": parts[1],
                    "entry_file": parts[2],
                    "group": current_group
                })

    return {
        "title": "common 类目系统地图（160+ 类目全览）",
        "total_categories": len(categories),
        "categories": categories,
        "content": sm_content,
        "type": "systems_map"
    }


def parse_kb_and_vanilla_defines(kb_dir: Path, game_dir: Optional[Path] = None) -> Dict[str, Any]:
    def_path = kb_dir / "guides" / "defines.md"
    def_content = def_path.read_text(encoding="utf-8") if def_path.exists() else ""

    blocks_dict = {}
    constants_dict = {}

    # 1. 先从 kb 的 defines.md 提取
    mode = None
    for line in def_content.split("\n"):
        if "## 00_defines.txt 的 N 块索引" in line:
            mode = "blocks"
        elif "## 散落在其它 N 块里的" in line or "## 殖民与探索常量" in line:
            mode = "constants"
        elif line.startswith("## "):
            mode = "other"
        elif line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if mode == "blocks" and len(parts) >= 3 and parts[0] and not parts[0].startswith("块"):
                b_name = parts[0].replace("**", "").strip()
                blocks_dict[b_name] = {
                    "block": b_name,
                    "line_range": parts[1].strip(),
                    "content": parts[2].strip()
                }
            elif mode == "constants" and len(parts) >= 4 and parts[0] and not parts[0].startswith("常量"):
                c_name = parts[0].replace("**", "").replace("`", "").strip()
                constants_dict[c_name] = {
                    "constant": c_name,
                    "value": parts[1].replace("**", "").strip(),
                    "location": parts[2].strip(),
                    "description": parts[3].strip()
                }

    # 2. 从本体 00_defines.txt 和 00_gfx.txt 进行完整提取
    if game_dir and game_dir.exists():
        defines_files = [
            game_dir / "loading_screen" / "common" / "defines" / "00_defines.txt",
            game_dir / "loading_screen" / "gfx" / "defines" / "00_gfx.txt"
        ]
        for df in defines_files:
            if not df.exists():
                continue
            lines = df.read_text(encoding="utf-8", errors="replace").splitlines()
            current_block = None
            block_start = 1
            for idx, line in enumerate(lines, start=1):
                m_block = re.match(r'^([A-Z][A-Za-z0-9_]+)\s*=\s*\{', line)
                if m_block:
                    current_block = m_block.group(1)
                    block_start = idx
                    if current_block not in blocks_dict:
                        blocks_dict[current_block] = {
                            "block": current_block,
                            "line_range": f"{idx}-",
                            "content": f"{current_block} 引擎核心定义块"
                        }
                    continue

                if current_block:
                    if re.match(r'^\}', line.strip()):
                        if current_block in blocks_dict and "-" in blocks_dict[current_block]["line_range"]:
                            blocks_dict[current_block]["line_range"] = f"{block_start}-{idx}"
                        current_block = None
                        continue

                    m_const = re.match(r'^\s*([A-Z0-9_]{3,})\s*=\s*([^#\n]+)(?:#(.*))?', line)
                    if m_const:
                        c_name = m_const.group(1).strip()
                        c_val = m_const.group(2).strip()
                        c_comment = (m_const.group(3) or "").strip()
                        if c_name not in constants_dict:
                            constants_dict[c_name] = {
                                "constant": c_name,
                                "value": c_val,
                                "location": current_block,
                                "description": c_comment or f"{current_block} 引擎定义常量",
                                "line": idx
                            }

    # 从各个 N 块的 content 中补充常量
    for b in blocks_dict.values():
        b_name = b.get("block", "")
        b_content = b.get("content", "")
        pairs = re.findall(r'([A-Z0-9_]{3,})\s*=\s*([^\s、，；]+)', b_content)
        for k, v in pairs:
            if k not in constants_dict:
                constants_dict[k] = {
                    "constant": k,
                    "value": v,
                    "location": b_name,
                    "description": f"{b_name} 关键定义常量"
                }

    return {
        "title": "Defines 体系与 00_defines.txt 常量索引（含本体与KB完整聚合）",
        "blocks": list(blocks_dict.values()),
        "constants": list(constants_dict.values()),
        "content": def_content,
        "type": "engine_defines"
    }


def parse_vanilla_readmes(game_dir: Path) -> List[Dict[str, Any]]:
    """提取游戏本体所有 74 份官方开发者 readme.txt 规范"""
    results = []
    if not game_dir or not game_dir.exists():
        return results

    for p in sorted(game_dir.rglob("*readme*")):
        if p.is_file() and p.suffix in [".txt", ".info"]:
            try:
                content = p.read_text(encoding="utf-8", errors="replace").strip()
                rel_path = p.relative_to(game_dir).as_posix()
                cat_name = p.parent.name
                first_line = content.split("\n")[0].strip() if content else ""
                results.append({
                    "name": cat_name,
                    "category": cat_name,
                    "path": rel_path,
                    "summary": first_line[:120],
                    "content_length": len(content),
                    "content": content,
                    "type": "vanilla_readme"
                })
            except Exception as e:
                print(f"Error reading readme {p}: {e}")
    return results


def generate_mod_architecture_guide() -> Dict[str, Any]:
    """生成 EU5 三层生命周期架构、工坊 CMF 规范与最佳实践指南"""
    return {
        "title": "EU5 模组架构体系与创意工坊实践指南 (3-Tier Lifecycle Architecture)",
        "version": "1.4.0-compatible",
        "lifecycle_tiers": {
            "loading_screen": {
                "purpose": "引擎启动与全局引导层 (Boot & Initialization)",
                "critical_paths": [
                    "loading_screen/common/defines/00_defines.txt (所有全局宏、AI、战斗、经济常量必须放此处)",
                    "loading_screen/gfx/defines/00_gfx.txt (摄像机 NCamera 配置)",
                    "loading_screen/data_binding/ (全局数据绑定宏，如 CMF 跨模组宏)",
                    "loading_screen/input_profile/ (*.profile 按键绑定映射)",
                    "loading_screen/fonts/ (全局字体与字形配置)"
                ],
                "pitfall": "严禁将 00_defines.txt 误放入根目录 common/defines/，否则引擎完全静默忽略！"
            },
            "main_menu": {
                "purpose": "前端界面与全局静态数据库 (Frontend & Global DB)",
                "critical_paths": [
                    "main_menu/common/static_modifiers/ (全局国家、行省、难度静态修正)",
                    "main_menu/common/achievements/ (成就体系定义)",
                    "main_menu/gui/ (主菜单、选国界面、大厅等前端控件)",
                    "main_menu/localization/ (前端及全局通用本地化)",
                    "main_menu/setup/start/ (开局全局初始化设置)"
                ],
                "pitfall": "禁止在 main_menu 阶段调用依赖活动存档的数据函数 (如 GetPlayer, ShowDBDefinitionName)，会导致 Trying to use ... when there is no game state 崩溃"
            },
            "in_game": {
                "purpose": "运行时游戏玩法模拟层 (Gameplay Simulation)",
                "critical_paths": [
                    "in_game/common/ (全部 124 个玩法类目：advances, building_types, laws, generic_actions, country_interactions 等)",
                    "in_game/events/ (国家、角色、灾难、局势等事件)",
                    "in_game/gui/ (游戏内 HUD、lateralview、脚本组件)",
                    "in_game/localization/ (游戏内事件、任务、修正描述本地化)",
                    "in_game/map_data/ (地图投影、河流、地块)",
                    "in_game/setup/ (历史剧本、国家开局数据、省份人口分布)"
                ],
                "pitfall": "玩法逻辑严禁散落至 main_menu 或根目录；common 和 events 必须置于 in_game/ 下"
            }
        },
        "best_practices": {
            "sub_on_action_chaining": {
                "pattern": "无冲突 Sub-on-action 链式挂载",
                "description": "严禁直接使用 on_game_start = { effect = { ... } }，否则会完全覆盖原版和其他模组的初始化逻辑。应使用 on_actions 嵌套子动作：\n"
                             "on_game_start = { on_actions = { mymod_init_hook } }\n"
                             "mymod_init_hook = { effect = { ... } }"
            },
            "storage_country": {
                "pattern": "CMF 虚拟存储国机制 (Storage Country)",
                "description": "由于全局变量表在跨网络或重载时可能存在作用域穿透问题，大型工坊模组（如 CMF）在 setup/countries/ 定义无地虚拟存储国 (如 c:CMF)，用于全局数据、配置选项与异步任务队列的安全存取。"
            },
            "scripted_gui_actionbar": {
                "pattern": "动态脚本化 GUI 注入",
                "description": "通过 scripted_widgets 与 scripted_guis 在不替换原版 topbar 文件的原则下，将自定义功能栏安全注入到 foreign_country_lateralview 或 ingame_topbar。"
            },
            "performance_tuning": {
                "pattern": "Faster Universalis 级引擎性能优化常量",
                "key_defines": [
                    "AI_PERFORMANCE_EVALUATE_MARKET_RATIO_PER_BUILDING = 0.02 (降低巨型市场建筑穷举频率)",
                    "AI_PERFORMANCE_CABINET_ACTION_MONTHS_BETWEEN_UPDATES = 72 (拉长内阁动作评估周期)",
                    "AI_CONSTRUCTION_QUEUE_PARALLEL_CHECK_MAX = 30 (硬性约束 AI 每月建筑评估峰值)",
                    "AI_PERFORMANCE_PATHFIND_DISTANCE_THRESHOLD = 50 (缩减非必要路径寻路精度)",
                    "CARPET_SIEGE_SEARCH_DEPTHS = { 5 4 3 2 2 2 2 2 1 1 1 1 1 1 1 1 1 1 } (地毯式围城寻路步长限制)"
                ]
            }
        },
        "type": "mod_architecture_guide"
    }


def parse_kb_start_here(kb_dir: Path) -> Dict[str, Any]:
    sh_path = kb_dir / "START-HERE.md"
    if not sh_path.exists():
        return {}

    content = sh_path.read_text(encoding="utf-8")
    sections = {}
    curr_s = "overview"
    s_lines = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if s_lines:
                sections[curr_s] = "\n".join(s_lines).strip()
            curr_s = line.replace("## ", "").strip()
            s_lines = []
        else:
            s_lines.append(line)
    if s_lines:
        sections[curr_s] = "\n".join(s_lines).strip()

    return {
        "title": "从这里开始（新手路线与任务速查）",
        "sections": sections,
        "content": content,
        "type": "start_here"
    }


def convert_all_kb_extensions(kb_dir: Path, output_dir: Path, game_dir: Optional[Path] = None) -> Dict[str, Any]:
    print("\n📚 提取 eu5-modding-kb 与本体全量扩展数据 (Guides/Cases/Tools/Defines/Readmes/Architecture)...")

    guides = parse_kb_guides(kb_dir)
    with open(output_dir / "guides.json", "w", encoding="utf-8") as f:
        json.dump(guides, f, ensure_ascii=False, indent=2)
    print(f"  ✓ guides.json: {len(guides)} 篇制作指南与实战教程")

    cases = parse_kb_cases(kb_dir)
    with open(output_dir / "modding_cases.json", "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    print(f"  ✓ modding_cases.json: {len(cases)} 篇实操案例复盘")

    error_log_decoder = parse_kb_error_log_decoder(kb_dir)
    with open(output_dir / "error_log_decoder.json", "w", encoding="utf-8") as f:
        json.dump(error_log_decoder, f, ensure_ascii=False, indent=2)
    print(f"  ✓ error_log_decoder.json: 包含 {len(error_log_decoder.get('entries', []))} 条权威报错排查规则 (含真实C++引擎签名)")

    id_rules = parse_kb_id_rules(kb_dir)
    with open(output_dir / "id_rules.json", "w", encoding="utf-8") as f:
        json.dump(id_rules, f, ensure_ascii=False, indent=2)
    print(f"  ✓ id_rules.json: 包含 {len(id_rules.get('prefixed_rules', []))} 前缀族 + {len(id_rules.get('bare_rules', []))} 裸写族规范")

    loc_rules = parse_kb_loc_rules(kb_dir)
    with open(output_dir / "loc_rules.json", "w", encoding="utf-8") as f:
        json.dump(loc_rules, f, ensure_ascii=False, indent=2)
    print(f"  ✓ loc_rules.json: 包含 {len(loc_rules.get('sections', {}))} 类目本地化形态与缺键规则")

    review_checklist = parse_kb_review_checklist(kb_dir)
    with open(output_dir / "review_checklist.json", "w", encoding="utf-8") as f:
        json.dump(review_checklist, f, ensure_ascii=False, indent=2)
    print(f"  ✓ review_checklist.json: 包含 {len(review_checklist.get('sections', {}))} 维度机械审查项")

    systems_map = parse_kb_systems_map(kb_dir)
    with open(output_dir / "systems_map.json", "w", encoding="utf-8") as f:
        json.dump(systems_map, f, ensure_ascii=False, indent=2)
    print(f"  ✓ systems_map.json: 包含 {systems_map.get('total_categories', 0)} 个 common 类目入口地图")

    engine_defines = parse_kb_and_vanilla_defines(kb_dir, game_dir)
    with open(output_dir / "engine_defines.json", "w", encoding="utf-8") as f:
        json.dump(engine_defines, f, ensure_ascii=False, indent=2)
    print(f"  ✓ engine_defines.json: 包含 {len(engine_defines.get('blocks', []))} 个 N 块与 {len(engine_defines.get('constants', []))} 个核心常量 (全量提取游戏本体 00_defines.txt)")

    start_here = parse_kb_start_here(kb_dir)
    with open(output_dir / "start_here.json", "w", encoding="utf-8") as f:
        json.dump(start_here, f, ensure_ascii=False, indent=2)
    print("  ✓ start_here.json: 新手任务与上手导引")

    vanilla_readmes = parse_vanilla_readmes(game_dir) if game_dir else []
    with open(output_dir / "vanilla_readmes.json", "w", encoding="utf-8") as f:
        json.dump(vanilla_readmes, f, ensure_ascii=False, indent=2)
    print(f"  ✓ vanilla_readmes.json: 包含 {len(vanilla_readmes)} 份官方开发者 readme.txt 规范")

    mod_architecture = generate_mod_architecture_guide()
    with open(output_dir / "mod_architecture_guide.json", "w", encoding="utf-8") as f:
        json.dump(mod_architecture, f, ensure_ascii=False, indent=2)
    print("  ✓ mod_architecture_guide.json: EU5 三层生命周期架构与工坊实践指南")

    return {
        "guides": guides,
        "cases": cases,
        "error_log_decoder": error_log_decoder,
        "id_rules": id_rules,
        "loc_rules": loc_rules,
        "review_checklist": review_checklist,
        "systems_map": systems_map,
        "engine_defines": engine_defines,
        "start_here": start_here,
        "vanilla_readmes": vanilla_readmes,
        "mod_architecture": mod_architecture
    }
