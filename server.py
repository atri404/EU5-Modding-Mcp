import json
import logging
import sys
from pathlib import Path
from typing import Any

# 确保脚本所在目录位于 sys.path 最前端，支持作为插件独立调用
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

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
    """注册所有功能（36 个工具和 25 项只读资源）"""
    if not initialize_data_handler():
        logger.warning("Data handler initialization failed, some features may be unavailable")

    register_tools(mcp, data_handler)
    logger.info("Tools registered successfully (36 tools)")

    register_resources(mcp, data_handler)
    logger.info("Resources registered successfully (25 resources)")


def main():
    """MCP 服务器入口"""
    logger.info("Starting EU5 Modding MCP Server (v2.3.1)...")
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
