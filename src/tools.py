"""
EU5 Modding MCP 工具模块 (v2.1.0 / 1.4 Beta 适配)
定义供 AI 助手与开发环境调用的全面工具集
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def register_tools(mcp, data_handler):
    """
    注册所有 EU5 Modding MCP 工具
    """

    @mcp.tool()
    def search_by_name(name: str, fuzzy: bool = True, limit: int = 20) -> str:
        """
        全库综合模糊/精确搜索（覆盖修改器、效果、触发器、事件目标、数据类型等 30,000+ 条目）

        Args:
            name: 搜索名称或关键词
            fuzzy: 是否使用模糊匹配（默认为 True）
            limit: 返回结果数量限制（默认为 20）

        Returns:
            JSON 格式的搜索结果
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
        搜索事件目标（Event Targets，共 299 条，已彻底修复原版仅有1条的Bug）

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

    @mcp.tool()
    def get_modding_pitfalls(topic: Optional[str] = None) -> str:
        """
        查询 EU5 实测踩坑指南与 EU4 对照（作用域失效、变量守卫、合并陷阱、BOM 编码、1.4 废弃接口）

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
        静态检测 EU5 模组脚本片段的常见语法错误（检测大写 ROOT、已废弃的 event_target、:0 后缀、变量守卫陷阱等）

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
        获取当前 MCP 服务器的数据统计信息（包含全库各分类条目总数）
        """
        if not data_handler:
            return json.dumps({"error": "Data handler not initialized"}, ensure_ascii=False)
        try:
            stats = data_handler.get_statistics()
            return json.dumps(stats, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
