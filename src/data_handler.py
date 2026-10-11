"""
EU5 Modding MCP 数据处理器 (v2.1.0 / 1.4 Beta 适配)
管理与查询修改器、效果、触发器、事件目标、on_actions、自定义本地化、
类目字段规范 (103篇)、原版机制解析 (24篇)、避坑指南与脚本校验器。
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class DataHandler:
    """EU5 Modding 数据处理与综合检索核心类"""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.index: Dict[str, List[Dict[str, Any]]] = {}
        self.all_data: List[Dict[str, Any]] = []
        self.modifiers: List[Dict[str, Any]] = []
        self.effects: List[Dict[str, Any]] = []
        self.triggers: List[Dict[str, Any]] = []
        self.event_targets: List[Dict[str, Any]] = []
        self.on_actions: List[Dict[str, Any]] = []
        self.custom_localization: List[Dict[str, Any]] = []
        self.field_definitions: List[Dict[str, Any]] = []
        self.vanilla_mechanics: List[Dict[str, Any]] = []
        self.modding_pitfalls: Dict[str, Any] = {}
        self.glossary: List[Dict[str, str]] = []
        self.version_1_4_beta: Dict[str, Any] = {}
        self.data_types_by_category: Dict[str, List[Dict[str, Any]]] = {}

        self._load_all_data()

    def _load_all_data(self):
        """加载所有数据文件"""
        try:
            # 1. 基础索引与全量
            idx_p = self.data_dir / "index.json"
            if idx_p.exists():
                with open(idx_p, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
                logger.info(f"Loaded index with {len(self.index)} entries")

            all_p = self.data_dir / "all_data.json"
            if all_p.exists():
                with open(all_p, "r", encoding="utf-8") as f:
                    self.all_data = json.load(f)
                logger.info(f"Loaded {len(self.all_data)} all_data entries")

            # 2. 核心语法与API
            for attr, filename in [
                ("modifiers", "modifiers.json"),
                ("effects", "effects.json"),
                ("triggers", "triggers.json"),
                ("event_targets", "event_targets.json"),
                ("on_actions", "on_actions.json"),
                ("custom_localization", "custom_localization.json"),
                ("field_definitions", "field_definitions.json"),
                ("vanilla_mechanics", "vanilla_mechanics.json"),
                ("glossary", "glossary.json"),
            ]:
                p = self.data_dir / filename
                if p.exists():
                    with open(p, "r", encoding="utf-8") as f:
                        setattr(self, attr, json.load(f))
                    logger.info(f"Loaded {len(getattr(self, attr))} {attr}")

            # 3. 避坑指南与 1.4 测试版变更综述
            pit_p = self.data_dir / "modding_pitfalls.json"
            if pit_p.exists():
                with open(pit_p, "r", encoding="utf-8") as f:
                    self.modding_pitfalls = json.load(f)

            v14_p = self.data_dir / "version_1_4_beta.json"
            if v14_p.exists():
                with open(v14_p, "r", encoding="utf-8") as f:
                    self.version_1_4_beta = json.load(f)

            # 4. 数据类型
            for category in ["common", "gui", "internalclausewitzgui", "script", "uncategorized"]:
                dt_p = self.data_dir / f"data_types_{category}.json"
                if dt_p.exists():
                    with open(dt_p, "r", encoding="utf-8") as f:
                        self.data_types_by_category[category] = json.load(f)

        except Exception as e:
            logger.error(f"Error loading data: {e}", exc_info=True)
            raise

    # ---------------- 基础与模糊检索 ----------------

    def search_by_name(self, name: str, fuzzy: bool = True, limit: int = 20) -> List[Dict[str, Any]]:
        name_lower = name.lower()
        if name_lower in self.index:
            return self.index[name_lower][:limit]
        if not fuzzy:
            return []

        results = []
        for key, entries in self.index.items():
            similarity = SequenceMatcher(None, name_lower, key).ratio()
            if similarity > 0.6:
                for entry in entries:
                    entry_copy = entry.copy()
                    entry_copy["similarity"] = round(similarity, 3)
                    results.append(entry_copy)

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]

    # ---------------- 专用类目检索 ----------------

    def search_modifiers(self, query: str, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for m in self.modifiers:
            name = m.get("name", "").lower()
            desc = m.get("description", "").lower()
            cats = [c.lower() for c in m.get("categories", [])]

            if category and category.lower() not in cats and "all" not in cats:
                continue

            if q in name or q in desc:
                results.append(m)
        return results[:limit]

    def search_effects(self, query: str, scope: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for e in self.effects:
            name = e.get("name", "").lower()
            desc = e.get("description", "").lower()
            scopes = [s.lower() for s in e.get("supported_scopes", [])]

            if scope and scope.lower() not in scopes:
                continue

            if q in name or q in desc:
                results.append(e)
        return results[:limit]

    def search_triggers(self, query: str, scope: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for t in self.triggers:
            name = t.get("name", "").lower()
            desc = t.get("description", "").lower()
            scopes = [s.lower() for s in t.get("supported_scopes", [])]

            if scope and scope.lower() not in scopes:
                continue

            if q in name or q in desc:
                results.append(t)
        return results[:limit]

    def search_event_targets(self, query: str, scope: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for et in self.event_targets:
            name = et.get("name", "").lower()
            desc = et.get("description", "").lower()
            in_scopes = [s.lower() for s in et.get("input_scopes", [])]
            out_scopes = [s.lower() for s in et.get("output_scopes", [])]

            if scope and scope.lower() not in in_scopes and scope.lower() not in out_scopes:
                continue

            if q in name or q in desc:
                results.append(et)
        return results[:limit]

    def search_on_actions(self, query: str, scope: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for oa in self.on_actions:
            name = oa.get("name", "").lower()
            exp_scope = oa.get("expected_scope", "").lower()

            if scope and scope.lower() != exp_scope and exp_scope != "none":
                continue

            if q in name or q in exp_scope:
                results.append(oa)
        return results[:limit]

    def search_custom_localization(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for cl in self.custom_localization:
            name = cl.get("name", "").lower()
            entries = [e.lower() for e in cl.get("entries", [])]
            if q in name or any(q in e for e in entries):
                results.append(cl)
        return results[:limit]

    # ---------------- 知识库深层检索 (1.4open_beta) ----------------

    def search_field_definitions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for f in self.field_definitions:
            name = f.get("name", "").lower()
            cat = f.get("category", "").lower()
            title = f.get("title", "").lower()
            summary = f.get("summary", "").lower()
            if q in name or q in cat or q in title or q in summary:
                item = f.copy()
                item["content_length"] = len(item.get("content", ""))
                del item["content"]
                results.append(item)
        return results[:limit]

    def get_field_definition(self, category: str) -> Optional[Dict[str, Any]]:
        cat_norm = category.lower().replace("_", "-")
        for f in self.field_definitions:
            f_cat = f.get("category", "").lower().replace("_", "-")
            f_name = f.get("name", "").lower().replace("_", "-")
            if f_cat == cat_norm or f_name == cat_norm or f_name == f"common-{cat_norm}":
                return f
        for f in self.field_definitions:
            f_cat = f.get("category", "").lower().replace("_", "-")
            if cat_norm in f_cat:
                return f
        return None

    def search_vanilla_mechanics(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for vm in self.vanilla_mechanics:
            name = vm.get("name", "").lower()
            sys_name = vm.get("system", "").lower()
            title = vm.get("title", "").lower()
            summary = vm.get("summary", "").lower()
            if q in name or q in sys_name or q in title or q in summary:
                item = vm.copy()
                item["content_length"] = len(item.get("content", ""))
                del item["content"]
                results.append(item)
        return results[:limit]

    def get_vanilla_mechanic(self, system: str) -> Optional[Dict[str, Any]]:
        sys_norm = system.lower().replace("_", "-")
        for vm in self.vanilla_mechanics:
            vm_sys = vm.get("system", "").lower().replace("_", "-")
            vm_name = vm.get("name", "").lower().replace("_", "-")
            if vm_sys == sys_norm or vm_name == sys_norm or vm_name == f"vanilla-{sys_norm}":
                return vm
        for vm in self.vanilla_mechanics:
            vm_sys = vm.get("system", "").lower().replace("_", "-")
            if sys_norm in vm_sys:
                return vm
        return None

    def get_modding_pitfalls(self, topic: Optional[str] = None) -> Dict[str, Any]:
        if not topic:
            return self.modding_pitfalls

        t_lower = topic.lower()
        matched_sections = {}
        for sec_name, sec_content in self.modding_pitfalls.get("sections", {}).items():
            if t_lower in sec_name.lower() or t_lower in sec_content.lower():
                matched_sections[sec_name] = sec_content
        return {
            "title": self.modding_pitfalls.get("title", ""),
            "matched_topic": topic,
            "sections": matched_sections or {"not_found": f"未找到与 '{topic}' 直接相关的避坑小节，可查询全文"}
        }

    def search_glossary(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        q = query.lower()
        results = []
        for g in self.glossary:
            k = g.get("key", "").lower()
            cn = g.get("cn_name", "").lower()
            note = g.get("note", "").lower()
            if q in k or q in cn or q in note:
                results.append(g)
        return results[:limit]

    def get_1_4_beta_summary(self) -> Dict[str, Any]:
        return self.version_1_4_beta

    # ---------------- Mod 脚本离线静态校验器 ----------------

    def validate_mod_snippet(self, snippet: str) -> Dict[str, Any]:
        """
        基于 EU5/Jomini 引擎底层规则与 pitfalls.md 实战总结，
        对传入的模组脚本片段进行静态诊断与纠错提示。
        """
        issues = []
        suggestions = []

        # 1. EU4 大写作用域检查
        if re.search(r'\b(ROOT|PREV|FROM|THIS)\b', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "EU4_UPPERCASE_SCOPE",
                "message": "检测到 EU4 风格的大写作用域 (ROOT/PREV/FROM/THIS)。EU5 严格要求小写作用域: root / prev / this。"
            })

        # 2. event_target 检查
        if re.search(r'\b(event_target|global_event_target):', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "DEPRECATED_EVENT_TARGET",
                "message": "EU5 无 event_target / global_event_target 概念！请使用 save_scope_as = xxx 并在后续通过 scope:xxx 引用。"
            })

        # 3. 本地化 :0 检查
        if re.search(r'(:0\b|[a-zA-Z0-9_]+:0)', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "EU4_LOC_VERSION_SUFFIX",
                "message": "检测到本地化词条带 ':0' 后缀。EU5 本地化键无版本数字后缀，直接写 'KEY: \"文本\"' 或引用裸键名。"
            })

        # 4. province_event 检查
        if "province_event" in snippet:
            issues.append({
                "severity": "ERROR",
                "code": "DEPRECATED_PROVINCE_EVENT",
                "message": "EU5 无 province_event。事件类型必须五选一: country_event, location_event, unit_event, exploration_event, age_event。"
            })

        # 5. weight 检查
        if re.search(r'\bweight\s*=\s*\d+', snippet):
            issues.append({
                "severity": "WARNING",
                "code": "EU4_OPTION_WEIGHT",
                "message": "选项权重请勿使用 EU4 式的 'weight = N'。EU5 使用 'ai_chance = { base = N modifier = {...} }' 或 'ai_will_select'。"
            })

        # 6. exists = var:X 数值变量守卫误用
        if re.search(r'exists\s*=\s*var:[a-zA-Z0-9_]+', snippet):
            suggestions.append({
                "code": "VARIABLE_EXISTENCE_GUARD",
                "message": "提示: 'exists = var:X' 只宜用于国家/实体引用变量！若 X 是数值变量，守卫必须使用 'has_variable = X'，否则在 trigger 中会因无法判断导致 error.log 刷屏报错。"
            })

        # 7. INJECT 与顺序敏感块
        if re.search(r'INJECT:\s*(levies|country_name_construction)', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "INJECT_ORDER_SENSITIVE",
                "message": "levies 特化单位或国家名称构建是顺序敏感块（按从上到下第一个匹配生效）。使用 INJECT 追加会排在 fallback 后面永远无法生效！必须整体覆盖并在 fallback 之前插入。"
            })

        # 8. 编码提示
        suggestions.append({
            "code": "UTF8_BOM_REMINDER",
            "message": "部署提醒: EU5 所有 mod 脚本和本地化 .yml 文件必须带 UTF-8 BOM（EF BB BF）。普通无 BOM 文件会被游戏引擎忽略或解析为乱码。"
        })

        return {
            "is_valid": len([i for i in issues if i["severity"] == "ERROR"]) == 0,
            "issues_count": len(issues),
            "issues": issues,
            "suggestions": suggestions
        }

    # ---------------- 数据统计 ----------------

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "version": "2.1.0 (EU5 1.4-Beta Update)",
            "total_entries": len(self.all_data),
            "breakdown": {
                "modifiers": len(self.modifiers),
                "effects": len(self.effects),
                "triggers": len(self.triggers),
                "event_targets": len(self.event_targets),
                "on_actions": len(self.on_actions),
                "custom_localization": len(self.custom_localization),
                "field_definitions": len(self.field_definitions),
                "vanilla_mechanics": len(self.vanilla_mechanics),
                "pitfalls_topics": len(self.modding_pitfalls.get("sections", {})),
                "glossary_terms": len(self.glossary),
                "data_types_total": len([item for item in self.all_data if item.get("type") == "data_type"]),
            },
            "data_type_categories": {
                cat: len(entries) for cat, entries in self.data_types_by_category.items()
            }
        }
