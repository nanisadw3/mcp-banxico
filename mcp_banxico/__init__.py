"""mcp-banxico - Servidor MCP oficial para consultar datos económicos y tipo de cambio de Banxico."""

__version__ = "0.1.0"
__author__ = "Inaki Sobera"
__email__ = "inakisobera8@gmail.com"

from .client import BanxicoAPIError, BanxicoClient
from .server import create_server

__all__ = ["BanxicoAPIError", "BanxicoClient", "__version__", "create_server"]
