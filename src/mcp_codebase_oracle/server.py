"""🔮 MCP Codebase Oracle — Ana MCP Server modülü.

Bu sunucu, herhangi bir codebase'i analiz eden, mimari yapıyı çıkaran
ve etki analizi yapan MCP tool'larını sağlar.
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from mcp_codebase_oracle import __version__
from mcp_codebase_oracle.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("mcp_codebase_oracle")

# Create MCP server instance
mcp = FastMCP("Codebase Oracle")

# ═══════════════════════════════════════════════════════════════════════
# Tool imports — her tool modülü kendi @mcp.tool() dekoratörlerini
# register eder. Import sırası önemli değil.
# ═══════════════════════════════════════════════════════════════════════

from mcp_codebase_oracle.tools.architecture_tools import register_architecture_tools
from mcp_codebase_oracle.tools.explain_tools import register_explain_tools
from mcp_codebase_oracle.tools.graph_tools import register_graph_tools
from mcp_codebase_oracle.tools.impact_tools import register_impact_tools
from mcp_codebase_oracle.tools.query_tools import register_query_tools
from mcp_codebase_oracle.tools.scan_tools import register_scan_tools
from mcp_codebase_oracle.tools.visualization_tools import register_visualization_tools

# Register all tools
register_scan_tools(mcp)
register_query_tools(mcp)
register_graph_tools(mcp)
register_impact_tools(mcp)
register_architecture_tools(mcp)
register_explain_tools(mcp)
register_visualization_tools(mcp)

logger.info(f"🔮 Codebase Oracle v{__version__} — tools registered")


def main() -> None:
    """MCP sunucusunu başlat."""
    config = get_config()
    logger.setLevel(config.log_level)
    logger.info(f"Starting Codebase Oracle v{__version__}")
    logger.info(f"Cache dir: {config.cache_dir}")
    mcp.run()


if __name__ == "__main__":
    main()
