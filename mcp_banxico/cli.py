"""Interfaz de línea de comandos para mcp-banxico."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from . import __version__
from .client import BanxicoAPIError, BanxicoClient
from .constants import BANXICO_TOKEN_HELP_URL, SERIES
from .server import create_server


def test_connection(token: str | None = None) -> int:
    """Prueba la conexión a la API de Banxico consultando los datos más recientes."""
    print("=" * 60)
    print(f"mcp-banxico v{__version__} - Verificación de Conexión a Banxico SIE")
    print("=" * 60)

    effective_token = token or os.environ.get("BANXICO_TOKEN")
    if not effective_token:
        print("\n[AVISO] No se detectó la variable de entorno BANXICO_TOKEN.")
        print(f"Para obtener un token oficial gratuito, visita: {BANXICO_TOKEN_HELP_URL}\n")
        print("Ejemplo de uso:")
        print('  export BANXICO_TOKEN="tu_token_aqui"')
        print("  mcp-banxico\n")
        return 1

    client = BanxicoClient(token=effective_token)

    async def _run():
        print(f"Consultando tipo de cambio FIX (serie {SERIES['TIPO_CAMBIO_FIX']['id']})...")
        try:
            res = await client.get_latest_value("TIPO_CAMBIO_FIX")
            print(f"-> Éxito: Fecha {res['fecha']}, Valor: ${res['valor']} MXN por USD")
            return 0
        except BanxicoAPIError as e:
            print(f"[ERROR] Falló la consulta a Banxico: {e}")
            return 1

    return asyncio.run(_run())


def main() -> None:
    """Punto de entrada principal para el comando mcp-banxico."""
    parser = argparse.ArgumentParser(
        prog="mcp-banxico",
        description="Servidor MCP oficial para consultar datos económicos y tipo de cambio de Banxico.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"mcp-banxico {__version__}",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Token de la API de Banxico SIE (o configurar variable BANXICO_TOKEN)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Verifica la conectividad con la API de Banxico y muestra el tipo de cambio FIX",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Tipo de transporte para el protocolo MCP (por defecto: stdio)",
    )

    args = parser.parse_args()

    if args.test:
        sys.exit(test_connection(args.token))

    # Iniciar servidor MCP en modo stdio (o sse)
    server = create_server(token=args.token)
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()
