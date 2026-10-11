---
description: 诊断分析 error.log 报错文本，精准匹配 23 组 Jomini C++ 引擎报错特征并给出病因与首查点
argument: log_text
---

使用 EU5 Modding MCP 工具 `decode_error_log` 诊断用户提供的报错文本 `$ARGUMENTS`。结合 Jomini C++ 引擎源码定位（如 `lexer.cpp`, `pdx_gui_layout.cpp`, `pdx_localize.cpp`），指出确切病因、排查优先级与修复方案。
