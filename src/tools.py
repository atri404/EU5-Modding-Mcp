"""
EU5 Modding MCP 工具模块 (v2.3.1 / 1.4 Beta 深度完善与 Token 极致优化版)
定义供 AI 助手与开发环境调用的全面工具集 (共 36 个专业工具，覆盖全库 156 篇知识、游戏本体与工坊最佳实践)
特性：
1. 统一序列化器 (serialize_response)：默认输出紧凑 JSON，消除多余缩进与换行，Token 消耗直降 30%~50%
2. 一站式智能统一检索 (eu5_omni_search)：在单次请求中跨 10 大系统检索并返回高密度摘要卡片
3. 结构化类目标签：工具文档首行统一采用 [类目标签] 与精准关键词，极大提高 ToolSearch / 智能路由命中率
4. 深度知识按需分段读取 (section)：字段规范、原版机制与教程支持提取指定小节，避免单次返回 30KB+ 造成上下文挤爆
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def serialize_response(data: Any, compact: bool = True) -> str:
    """
    统一响应序列化器：默认采用紧凑 JSON 格式，去除冗余缩进空格与换行，
    节约 30%~50% 上下文 Token 占用。
    """
    if compact:
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    return json.dumps(data, ensure_ascii=False, indent=2)


def register_tools(mcp, data_handler):
    """
    注册所有 EU5 Modding MCP 工具 (共 36 个)
    """

    # ==================== 服务器状态与全库统一检索 ====================

    @mcp.tool()
    def ping() -> str:
        """
        [服务器状态] 检查 EU5 Modding MCP 服务器运行状态与底层连接
        """
        return "EU5 Modding MCP Server (v2.3.1 / 1.4 Beta & Vanilla Engine) is running successfully!"

    @mcp.tool()
    def get_server_info() -> str:
        """
        [服务器信息] 获取 MCP 服务器架构规范、版本号与全量知识库统计元数据
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        stats = data_handler.get_statistics()
        info = {
            "name": "EU5 Modding MCP Server",
            "version": "2.3.1",
            "architecture": "Unified Claude Code Plugin (MCP + Skills + Commands)",
            "game_version_baseline": "EU5 1.3.x (Pavia) & 1.4.0 Open Beta (Across the Pillars)",
            "description": "Comprehensive Europa Universalis V modding intelligence suite for Claude Code",
            "token_optimization": "Compact JSON encoding enabled with omni-search multi-index routing",
            "tools_count": 36,
            "resources_count": 25,
            "statistics": stats
        }
        return serialize_response(info)

    @mcp.tool()
    def eu5_omni_search(
        query: str,
        categories: Optional[str] = None,
        limit_per_category: int = 3,
        total_limit: int = 15
    ) -> str:
        """
        [全库一站式检索 - 优先推荐] 极低 Token 消耗同时跨库检索修改器、效果、触发器、原生挂钩点、开发者Readme、Defines常量与机制规范

        Args:
            query: 检索关键词或概念名称（例如 'tax', 'building', 'army', 'stability', 'reform', 'cavalry', 'ai'）
            categories: 可选过滤类目，逗号分隔（例如 'modifiers,effects,triggers,readmes,defines,mechanics'，默认检索全类目）
            limit_per_category: 每个类目最多返回结果数（默认 3，避免单类目刷屏）
            total_limit: 总返回结果数上限（默认 15）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            cats_list = [c.strip().lower() for c in categories.split(",")] if categories else None
            result = data_handler.omni_search(
                query=query,
                categories=cats_list,
                limit_per_category=limit_per_category,
                total_limit=total_limit
            )
            return serialize_response(result)
        except Exception as e:
            logger.error(f"Error in eu5_omni_search: {e}")
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_by_name(name: str, fuzzy: bool = True, limit: int = 20) -> str:
        """
        [全库基础模糊搜索] 按名称快速模糊搜索全库 30,000+ 条目基础卡片 (已脱敏超大 content 字段以节约 Token)

        Args:
            name: 搜索名称或关键词
            fuzzy: 是否使用模糊匹配（默认为 True）
            limit: 返回结果数量限制（默认为 20）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_by_name(name, fuzzy=fuzzy, limit=limit)
            return serialize_response({
                "query": name,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            logger.error(f"Error in search_by_name: {e}")
            return serialize_response({"error": str(e)})

    # ==================== 语法与 API 专用类目检索 ====================

    @mcp.tool()
    def search_modifiers(query: str, category: Optional[str] = None, limit: int = 20) -> str:
        """
        [修改器检索] 搜索 EU5 属性修改器 (Modifiers，共 2,497 条，包含本体定义、类别、布尔/百分比属性)

        Args:
            query: 修改器名称或描述搜索词（例如 'tax', 'manpower', 'morale', 'discipline'）
            category: 可选类别过滤（例如 'country', 'location', 'character', 'unit'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_modifiers(query, category=category, limit=limit)
            return serialize_response({
                "query": query,
                "category_filter": category,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_effects(query: str, scope: Optional[str] = None, limit: int = 20) -> str:
        """
        [脚本动作/效果] 搜索 EU5 脚本指令与动作效果 (Effects，共 1,323 条，支持按作用域过滤)

        Args:
            query: 效果名称或说明关键词（例如 'add_gold', 'add_treasury', 'set_variable', 'create_character'）
            scope: 可选的作用域过滤（例如 'country', 'location', 'character'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_effects(query, scope=scope, limit=limit)
            return serialize_response({
                "query": query,
                "scope_filter": scope,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_triggers(query: str, scope: Optional[str] = None, limit: int = 20) -> str:
        """
        [触发条件/判断] 搜索 EU5 只读判断条件 (Triggers，共 1,499 条，支持按作用域过滤)

        Args:
            query: 触发器名称或说明关键词（例如 'has_variable', 'is_at_war', 'has_advance'）
            scope: 可选的作用域过滤（例如 'country', 'location', 'character'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_triggers(query, scope=scope, limit=limit)
            return serialize_response({
                "query": query,
                "scope_filter": scope,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_event_targets(query: str, scope: Optional[str] = None, limit: int = 20) -> str:
        """
        [事件目标] 搜索 EU5 作用域事件目标 (Event Targets，共 299 条，包含完整输入与输出作用域)

        Args:
            query: 事件目标名称或描述（例如 'capital', 'ruler', 'law_policy', 'overlord'）
            scope: 可选的作用域过滤（例如 'country', 'location'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_event_targets(query, scope=scope, limit=limit)
            return serialize_response({
                "query": query,
                "scope_filter": scope,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_on_actions(query: str, scope: Optional[str] = None, limit: int = 20) -> str:
        """
        [原生挂钩点] 搜索 EU5 原生脉冲挂钩点与执行作用域 (共 216 条 on_actions，包含 131 个底层 hardcoded 钩子)

        Args:
            query: 挂钩点名称（例如 'on_startup', 'on_game_start', 'yearly_country_pulse', 'on_action_monthly_pulse'）
            scope: 可选执行作用域（例如 'country', 'location', 'character', 'none'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_on_actions(query, scope=scope, limit=limit)
            return serialize_response({
                "query": query,
                "scope_filter": scope,
                "count": len(results),
                "results": results,
                "best_practice_hint": "严禁在根挂钩点直接写 effect，必须使用 on_actions = { mymod_hook } 子挂钩点链式挂载"
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_custom_localization(query: str, limit: int = 20) -> str:
        """
        [动态本地化] 搜索 EU5 自定义动态本地化函数与备选分支 (Custom Localization，共 413 条)

        Args:
            query: 函数名称或分支词条（例如 'GetRulerTitle', 'GetGovernmentName', 'Tooltip'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_custom_localization(query, limit=limit)
            return serialize_response({
                "query": query,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    # ==================== 知识库深度规范与机制拆解 ====================

    @mcp.tool()
    def search_field_definitions(query: str, limit: int = 10) -> str:
        """
        [类目字段清单] 检索 103 篇 common 类目字段白名单概要（包含 1.4 测试版新增类目）

        Args:
            query: 类目名称或中文关键词（例如 'advances', 'estates', 'laws', 'building_types', '远征'）
            limit: 返回数量限制（默认 10）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_field_definitions(query, limit=limit)
            return serialize_response({
                "query": query,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_field_definition(category: str, section: Optional[str] = None) -> str:
        """
        [类目字段全文] 获取指定 common 类目的字段白名单全文（支持按 section 查询小节以节约 Token）

        Args:
            category: 类目名称（例如 'advances', 'building_types', 'laws', 'expedition_types', 'estates'）
            section: 可选小节关键词（例如 '补缺', 'whitelist', '格式', '核心要点'，节约 80%+ Token）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_field_definition(category, section=section)
            if not result:
                return serialize_response({"error": f"未找到类目 '{category}' 的字段规范"})
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_vanilla_mechanics(query: str, limit: int = 10) -> str:
        """
        [原版机制拆解检索] 检索 24 篇原版机制深度拆解概要（军队移动、POP、市场、内阁、AI、国际关系等）

        Args:
            query: 机制系统名称（例如 'army_movement', 'pop', 'market', 'cabinet', 'ai', 'peace_deal'）
            limit: 返回数量限制（默认 10）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_vanilla_mechanics(query, limit=limit)
            return serialize_response({
                "query": query,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_vanilla_mechanic(system: str, section: Optional[str] = None) -> str:
        """
        [原版机制全文] 获取原版机制深度解析全文与硬编码边界（支持按 section 查询小节以节约 Token）

        Args:
            system: 系统名称（例如 'army_movement', 'production_and_buildings', 'pop', 'ai', 'estates'）
            section: 可选小节关键词（例如 '可改', '硬编码', 'mod', '目录'，节约 80%+ Token）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_vanilla_mechanic(system, section=section)
            if not result:
                return serialize_response({"error": f"未找到机制系统 '{system}' 的拆解文档"})
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    # ==================== 制作教程与实战复盘 ====================

    @mcp.tool()
    def search_guides(query: str, limit: int = 10) -> str:
        """
        [制作教程检索] 检索制作指南与实战教程清单（新国家、新任务链、骨架、合并、法律等 12 篇教程）

        Args:
            query: 制作场景搜索词（例如 'new-country', 'new-mission', 'merging', 'laws', 'events'）
            limit: 返回数量限制（默认 10）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_guides(query, limit=limit)
            return serialize_response({
                "query": query,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_guide(guide_name: str, section: Optional[str] = None) -> str:
        """
        [制作教程全文] 获取指定制作指南或教程全文（支持按 section 查询小节以节约 Token）

        Args:
            guide_name: 指南名称（例如 'new-country-tutorial', 'new-mission-pack-tutorial', 'merging', 'skeleton'）
            section: 可选小节关键词（例如 '步骤', '避坑', '代码', '测试'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_guide(guide_name, section=section)
            if not result:
                return serialize_response({"error": f"未找到指南 '{guide_name}'"})
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_modding_cases(query: str, limit: int = 10) -> str:
        """
        [实战案例检索] 检索实战案例复盘清单（BOM 乱码抢救、法律撤销机制、作用域泄漏、复杂排错）

        Args:
            query: 案例问题关键词（例如 'encoding', 'corruption', 'laws', 'revocation', 'scope'）
            limit: 返回数量限制（默认 10）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_modding_cases(query, limit=limit)
            return serialize_response({
                "query": query,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_modding_case(case_name: str) -> str:
        """
        [实战案例全文] 获取指定实战案例复盘全文

        Args:
            case_name: 案例名称（例如 'encoding-corruption-2026-10', 'laws-events-and-estates-2026-09'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_modding_case(case_name)
            if not result:
                return serialize_response({"error": f"未找到实战案例 '{case_name}'"})
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    # ==================== 日志解码、查表工具箱与 Defines ====================

    @mcp.tool()
    def decode_error_log(log_text: str) -> str:
        """
        [日志智能解码] 诊断分析 error.log 报错文本，精准匹配 23 组 Jomini C++ 引擎报错特征并给出病因与首查点

        Args:
            log_text: 粘贴的 error.log 报错文本片段
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.decode_error_log(log_text)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_id_rules(query: str, limit: int = 15) -> str:
        """
        [ID族规范检索] 查询全游戏 ID 族引用规范（前缀族 building_type: vs 裸写族 has_advance = <id>，防止静默失效）

        Args:
            query: ID 类目关键词（例如 'building', 'unit', 'advance', 'trait', 'road'）
            limit: 返回数量限制（默认 15）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_id_rules(query, limit=limit)
            return serialize_response({
                "query": query,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_id_rule(family: str) -> str:
        """
        [ID族规范详情] 获取特定 ID 族的权威写法规则与避坑说明

        Args:
            family: ID 族名称（例如 'building_type', 'advance', 'trait', 'unit_category', 'sub_unit_category'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_id_rule(family)
            if not result:
                return serialize_response({"error": f"未找到 ID 族 '{family}' 的规则定义"})
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_loc_key_rules(category: Optional[str] = None) -> str:
        """
        [本地化键规范] 获取各类目本地化键（loc 键）形态规范与缺键排查原则

        Args:
            category: 可选类目名称（例如 'event', 'mission', 'modifier', 'character', 'trait'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_loc_key_rules(category=category)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_review_checklist(section: Optional[str] = None) -> str:
        """
        [结构化审查] 获取 8 维度机械审查清单（生命周期隔离、文件命名、作用域穿透、GUI布局坐标、ID前缀）

        Args:
            section: 可选审查小节关键词（例如 '文件', '作用域', '白名单', '布局', '生命周期'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_review_checklist(section=section)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_systems_map(category: Optional[str] = None) -> str:
        """
        [common系统地图] 查询 common 137+ 类目系统地图、入口文件与分组概览 (默认返回紧凑分组概览，节约 86% Token)

        Args:
            category: 可选类目关键词（例如 'building', 'army', 'law'，传入 'all' 可获取全量完整列表）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_systems_map(category=category)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_defines(query: str, block: Optional[str] = None, limit: int = 20) -> str:
        """
        [引擎常量检索] 搜索 00_defines.txt 常量索引与数值（全量 38 个 N 块 / 1,430 个常量，已对块源码摘要以节约 Token）

        Args:
            query: 常量名称或含义搜索词（例如 'COMBAT_BASE', 'AI_', 'REBEL', 'POP_SIZE', 'COLONIAL'）
            block: 可选 N 块过滤（例如 'NAI', 'NCombat', 'NUnit', 'NPop', 'NCountry', 'NColony'）
            limit: 返回数量限制（默认 20）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.search_defines(query, block=block, limit=limit)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_define_block(block_name: str) -> str:
        """
        [引擎常量N块] 获取指定 N 块（如 NAI, NCombat, NUnit, NPop）的行范围、主要常量与源码

        Args:
            block_name: N 块名称（例如 'NAI', 'NCombat', 'NUnit', 'NPop', 'NEstate', 'NCountry', 'NLocation'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_define_block(block_name)
            if not result:
                return serialize_response({"error": f"未找到 N 块 '{block_name}'"})
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_newbie_guide(topic: Optional[str] = None) -> str:
        """
        [新手速查导览] 获取零基础 7 步闭环导览与最容易翻车的 5 件事 (来自 START-HERE.md)

        Args:
            topic: 可选主题关键词（例如 '零基础', '任务', '翻车', '路线'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_newbie_guide(topic=topic)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def recover_corrupted_encoding(text: str) -> str:
        """
        [乱码智能抢救] 基于 A 类乱码回环算法自动抢救 UTF-8 误按 GBK 损坏的文本（如 '鍚堝悓' 还原为 '合同'）

        Args:
            text: 待抢救的乱码文本字符串
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.recover_corrupted_encoding(text)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    # ==================== 避坑、术语与静态代码校验 ====================

    @mcp.tool()
    def get_modding_pitfalls(topic: Optional[str] = None) -> str:
        """
        [避坑指南全文] 查询 EU5 实测踩坑指南与 EU4 对照（作用域失效、变量守卫、合并陷阱、BOM 编码、法规自动撤销、灾难死循环）

        Args:
            topic: 可选查询的主题关键词（例如 'EU4', 'scope', 'variable', 'merging', 'BOM', '1.4'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_modding_pitfalls(topic=topic)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_glossary(query: str, limit: int = 15) -> str:
        """
        [标准术语词典] 查询 EU5 官方与社区 167 条中英双语标准术语对照（含已订正的官方概念词）

        Args:
            query: 中文或英文术语（例如 'market_access', '贸易优势', 'pop', 'estates'）
            limit: 返回数量限制（默认 15）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_glossary(query, limit=limit)
            return serialize_response({
                "query": query,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_1_4_beta_summary() -> str:
        """
        [1.4公测版变更] 获取 EU5 1.4.0 公测版 (Open Beta) 关键语法与系统变更核心汇总
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_1_4_beta_summary()
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def validate_mod_snippet(snippet: str) -> str:
        """
        [静态代码诊断] 扫描 Jomini 脚本代码片段，精准拦截 15+ 项引擎致命错误（全角标点、花括号、大写ROOT、布局坐标、触发器误写修改效果等）

        Args:
            snippet: 待检测的 Jomini 脚本代码段文本
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.validate_mod_snippet(snippet)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_mod_architecture_guide(topic: Optional[str] = None) -> str:
        """
        [三层架构与工坊规范] 查询 EU5 三层生命周期隔离 (loading_screen/main_menu/in_game)、无冲突 Sub-on-action 链与工坊实践

        Args:
            topic: 可选主题关键词（例如 'lifecycle', 'loading_screen', 'main_menu', 'in_game', 'sub_on_action', 'storage_country', 'performance', 'cmf'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_mod_architecture_guide(topic=topic)
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def search_vanilla_readmes(query: str, limit: int = 10) -> str:
        """
        [原版开发者规范检索] 检索游戏本体全部 74 篇官方开发者 readme.txt 规范（涵盖 advances, building_types, laws, generic_actions 等）

        Args:
            query: 搜索关键词（例如 'advances', 'building', 'cabinet', 'action', 'law', 'estate', 'military'）
            limit: 返回数量限制（默认 10）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            results = data_handler.search_vanilla_readmes(query, limit=limit)
            return serialize_response({
                "query": query,
                "count": len(results),
                "results": results
            })
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_vanilla_readme(category: str) -> str:
        """
        [原版开发者规范全文] 获取游戏本体指定类目的官方开发者 readme.txt 完整设计规范与语法说明

        Args:
            category: 类目名称（例如 'advances', 'building_types', 'cabinet_actions', 'casus_belli', 'laws', 'generic_actions', 'disasters'）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            result = data_handler.get_vanilla_readme(category)
            if not result:
                return serialize_response({"error": f"未找到类目 '{category}' 的开发者 readme.txt"})
            return serialize_response(result)
        except Exception as e:
            return serialize_response({"error": str(e)})

    @mcp.tool()
    def get_statistics() -> str:
        """
        [数据全景统计] 获取当前 MCP 服务器的全景数据统计（包含全库各分类条目总数与 156 篇知识库覆盖率）
        """
        if not data_handler:
            return serialize_response({"error": "Data handler not initialized"})
        try:
            stats = data_handler.get_statistics()
            return serialize_response(stats)
        except Exception as e:
            return serialize_response({"error": str(e)})
