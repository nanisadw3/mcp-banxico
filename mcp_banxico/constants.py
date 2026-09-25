"""Constantes y catalogo de series oficiales del Banco de México (Banxico SIE)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:  # instalado normalmente
    PACKAGE_VERSION = version("mcp-banxico")
except PackageNotFoundError:  # ejecutado desde el árbol de fuentes
    PACKAGE_VERSION = "0.0.0.dev0"

# URL base oficial de la API SIE (Sistema de Información Económica)
BANXICO_API_BASE_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"

# Token público de demostración o URL de solicitud
BANXICO_TOKEN_HELP_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/token"

# Series económicas más relevantes de Banxico
SERIES = {
    # Tipo de Cambio (USD / MXN)
    "TIPO_CAMBIO_FIX": {
        "id": "SF43718",
        "nombre": "Tipo de cambio FIX (Pesos por Dólar)",
        "unidad": "Pesos por dólar",
        "descripcion": "Tipo de cambio determinado por Banxico para solventar obligaciones en moneda extranjera.",
    },
    "TIPO_CAMBIO_LIQUIDACION": {
        "id": "SF60653",
        "nombre": "Tipo de cambio de Liquidación (Pesos por Dólar)",
        "unidad": "Pesos por dólar",
        "descripcion": "Tipo de cambio publicado en el Diario Oficial de la Federación aplicable para el día.",
    },
    # Inflación (INPC)
    "INFLACION_MENSUAL": {
        "id": "SP30577",
        "nombre": "Inflación Mensual (INPC)",
        "unidad": "Por ciento",
        "descripcion": "Variación porcentual mensual del Índice Nacional de Precios al Consumidor.",
    },
    "INFLACION_ANUAL": {
        "id": "SP30578",
        "nombre": "Inflación Anual (INPC)",
        "unidad": "Por ciento",
        "descripcion": "Variación porcentual anual del Índice Nacional de Precios al Consumidor.",
    },
    "INDICE_INPC": {
        "id": "SP1",
        "nombre": "Índice General INPC",
        "unidad": "Índice (base 2018 = 100)",
        "descripcion": "Nivel del Índice Nacional de Precios al Consumidor.",
    },
    # Unidades de Inversión (UDI)
    "UDIS": {
        "id": "SP68257",
        "nombre": "Valor de la UDI (Pesos por UDI)",
        "unidad": "Pesos por UDI",
        "descripcion": "Unidades de Inversión cuyo valor en pesos se actualiza con base en la inflación.",
    },
    # Tasas de Interés
    "TIIE_28": {
        "id": "SF43783",
        "nombre": "Tasa de Interés Interbancaria de Equilibrio (TIIE 28 días)",
        "unidad": "Por ciento anual",
        "descripcion": "Tasa representativa de operaciones de crédito entre bancos a plazo de 28 días.",
    },
    "TASA_OBJETIVO": {
        "id": "SF61745",
        "nombre": "Tasa de Interés Objetivo (Fondeo)",
        "unidad": "Por ciento anual",
        "descripcion": "Tasa de referencia de política monetaria fijada por la Junta de Gobierno de Banxico.",
    },
    # Reservas Internacionales
    "RESERVAS_INTERNACIONALES": {
        "id": "SF43707",
        "nombre": "Reserva Internacional",
        "unidad": "Millones de dólares",
        "descripcion": "Saldo de la reserva internacional del Banco de México, en millones de dólares.",
    },
}
