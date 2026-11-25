"""Run the pinned NotebookLM MCP server over stdio with local guardrails."""

from __future__ import annotations

import importlib.metadata

from fastmcp.server.middleware import Middleware, MiddlewareContext
from notebooklm.mcp.server import create_server

from .guards import check_version, sanitize_args


class GuardMiddleware(Middleware):
    """Sanitize every tool call before upstream sees its arguments."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        message = context.message
        args = dict(getattr(message, "arguments", None) or {})
        safe = sanitize_args(args)
        if safe != args:
            message = message.model_copy(update={"arguments": safe})
            context = context.copy(message=message)
        return await call_next(context)


def main() -> None:
    check_version(importlib.metadata.version("notebooklm-py"))
    server = create_server()
    server.add_middleware(GuardMiddleware())
    server.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
