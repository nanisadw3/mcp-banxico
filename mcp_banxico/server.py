"""Servidor MCP oficial para datos económicos y tipo de cambio de Banxico."""

from __future__ import annotations

import json

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:  # pragma: no cover
    from mcp.server.fastmcp import FastMCP as MCPServer

from .client import BanxicoAPIError, BanxicoClient
from .constants import SERIES


def create_server(token: str | None = None) -> MCPServer:
    """Crea y configura una instancia del servidor MCP para Banxico."""
    server = MCPServer(
        name="mcp-banxico",
        instructions=(
            "Servidor MCP para consultar datos económicos oficiales del Banco de México (Banxico). "
            "Proporciona tipos de cambio (USD/MXN FIX y liquidación), inflación (INPC), "
            "valor de las UDIS, tasas de interés (TIIE y Tasa Objetivo) y reservas internacionales."
        ),
    )
    client = BanxicoClient(token=token)

    @server.tool()
    async def tipo_cambio_usd(
        tipo: str = "FIX",
        fecha_inicio: str | None = None,
        fecha_fin: str | None = None,
    ) -> str:
        """Consulta el tipo de cambio oficial peso mexicano vs dólar estadounidense (USD/MXN).

        Args:
            tipo: Modalidad del tipo de cambio. Opciones: 'FIX' (por defecto) o 'LIQUIDACION'.
            fecha_inicio: Fecha inicial en formato YYYY-MM-DD o DD/MM/YYYY (opcional).
            fecha_fin: Fecha final en formato YYYY-MM-DD o DD/MM/YYYY (opcional).
        """
        key = "TIPO_CAMBIO_LIQUIDACION" if tipo.upper() == "LIQUIDACION" else "TIPO_CAMBIO_FIX"
        serie_info = SERIES[key]

        try:
            if fecha_inicio:
                data = await client.get_series_data(serie_info["id"], fecha_inicio, fecha_fin)
                return json.dumps(
                    {
                        "indicador": serie_info["nombre"],
                        "serie_id": serie_info["id"],
                        "observaciones": data.get("datos", []),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            result = await client.get_latest_value(key)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except BanxicoAPIError as e:
            return f"Error al consultar tipo de cambio: {e}"

    @server.tool()
    async def inflacion_mexico(tipo: str = "anual") -> str:
        """Consulta la inflación oficial en México según el INPC de Banxico.

        Args:
            tipo: Tipo de medición de inflación. Opciones: 'anual' (por defecto) o 'mensual'.
        """
        key = "INFLACION_MENSUAL" if tipo.lower() == "mensual" else "INFLACION_ANUAL"
        try:
            result = await client.get_latest_value(key)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except BanxicoAPIError as e:
            return f"Error al consultar inflación: {e}"

    @server.tool()
    async def valor_udis(fecha: str | None = None) -> str:
        """Consulta el valor oficial de las Unidades de Inversión (UDIS) en pesos mexicanos.

        Args:
            fecha: Fecha específica a consultar en formato YYYY-MM-DD o DD/MM/YYYY (opcional).
        """
        serie_info = SERIES["UDIS"]
        try:
            if fecha:
                data = await client.get_series_data(serie_info["id"], fecha, fecha)
                return json.dumps(
                    {
                        "indicador": serie_info["nombre"],
                        "serie_id": serie_info["id"],
                        "observaciones": data.get("datos", []),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            result = await client.get_latest_value("UDIS")
            return json.dumps(result, ensure_ascii=False, indent=2)
        except BanxicoAPIError as e:
            return f"Error al consultar UDIS: {e}"

    @server.tool()
    async def tasa_interes_banxico(tipo: str = "tiie_28") -> str:
        """Consulta las tasas de interés interbancarias y de política monetaria en México.

        Args:
            tipo: Tipo de tasa. Opciones: 'tiie_28' (TIIE a 28 días) o 'objetivo' (Tasa de referencia/fondeo).
        """
        key = "TASA_OBJETIVO" if tipo.lower() == "objetivo" else "TIIE_28"
        try:
            result = await client.get_latest_value(key)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except BanxicoAPIError as e:
            return f"Error al consultar tasa de interés: {e}"

    @server.tool()
    async def reservas_internacionales() -> str:
        """Consulta el saldo de reservas internacionales netas del Banco de México (en millones de dólares)."""
        try:
            result = await client.get_latest_value("RESERVAS_INTERNACIONALES")
            return json.dumps(result, ensure_ascii=False, indent=2)
        except BanxicoAPIError as e:
            return f"Error al consultar reservas internacionales: {e}"

    @server.tool()
    async def consultar_serie_sie(
        id_serie: str,
        fecha_inicio: str | None = None,
        fecha_fin: str | None = None,
    ) -> str:
        """Consulta avanzada para obtener observaciones de cualquier serie económica del catálogo SIE de Banxico.

        Args:
            id_serie: Identificador de la serie oficial (por ejemplo: 'SF43718', 'SP68257', 'SF61745').
            fecha_inicio: Fecha inicial en formato YYYY-MM-DD o DD/MM/YYYY (opcional).
            fecha_fin: Fecha final en formato YYYY-MM-DD o DD/MM/YYYY (opcional).
        """
        try:
            data = await client.get_series_data(id_serie, fecha_inicio, fecha_fin)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except BanxicoAPIError as e:
            return f"Error al consultar serie {id_serie}: {e}"

    return server
