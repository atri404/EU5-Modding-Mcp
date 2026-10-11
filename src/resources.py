"""
EU5 Modding MCP 资源模块 (v2.1.0 / 1.4 Beta 适配)
定义供客户端直接读取的各类只读数据资源 URI
"""

import json
import logging

logger = logging.getLogger(__name__)


def register_resources(mcp, data_handler):
    """
    注册所有 EU5 Modding MCP 资源
    """

    @mcp.resource("eu5://index")
    def get_index_resource() -> str:
        """获取按名称建立的快速索引数据"""
        if not data_handler:
            return "{}"
        return json.dumps(data_handler.index, ensure_ascii=False)

    @mcp.resource("eu5://modifiers")
    def get_modifiers_resource() -> str:
        """获取全部 2,497 条修改器定义（含本体定义和分类）"""
        if not data_handler:
            return "[]"
        return json.dumps(data_handler.modifiers, ensure_ascii=False, indent=2)

    @mcp.resource("eu5://effects")
    def get_effects_resource() -> str:
        """获取全部 1,323 条游戏效果定义与支持的作用域"""
        if not data_handler:
            return "[]"
        return json.dumps(data_handler.effects, ensure_ascii=False, indent=2)

    @mcp.resource("eu5://triggers")
    def get_triggers_resource() -> str:
        """获取全部 1,499 条触发条件定义与支持的作用域"""
        if not data_handler:
            return "[]"
        return json.dumps(data_handler.triggers, ensure_ascii=False, indent=2)

    @mcp.resource("eu5://event_targets")
    def get_event_targets_resource() -> str:
        """获取全部 299 条事件目标（修复了原版只有1条的Bug）"""
        if not data_handler:
            return "[]"
        return json.dumps(data_handler.event_targets, ensure_ascii=False, indent=2)

    @mcp.resource("eu5://on_actions")
    def get_on_actions_resource() -> str:
        """获取全部 159 条 on_actions 挂钩点及执行作用域"""
        if not data_handler:
            return "[]"
        return json.dumps(data_handler.on_actions, ensure_ascii=False, indent=2)

    @mcp.resource("eu5://custom_loc")
    def get_custom_loc_resource() -> str:
        """获取全部 413 条自定义本地化函数及其候选条目"""
        if not data_handler:
            return "[]"
        return json.dumps(data_handler.custom_localization, ensure_ascii=False, indent=2)

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
        return json.dumps(summary_list, ensure_ascii=False, indent=2)

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
        return json.dumps(summary_list, ensure_ascii=False, indent=2)

    @mcp.resource("eu5://pitfalls")
    def get_pitfalls_resource() -> str:
        """获取 EU5 实测踩坑指南与 EU4 对照全文本"""
        if not data_handler:
            return "{}"
        return json.dumps(data_handler.modding_pitfalls, ensure_ascii=False, indent=2)

    @mcp.resource("eu5://glossary")
    def get_glossary_resource() -> str:
        """获取 167 条标准中英双语术语表"""
        if not data_handler:
            return "[]"
        return json.dumps(data_handler.glossary, ensure_ascii=False, indent=2)

    @mcp.resource("eu5://1.4-beta/summary")
    def get_1_4_beta_resource() -> str:
        """获取 1.4.0 公测版变更核心摘要"""
        if not data_handler:
            return "{}"
        return json.dumps(data_handler.version_1_4_beta, ensure_ascii=False, indent=2)

    @mcp.resource("eu5://statistics")
    def get_statistics_resource() -> str:
        """获取全库条目统计信息"""
        if not data_handler:
            return "{}"
        return json.dumps(data_handler.get_statistics(), ensure_ascii=False, indent=2)

    @mcp.resource("eu5://data_types/{category}")
    def get_data_types_by_category_resource(category: str) -> str:
        """获取特定类别的数据类型定义列表 (common, gui, internalclausewitzgui, script, uncategorized)"""
        if not data_handler:
            return "[]"
        data = data_handler.get_data_types_by_category(category)
        return json.dumps(data, ensure_ascii=False, indent=2)
