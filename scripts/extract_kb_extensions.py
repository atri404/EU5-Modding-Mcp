# coding: utf-8
import json
import re
from pathlib import Path
from typing import List, Dict, Any


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
    if not eld_path.exists():
        return {}

    content = eld_path.read_text(encoding="utf-8")
    entries = []
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
        "title": "本地化键（loc 键）规则与判缺键规范",
        "sections": sections,
        "content": content,
        "type": "loc_rules"
    }


def parse_kb_review_checklist(kb_dir: Path) -> Dict[str, Any]:
    chk_path = kb_dir / "tools" / "review-checklist.md"
    if not chk_path.exists():
        return {}

    content = chk_path.read_text(encoding="utf-8")
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
        "title": "审查清单（review-checklist）：可机械判定的项",
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


def parse_kb_defines(kb_dir: Path) -> Dict[str, Any]:
    def_path = kb_dir / "guides" / "defines.md"
    if not def_path.exists():
        return {}

    def_content = def_path.read_text(encoding="utf-8")
    blocks = []
    constants = []
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
                blocks.append({
                    "block": parts[0].replace("**", "").strip(),
                    "line_range": parts[1].strip(),
                    "content": parts[2].strip()
                })
            elif mode == "constants" and len(parts) >= 4 and parts[0] and not parts[0].startswith("常量"):
                constants.append({
                    "constant": parts[0].replace("**", "").replace("`", "").strip(),
                    "value": parts[1].replace("**", "").strip(),
                    "location": parts[2].strip(),
                    "description": parts[3].strip()
                })

    # 从各个 N 块的 content 中提取关键常量对 (例如 COMBAT_BASE=5, ARMY_MOVEMENT_SPEED=0.13 等)
    for b in blocks:
        b_name = b.get("block", "")
        b_content = b.get("content", "")
        pairs = re.findall(r'([A-Z0-9_]{3,})\s*=\s*([^\s、，；]+)', b_content)
        for k, v in pairs:
            # 避免重复
            if not any(c.get("constant") == k for c in constants):
                constants.append({
                    "constant": k,
                    "value": v,
                    "location": b_name,
                    "description": f"{b_name} 关键定义常量"
                })

    return {
        "title": "Defines 体系与 00_defines.txt 常量索引",
        "blocks": blocks,
        "constants": constants,
        "content": def_content,
        "type": "engine_defines"
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


def convert_all_kb_extensions(kb_dir: Path, output_dir: Path) -> Dict[str, Any]:
    print("\n📚 提取 eu5-modding-kb 全量扩展数据 (Guides/Cases/Tools/Defines)...")

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
    print(f"  ✓ error_log_decoder.json: 包含 {len(error_log_decoder.get('entries', []))} 条权威报错排查规则")

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

    engine_defines = parse_kb_defines(kb_dir)
    with open(output_dir / "engine_defines.json", "w", encoding="utf-8") as f:
        json.dump(engine_defines, f, ensure_ascii=False, indent=2)
    print(f"  ✓ engine_defines.json: 包含 {len(engine_defines.get('blocks', []))} 个 N 块与 {len(engine_defines.get('constants', []))} 个核心常量")

    start_here = parse_kb_start_here(kb_dir)
    with open(output_dir / "start_here.json", "w", encoding="utf-8") as f:
        json.dump(start_here, f, ensure_ascii=False, indent=2)
    print("  ✓ start_here.json: 新手任务与上手导引")

    return {
        "guides": guides,
        "cases": cases,
        "error_log_decoder": error_log_decoder,
        "id_rules": id_rules,
        "loc_rules": loc_rules,
        "review_checklist": review_checklist,
        "systems_map": systems_map,
        "engine_defines": engine_defines,
        "start_here": start_here
    }
