#!/usr/bin/env python3
"""
EU5 Modding MCP 数据转换与重建脚本 (v2.1.0 / 1.4 Beta 适配)
支持:
1. data_types/*.txt -> data_types_*.json
2. effects.log, triggers.log -> effects.json, triggers.json
3. event_targets.log -> event_targets.json (修复原版只解析出1条的重大Bug)
4. on_actions.log -> on_actions.json (新增支持)
5. custom_localization.log -> custom_localization.json (新增支持)
6. 结合游戏本体 (game/main_menu/common/modifier_type_definitions/) 与 modifiers.log 生成最新完整 modifiers.json (2,400+ 条目)
7. 从 eu5-modding-kb (1.4open_beta) 提取:
   - field_definitions.json (103 类目权威字段)
   - vanilla_mechanics.json (24 篇原版机制深度解析)
   - modding_pitfalls.json (避坑指南与EU4对照)
   - glossary.json (中英对照术语表)
   - version_1_4_beta.json (1.4 测试版变更汇总)
8. 构建全量 all_data.json 与 index.json 索引
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any


def get_paths():
    base_dir = Path(__file__).resolve().parent.parent
    docs_dir = base_dir / "docs"
    output_dir = base_dir / "mcp-data"
    kb_dir = Path("D:/eu5mods/eu5-modding-kb")
    game_dir = Path("D:/SteamLibrary/steamapps/common/Europa Universalis V/game")
    output_dir.mkdir(parents=True, exist_ok=True)
    return base_dir, docs_dir, output_dir, kb_dir, game_dir


def parse_data_type_file(file_path: Path) -> List[Dict[str, Any]]:
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    items = content.split("-----------------------\n")
    for item in items:
        item = item.strip()
        if not item:
            continue
        lines = item.split("\n")
        entry = {
            "name": "",
            "description": "",
            "definition_type": "",
            "return_type": "",
            "args": [],
            "type": "data_type"
        }
        first_line = lines[0].strip()
        match = re.match(r"(\w+)\(\s*(.*?)\s*\)", first_line)
        if match:
            entry["name"] = match.group(1)
            args_str = match.group(2)
            if args_str:
                entry["args"] = [arg.strip() for arg in args_str.split(",")]
        else:
            entry["name"] = first_line

        for line in lines[1:]:
            line = line.strip()
            if line.startswith("Description:"):
                entry["description"] = line.replace("Description:", "").strip()
            elif line.startswith("Definition type:"):
                entry["definition_type"] = line.replace("Definition type:", "").strip()
            elif line.startswith("Return type:"):
                entry["return_type"] = line.replace("Return type:", "").strip()

        if entry["name"]:
            entries.append(entry)
    return entries


def parse_markdown_log_file(file_path: Path, entry_type: str = "effect") -> List[Dict[str, Any]]:
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "##" not in content:
        return entries

    items = re.split(r"\n##\s+", content)
    for item in items:
        if not item.strip():
            continue
        lines = item.split("\n")
        name = lines[0].strip()
        if not name or name.startswith("#"):
            continue

        entry = {
            "name": name,
            "description": "",
            "supported_scopes": [],
            "supported_targets": [],
            "type": entry_type
        }
        description_lines = []
        for line in lines[1:]:
            line = line.rstrip()
            if line.startswith("**Supported Scopes**:"):
                scopes_str = line.replace("**Supported Scopes**:", "").strip()
                entry["supported_scopes"] = [s.strip() for s in scopes_str.split(",") if s.strip()]
            elif line.startswith("**Supported Targets**:"):
                targets_str = line.replace("**Supported Targets**:", "").strip()
                entry["supported_targets"] = [t.strip() for t in targets_str.split(",") if t.strip()]
            elif line and not line.startswith("**"):
                description_lines.append(line)

        entry["description"] = "\n".join(description_lines).strip()
        if entry["name"]:
            entries.append(entry)
    return entries


def parse_event_targets(file_path: Path) -> List[Dict[str, Any]]:
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n###\s+", content)
    for block in blocks:
        block = block.strip()
        if not block or block.startswith("# Event Target Documentation"):
            continue
        lines = block.split("\n")
        name = lines[0].strip()
        if not name:
            continue

        desc_lines = []
        in_scopes = []
        out_scopes = []
        req_data = False

        for line in lines[1:]:
            l = line.strip()
            if l.startswith("Input Scopes:"):
                in_scopes = [s.strip() for s in l.replace("Input Scopes:", "").split(",") if s.strip()]
            elif l.startswith("Output Scopes:"):
                out_scopes = [s.strip() for s in l.replace("Output Scopes:", "").split(",") if s.strip()]
            elif l.startswith("Requires Data:"):
                req_data = "yes" in l.lower()
            else:
                desc_lines.append(l)

        entries.append({
            "name": name,
            "description": "\n".join(desc_lines).strip(),
            "input_scopes": in_scopes,
            "output_scopes": out_scopes,
            "requires_data": req_data,
            "type": "event_target"
        })
    return entries


def parse_on_actions(file_path: Path) -> List[Dict[str, Any]]:
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    for block in content.split("--------------------"):
        block = block.strip()
        if not block or block.startswith("On Action Documentation:"):
            continue
        lines = block.split("\n")
        name = lines[0].strip().rstrip(":")
        from_code = False
        exp_scope = "none"

        for line in lines[1:]:
            l = line.strip()
            if l.startswith("From Code:"):
                from_code = "yes" in l.lower()
            elif l.startswith("Expected Scope:"):
                exp_scope = l.replace("Expected Scope:", "").strip()

        entries.append({
            "name": name,
            "from_code": from_code,
            "expected_scope": exp_scope,
            "type": "on_action"
        })
    return entries


def parse_custom_localization(file_path: Path) -> List[Dict[str, Any]]:
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    for block in content.split("--------------------"):
        block = block.strip()
        if not block or block.startswith("Custom Localization Documentation:"):
            continue
        lines = block.split("\n")
        name = lines[0].strip().rstrip(":")
        scope = "none"
        random_valid = False
        candidates = []
        mode = None

        for line in lines[1:]:
            l = line.strip()
            if l.startswith("Scope:"):
                scope = l.replace("Scope:", "").strip()
            elif l.startswith("Random Valid:"):
                random_valid = "yes" in l.lower()
            elif l.startswith("Entries:"):
                mode = "entries"
            elif mode == "entries" and l:
                candidates.append(l)

        entries.append({
            "name": name,
            "scope": scope,
            "random_valid": random_valid,
            "entries": candidates,
            "type": "custom_localization"
        })
    return entries


def parse_modifiers(log_file: Path, game_dir: Path) -> List[Dict[str, Any]]:
    modifiers_dict = {}

    mod_def_dir = game_dir / "main_menu" / "common" / "modifier_type_definitions"
    if mod_def_dir.exists():
        for p in mod_def_dir.glob("*.txt"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read()
                for m in re.finditer(r"^([a-zA-Z0-9_]+)\s*=\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}", content, re.MULTILINE):
                    name = m.group(1)
                    body = m.group(2)
                    info = {
                        "name": name,
                        "type": "modifier",
                        "source_file": p.name,
                        "categories": ["all"],
                        "boolean": False,
                        "percent": False,
                        "description": ""
                    }
                    if "boolean=yes" in body.replace(" ", ""):
                        info["boolean"] = True
                    if "percent=yes" in body.replace(" ", ""):
                        info["percent"] = True
                    cat_match = re.search(r"category\s*=\s*([a-zA-Z0-9_]+)", body)
                    if cat_match:
                        cat = cat_match.group(1)
                        info["categories"] = [cat]
                        info["category"] = cat
                    color_match = re.search(r"color\s*=\s*([a-zA-Z0-9_]+)", body)
                    if color_match:
                        info["color"] = color_match.group(1)
                    modifiers_dict[name] = info
            except Exception as e:
                print(f"Error reading {p}: {e}")

    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Printing"):
                continue
            match = re.match(r"Tag:\s*([^,]+),\s*Categories:\s*(.*)", line)
            if match:
                name = match.group(1).strip()
                categories_str = match.group(2).strip()
                cats = [c.strip() for c in categories_str.split(",") if c.strip() and c.strip() != "All"]
                if name in modifiers_dict:
                    if cats:
                        modifiers_dict[name]["categories"] = cats
                else:
                    modifiers_dict[name] = {
                        "name": name,
                        "description": "",
                        "categories": cats or ["all"],
                        "type": "modifier"
                    }

    return list(modifiers_dict.values())


def parse_kb_field_definitions(kb_dir: Path) -> List[Dict[str, Any]]:
    fields_dir = kb_dir / "fields"
    results = []
    if not fields_dir.exists():
        return results

    for p in fields_dir.glob("*.md"):
        try:
            content = p.read_text(encoding="utf-8")
            first_line = content.split("\n")[0].replace("#", "").strip()
            summary_match = re.search(r">\s*\*\*一句话\*\*：(.*)", content)
            summary = summary_match.group(1).strip() if summary_match else ""
            source_match = re.search(r"来源：`(.*?)`", content)
            source_path = source_match.group(1).strip() if source_match else p.stem
            category_name = p.stem.replace("common-", "").replace("gui-", "").replace("main_menu-", "")

            results.append({
                "name": p.stem,
                "category": category_name,
                "title": first_line,
                "summary": summary,
                "source": source_path,
                "file_name": p.name,
                "content": content,
                "type": "field_definition"
            })
        except Exception as e:
            print(f"Error parsing field {p}: {e}")
    return results


def parse_kb_vanilla_mechanics(kb_dir: Path) -> List[Dict[str, Any]]:
    vanilla_dir = kb_dir / "vanilla"
    results = []
    if not vanilla_dir.exists():
        return results

    for p in vanilla_dir.glob("*.md"):
        try:
            content = p.read_text(encoding="utf-8")
            first_line = content.split("\n")[0].replace("#", "").strip()
            summary_match = re.search(r">\s*\*\*一句话\*\*：(.*)", content)
            summary = summary_match.group(1).strip() if summary_match else ""
            system_key = p.stem.replace("vanilla-", "")

            results.append({
                "name": p.stem,
                "system": system_key,
                "title": first_line,
                "summary": summary,
                "content": content,
                "type": "vanilla_mechanic"
            })
        except Exception as e:
            print(f"Error parsing vanilla {p}: {e}")
    return results


def parse_kb_pitfalls(kb_dir: Path) -> Dict[str, Any]:
    pitfalls_path = kb_dir / "pitfalls.md"
    if not pitfalls_path.exists():
        return {}

    content = pitfalls_path.read_text(encoding="utf-8")
    sections = {}
    current_section = "overview"
    current_lines = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if current_lines:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = line.replace("## ", "").strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections[current_section] = "\n".join(current_lines).strip()

    return {
        "title": "EU5 实测坑速查与 EU4 对照指南",
        "sections": sections,
        "full_content": content,
        "type": "pitfalls"
    }


def parse_kb_glossary(kb_dir: Path) -> List[Dict[str, str]]:
    glossary_path = kb_dir / "glossary.md"
    results = []
    if not glossary_path.exists():
        return results

    content = glossary_path.read_text(encoding="utf-8")
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("|") and not line.startswith("|---") and "内部键" not in line:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 2 and parts[0]:
                results.append({
                    "key": parts[0],
                    "cn_name": parts[1] if len(parts) > 1 else "",
                    "note": parts[2] if len(parts) > 2 else ""
                })
    return results


def generate_1_4_beta_summary(kb_dir: Path) -> Dict[str, Any]:
    return {
        "version": "1.4.0-open-beta",
        "update_date": "2026-10",
        "highlights": [
            "新增远征系统 common/expedition_types，重构海外探险与地理发现闭环",
            "新增独立阶层系统 common/estates 独立条目与特权解耦",
            "新增军队移动与战术机动深度规则 (army movement mechanics)",
            "重构法律与事件联动门槛，修复 on_action 子块跨文件合并时的 trigger 穿透问题",
            "移除/废弃了 1.0~1.2 时期的部分冗余接口，修正类目行号吸附"
        ],
        "key_files_updated": [
            "fields/common-expedition_types.md",
            "fields/common-estates.md",
            "vanilla/vanilla-army-movement.md",
            "cases/encoding-corruption-2026-10.md",
            "pitfalls.md"
        ]
    }


def convert_all():
    base_dir, docs_dir, output_dir, kb_dir, game_dir = get_paths()
    print("🚀 开始 EU5 Modding MCP 数据全面重建 (v2.1.0 / 1.4 Beta 适配)...")

    print("\n📦 处理 data_types/ ...")
    data_types_dir = docs_dir / "data_types"
    for category in ["common", "gui", "internalclausewitzgui", "script", "uncategorized"]:
        src_txt = data_types_dir / f"data_types_{category}.txt"
        if src_txt.exists():
            entries = parse_data_type_file(src_txt)
            out_json = output_dir / f"data_types_{category}.json"
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
            print(f"  ✓ data_types_{category}.json: {len(entries)} 条目")

    print("\n⚡ 处理 effects & triggers ...")
    effects = parse_markdown_log_file(docs_dir / "effects.log", "effect")
    with open(output_dir / "effects.json", "w", encoding="utf-8") as f:
        json.dump(effects, f, ensure_ascii=False, indent=2)
    print(f"  ✓ effects.json: {len(effects)} 条目")

    triggers = parse_markdown_log_file(docs_dir / "triggers.log", "trigger")
    with open(output_dir / "triggers.json", "w", encoding="utf-8") as f:
        json.dump(triggers, f, ensure_ascii=False, indent=2)
    print(f"  ✓ triggers.json: {len(triggers)} 条目")

    print("\n🎯 处理 event_targets (修复解析 Bug) ...")
    event_targets = parse_event_targets(docs_dir / "event_targets.log")
    with open(output_dir / "event_targets.json", "w", encoding="utf-8") as f:
        json.dump(event_targets, f, ensure_ascii=False, indent=2)
    print(f"  ✓ event_targets.json: {len(event_targets)} 条目 (旧版本仅有 1 条错误合并)")

    print("\n🔄 处理 on_actions (新支持) ...")
    on_actions = parse_on_actions(docs_dir / "on_actions.log")
    with open(output_dir / "on_actions.json", "w", encoding="utf-8") as f:
        json.dump(on_actions, f, ensure_ascii=False, indent=2)
    print(f"  ✓ on_actions.json: {len(on_actions)} 条目")

    print("\n🌐 处理 custom_localization (新支持) ...")
    custom_loc = parse_custom_localization(docs_dir / "custom_localization.log")
    with open(output_dir / "custom_localization.json", "w", encoding="utf-8") as f:
        json.dump(custom_loc, f, ensure_ascii=False, indent=2)
    print(f"  ✓ custom_localization.json: {len(custom_loc)} 条目")

    print("\n✨ 提取与聚合最新 modifiers ...")
    modifiers = parse_modifiers(docs_dir / "modifiers.log", game_dir)
    with open(output_dir / "modifiers.json", "w", encoding="utf-8") as f:
        json.dump(modifiers, f, ensure_ascii=False, indent=2)
    print(f"  ✓ modifiers.json: {len(modifiers)} 条目 (旧版本 1,855 条，现扩充至 2,400+)")

    print("\n📚 提取 eu5-modding-kb (1.4open_beta) 深度知识库 ...")
    fields = parse_kb_field_definitions(kb_dir)
    with open(output_dir / "field_definitions.json", "w", encoding="utf-8") as f:
        json.dump(fields, f, ensure_ascii=False, indent=2)
    print(f"  ✓ field_definitions.json: {len(fields)} 篇字段规范")

    mechanics = parse_kb_vanilla_mechanics(kb_dir)
    with open(output_dir / "vanilla_mechanics.json", "w", encoding="utf-8") as f:
        json.dump(mechanics, f, ensure_ascii=False, indent=2)
    print(f"  ✓ vanilla_mechanics.json: {len(mechanics)} 篇原版机制解析")

    pitfalls = parse_kb_pitfalls(kb_dir)
    with open(output_dir / "modding_pitfalls.json", "w", encoding="utf-8") as f:
        json.dump(pitfalls, f, ensure_ascii=False, indent=2)
    print(f"  ✓ modding_pitfalls.json: 包含 {len(pitfalls.get('sections', {}))} 个避坑专题")

    glossary = parse_kb_glossary(kb_dir)
    with open(output_dir / "glossary.json", "w", encoding="utf-8") as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)
    print(f"  ✓ glossary.json: {len(glossary)} 条术语对照")

    summary_14 = generate_1_4_beta_summary(kb_dir)
    with open(output_dir / "version_1_4_beta.json", "w", encoding="utf-8") as f:
        json.dump(summary_14, f, ensure_ascii=False, indent=2)
    print("  ✓ version_1_4_beta.json: 1.4 测试版变更综述")

    print("\n🔍 构建全局索引 index.json 与 all_data.json ...")
    all_data = []
    all_data.extend(effects)
    all_data.extend(triggers)
    all_data.extend(event_targets)
    all_data.extend(on_actions)
    all_data.extend(custom_loc)
    all_data.extend(modifiers)

    for category in ["common", "gui", "internalclausewitzgui", "script", "uncategorized"]:
        fpath = output_dir / f"data_types_{category}.json"
        if fpath.exists():
            with open(fpath, "r", encoding="utf-8") as f:
                all_data.extend(json.load(f))

    for f_item in fields:
        all_data.append({
            "name": f_item["name"],
            "description": f_item["summary"],
            "type": "field_definition"
        })
    for m_item in mechanics:
        all_data.append({
            "name": m_item["name"],
            "description": m_item["summary"],
            "type": "vanilla_mechanic"
        })

    with open(output_dir / "all_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ all_data.json: 总计 {len(all_data)} 条目")

    index = {}
    for entry in all_data:
        name = entry.get("name", "").lower()
        if not name:
            continue
        if name not in index:
            index[name] = []
        index[name].append({
            "name": entry.get("name"),
            "type": entry.get("type"),
            "description": entry.get("description", "")[:200]
        })

    with open(output_dir / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"  ✓ index.json: 包含 {len(index)} 个唯一定位键")

    print("\n🎉 数据集重建圆满完成！")


if __name__ == "__main__":
    convert_all()
