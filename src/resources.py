"""
EU5 Modding MCP 资源模块 (v2.3.1 / 1.4 Beta 深度完善与 Token 紧凑版)
定义供客户端直接读取的各类只读数据资源 URI (共 25 项权威资源，紧凑 JSON 序列化节约 40%+ 传输体积)
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _dump_res(data: Any) -> str:
    """资源统一紧凑序列化"""
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def register_resources(mcp, data_handler):
    """
    注册所有 EU5 Modding MCP 资源 (共 25 项)
    """

    @mcp.resource("eu5://index")
    def get_index_resource() -> str:
        """获取按名称建立的快速索引数据"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.index)

    @mcp.resource("eu5://modifiers")
    def get_modifiers_resource() -> str:
        """获取全部 2,497 条修改器定义（含本体定义和分类）"""
        if not data_handler:
            return "[]"
        return _dump_res(data_handler.modifiers)

    @mcp.resource("eu5://effects")
    def get_effects_resource() -> str:
        """获取全部 1,323 条游戏效果定义与支持的作用域"""
        if not data_handler:
            return "[]"
        return _dump_res(data_handler.effects)

    @mcp.resource("eu5://triggers")
    def get_triggers_resource() -> str:
        """获取全部 1,499 条触发条件定义与支持的作用域"""
        if not data_handler:
            return "[]"
        return _dump_res(data_handler.triggers)

    @mcp.resource("eu5://event_targets")
    def get_event_targets_resource() -> str:
        """获取全部 299 条事件目标（含完整输入/输出作用域）"""
        if not data_handler:
            return "[]"
        return _dump_res(data_handler.event_targets)

    @mcp.resource("eu5://on_actions")
    def get_on_actions_resource() -> str:
        """获取全部 216 条 on_actions 挂钩点及执行作用域"""
        if not data_handler:
            return "[]"
        return _dump_res(data_handler.on_actions)

    @mcp.resource("eu5://custom_loc")
    def get_custom_loc_resource() -> str:
        """获取全部 413 条自定义本地化函数及其候选条目"""
        if not data_handler:
            return "[]"
        return _dump_res(data_handler.custom_localization)

    @mcp.resource("eu5://fields")
    def get_fields_resource() -> str:
        """获取 103 篇类目权威字段清单（eu5-modding-kb 1.4open_beta 实查）"""
        if not data_handler:
            return "[]"
        summary_list = [{
            "name": f.get("name"),
            "category": f.get("category"),
            "title": f.get("title"),
            "summary": f.get("summary"),
            "source": f.get("source")
        } for f in data_handler.field_definitions]
        return _dump_res(summary_list)

    @mcp.resource("eu5://mechanics")
    def get_mechanics_resource() -> str:
        """获取 24 篇原版机制系统深度解析清单（含可改点与硬编码边界）"""
        if not data_handler:
            return "[]"
        summary_list = [{
            "name": m.get("name"),
            "system": m.get("system"),
            "title": m.get("title"),
            "summary": m.get("summary")
        } for m in data_handler.vanilla_mechanics]
        return _dump_res(summary_list)

    @mcp.resource("eu5://guides")
    def get_guides_resource() -> str:
        """获取全部 12 篇制作指南与实战教程清单（新国家、新任务、骨架、合并、法律等）"""
        if not data_handler:
            return "[]"
        summary_list = [{
            "name": g.get("name"),
            "title": g.get("title"),
            "summary": g.get("summary"),
            "when_to_read": g.get("when_to_read")
        } for g in data_handler.guides]
        return _dump_res(summary_list)

    @mcp.resource("eu5://cases")
    def get_cases_resource() -> str:
        """获取 4 篇实操案例复盘清单（BOM损坏抢救、法律撤销机理、无地国事件等）"""
        if not data_handler:
            return "[]"
        summary_list = [{
            "name": c.get("name"),
            "title": c.get("title"),
            "summary": c.get("summary")
        } for c in data_handler.modding_cases]
        return _dump_res(summary_list)

    @mcp.resource("eu5://error_log_decoder")
    def get_error_log_decoder_resource() -> str:
        """获取 error.log 权威解码表（报错串 → 病因 → 首查点，含 23 组 C++ 引擎报错特征）"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.error_log_decoder)

    @mcp.resource("eu5://id_rules")
    def get_id_rules_resource() -> str:
        """获取全游戏 ID 族规范总表（前缀族 vs 裸写族）"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.id_rules)

    @mcp.resource("eu5://loc_rules")
    def get_loc_key_rules_resource() -> str:
        """获取本地化键形态总表与缺键排查规范"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.loc_rules)

    @mcp.resource("eu5://review_checklist")
    def get_review_checklist_resource() -> str:
        """获取 8 维度机械审查清单"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.review_checklist)

    @mcp.resource("eu5://systems_map")
    def get_systems_map_resource() -> str:
        """获取 common 137+ 类目系统地图与入口文件"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.systems_map)

    @mcp.resource("eu5://defines")
    def get_defines_resource() -> str:
        """获取 00_defines.txt 常量索引与 N 块清单（全量 38 块 / 1,430 常量）"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.engine_defines)

    @mcp.resource("eu5://start_here")
    def get_start_here_resource() -> str:
        """获取从零开始新手路线与按任务速查路线"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.start_here)

    @mcp.resource("eu5://pitfalls")
    def get_pitfalls_resource() -> str:
        """获取 EU5 实测踩坑指南与 EU4 对照全文本"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.modding_pitfalls)

    @mcp.resource("eu5://glossary")
    def get_glossary_resource() -> str:
        """获取 167 条标准中英双语术语表"""
        if not data_handler:
            return "[]"
        return _dump_res(data_handler.glossary)

    @mcp.resource("eu5://1.4-beta/summary")
    def get_1_4_beta_resource() -> str:
        """获取 1.4.0 公测版变更核心摘要"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.version_1_4_beta)

    @mcp.resource("eu5://statistics")
    def get_statistics_resource() -> str:
        """获取全库条目统计信息与知识库覆盖率"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.get_statistics())

    @mcp.resource("eu5://mod_architecture")
    def get_mod_architecture_resource() -> str:
        """获取 EU5 三层生命周期架构 (loading_screen/main_menu/in_game) 与工坊实践指南"""
        if not data_handler:
            return "{}"
        return _dump_res(data_handler.mod_architecture_guide)

    @mcp.resource("eu5://vanilla_readmes")
    def get_vanilla_readmes_resource() -> str:
        """获取游戏本体全部 74 份官方开发者 readme.txt 规范概要清单"""
        if not data_handler:
            return "[]"
        summary_list = [{
            "name": r.get("name"),
            "category": r.get("category"),
            "path": r.get("path"),
            "summary": r.get("summary"),
            "content_length": r.get("content_length")
        } for r in data_handler.vanilla_readmes]
        return _dump_res(summary_list)

    @mcp.resource("eu5://data_types/{category}")
    def get_data_types_by_category_resource(category: str) -> str:
        """获取特定类别的数据类型定义列表 (common, gui, internalclausewitzgui, script, uncategorized)"""
        if not data_handler:
            return "[]"
        data = data_handler.data_types_by_category.get(category, [])
        return _dump_res(data)
