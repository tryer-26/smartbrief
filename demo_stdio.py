# -*- coding: utf-8 -*-
# ============================================================
# 演示：在真实终端建立 MCP stdio 会话并调用 web_search 工具
# 运行：cd smartbrief && python demo_stdio.py
# ============================================================
import asyncio
import json
import sys
from pathlib import Path


# 定位 backend/（与 notebook Cell 1 相同的自动定位逻辑）
def _find_backend(start: Path) -> Path:
    p = start
    while True:
        if (p / "backend").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    for sub in sorted(start.iterdir()):
        if sub.is_dir() and (sub / "backend").exists():
            return sub
    raise RuntimeError("未找到 backend/ 目录，请在 smartbrief/ 下运行")


root = _find_backend(Path(__file__).resolve().parent)
sys.path.insert(0, str(root / "backend"))

from mcp_client.mcp_client import StdioConnection, _to_openai_schema  # noqa: E402


async def demo_stdio():
    # 新建一个独立的 stdio 连接（拉起 web_search_server.py 子进程）
    conn = StdioConnection({
        "id": "demo", "name": "demo", "kind": "stdio", "url": "",
        "description": "演示", "enabled": True, "builtin": True,
    })
    try:
        await conn.start()
        print("[OK] MCP stdio 会话建立成功")
        print(f"  会话状态: is_running={conn.is_running}")

        tools = await conn.list_tools()
        print(f"  [OK] 发现 {len(tools)} 个工具:")
        for t in tools:
            schema = _to_openai_schema(t)
            print(f"       • {t['name']} -> "
                  f"{json.dumps(schema, ensure_ascii=False)[:80]}...")

        result = await conn.call_tool("web_search",
                                      {"query": "智能手表 2026", "num_results": 2})
        print(f"  [OK] 调用 web_search 结果 source = {result.get('source')}")
        print(f"       results 条数 = {len(result.get('results', []))}")
    except Exception as exc:
        print(f"[NO] 连接失败: {exc}")
    finally:
        await conn.close()
        print("  [OK] 会话已关闭")


if __name__ == "__main__":
    asyncio.run(demo_stdio())
