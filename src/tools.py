"""
EU5 Modding MCP 工具模块 (v2.2.0 / 1.4 Beta 深度完善版)
定义供 AI 助手与开发环境调用的全面工具集 (共 30 个专业工具，覆盖全库 156 篇知识)
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def register_tools(mcp, data_handler):
    """
    注册所有 EU5 Modding MCP 工具
    """

    # ==================== 基础与全库检索 ====================

    @mcp.tool()
    def search_by_name(name: str, fuzzy: bool = True, limit: int = 20) -> str:
        """
        全库综合模糊/精确搜索（覆盖修改器、效果、触发器、事件目标、指南、案例、数据类型等 30,000+ 条目）

        Args:
            name: 搜索名称或关键词
            fuzzy: 是否使用模糊匹配（默认为 True）
            limit: 返回结果数量限制（默认为 20）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_by_name(name, fuzzy=fuzzy, limit=limit)
            return json.dumps({
                "query": name,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error in search_by_name: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_modifiers(query: str, category: Optional[str] = None, limit: int = 20) -> str:
        """
        搜索游戏修改器（Modifiers，共 2,497 条，包含本体定义、类别、布尔/百分比属性）

        Args:
            query: 修改器名称或描述搜索词（例如 'tax', 'manpower', 'morale'）
            category: 可选类别过滤（例如 'country', 'location', 'character', 'unit'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_modifiers(query, category=category, limit=limit)
            return json.dumps({
                "query": query,
                "category_filter": category,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_effects(query: str, scope: Optional[str] = None, limit: int = 20) -> str:
        """
        搜索游戏效果（Effects，共 1,323 条，支持按作用域过滤）

        Args:
            query: 效果名称或说明关键词（例如 'add_gold', 'create_character'）
            scope: 可选的作用域过滤（例如 'country', 'location', 'character'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_effects(query, scope=scope, limit=limit)
            return json.dumps({
                "query": query,
                "scope_filter": scope,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_triggers(query: str, scope: Optional[str] = None, limit: int = 20) -> str:
        """
        搜索触发条件（Triggers，共 1,499 条，支持按作用域过滤）

        Args:
            query: 触发器名称或说明关键词（例如 'has_variable', 'is_at_war'）
            scope: 可选的作用域过滤（例如 'country', 'location', 'character'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_triggers(query, scope=scope, limit=limit)
            return json.dumps({
                "query": query,
                "scope_filter": scope,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_event_targets(query: str, scope: Optional[str] = None, limit: int = 20) -> str:
        """
        搜索事件目标（Event Targets，共 299 条，包含完整输入与输出作用域）

        Args:
            query: 事件目标名称或描述（例如 'capital', 'ruler', 'law_policy'）
            scope: 可选的作用域过滤（例如 'country', 'location'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_event_targets(query, scope=scope, limit=limit)
            return json.dumps({
                "query": query,
                "scope_filter": scope,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_on_actions(query: str, scope: Optional[str] = None, limit: int = 20) -> str:
        """
        搜索 on_actions 挂钩点（共 159 条，包含脉冲事件和执行作用域）

        Args:
            query: 关键词（例如 'pulse', 'death', 'war'）
            scope: 可选的作用域过滤（例如 'country', 'character'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_on_actions(query, scope=scope, limit=limit)
            return json.dumps({
                "query": query,
                "scope_filter": scope,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_custom_localization(query: str, limit: int = 20) -> str:
        """
        搜索动态文本与自定义本地化函数（Custom Localization，共 413 条）

        Args:
            query: 函数名或条目文本（例如 'CallToArms', 'RulerTitle'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_custom_localization(query, limit=limit)
            return json.dumps({
                "query": query,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ==================== 权威字段库与机制拆解 ====================

    @mcp.tool()
    def search_field_definitions(query: str, limit: int = 10) -> str:
        """
        搜索游戏类目字段规范（103 篇权威字段库，来自 eu5-modding-kb 1.4open_beta 实查）

        Args:
            query: 类目关键词（例如 'building', 'laws', 'estates', 'expedition', 'advances'）
            limit: 返回数量限制（默认 10）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_field_definitions(query, limit=limit)
            return json.dumps({
                "query": query,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_field_definition(category: str) -> str:
        """
        获取指定 common/ 或 gui/ 类目的完整字段规范（包含官方 readme 声明、本体实测漏写字段、1.4beta 更新）

        Args:
            category: 类目名称（例如 'building_types', 'laws', 'events', 'expedition_types', 'estates'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_field_definition(category)
            if not result:
                return json.dumps({"error": f"未找到类目 '{category}' 的字段规范"}, ensure_ascii=False)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_vanilla_mechanics(query: str, limit: int = 10) -> str:
        """
        搜索原版机制深度解析（24 篇系统机制，解析文件构成、数值位置、可改点与硬编码边界）

        Args:
            query: 机制关键词（例如 'production', 'pop', 'combat', 'army_movement', 'mandate'）
            limit: 返回数量限制（默认 10）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_vanilla_mechanics(query, limit=limit)
            return json.dumps({
                "query": query,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_vanilla_mechanic(system: str) -> str:
        """
        获取指定原版机制系统的完整深度解析（包含可改点与引擎硬编码边界）

        Args:
            system: 系统名称（例如 'production_and_buildings', 'army_movement', 'combat', 'pop', 'law_and_estate'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_vanilla_mechanic(system)
            if not result:
                return json.dumps({"error": f"未找到机制系统 '{system}' 的深度解析"}, ensure_ascii=False)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ==================== 制作指南与实战教程 ====================

    @mcp.tool()
    def search_guides(query: str, limit: int = 10) -> str:
        """
        搜索制作指南与端到端教程（12 篇文档，含新国家教程、新任务链教程、模组骨架、合并规则、法律设计、事件制作等）

        Args:
            query: 关键词（例如 'new-country', 'new-mission', 'skeleton', 'merging', 'law-design', 'event-making'）
            limit: 返回数量限制（默认 10）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_guides(query, limit=limit)
            return json.dumps({
                "query": query,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_guide(guide_name: str) -> str:
        """
        获取指定制作指南或教程全文

        Args:
            guide_name: 指南名称（例如 'new-country-tutorial', 'new-mission-pack-tutorial', 'mod-skeleton', 'merging', 'event-making', 'law-design', 'scripting-core', 'testing', 'localization', 'defines'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_guide(guide_name)
            if not result:
                return json.dumps({"error": f"未找到指南 '{guide_name}'"}, ensure_ascii=False)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ==================== 实战案例复盘 ====================

    @mcp.tool()
    def search_modding_cases(query: str, limit: int = 10) -> str:
        """
        搜索真实模组排错案例复盘（4 篇实操案例：BOM损坏抢救、法律撤销机理、无地佣兵国事件与作用域泄漏、本地化审计）

        Args:
            query: 关键词（例如 'encoding', 'corruption', 'laws', 'estates', 'blades-and-thrones', 'loc-audit'）
            limit: 返回数量限制（默认 10）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_modding_cases(query, limit=limit)
            return json.dumps({
                "query": query,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_modding_case(case_name: str) -> str:
        """
        获取指定模组实战案例全文

        Args:
            case_name: 案例名称（例如 'encoding-corruption-2026-10', 'laws-events-and-estates-2026-09', 'blades-and-thrones-2026-08', 'loc-audit-baseline-2026-10'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_modding_case(case_name)
            if not result:
                return json.dumps({"error": f"未找到案例 '{case_name}'"}, ensure_ascii=False)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ==================== 排错与诊断工具箱 ====================

    @mcp.tool()
    def decode_error_log(log_text: str) -> str:
        """
        error.log 智能解码器：输入游戏 error.log 中的报错行或日志片段，自动匹配病因、首查点、发生阶段并提供排查修复建议

        Args:
            log_text: 报错日志文本（例如 'Failed to fetch variable', 'Event target link var returned an unset scope', 'Invalid scope types', 'missing effect', 'Duplicated event ID' 等）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.decode_error_log(log_text)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_id_rules(query: str, limit: int = 15) -> str:
        """
        查询全游戏 ID 族的引用规则（查询某个对象在脚本中到底是必须带前缀如 'building_type:xxx'，还是必须裸写如 'has_advance = xxx'，避免静默失效）

        Args:
            query: ID 族名称或关键词（例如 'building', 'unit_category', 'advance', 'trait', 'road_type', 'culture', 'law'）
            limit: 返回数量限制（默认 15）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_id_rules(query, limit=limit)
            return json.dumps({
                "query": query,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_id_rule(family: str) -> str:
        """
        获取指定 ID 族的权威书写规则（前缀族 vs 裸写族详细说明与原版用量）

        Args:
            family: 族名称（例如 'building_type', 'sub_unit_category', 'advance', 'trait', 'culture', 'disaster_type'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_id_rule(family)
            if not result:
                return json.dumps({"error": f"未找到 ID 族 '{family}' 的规则"}, ensure_ascii=False)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_loc_key_rules(category: Optional[str] = None) -> str:
        """
        查询本地化键（loc 键）形态规则表（事件、任务、音乐、修正名、概念词条、特质等类目的必须前缀和缺键排查三原则）

        Args:
            category: 可选类目关键词（例如 'event', 'mission', 'modifier', 'concept', 'trait', 'music', 'death_reason'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_loc_key_rules(category=category)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_review_checklist(section: Optional[str] = None) -> str:
        """
        获取 7 维度结构化模组审查清单（文件与结构、引用完整性、作用域、语义陷阱、本地化、合并与覆盖、防误报白名单）

        Args:
            section: 可选审查小节关键词（例如 '文件', '引用', '作用域', '语义陷阱', '本地化', '合并', '白名单'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_review_checklist(section=section)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_systems_map(category: Optional[str] = None) -> str:
        """
        查询 in_game/common 160+ 类目系统地图（原版入口文件位置、官方 readme 状态、功能分组与制作指引）

        Args:
            category: 可选类目名称或功能分组（例如 'building', 'laws', 'goods', 'levies', '军事', '经济与生产'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_systems_map(category=category)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_defines(query: str, block: Optional[str] = None, limit: int = 20) -> str:
        """
        检索 00_defines.txt 引擎常量索引与数值（支持 NAI, NCombat, NUnit, NPop, NEstate, NColony 等关键常量搜索）

        Args:
            query: 常量名称或含义搜索词（例如 'COMBAT_BASE', 'AI_', 'REBEL', 'POP_SIZE', 'COLONIAL'）
            block: 可选 N 块过滤（例如 'NAI', 'NCombat', 'NUnit', 'NPop', 'NCountry', 'NColony'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.search_defines(query, block=block, limit=limit)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_define_block(block_name: str) -> str:
        """
        获取指定 N 块的行区间范围、主要常量与机制说明

        Args:
            block_name: N 块名称（例如 'NAI', 'NCombat', 'NUnit', 'NPop', 'NEstate', 'NCountry', 'NLocation', 'NDiplomacy'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_define_block(block_name)
            if not result:
                return json.dumps({"error": f"未找到 N 块 '{block_name}'"}, ensure_ascii=False)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_newbie_guide(topic: Optional[str] = None) -> str:
        """
        获取新手上手路线图与按任务速查表 (来自 START-HERE.md 零基础 7 步闭环与最容易翻车的 5 件事)

        Args:
            topic: 可选主题关键词（例如 '零基础', '任务', '翻车', '路线'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_newbie_guide(topic=topic)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def recover_corrupted_encoding(text: str) -> str:
        """
        乱码文本智能抢救器：基于实测 A 类乱码回环算法，将因 UTF-8 被按 GBK/ANSI 误读造成的损坏中文（如 '鍚堝悓'）还原为正确汉字（如 '合同'）

        Args:
            text: 待抢救的乱码文本字符串
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.recover_corrupted_encoding(text)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    # ==================== 避坑、术语与静态代码校验 ====================

    @mcp.tool()
    def get_modding_pitfalls(topic: Optional[str] = None) -> str:
        """
        查询 EU5 实测踩坑指南与 EU4 对照（作用域失效、变量守卫、合并陷阱、BOM 编码、法规自动撤销、灾难死循环、1.4 废弃接口）

        Args:
            topic: 可选查询的主题关键词（例如 'EU4', 'scope', 'variable', 'merging', 'BOM', '1.4'）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_modding_pitfalls(topic=topic)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def search_glossary(query: str, limit: int = 15) -> str:
        """
        查询 EU5 官方与社区标准中英对照术语表（167 条术语，含已订正的官方概念词）

        Args:
            query: 中文或英文术语（例如 'market_access', '贸易优势', 'pop', 'estates'）
            limit: 返回数量限制（默认 15）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            results = data_handler.search_glossary(query, limit=limit)
            return json.dumps({
                "query": query,
                "count": len(results),
                "results": results
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_1_4_beta_summary() -> str:
        """
        获取 EU5 1.4.0 公测版 (Open Beta) 关键语法与系统变更汇总
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.get_1_4_beta_summary()
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def validate_mod_snippet(snippet: str) -> str:
        """
        静态检测 EU5 模组脚本片段的语法错误与高危陷阱（花括号配对、大写 ROOT、废弃 event_target、:0 后缀、错误 building:/unit_category: 前缀、裸写族误加前缀、法规 potential 周期撤销陷阱、灾难重入死循环等）

        Args:
            snippet: 待检测的 Jomini 脚本代码段文本
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            result = data_handler.validate_mod_snippet(snippet)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def get_statistics() -> str:
        """
        获取当前 MCP 服务器的数据统计信息（包含全库各分类条目总数与 156 篇知识库覆盖率）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            stats = data_handler.get_statistics()
            return json.dumps(stats, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
