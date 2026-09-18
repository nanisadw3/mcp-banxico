"""Constantes y catalogo de series oficiales del Banco de México (Banxico SIE)."""

from __future__ import annotations

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
        "descripcion": "Tipo de cambio determinado por Banxico para solventar obligaciones en moneda extranjera.",
    },
    "TIPO_CAMBIO_LIQUIDACION": {
        "id": "SF60653",
        "nombre": "Tipo de cambio de Liquidación (Pesos por Dólar)",
        "descripcion": "Tipo de cambio publicado en el Diario Oficial de la Federación aplicable para el día.",
    },
    # Inflación (INPC)
    "INFLACION_MENSUAL": {
        "id": "SP68257",
        "nombre": "Inflación Mensual (INPC)",
        "descripcion": "Variación porcentual mensual del Índice Nacional de Precios al Consumidor.",
    },
    "INFLACION_ANUAL": {
        "id": "SP74625",
        "nombre": "Inflación Anual (INPC)",
        "descripcion": "Variación porcentual anual del Índice Nacional de Precios al Consumidor.",
    },
    "INDICE_INPC": {
        "id": "SP68258",
        "nombre": "Índice General INPC",
        "descripcion": "Nivel del Índice Nacional de Precios al Consumidor.",
    },
    # Unidades de Inversión (UDI)
    "UDIS": {
        "id": "SP68254",
        "nombre": "Valor de la UDI (Pesos por UDI)",
        "descripcion": "Unidades de Inversión cuyo valor en pesos se actualiza con base en la inflación.",
    },
    # Tasas de Interés
    "TIIE_28": {
        "id": "SF61745",
        "nombre": "Tasa de Interés Interbancaria de Equilibrio (TIIE 28 días)",
        "descripcion": "Tasa representativa de operaciones de crédito entre bancos a plazo de 28 días.",
    },
    "TASA_OBJETIVO": {
        "id": "SF43783",
        "nombre": "Tasa de Interés Objetivo (Fondeo)",
        "descripcion": "Tasa de referencia de política monetaria fijada por la Junta de Gobierno de Banxico.",
    },
    # Reservas Internacionales
    "RESERVAS_INTERNACIONALES": {
        "id": "SF46410",
        "nombre": "Reservas Internacionales Netas",
        "descripcion": "Saldo de reservas internacionales del Banco de México en millones de dólares.",
    },
}
