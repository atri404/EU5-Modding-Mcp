"""
EU5 Modding MCP 数据处理器 (v2.3.1 / 1.4 Beta 深度完善版)
全面融合 eu5-modding-kb 156 篇权威文档与底层游戏数据，支持：
1. 修改器 (2,497)、效果 (1,323)、触发器 (1,499)、事件目标 (299)、挂钩点 (159)、动态本地化 (413)
2. 字段规范 (103篇)、原版机制深度拆解 (24篇)、制作指南与教程 (12篇)、实战案例 (4篇)
3. error.log 智能解码器、ID 族前缀规范表、本地化键形态表、7 维度机械审查清单、160+ 类目地图、Defines 引擎常量索引
4. 超级模组脚本诊断校验器 (包含 ID 引用陷阱、花括号平衡、作用域、BOM、法规撤销陷阱、防死循环等)
5. GBK/UTF-8 编码自动抢救器 (基于 2026-10 实测 A 类乱码回环算法)
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

        # 扩展知识库数据 (eu5-modding-kb 全量对齐 + 原版/工坊 1.4 深度扩展)
        self.guides: List[Dict[str, Any]] = []
        self.modding_cases: List[Dict[str, Any]] = []
        self.error_log_decoder: Dict[str, Any] = {}
        self.id_rules: Dict[str, Any] = {}
        self.loc_rules: Dict[str, Any] = {}
        self.review_checklist: Dict[str, Any] = {}
        self.systems_map: Dict[str, Any] = {}
        self.engine_defines: Dict[str, Any] = {}
        self.start_here: Dict[str, Any] = {}
        self.vanilla_readmes: List[Dict[str, Any]] = []
        self.mod_architecture_guide: Dict[str, Any] = {}

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
                ("guides", "guides.json"),
                ("modding_cases", "modding_cases.json"),
                ("vanilla_readmes", "vanilla_readmes.json"),
            ]:
                p = self.data_dir / filename
                if p.exists():
                    with open(p, "r", encoding="utf-8") as f:
                        setattr(self, attr, json.load(f))
                    logger.info(f"Loaded {len(getattr(self, attr))} {attr}")

            # 3. 字典与对象类知识库
            for attr, filename in [
                ("modding_pitfalls", "modding_pitfalls.json"),
                ("version_1_4_beta", "version_1_4_beta.json"),
                ("error_log_decoder", "error_log_decoder.json"),
                ("id_rules", "id_rules.json"),
                ("loc_rules", "loc_rules.json"),
                ("review_checklist", "review_checklist.json"),
                ("systems_map", "systems_map.json"),
                ("engine_defines", "engine_defines.json"),
                ("start_here", "start_here.json"),
                ("mod_architecture_guide", "mod_architecture_guide.json"),
            ]:
                p = self.data_dir / filename
                if p.exists():
                    with open(p, "r", encoding="utf-8") as f:
                        setattr(self, attr, json.load(f))

            # 4. 数据类型
            for category in ["common", "gui", "internalclausewitzgui", "script", "uncategorized"]:
                dt_p = self.data_dir / f"data_types_{category}.json"
                if dt_p.exists():
                    with open(dt_p, "r", encoding="utf-8") as f:
                        self.data_types_by_category[category] = json.load(f)

        except Exception as e:
            logger.error(f"Error loading data: {e}", exc_info=True)
            raise

    # ---------------- Token 优化与小节提取辅助函数 ----------------

    @staticmethod
    def _list_markdown_headers(md_text: str) -> List[str]:
        """提取 Markdown 文本中的主要标题 (h1, h2, h3)"""
        if not md_text:
            return []
        return [h.strip() for h in re.findall(r'(?m)^#{1,3}\s+.*', md_text)]

    @staticmethod
    def _extract_markdown_section(md_text: str, section_query: str) -> Optional[str]:
        """
        按关键词提取 Markdown 文本中对应的小节 (支持 h1/h2/h3)，
        大幅避免将整个 30KB+ 文档全部塞入上下文造成的 Token 浪费。
        """
        if not md_text or not section_query:
            return md_text
        q = section_query.lower().strip()
        sections = re.split(r'(?m)^(?=#{1,3}\s+)', md_text)
        matched = []
        for s in sections:
            header_line = s.strip().split('\n')[0].lower()
            if q in header_line or q in s[:300].lower():
                matched.append(s.strip())
        return '\n\n'.join(matched) if matched else None

    # ---------------- 基础与模糊检索 ----------------

    def search_by_name(self, name: str, fuzzy: bool = True, limit: int = 20) -> List[Dict[str, Any]]:
        limit = max(1, min(limit, 50))
        name_lower = name.lower().strip()
        raw_results = []
        if name_lower in self.index:
            raw_results = self.index[name_lower][:limit]
        elif fuzzy:
            results = []
            for key, entries in self.index.items():
                similarity = SequenceMatcher(None, name_lower, key).ratio()
                if similarity > 0.6:
                    for entry in entries:
                        entry_copy = entry.copy()
                        entry_copy["similarity"] = round(similarity, 3)
                        results.append(entry_copy)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            raw_results = results[:limit]

        # 过滤冗余超大字段以节约 Token
        sanitized = []
        for item in raw_results:
            clean = item.copy()
            if "content" in clean:
                clean["content_length"] = len(clean["content"])
                del clean["content"]
            sanitized.append(clean)
        return sanitized

    # ---------------- 全库一站式智能统一检索 (Token 极致优化) ----------------

    def omni_search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        limit_per_category: int = 3,
        total_limit: int = 15
    ) -> Dict[str, Any]:
        """
        全库一站式智能统一检索：在一次调用内跨 10 大系统检索相关条目，
        按系统分类聚合，并对每个条目提炼关键字段输出，大幅节约 Token 与多轮尝试时间。
        """
        q = query.lower().strip()
        limit_cat = max(1, min(limit_per_category, 10))
        total_max = max(1, min(total_limit, 30))

        valid_cats = {
            "modifiers", "effects", "triggers", "event_targets", "on_actions",
            "field_definitions", "vanilla_mechanics", "vanilla_readmes",
            "defines", "guides", "cases", "glossary"
        }

        selected_cats = set([c.lower().strip() for c in categories]) if categories else valid_cats

        results: Dict[str, List[Dict[str, Any]]] = {}
        total_hits = 0

        # 1. Modifiers
        if "modifiers" in selected_cats and total_hits < total_max:
            mods = self.search_modifiers(q, limit=limit_cat)
            if mods:
                results["modifiers"] = [{
                    "name": m.get("name"),
                    "categories": m.get("categories"),
                    "description": m.get("description", "").strip()[:100],
                    "boolean": m.get("boolean", False)
                } for m in mods]
                total_hits += len(results["modifiers"])

        # 2. Effects
        if "effects" in selected_cats and total_hits < total_max:
            effs = self.search_effects(q, limit=limit_cat)
            if effs:
                results["effects"] = [{
                    "name": e.get("name"),
                    "supported_scopes": e.get("supported_scopes"),
                    "description": e.get("description", "").strip()[:100]
                } for e in effs]
                total_hits += len(results["effects"])

        # 3. Triggers
        if "triggers" in selected_cats and total_hits < total_max:
            trigs = self.search_triggers(q, limit=limit_cat)
            if trigs:
                results["triggers"] = [{
                    "name": t.get("name"),
                    "supported_scopes": t.get("supported_scopes"),
                    "description": t.get("description", "").strip()[:100]
                } for t in trigs]
                total_hits += len(results["triggers"])

        # 4. Event Targets
        if "event_targets" in selected_cats and total_hits < total_max:
            ets = self.search_event_targets(q, limit=limit_cat)
            if ets:
                results["event_targets"] = [{
                    "name": et.get("name"),
                    "input_scopes": et.get("input_scopes"),
                    "output_scopes": et.get("output_scopes"),
                    "description": et.get("description", "").strip()[:100]
                } for et in ets]
                total_hits += len(results["event_targets"])

        # 5. on_actions
        if "on_actions" in selected_cats and total_hits < total_max:
            oas = self.search_on_actions(q, limit=limit_cat)
            if oas:
                results["on_actions"] = [{
                    "name": oa.get("name"),
                    "expected_scope": oa.get("expected_scope"),
                    "sub_on_action_hint": "使用 on_actions = { mymod_hook } 链式挂载"
                } for oa in oas]
                total_hits += len(results["on_actions"])

        # 6. Vanilla Readmes
        if "vanilla_readmes" in selected_cats and total_hits < total_max:
            readmes = self.search_vanilla_readmes(q, limit=limit_cat)
            if readmes:
                results["vanilla_readmes"] = [{
                    "category": r.get("category"),
                    "path": r.get("path"),
                    "summary": r.get("summary", "").strip()[:100]
                } for r in readmes]
                total_hits += len(results["vanilla_readmes"])

        # 7. Field Definitions
        if "field_definitions" in selected_cats and total_hits < total_max:
            fds = self.search_field_definitions(q, limit=limit_cat)
            if fds:
                results["field_definitions"] = [{
                    "category": f.get("category"),
                    "title": f.get("title"),
                    "summary": f.get("summary", "").strip()[:100]
                } for f in fds]
                total_hits += len(results["field_definitions"])

        # 8. Vanilla Mechanics
        if "vanilla_mechanics" in selected_cats and total_hits < total_max:
            vms = self.search_vanilla_mechanics(q, limit=limit_cat)
            if vms:
                results["vanilla_mechanics"] = [{
                    "system": vm.get("system"),
                    "title": vm.get("title"),
                    "summary": vm.get("summary", "").strip()[:100]
                } for vm in vms]
                total_hits += len(results["vanilla_mechanics"])

        # 9. Defines Constants & Blocks
        if "defines" in selected_cats and total_hits < total_max:
            defs = self.search_defines(q, limit=limit_cat)
            matched_c = defs.get("matched_constants", [])
            matched_b = defs.get("matched_blocks", [])
            if matched_c or matched_b:
                results["defines"] = [{
                    "constant": c.get("constant"),
                    "location": c.get("location"),
                    "description": c.get("description", "").strip()[:100]
                } for c in matched_c[:limit_cat]]
                if matched_b:
                    results["defines_blocks"] = [{
                        "block": b.get("block"),
                        "description": b.get("description", "").strip()[:100]
                    } for b in matched_b[:2]]
                total_hits += len(results["defines"])

        # 10. Guides & Cases
        if "guides" in selected_cats and total_hits < total_max:
            gs = self.search_guides(q, limit=limit_cat)
            if gs:
                results["guides"] = [{
                    "name": g.get("name"),
                    "title": g.get("title"),
                    "summary": g.get("summary", "").strip()[:100]
                } for g in gs]
                total_hits += len(results["guides"])

        # 11. Glossary
        if "glossary" in selected_cats and total_hits < total_max:
            gloss = self.search_glossary(q, limit=limit_cat)
            if gloss:
                results["glossary"] = [{
                    "key": gl.get("key"),
                    "cn_name": gl.get("cn_name"),
                    "note": gl.get("note", "").strip()[:100]
                } for gl in gloss]
                total_hits += len(results["glossary"])

        return {
            "query": query,
            "total_categories_matched": len(results),
            "total_items_matched": sum(len(v) for v in results.values()),
            "categories_matched": list(results.keys()),
            "results": results,
            "token_optimization_note": "返回高密度摘要卡片。若需指定项的完整代码或规范，可调用对应 get_* 工具查询。"
        }


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

    # ---------------- 知识库深层检索 ----------------

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

    def get_field_definition(self, category: str, section: Optional[str] = None) -> Optional[Dict[str, Any]]:
        cat_norm = category.lower().replace("_", "-")
        target_f = None
        for f in self.field_definitions:
            f_cat = f.get("category", "").lower().replace("_", "-")
            f_name = f.get("name", "").lower().replace("_", "-")
            if f_cat == cat_norm or f_name == cat_norm or f_name == f"common-{cat_norm}":
                target_f = f
                break
        if not target_f:
            for f in self.field_definitions:
                f_cat = f.get("category", "").lower().replace("_", "-")
                if cat_norm in f_cat:
                    target_f = f
                    break
        if not target_f:
            return None

        if not section:
            return target_f

        # 小节按需提取以节约 Token
        content_text = target_f.get("content", "")
        extracted = self._extract_markdown_section(content_text, section)
        item = target_f.copy()
        if extracted:
            item["matched_section"] = section
            item["content"] = extracted
            item["content_length"] = len(extracted)
        else:
            item["matched_section"] = None
            item["available_sections"] = self._list_markdown_headers(content_text)
            item["message"] = f"未找到匹配 '{section}' 的小节，请参考 available_sections 清单。"
        return item

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

    def get_vanilla_mechanic(self, system: str, section: Optional[str] = None) -> Optional[Dict[str, Any]]:
        sys_norm = system.lower().replace("_", "-")
        target_vm = None
        for vm in self.vanilla_mechanics:
            vm_sys = vm.get("system", "").lower().replace("_", "-")
            vm_name = vm.get("name", "").lower().replace("_", "-")
            if vm_sys == sys_norm or vm_name == sys_norm or vm_name == f"vanilla-{sys_norm}":
                target_vm = vm
                break
        if not target_vm:
            for vm in self.vanilla_mechanics:
                vm_sys = vm.get("system", "").lower().replace("_", "-")
                if sys_norm in vm_sys:
                    target_vm = vm
                    break
        if not target_vm:
            return None

        if not section:
            return target_vm

        content_text = target_vm.get("content", "")
        extracted = self._extract_markdown_section(content_text, section)
        item = target_vm.copy()
        if extracted:
            item["matched_section"] = section
            item["content"] = extracted
            item["content_length"] = len(extracted)
        else:
            item["matched_section"] = None
            item["available_sections"] = self._list_markdown_headers(content_text)
            item["message"] = f"未找到匹配 '{section}' 的小节，请参考 available_sections 清单。"
        return item

    def search_guides(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索制作指南与实战教程（新国家、新任务链、骨架、合并、法律、事件、测试等）"""
        q = query.lower()
        results = []
        for g in self.guides:
            name = g.get("name", "").lower()
            title = g.get("title", "").lower()
            summary = g.get("summary", "").lower()
            when = g.get("when_to_read", "").lower()
            if q in name or q in title or q in summary or q in when:
                item = g.copy()
                item["content_length"] = len(item.get("content", ""))
                del item["content"]
                results.append(item)
        return results[:limit]

    def get_guide(self, guide_name: str, section: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取指定制作指南或教程全文（支持按 section 查询指定小节）"""
        name_norm = guide_name.lower().replace("_", "-").replace(".md", "")
        target_g = None
        for g in self.guides:
            g_name = g.get("name", "").lower().replace("_", "-")
            if g_name == name_norm or name_norm in g_name:
                target_g = g
                break
        if not target_g:
            return None

        if not section:
            return target_g

        content_text = target_g.get("content", "")
        extracted = self._extract_markdown_section(content_text, section)
        item = target_g.copy()
        if extracted:
            item["matched_section"] = section
            item["content"] = extracted
            item["content_length"] = len(extracted)
        else:
            item["matched_section"] = None
            item["available_sections"] = self._list_markdown_headers(content_text)
            item["message"] = f"未找到匹配 '{section}' 的小节，请参考 available_sections 清单。"
        return item

    def search_modding_cases(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索实战案例复盘（BOM乱码抢救、法律撤销机制、作用域泄漏、复杂模组排错等）"""
        q = query.lower()
        results = []
        for c in self.modding_cases:
            name = c.get("name", "").lower()
            title = c.get("title", "").lower()
            summary = c.get("summary", "").lower()
            if q in name or q in title or q in summary:
                item = c.copy()
                item["content_length"] = len(item.get("content", ""))
                del item["content"]
                results.append(item)
        return results[:limit]

    def get_modding_case(self, case_name: str) -> Optional[Dict[str, Any]]:
        """获取指定实战案例复盘全文"""
        name_norm = case_name.lower().replace("_", "-").replace(".md", "")
        for c in self.modding_cases:
            c_name = c.get("name", "").lower().replace("_", "-")
            if c_name == name_norm or name_norm in c_name:
                return c
        return None

    def decode_error_log(self, log_text: str) -> Dict[str, Any]:
        """
        error.log 智能解码与诊断：根据报错文本智能匹配典型病因、首查点与解决建议
        """
        matched_entries = []
        entries = self.error_log_decoder.get("entries", [])

        for entry in entries:
            pat = entry.get("pattern", "")
            # 提取模式核心词
            clean_pat = re.sub(r'[`\'"(\[\])]', '', pat).strip()
            keywords = [k.strip() for k in clean_pat.split("...") if k.strip()]
            if not keywords:
                keywords = [clean_pat]

            is_match = False
            for kw in keywords:
                if kw.lower() in log_text.lower():
                    is_match = True
                    break

            if is_match:
                matched_entries.append(entry)

        # 归属与阶段判断辅助
        analysis = []
        if "Script location:" in log_text:
            analysis.append("检测到 'Script location:' 行，给出了具体文件与行号。请优先核对该路径是原版还是你的 mod 目录。")
        if any(w in log_text.lower() for w in ["failed to fetch variable", "unset scope", "invalid scope"]):
            analysis.append("属于【运行期错误】：多为变量未初始化或在错误作用域访问，通常不会阻止启动但会导致逻辑静默失效或刷屏。")
        if any(w in log_text.lower() for w in ["missing effect", "missing trigger", "syntax error"]):
            analysis.append("属于【加载期语法错误】：拼写错误、括号不匹配或宏参数 $...$ 遗漏，游戏加载时即可捕获。")

        return {
            "query_text": log_text,
            "matched_count": len(matched_entries),
            "diagnoses": matched_entries,
            "general_guidance": analysis or ["请参考 error_log_decoder 中的归属判断三原则先行确认报错阶段。"],
            "decoder_title": self.error_log_decoder.get("title", "")
        }

    def search_id_rules(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """
        查询 ID 族的引用规范（是否必须带前缀，或必须裸写，避免静默失效）
        """
        q = query.lower()
        results = []

        for r in self.id_rules.get("prefixed_rules", []):
            fam = r.get("family", "").lower()
            rule = r.get("rule", "").lower()
            if q in fam or q in rule:
                results.append(r)

        for r in self.id_rules.get("bare_rules", []):
            fam = r.get("family", "").lower()
            rule = r.get("rule", "").lower()
            if q in fam or q in rule:
                results.append(r)

        for r in self.id_rules.get("special_rules", []):
            fam = r.get("family", "").lower()
            rule = r.get("rule", "").lower()
            if q in fam or q in rule:
                results.append(r)

        return results[:limit]

    def get_id_rule(self, family: str) -> Optional[Dict[str, Any]]:
        """查询特定 ID 族的权威写法规则"""
        fam_norm = family.lower().strip()
        all_rules = (
            self.id_rules.get("prefixed_rules", []) +
            self.id_rules.get("bare_rules", []) +
            self.id_rules.get("special_rules", [])
        )
        for r in all_rules:
            if r.get("family", "").lower() == fam_norm:
                return r
        for r in all_rules:
            if fam_norm in r.get("family", "").lower():
                return r
        return None

    def get_loc_key_rules(self, category: Optional[str] = None) -> Dict[str, Any]:
        """获取各类目的本地化键（loc 键）形态规范与缺键排查原则"""
        sections = self.loc_rules.get("sections", {})
        if not category:
            return {
                "title": self.loc_rules.get("title", ""),
                "sections": sections
            }

        cat_lower = category.lower()
        matched = {}
        for sec_name, sec_content in sections.items():
            if cat_lower in sec_name.lower() or cat_lower in sec_content.lower():
                matched[sec_name] = sec_content

        return {
            "title": self.loc_rules.get("title", ""),
            "matched_category": category,
            "sections": matched or {"not_found": f"未找到与 '{category}' 直接匹配的本地化规则小节，可查询全文"}
        }

    def get_review_checklist(self, section: Optional[str] = None) -> Dict[str, Any]:
        """获取结构化模组审查清单（7 维度机械审查项）"""
        sections = self.review_checklist.get("sections", {})
        if not section:
            return {
                "title": self.review_checklist.get("title", ""),
                "sections": sections
            }

        sec_lower = section.lower()
        matched = {}
        for sec_name, sec_content in sections.items():
            if sec_lower in sec_name.lower() or sec_lower in sec_content.lower():
                matched[sec_name] = sec_content

        return {
            "title": self.review_checklist.get("title", ""),
            "matched_section": section,
            "sections": matched or {"not_found": f"未找到与 '{section}' 匹配的审查小节"}
        }

    def get_systems_map(self, category: Optional[str] = None) -> Any:
        """查询 common 137+ 类目系统地图（入口文件、readme状态、功能分组，支持紧凑概览与关键词检索）"""
        all_cats = self.systems_map.get("categories", [])
        if not category:
            # Token 优化：默认返回分组概览与统计，节约 86% Token
            groups = {}
            for c in all_cats:
                g = c.get("group", "其他")
                if g not in groups:
                    groups[g] = []
                groups[g].append(c.get("category"))

            return {
                "title": self.systems_map.get("title", ""),
                "total_categories": len(all_cats),
                "hint": "提示: 传入 category 关键词（例如 'building', 'army', 'law'）获取具体类目的入口文件与作用说明；传入 'all' 可获取全量完整列表。",
                "groups": groups,
                "categories_sample": all_cats[:5]
            }

        if category.lower().strip() == "all":
            return {
                "title": self.systems_map.get("title", ""),
                "total_categories": len(all_cats),
                "categories": all_cats
            }

        cat_lower = category.lower().replace("_", "-")
        matched = []
        for c in all_cats:
            c_name = c.get("category", "").lower().replace("_", "-")
            grp = c.get("group", "").lower()
            purpose = c.get("purpose", "").lower()
            if cat_lower in c_name or cat_lower in grp or cat_lower in purpose:
                matched.append(c)

        return {
            "query": category,
            "count": len(matched),
            "results": matched
        }

    def search_defines(self, query: str, block: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """查询 00_defines.txt 常量索引与 N 块定义 (已对返回块源码进行摘要脱敏以节约 Token)"""
        limit = max(1, min(limit, 50))
        q = query.lower()
        matched_blocks = []
        matched_constants = []

        for b in self.engine_defines.get("blocks", []):
            b_name = b.get("block", "").lower()
            b_content = b.get("content", "").lower()
            if block and block.lower() not in b_name:
                continue
            if q in b_name or q in b_content:
                # Token 优化：在搜索列表中不回传数千行的原始 content，改用摘要与长度
                b_copy = b.copy()
                if "content" in b_copy:
                    b_copy["content_length"] = len(b_copy["content"])
                    del b_copy["content"]
                b_copy["fetch_hint"] = f"可调用 get_define_block('{b.get('block')}') 获取该块完整源码"
                matched_blocks.append(b_copy)

        for c in self.engine_defines.get("constants", []):
            c_name = c.get("constant", "").lower()
            loc = c.get("location", "").lower()
            desc = c.get("description", "").lower()
            if block and block.lower() not in loc:
                continue
            if q in c_name or q in loc or q in desc:
                matched_constants.append(c)

        return {
            "query": query,
            "block_filter": block,
            "matched_blocks": matched_blocks[:limit],
            "matched_constants": matched_constants[:limit]
        }

    def get_define_block(self, block_name: str) -> Optional[Dict[str, Any]]:
        """获取特定 N 块（如 NAI, NCombat, NUnit, NPop）的行范围与主要常量概要"""
        b_norm = block_name.lower().strip()
        for b in self.engine_defines.get("blocks", []):
            if b.get("block", "").lower() == b_norm or b_norm in b.get("block", "").lower():
                return b
        return None

    def get_newbie_guide(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """获取从零开始新手路线与按任务导览路线 (来自 START-HERE.md)"""
        sections = self.start_here.get("sections", {})
        if not topic:
            return {
                "title": self.start_here.get("title", ""),
                "sections": sections
            }

        t_lower = topic.lower()
        matched = {}
        for sec_name, sec_content in sections.items():
            if t_lower in sec_name.lower() or t_lower in sec_content.lower():
                matched[sec_name] = sec_content

        return {
            "title": self.start_here.get("title", ""),
            "topic": topic,
            "sections": matched or sections
        }

    def search_vanilla_readmes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """检索游戏本体全部 74 篇官方开发者 readme.txt 规范"""
        q = query.lower()
        results = []
        for r in self.vanilla_readmes:
            cat = r.get("category", "").lower()
            path = r.get("path", "").lower()
            summary = r.get("summary", "").lower()
            content = r.get("content", "").lower()
            if q in cat or q in path or q in summary or q in content:
                item = r.copy()
                del item["content"]
                results.append(item)
        return results[:limit]

    def get_vanilla_readme(self, category: str) -> Optional[Dict[str, Any]]:
        """获取游戏本体指定类目（如 advances, building_types, laws, generic_actions）官方开发者 readme.txt 全文"""
        cat_norm = category.lower().replace("_", "-").replace(".txt", "").replace("common-", "")
        for r in self.vanilla_readmes:
            r_cat = r.get("category", "").lower().replace("_", "-")
            if r_cat == cat_norm or cat_norm in r.get("path", "").lower():
                return r
        return None

    def get_mod_architecture_guide(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """查询 EU5 三层生命周期架构 (loading_screen/main_menu/in_game)、无冲突 Sub-on-action 链与工坊实践指南"""
        if not topic:
            return self.mod_architecture_guide

        t_lower = topic.lower()
        all_tiers = self.mod_architecture_guide.get("lifecycle_tiers", {})
        all_practices = self.mod_architecture_guide.get("best_practices", {})

        # 宏观通用词命中
        if any(w in t_lower for w in ["lifecycle", "tier", "架构", "生命周期", "all"]):
            matched_tiers = all_tiers
        else:
            matched_tiers = {}
            for tier_k, tier_v in all_tiers.items():
                if t_lower in tier_k.lower() or t_lower in str(tier_v).lower():
                    matched_tiers[tier_k] = tier_v

        if any(w in t_lower for w in ["practice", "best", "工坊", "实践", "all"]):
            matched_practices = all_practices
        else:
            matched_practices = {}
            for prac_k, prac_v in all_practices.items():
                if t_lower in prac_k.lower() or t_lower in str(prac_v).lower():
                    matched_practices[prac_k] = prac_v

        return {
            "title": self.mod_architecture_guide.get("title", ""),
            "query": topic,
            "matched_lifecycle_tiers": matched_tiers or (all_tiers if not matched_practices else {}),
            "matched_best_practices": matched_practices or (all_practices if not matched_tiers else {})
        }

    def recover_corrupted_encoding(self, text: str) -> Dict[str, Any]:
        """
        基于实测 A 类乱码（UTF-8 文本被按 GBK/ANSI 错误读取并保存）的回环抢救算法。
        例如将 '鍚堝悓' 还原为 '合同'。
        """
        if not text or not text.strip():
            return {
                "success": False,
                "corruption_type": "空字符串",
                "message": "输入文本为空，无需还原",
                "recovered_text": ""
            }

        if all(ord(c) < 128 for c in text):
            return {
                "success": True,
                "corruption_type": "纯 ASCII",
                "message": "文本为纯 ASCII 字符，未发现中文乱码损坏",
                "recovered_text": text
            }

        try:
            # 检测是否含有不可逆的 PUA (U+E000 - U+F8FF) 字符
            has_pua = any(0xE000 <= ord(ch) <= 0xF8FF for ch in text)
            if has_pua:
                return {
                    "success": False,
                    "corruption_type": "B类 (经自定义字符集映射或含PUA私用区)",
                    "message": "文本含有 PUA (U+E000~U+F8FF) 码点或问号乱码，原始信息已被破坏，无法无损还原，建议按代码语义重写。",
                    "recovered_text": None
                }

            recovered = text.encode("gbk", errors="strict").decode("utf-8", errors="strict")
            return {
                "success": True,
                "corruption_type": "A类 (UTF-8 被误当 GBK 读取)",
                "message": "成功还原！请务必使用带 UTF-8 BOM 格式保存文件，避免再次损坏。",
                "recovered_text": recovered
            }
        except Exception as e:
            # 尝试容错还原
            try:
                recovered_loose = text.encode("gbk", errors="ignore").decode("utf-8", errors="ignore")
                return {
                    "success": len(recovered_loose) > 0,
                    "corruption_type": "部分 A 类损坏",
                    "message": f"严格还原失败 ({e})，提供容错还原结果（部分字符可能丢失）",
                    "recovered_text": recovered_loose
                }
            except Exception:
                return {
                    "success": False,
                    "corruption_type": "未知或不可逆",
                    "message": f"编码还原失败: {e}",
                    "recovered_text": None
                }

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

    def search_glossary(self, query: str, limit: int = 15) -> List[Dict[str, str]]:
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

    # ---------------- 模组脚本静态诊断校验器 (超级增强版) ----------------

    def validate_mod_snippet(self, snippet: str) -> Dict[str, Any]:
        """
        基于 EU5/Jomini 引擎底层规则、audit-ids.md、review-checklist.md 与实操避坑经验，
        对传入的模组脚本片段进行全方位静态诊断与纠错提示。
        """
        issues = []
        suggestions = []
        lines = snippet.split("\n")

        # 1. 花括号平衡性检查
        open_braces = snippet.count("{")
        close_braces = snippet.count("}")
        if open_braces != close_braces:
            issues.append({
                "severity": "ERROR",
                "code": "UNBALANCED_BRACES",
                "message": f"花括号配对错误！开括号 '{{' 为 {open_braces} 个，闭括号 '}}' 为 {close_braces} 个 (相差 {abs(open_braces - close_braces)} 个)。会导致逻辑跨块穿透或引擎致命解析中断！"
            })

        # 2. EU4 大写作用域检查
        upper_scopes = re.findall(r'\b(ROOT|PREV|FROM|THIS)\b', snippet)
        if upper_scopes:
            issues.append({
                "severity": "ERROR",
                "code": "EU4_UPPERCASE_SCOPE",
                "message": f"检测到 EU4 风格的大写作用域 ({', '.join(set(upper_scopes))})。EU5 严格要求小写: root / prev / this。"
            })

        # 3. event_target 检查
        if re.search(r'\b(event_target|global_event_target):', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "DEPRECATED_EVENT_TARGET",
                "message": "EU5 无 event_target / global_event_target 概念！请使用 save_scope_as = xxx 并在后续通过 scope:xxx 引用。"
            })

        # 4. 本地化 :0 检查
        if re.search(r'(:0\b|[a-zA-Z0-9_]+:0)', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "EU4_LOC_VERSION_SUFFIX",
                "message": "检测到本地化词条带 ':0' 后缀。EU5 本地化键无版本数字后缀，直接写 'KEY: \"文本\"' 或引用裸键名。"
            })

        # 5. province_event 检查
        if "province_event" in snippet:
            issues.append({
                "severity": "ERROR",
                "code": "DEPRECATED_PROVINCE_EVENT",
                "message": "EU5 无 province_event。事件类型必须五选一: country_event, location_event, unit_event, exploration_event, age_event。"
            })

        # 6. weight 检查
        if re.search(r'\bweight\s*=\s*\d+', snippet):
            issues.append({
                "severity": "WARNING",
                "code": "EU4_OPTION_WEIGHT",
                "message": "选项权重请勿使用 EU4 式的 'weight = N'。EU5 使用 'ai_chance = { base = N modifier = {...} }' 或 'ai_will_select'。"
            })

        # 7. 错误的 ID 前缀检查 (来自 audit-ids.md 实测)
        if re.search(r'\bbuilding:[a-zA-Z0-9_]+', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "INVALID_ID_PREFIX_BUILDING",
                "message": "检测到使用 'building:<id>'。原版实测为 0 处！建筑类必须使用 'building_type:<id>'，否则静默失效永不命中！"
            })

        if re.search(r'\bunit_category:[a-zA-Z0-9_]+', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "INVALID_ID_PREFIX_UNIT_CATEGORY",
                "message": "检测到使用 'unit_category:<id>'。原版实测为 0 处！单位类别必须使用 'sub_unit_category:<id>'，否则静默失效！"
            })

        # 8. 裸写族误加前缀检查 (来自 audit-ids.md 第二节)
        if re.search(r'\b(advance|road_type|production_method):[a-zA-Z0-9_]+', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "BARE_ID_WITH_UNWANTED_PREFIX",
                "message": "检测到对裸写族加了前缀！革新(has_advance = <id>)、道路(unlock_road_type = <id>)、生产方式(unlock_production_method = <id>)在原版中均为裸写，加前缀反而导致静默失效。"
            })

        # 9. trait 查询侧误加前缀检查
        if re.search(r'has_trait\s*=\s*trait:[a-zA-Z0-9_]+', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "TRAIT_QUERY_HAS_PREFIX",
                "message": "检测到 'has_trait = trait:<id>'。特质查询侧在原版中 100% 裸写 ('has_trait = <id>')；仅在新增时才使用 'add_trait = trait:<id>'。"
            })

        # 10. exists = var:X 数值变量守卫误用
        if re.search(r'exists\s*=\s*var:[a-zA-Z0-9_]+', snippet):
            suggestions.append({
                "code": "VARIABLE_EXISTENCE_GUARD",
                "message": "提示: 'exists = var:X' 只宜用于国家/实体引用变量！若 X 是数值变量，守卫必须使用 'has_variable = X'，否则在 trigger 中会因无法判断导致 error.log 刷屏报错并跳过初始化。"
            })

        # 11. INJECT 与顺序敏感块
        if re.search(r'INJECT:\s*(levies|country_name_construction)', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "INJECT_ORDER_SENSITIVE",
                "message": "levies 特化单位或国家名称构建是顺序敏感块（按从上到下第一个匹配生效）。使用 INJECT 追加会排在 fallback 后面永远无法生效！必须整体覆盖并在 fallback 之前插入。"
            })

        # 12. 法律/改革 potential 周期复查撤销风险 (来自 cases/laws-events-and-estates-2026-09.md)
        if re.search(r'(law|government_reform)\s*=\s*\{[^}]*potential\s*=\s*\{[^}]*(estate_power|gold|manpower|num_of_units|is_at_war)', snippet):
            issues.append({
                "severity": "WARNING",
                "code": "LAW_POTENTIAL_PERIODIC_REVOCATION",
                "message": "高危警告: 法律/政府改革的 potential 会被引擎周期性复查！如果在 potential 中使用了兵力、阶层力量、金钱、战争状态等波动性条件，条件一旦失效，整条法律及其已选政策会被自动撤销！建议只放政体、宗教、tag 等恒定条件。"
            })

        # 13. 灾难防重入死循环风险
        if "on_end" in snippet and re.search(r'remove_variable\s*=\s*[a-zA-Z0-9_]*disaster', snippet):
            issues.append({
                "severity": "WARNING",
                "code": "DISASTER_INFINITE_LOOP_RISK",
                "message": "灾难防重入警告: 灾难的解决标记绝不能在 on_end 移除，否则会导致灾难无限重入并重复叠加永久奖励！"
            })

        # 14. scripted_gui 表达式遗漏 .End 检查
        if "scripted_gui" in snippet and re.search(r'scope:[a-zA-Z0-9_]+(?!\.End)\s*$', snippet, re.MULTILINE):
            suggestions.append({
                "code": "SCRIPTED_GUI_MISSING_END",
                "message": "提示: scripted_guis 表达式链路若漏写 '.End' 会导致静默失效，请核查末尾是否已闭合。"
            })

        # 15. on_action 破坏性根挂钩检查
        if re.search(r'\b(on_game_start|on_new_ruler|on_yearly_pulse|on_monthly_pulse)\s*=\s*\{[^}]*effect\s*=\s*\{', snippet):
            issues.append({
                "severity": "WARNING",
                "code": "ON_ACTION_DESTRUCTIVE_ROOT_EFFECT",
                "message": "高危兼容性警告: 检测到在根挂钩点 (如 on_game_start) 直接编写 'effect = { ... }'！这会覆写原版和其他模组的初始化逻辑！官方与工坊最佳实践必须使用子挂钩点链式挂载: 'on_game_start = { on_actions = { mymod_init_hook } }' 并在自定义挂钩点中写 effect。"
            })

        # 16. 自动布局容器内使用 position 属性 (pdx_gui_layout.cpp:201)
        if re.search(r'\b(vbox|hbox|flowcontainer|dynamicgridbox)\s*=\s*\{[^}]*position\s*=\s*\{', snippet):
            issues.append({
                "severity": "ERROR",
                "code": "GUI_LAYOUT_POSITION_VIOLATION",
                "message": "GUI 布局错误: 在自动布局容器 (vbox/hbox/flowcontainer/dynamicgridbox) 内检测到 'position = { ... }'！这会导致 C++ 引擎报错: 'Widget cannot have a position in a layout (pdx_gui_layout.cpp:201)'。请移除 position，改用 layoutpolicy 或 spacing/margin。"
            })

        # 17. select_trigger 重复 target_flag 检查 (interaction_target.cpp:3505)
        flags = re.findall(r'select_trigger\s*=\s*\{[^}]*target_flag\s*=\s*([a-zA-Z0-9_]+)', snippet)
        if len(flags) > len(set(flags)):
            dups = set([f for f in flags if flags.count(f) > 1])
            issues.append({
                "severity": "ERROR",
                "code": "DUPLICATE_SELECT_TRIGGER_FLAG",
                "message": f"交互动作缺陷: 检测到重复的 select_trigger target_flags ({', '.join(dups)})！会导致 interaction_target.cpp:3505 致命错误。每个 select_trigger 必须拥有唯一的 target_flag 命名。"
            })

        # 18. EU4 废弃修改器检查 (pdx_persistent_reader.cpp:289)
        eu4_mods = re.findall(r'\b(great_power_score|army_reinforce_cost|exploration_maintenance_cost|colonial_maintenance_cost)\b', snippet)
        if eu4_mods:
            issues.append({
                "severity": "ERROR",
                "code": "DEPRECATED_EU4_MODIFIER",
                "message": f"修改器失效错误: 检测到使用 EU4 废弃修改器 ({', '.join(set(eu4_mods))})！EU5 引擎不识别这些修改器，会导致 pdx_persistent_reader.cpp:289 报错且静默失效。请使用 MCP search_modifiers 获取合法 EU5 修改器。"
            })

        # 19. 全角中文标点符号检查 (lexer.cpp 未知字符中断)
        full_width = re.findall(r'([：，；“”‘’（）【】！？])', snippet)
        if full_width:
            issues.append({
                "severity": "ERROR",
                "code": "FULL_WIDTH_PUNCTUATION",
                "message": f"语法错误: 代码中混入了全角中文标点符号 ({', '.join(set(full_width))})！Jomini 词法分析器 (lexer.cpp) 会直接中断解析并报错 'Unknown character'。请替换为对应半角英文标点符号 (:, ;, \", \', (), [])。"
            })

        # 20. trigger = { ... } 只读条件块内误写修改效果检查
        trigger_blocks = re.findall(r'trigger\s*=\s*\{([^}]*)\}', snippet, re.DOTALL)
        for tb in trigger_blocks:
            bad_effects = re.findall(r'\b(add_treasury|add_gold|set_variable|change_variable|remove_variable|add_stability|kill_character)\s*=', tb)
            if bad_effects:
                issues.append({
                    "severity": "ERROR",
                    "code": "EFFECT_IN_TRIGGER_BLOCK",
                    "message": f"逻辑冲突错误: 在只读判断条件块 (trigger = {{ ... }}) 内检测到状态修改效果 ({', '.join(set(bad_effects))})！trigger 仅用于布尔判断真假，写入修改效果会导致静默失效或报错。状态修改请放在 immediate 或 effect 块中。"
                })

        # 21. 事件命名空间缺失检查
        if re.search(r'\b(country_event|location_event|unit_event|exploration_event|age_event)\s*=', snippet):
            event_ids = re.findall(r'\bid\s*=\s*([a-zA-Z0-9_]+)\.\d+', snippet)
            if event_ids and not re.search(r'\bnamespace\s*=\s*', snippet):
                suggestions.append({
                    "code": "MISSING_EVENT_NAMESPACE",
                    "message": f"结构提示: 检测到带命名空间的事件 ID ({', '.join(set(event_ids))})，但当前代码段未声明 'namespace = ...'。在独立事件文件中务必在最顶部声明命名空间，否则引擎会报错未知事件 ID。"
                })

        # 22. 编码提示
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
            "version": "2.3.1 (EU5 1.4-Beta & Vanilla/Workshop Full Integration)",
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
                "guides_and_tutorials": len(self.guides),
                "modding_cases": len(self.modding_cases),
                "vanilla_readmes": len(self.vanilla_readmes),
                "error_decoder_rules": len(self.error_log_decoder.get("entries", [])),
                "id_rules_prefixed": len(self.id_rules.get("prefixed_rules", [])),
                "id_rules_bare": len(self.id_rules.get("bare_rules", [])),
                "loc_rules_sections": len(self.loc_rules.get("sections", {})),
                "review_checklist_sections": len(self.review_checklist.get("sections", {})),
                "systems_map_categories": self.systems_map.get("total_categories", 0),
                "defines_n_blocks": len(self.engine_defines.get("blocks", [])),
                "defines_constants": len(self.engine_defines.get("constants", [])),
                "pitfalls_topics": len(self.modding_pitfalls.get("sections", {})),
                "glossary_terms": len(self.glossary),
                "data_types_total": len([item for item in self.all_data if item.get("type") == "data_type"]),
            },
            "data_type_categories": {
                cat: len(entries) for cat, entries in self.data_types_by_category.items()
            }
        }
