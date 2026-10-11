#!/usr/bin/env python3
"""
EU5 Modding MCP Server (v2.1.0) 综合功能测试脚本
测试各项数据加载、搜索检索、知识库查询与静态校验器
"""

import sys
from pathlib import Path

# 将项目根目录添加至 sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import json
import logging
from src.data_handler import DataHandler
from src.tools import register_tools
from src.resources import register_resources

# 兼容 mcp 1.x / 2.x
try:
    from mcp.server.fastmcp import FastMCP
except (ImportError, ModuleNotFoundError):
    from mcp.server.mcpserver import MCPServer as FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_tests():
    print("=" * 60)
    print("EU5 Modding MCP Server v2.1.0 (1.4 Beta) - 综合测试")
    print("=" * 60)

    data_dir = root_dir / "mcp-data"
    handler = DataHandler(data_dir)

    # 1. 统计测试
    stats = handler.get_statistics()
    print("\n[Test 1] 数据统计概览:")
    print(f"  总条目: {stats['total_entries']}")
    for k, v in stats['breakdown'].items():
        print(f"  - {k}: {v}")
    assert stats['breakdown']['event_targets'] == 299, f"event_targets 预期 299，实际 {stats['breakdown']['event_targets']}"
    assert stats['breakdown']['modifiers'] >= 2400, f"modifiers 预期 >= 2400，实际 {stats['breakdown']['modifiers']}"
    assert stats['breakdown']['on_actions'] == 159, f"on_actions 预期 159，实际 {stats['breakdown']['on_actions']}"
    assert stats['breakdown']['field_definitions'] >= 100, f"field_definitions 预期 >= 100，实际 {stats['breakdown']['field_definitions']}"
    print("  ✓ 数据统计全部通过！")

    # 2. 搜索测试
    print("\n[Test 2] 搜索功能验证:")

    # 模糊名称搜索
    r1 = handler.search_by_name("building", limit=3)
    print(f"  - search_by_name('building'): 命中 {len(r1)} 条")
    assert len(r1) > 0

    # 修改器搜索 (含分类)
    r2 = handler.search_modifiers("tax", category="country", limit=3)
    print(f"  - search_modifiers('tax', cat='country'): 命中 {len(r2)} 条")
    assert len(r2) > 0

    # 效果搜索
    r3 = handler.search_effects("gold", limit=3)
    print(f"  - search_effects('gold'): 命中 {len(r3)} 条")
    assert len(r3) > 0

    # 触发器搜索
    r4 = handler.search_triggers("has_variable", limit=3)
    print(f"  - search_triggers('has_variable'): 命中 {len(r4)} 条")
    assert len(r4) > 0

    # 事件目标搜索 (Bug 修复验证)
    r5 = handler.search_event_targets("capital", limit=3)
    print(f"  - search_event_targets('capital'): 命中 {len(r5)} 条")
    assert len(r5) > 0

    # on_actions 搜索 (新功能)
    r6 = handler.search_on_actions("pulse", limit=3)
    print(f"  - search_on_actions('pulse'): 命中 {len(r6)} 条")
    assert len(r6) > 0

    # 自定义本地化搜索 (新功能)
    r7 = handler.search_custom_localization("Tooltip", limit=3)
    print(f"  - search_custom_localization('Tooltip'): 命中 {len(r7)} 条")
    assert len(r7) > 0

    print("  ✓ 核心与扩展搜索功能验证通过！")

    # 3. 1.4-beta 知识库与规范测试
    print("\n[Test 3] 1.4 测试版知识库功能验证:")

    # 字段库
    fd = handler.get_field_definition("expedition_types")
    print(f"  - get_field_definition('expedition_types'): 找到 {fd.get('name') if fd else 'None'}")
    assert fd is not None

    fd2 = handler.get_field_definition("estates")
    print(f"  - get_field_definition('estates'): 找到 {fd2.get('name') if fd2 else 'None'}")
    assert fd2 is not None

    # 原版机制深度解析
    vm = handler.get_vanilla_mechanic("army_movement")
    print(f"  - get_vanilla_mechanic('army_movement'): 找到 {vm.get('title') if vm else 'None'}")
    assert vm is not None

    # 避坑指南
    pit = handler.get_modding_pitfalls("EU4")
    print(f"  - get_modding_pitfalls('EU4'): 包含小节数 {len(pit.get('sections', {}))}")
    assert len(pit.get('sections', {})) > 0

    # 术语对照
    gl = handler.search_glossary("market_access")
    print(f"  - search_glossary('market_access'): {gl[0] if gl else 'None'}")
    assert len(gl) > 0

    # 1.4 综述
    summary = handler.get_1_4_beta_summary()
    print(f"  - get_1_4_beta_summary: 版本 {summary.get('version')}")
    assert "1.4" in summary.get("version", "")

    print("  ✓ 1.4 深度知识库功能验证通过！")

    # 4. 模组脚本静态诊断校验器测试
    print("\n[Test 4] 模组脚本诊断校验器验证:")
    bad_snippet = """
    country_event = {
        title = test:0
        trigger = {
            ROOT = {
                event_target:my_target = { exists = yes }
                exists = var:my_counter
            }
        }
        option = {
            name = "ok"
            weight = 100
        }
    }
    """
    lint_result = handler.validate_mod_snippet(bad_snippet)
    print(f"  - 校验结果: 发现 {lint_result['issues_count']} 个问题")
    for issue in lint_result["issues"]:
        print(f"    [{issue['severity']}] {issue['code']}: {issue['message']}")
    assert not lint_result["is_valid"], "坏代码应被标记为 is_valid = False"
    assert any(i["code"] == "EU4_UPPERCASE_SCOPE" for i in lint_result["issues"])
    assert any(i["code"] == "DEPRECATED_EVENT_TARGET" for i in lint_result["issues"])
    assert any(i["code"] == "EU4_LOC_VERSION_SUFFIX" for i in lint_result["issues"])
    print("  ✓ 诊断校验器准确捕获全部 EU4 误用与语法缺陷！")

    # 5. MCP 框架注册与集成测试
    print("\n[Test 5] MCP Server 集成注册测试:")
    mcp = FastMCP("EU5ModifierMCPTest")
    register_tools(mcp, handler)
    register_resources(mcp, handler)
    print("  ✓ FastMCP 工具与资源全部成功注册！")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! EU5 Modding MCP v2.1.0 运行完全正常！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()
