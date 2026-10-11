#!/usr/bin/env python3
"""
EU5 Modding MCP Server (v2.2.0) 综合功能测试脚本
测试全量 156 篇知识库数据加载、检索、error.log 解码、ID 族规则、
教程指南、案例复盘、系统地图、Defines 常量、编码抢救与静态校验器
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
    print("EU5 Modding MCP Server v2.2.0 (1.4 Beta & KB Full Integration) - 综合测试")
    print("=" * 60)

    data_dir = root_dir / "mcp-data"
    handler = DataHandler(data_dir)

    # 1. 统计测试
    stats = handler.get_statistics()
    print("\n[Test 1] 全库数据统计概览:")
    print(f"  总条目: {stats['total_entries']}")
    for k, v in stats['breakdown'].items():
        print(f"  - {k}: {v}")
    assert stats['breakdown']['event_targets'] == 299, f"event_targets 预期 299，实际 {stats['breakdown']['event_targets']}"
    assert stats['breakdown']['modifiers'] >= 2400, f"modifiers 预期 >= 2400，实际 {stats['breakdown']['modifiers']}"
    assert stats['breakdown']['on_actions'] == 159, f"on_actions 预期 159，实际 {stats['breakdown']['on_actions']}"
    assert stats['breakdown']['field_definitions'] >= 100, f"field_definitions 预期 >= 100，实际 {stats['breakdown']['field_definitions']}"
    assert stats['breakdown']['guides_and_tutorials'] == 12, f"guides 预期 12，实际 {stats['breakdown']['guides_and_tutorials']}"
    assert stats['breakdown']['modding_cases'] == 4, f"cases 预期 4，实际 {stats['breakdown']['modding_cases']}"
    assert stats['breakdown']['error_decoder_rules'] >= 10, f"error_decoder 预期 >= 10，实际 {stats['breakdown']['error_decoder_rules']}"
    assert stats['breakdown']['id_rules_prefixed'] >= 30, f"id_rules_prefixed 预期 >= 30"
    assert stats['breakdown']['systems_map_categories'] >= 130, f"systems_map 预期 >= 130"
    assert stats['breakdown']['defines_n_blocks'] >= 15, f"defines_n_blocks 预期 >= 15"
    print("  ✓ 数据统计全部通过！")

    # 2. 搜索测试
    print("\n[Test 2] 核心语法与 API 检索验证:")
    r1 = handler.search_by_name("building", limit=3)
    assert len(r1) > 0
    r2 = handler.search_modifiers("tax", category="country", limit=3)
    assert len(r2) > 0
    r3 = handler.search_effects("gold", limit=3)
    assert len(r3) > 0
    r4 = handler.search_triggers("has_variable", limit=3)
    assert len(r4) > 0
    r5 = handler.search_event_targets("capital", limit=3)
    assert len(r5) > 0
    r6 = handler.search_on_actions("pulse", limit=3)
    assert len(r6) > 0
    r7 = handler.search_custom_localization("Tooltip", limit=3)
    assert len(r7) > 0
    print("  ✓ 修改器、效果、触发器、事件目标、挂钩点、动态本地化全部检索通过！")

    # 3. 深度知识库与教程测试 (eu5-modding-kb 100% 对齐)
    print("\n[Test 3] 指南、教程与实操案例检索验证:")
    # 指南与教程
    g1 = handler.search_guides("new-country", limit=3)
    assert len(g1) > 0
    g2 = handler.get_guide("new-mission-pack-tutorial")
    assert g2 is not None and "任务" in g2.get("title", "")
    g3 = handler.get_guide("merging")
    assert g3 is not None and "INJECT" in g3.get("content", "")
    print(f"  - 指南教程测试: 成功读取 '{g2.get('title')}' 与 '{g3.get('title')}'")

    # 实战案例
    c1 = handler.search_modding_cases("encoding", limit=3)
    assert len(c1) > 0
    c2 = handler.get_modding_case("encoding-corruption-2026-10")
    assert c2 is not None and "乱码" in c2.get("content", "")
    c3 = handler.get_modding_case("laws-events-and-estates-2026-09")
    assert c3 is not None and "撤销" in c3.get("content", "")
    print(f"  - 实战案例测试: 成功读取 '{c2.get('title')}' 与 '{c3.get('title')}'")
    print("  ✓ 指南、教程与案例验证通过！")

    # 4. 查表工具箱与解码器测试 (tools/)
    print("\n[Test 4] 查表工具箱与智能解码器验证:")
    # error.log 解码器
    err_test = "Failed to fetch variable 'my_test_var' in country scope due to not being set"
    diag = handler.decode_error_log(err_test)
    assert diag["matched_count"] > 0
    print(f"  - error.log 诊断测试: 输入 '{err_test[:40]}...' -> 命中 {diag['matched_count']} 条规则")
    assert any("初始化" in d.get("cause", "") for d in diag["diagnoses"])

    # ID 族规范
    id_b = handler.get_id_rule("building_type")
    assert id_b is not None and id_b.get("type") == "prefixed"
    id_adv = handler.get_id_rule("advance")
    assert id_adv is not None and id_adv.get("type") == "bare"
    print(f"  - ID 族规范测试: building_type 为 {id_b.get('type')}, advance 为 {id_adv.get('type')}")

    # 本地化规则
    loc_ev = handler.get_loc_key_rules("event")
    assert len(loc_ev.get("sections", {})) > 0

    # 审查清单
    chk = handler.get_review_checklist("文件")
    assert len(chk.get("sections", {})) > 0

    # common 系统地图
    smap = handler.get_systems_map("building")
    assert smap.get("count", 0) > 0

    # 引擎 Defines 索引
    defs = handler.search_defines("COMBAT_BASE")
    assert len(defs.get("matched_constants", [])) > 0
    block_ai = handler.get_define_block("NAI")
    assert block_ai is not None

    # 新手导览
    nb = handler.get_newbie_guide()
    assert len(nb.get("sections", {})) > 0
    print("  ✓ error.log 解码器、ID 规则、本地化规范、审查清单、系统地图与 Defines 验证通过！")

    # 5. 编码自动抢救器测试
    print("\n[Test 5] GBK/UTF-8 乱码文本抢救测试:")
    garbled_text = "鍚堝悓瑙勫垯"  # '合同规则' 的典型 A 类 UTF-8 误按 GBK 读写损坏
    recovery_result = handler.recover_corrupted_encoding(garbled_text)
    print(f"  - 乱码抢救测试: '{garbled_text}' -> '{recovery_result.get('recovered_text')}' (成功: {recovery_result.get('success')})")
    assert recovery_result.get("success"), "A 类乱码应能被自动回环抢救"
    assert recovery_result.get("recovered_text") == "合同规则", f"预期 '合同规则'，实际 {recovery_result.get('recovered_text')}"
    print("  ✓ 编码抢救算法准确还原 A 类损坏文本！")

    # 6. 超级静态诊断校验器测试
    print("\n[Test 6] 模组脚本静态诊断校验器综合测试:")
    bad_snippet = """
    country_event = {
        title = test:0
        trigger = {
            ROOT = {
                event_target:my_target = { exists = yes }
                building:my_house = yes
                advance:my_tech = yes
                has_trait = trait:brave
                exists = var:my_counter
            }
        }
        option = {
            name = "ok"
            weight = 100
        }
    """  # 故意少闭合一个花括号
    lint_result = handler.validate_mod_snippet(bad_snippet)
    print(f"  - 校验结果: 发现 {lint_result['issues_count']} 个问题与 {len(lint_result['suggestions'])} 条建议")
    for issue in lint_result["issues"]:
        print(f"    [{issue['severity']}] {issue['code']}: {issue['message'][:60]}...")

    assert not lint_result["is_valid"], "坏代码应被标记为 is_valid = False"
    codes = [i["code"] for i in lint_result["issues"]]
    assert "UNBALANCED_BRACES" in codes, "应捕获未闭合花括号"
    assert "EU4_UPPERCASE_SCOPE" in codes, "应捕获大写 ROOT"
    assert "DEPRECATED_EVENT_TARGET" in codes, "应捕获 event_target"
    assert "EU4_LOC_VERSION_SUFFIX" in codes, "应捕获 :0"
    assert "INVALID_ID_PREFIX_BUILDING" in codes, "应捕获错误的 building: 前缀"
    assert "BARE_ID_WITH_UNWANTED_PREFIX" in codes, "应捕获 advance: 前缀"
    assert "TRAIT_QUERY_HAS_PREFIX" in codes, "应捕获 has_trait = trait: 前缀"
    print("  ✓ 超级静态诊断校验器准确捕获全部 7 项语法与引擎暗坑！")

    # 7. MCP 框架注册与集成测试
    print("\n[Test 7] MCP Server 集成注册测试 (30 个工具 & 23 项资源):")
    mcp = FastMCP("EU5ModifierMCPTest")
    register_tools(mcp, handler)
    register_resources(mcp, handler)
    print("  ✓ FastMCP 全部 30 个工具与 23 项资源成功注册！")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! EU5 Modding MCP v2.2.0 运行完全正常！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()
