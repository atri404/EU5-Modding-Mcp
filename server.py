import json
import logging
import sys
from pathlib import Path
from typing import Any

# 兼容 mcp 1.x (FastMCP) 与 mcp 2.x (MCPServer)
try:
    from mcp.server.fastmcp import FastMCP
except (ImportError, ModuleNotFoundError):
    from mcp.server.mcpserver import MCPServer as FastMCP

from src.tools import register_tools
from src.resources import register_resources
from src.data_handler import DataHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 MCP 服务器实例
mcp = FastMCP("EU5ModifierMCP")

# 全局数据处理器引用
data_handler = None


def initialize_data_handler():
    """初始化数据处理器并加载全量数据"""
    global data_handler
    try:
        base_path = Path(__file__).resolve().parent / "mcp-data"
        data_handler = DataHandler(base_path)
        logger.info(f"Data handler successfully initialized with path: {base_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize data handler: {e}")
        return False


def register_all_features():
    """注册所有功能（工具和资源）"""
    if not initialize_data_handler():
        logger.warning("Data handler initialization failed, some features may be unavailable")

    register_tools(mcp, data_handler)
    logger.info("Tools registered successfully")

    register_resources(mcp, data_handler)
    logger.info("Resources registered successfully")


@mcp.tool()
def ping() -> str:
    """
    检查服务器是否正常运行

    Returns:
        str: 服务器运行确认信息
    """
    return "EU5 Modding MCP Server (v2.1.0 / 1.4 Beta) is running successfully!"


@mcp.tool()
def get_server_info() -> str:
    """
    获取服务器架构信息、版本与功能概览

    Returns:
        str: JSON 格式的服务器详细元数据
    """
    info = {
        "name": "EU5 Modding MCP Server",
        "version": "2.1.0",
        "game_version_baseline": "EU5 1.3.x (Pavia) & 1.4.0 Open Beta (Across the Pillars)",
        "description": "Model Context Protocol server for Europa Universalis V modding, integrated with eu5-modding-kb & official game data",
        "features": [
            "搜索修改器（Modifiers，2,497 条）",
            "搜索游戏效果（Effects，1,323 条）",
            "搜索触发条件（Triggers，1,499 条）",
            "搜索事件目标（Event Targets，299 条，Bug 已修复）",
            "搜索 on_actions 脉冲挂钩点（159 条）",
            "搜索自定义本地化函数（Custom Localization，413 条）",
            "类目字段规范库（Field Definitions，103 篇，含 1.4 字段）",
            "原版机制深度拆解（Vanilla Mechanics，24 篇，含军队移动/远征）",
            "实测踩坑指南（Modding Pitfalls，18 个避坑专题与 EU4 对照）",
            "标准中英对照术语表（Glossary，167 条）",
            "模组脚本静态诊断校验器（Validate Mod Snippet）",
            "1.4.0 公测版变更综述（1.4 Beta Summary）",
            "底层 Jomini/Clausewitz 数据类型检索（Data Types，24,442 条）"
        ],
        "data_summary": {
            "total_entries": 30759,
            "unique_index_keys": 28539
        }
    }
    return json.dumps(info, ensure_ascii=False, indent=2)


def main():
    """MCP 服务器入口"""
    logger.info("Starting EU5 Modding MCP Server (v2.1.0)...")
    register_all_features()

    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
