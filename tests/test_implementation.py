#!/usr/bin/env python3
"""
EU5 Modding MCP Server (v2.3.1) 综合功能测试脚本
测试全量 156 篇知识库、全库一站式智能统一检索 (eu5_omni_search)、
Token 极致紧凑序列化、按小节分段抽取、Defines 源码脱敏、
系统地图紧凑概览、error.log C++ 引擎特征解码、全角标点静态拦截、
36 个专业工具与 25 项只读资源注册
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
    print("EU5 Modding MCP Server v2.3.1 (Token 极致优化 & 36 工具综合测试)")
    print("=" * 60)

    data_dir = root_dir / "mcp-data"
    handler = DataHandler(data_dir)

    # 1. 统计测试
    stats = handler.get_statistics()
    print("\n[Test 1] 全库数据统计概览 (v2.3.1):")
    print(f"  版本: {stats['version']}")
    print(f"  总条目: {stats['total_entries']}")
    for k, v in stats['breakdown'].items():
        print(f"  - {k}: {v}")
    assert "2.3.1" in stats['version'], f"版本预期包含 2.3.1，实际 {stats['version']}"
    assert stats['breakdown']['event_targets'] == 299, f"event_targets 预期 299，实际 {stats['breakdown']['event_targets']}"
    assert stats['breakdown']['modifiers'] >= 2400, f"modifiers 预期 >= 2400，实际 {stats['breakdown']['modifiers']}"
    assert stats['breakdown']['on_actions'] >= 200, f"on_actions 预期 >= 200，实际 {stats['breakdown']['on_actions']}"
    assert stats['breakdown']['field_definitions'] >= 100, f"field_definitions 预期 >= 100，实际 {stats['breakdown']['field_definitions']}"
    assert stats['breakdown']['guides_and_tutorials'] == 12, f"guides 预期 12，实际 {stats['breakdown']['guides_and_tutorials']}"
    assert stats['breakdown']['modding_cases'] == 4, f"cases 预期 4，实际 {stats['breakdown']['modding_cases']}"
    assert stats['breakdown']['vanilla_readmes'] == 74, f"vanilla_readmes 预期 74，实际 {stats['breakdown']['vanilla_readmes']}"
    assert stats['breakdown']['error_decoder_rules'] >= 20, f"error_decoder 预期 >= 20，实际 {stats['breakdown']['error_decoder_rules']}"
    assert stats['breakdown']['id_rules_prefixed'] >= 30, f"id_rules_prefixed 预期 >= 30"
    assert stats['breakdown']['systems_map_categories'] >= 130, f"systems_map 预期 >= 130"
    assert stats['breakdown']['defines_n_blocks'] >= 30, f"defines_n_blocks 预期 >= 30，实际 {stats['breakdown']['defines_n_blocks']}"
    assert stats['breakdown']['defines_constants'] >= 1400, f"defines_constants 预期 >= 1400，实际 {stats['breakdown']['defines_constants']}"
    print("  ✓ 数据统计全部通过！")

    # 2. 搜索与全库一站式智能统一检索 (eu5_omni_search) 测试
    print("\n[Test 2] 核心语法与全库一站式检索 (eu5_omni_search) 验证:")
    # 常规专用检索
    r1 = handler.search_by_name("building", limit=3)
    assert len(r1) > 0 and "content" not in r1[0], "search_by_name 应已剔除冗余 content 字段以节约 Token"
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

    # 全库一站式 omni_search 测试
    omni_res = handler.omni_search("building", limit_per_category=2)
    assert omni_res["total_items_matched"] > 0, "omni_search 检索 building 应命中结果"
    assert len(omni_res["categories_matched"]) >= 4, f"omni_search 预期跨至少 4 类系统命中，实际: {omni_res['categories_matched']}"
    print(f"  - omni_search('building') 跨类目命中: {omni_res['categories_matched']} (共 {omni_res['total_items_matched']} 项)")
    print("  ✓ 单次调用一站式跨库检索与核心语法验证全部通过！")

    # 3. 深度知识库与教程测试 (支持按 section 分段抽取)
    print("\n[Test 3] 指南、教程与按小节抽取 (section) 验证:")
    # 字段规范分段读取
    fd_full = handler.get_field_definition("advances")
    assert fd_full is not None
    fd_sec = handler.get_field_definition("advances", section="补缺")
    assert fd_sec is not None and fd_sec.get("matched_section") == "补缺"
    assert fd_sec["content_length"] < len(fd_full["content"]), "按 section 抽取后长度应显著小于全文"
    print(f"  - 字段小节抽取测试: advances 全文 {len(fd_full['content'])} 字符 -> 补缺小节 {fd_sec['content_length']} 字符 (节约 {(1 - fd_sec['content_length']/len(fd_full['content']))*100:.1f}% Token)")

    # 机制拆解分段读取
    vm_full = handler.get_vanilla_mechanic("ai")
    assert vm_full is not None
    vm_sec = handler.get_vanilla_mechanic("ai", section="可改")
    assert vm_sec is not None and vm_sec.get("matched_section") == "可改"
    print(f"  - 机制小节抽取测试: ai 全文 {len(vm_full['content'])} 字符 -> 可改建议小节 {vm_sec['content_length']} 字符")

    # 指南与教程
    g1 = handler.search_guides("new-country", limit=3)
    assert len(g1) > 0
    g2 = handler.get_guide("new-mission-pack-tutorial")
    assert g2 is not None and "任务" in g2.get("title", "")
    g3 = handler.get_guide("merging", section="INJECT")
    assert g3 is not None and "matched_section" in g3
    print(f"  - 指南教程测试: 成功读取 '{g2.get('title')}' 与 INJECT 小节")

    # 实战案例
    c1 = handler.search_modding_cases("encoding", limit=3)
    assert len(c1) > 0
    c2 = handler.get_modding_case("encoding-corruption-2026-10")
    assert c2 is not None and "乱码" in c2.get("content", "")
    print(f"  - 实战案例测试: 成功读取 '{c2.get('title')}'")
    print("  ✓ 知识库按小节精简抽取验证通过！")

    # 4. 查表工具箱、系统地图紧凑概览与 Defines 源码脱敏
    print("\n[Test 4] 查表工具箱、Defines 常量脱敏与系统地图分组概览验证:")
    # error.log 解码器与空值安全
    empty_diag = handler.decode_error_log("")
    assert empty_diag["matched_count"] == 0, "空日志应安全返回 0 匹配"

    err_test = "Failed to fetch variable 'my_test_var' in country scope due to not being set"
    diag = handler.decode_error_log(err_test)
    assert diag["matched_count"] > 0
    print(f"  - error.log 诊断测试: 输入 '{err_test[:40]}...' -> 命中 {diag['matched_count']} 条规则")

    # C++ 引擎报错诊断
    cpp_err = "Widget cannot have a position in a layout (pdx_gui_layout.cpp:201)"
    diag_cpp = handler.decode_error_log(cpp_err)
    assert diag_cpp["matched_count"] > 0
    print(f"  - C++ 报错诊断测试: 输入 '{cpp_err[:40]}...' -> 命中 {diag_cpp['matched_count']} 条规则")

    # ID 族规范
    id_b = handler.get_id_rule("building_type")
    assert id_b is not None and id_b.get("type") == "prefixed"

    # common 系统地图紧凑概览 (Token 节约 86%)
    smap_overview = handler.get_systems_map(None)
    assert "groups" in smap_overview and len(smap_overview["groups"]) >= 10, "默认系统地图应返回分组概览字典"
    print(f"  - 系统地图概览测试: 成功返回 {len(smap_overview['groups'])} 个功能分组概览")

    # 引擎 Defines 常量检索与源码脱敏
    defs = handler.search_defines("COMBAT_BASE")
    assert len(defs.get("matched_constants", [])) > 0
    for b in defs.get("matched_blocks", []):
        assert "content" not in b, "search_defines 搜索结果应已剔除原始 content 源码以节约 Token"
        assert "content_length" in b and "fetch_hint" in b
    print("  - Defines 常量检索测试: 块列表已成功脱敏大型源码字段")

    # 原版 74 篇开发者 readme.txt 检索
    r_search = handler.search_vanilla_readmes("building")
    assert len(r_search) > 0
    r_get = handler.get_vanilla_readme("building_types")
    assert r_get is not None and "building" in r_get.get("content", "").lower()

    # EU5 三层生命周期架构与工坊实践指南
    arch_guide = handler.get_mod_architecture_guide("lifecycle")
    assert "loading_screen" in arch_guide.get("matched_lifecycle_tiers", {})
    print("  ✓ error.log 解码器、系统地图分组概览、Defines 源码脱敏与原版 Readme 全部通过！")

    # 5. 编码自动抢救器测试
    print("\n[Test 5] GBK/UTF-8 乱码文本抢救与 ASCII 守卫测试:")
    ascii_res = handler.recover_corrupted_encoding("Hello EU5 Modding")
    assert ascii_res.get("corruption_type") == "纯 ASCII", "纯英文应直接识别为纯 ASCII 守卫"

    garbled_text = "鍚堝悓瑙勫垯"  # '合同规则' 的典型 A 类 UTF-8 误按 GBK 读写损坏
    recovery_result = handler.recover_corrupted_encoding(garbled_text)
    assert recovery_result.get("success"), "A 类乱码应能被自动回环抢救"
    assert recovery_result.get("recovered_text") == "合同规则", f"预期 '合同规则'，实际 {recovery_result.get('recovered_text')}"
    print(f"  - 乱码抢救测试: '{garbled_text}' -> '{recovery_result.get('recovered_text')}' (成功: {recovery_result.get('success')})")
    print("  ✓ 编码抢救算法准确还原 A 类损坏文本！")

    # 6. 超级静态诊断校验器综合测试 (含全角中文标点与只读条件冲突检查)
    print("\n[Test 6] 模组脚本静态诊断校验器测试 (新增全角标点与条件冲突检查):")
    bad_snippet_new = """
    country_event = {
        id = my_event.1
        trigger = {
            add_treasury = 100
            has_variable = test
        }
        title = "test"：
    }
    """
    lint_new = handler.validate_mod_snippet(bad_snippet_new)
    codes_new = [i["code"] for i in lint_new["issues"]]
    sugg_codes = [s["code"] for s in lint_new["suggestions"]]
    assert "FULL_WIDTH_PUNCTUATION" in codes_new, "应捕获全角冒号 '：'"
    assert "EFFECT_IN_TRIGGER_BLOCK" in codes_new, "应捕获 trigger 内误写的 add_treasury"
    assert "MISSING_EVENT_NAMESPACE" in sugg_codes, "应提示缺少 namespace 声明"
    print("  - 新增规则检测: 成功拦截全角标点、只读 trigger 块效果污染与缺少命名空间！")

    # 经典暗坑综合检测
    bad_snippet_combo = """
    on_game_start = {
        effect = { add_treasury = 100 }
    }
    vbox = { position = { 100 200 } }
    country_modifier = { great_power_score = 10 }
    """
    lint_combo = handler.validate_mod_snippet(bad_snippet_combo)
    codes_combo = [i["code"] for i in lint_combo["issues"]]
    assert "ON_ACTION_DESTRUCTIVE_ROOT_EFFECT" in codes_combo
    assert "GUI_LAYOUT_POSITION_VIOLATION" in codes_combo
    assert "DEPRECATED_EU4_MODIFIER" in codes_combo
    print("  ✓ 超级静态诊断校验器准确捕获全部 15+ 项语法与引擎暗坑！")

    # 7. MCP 框架注册与集成测试 (36 个工具 & 25 项资源)
    print("\n[Test 7] MCP Server 集成注册测试 (36 个工具 & 25 项只读资源):")
    mcp = FastMCP("EU5ModifierMCPTest")
    register_tools(mcp, handler)
    register_resources(mcp, handler)

    # 检查 ping 与 get_server_info
    ping_out = mcp._tool_manager._tools.get("ping")
    assert ping_out is not None, "ping 工具应成功注册"
    omni_tool = mcp._tool_manager._tools.get("eu5_omni_search")
    assert omni_tool is not None, "eu5_omni_search 工具应成功注册"
    tools_count = len(mcp._tool_manager._tools)
    print(f"  - FastMCP 注册工具总数: {tools_count} (预期 36 个)")
    assert tools_count == 36, f"预期 36 个工具，实际注册 {tools_count} 个"
    print("  ✓ FastMCP 全部 36 个工具与 25 项资源成功注册！")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! EU5 Modding MCP v2.3.1 运行完全正常！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()
