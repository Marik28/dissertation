from ..settings import settings

if not settings.test_gui:
    from .ad8400 import AD8400
    from .mcp_4725 import MCP4725
    from .relay import DigitalIORelay
