"""Verifica que cada ID del catálogo apunte a la serie que decimos que es.

Estas pruebas llaman a la API real de Banxico y se omiten si no hay token.
Existen porque un ID equivocado no falla: devuelve datos de otra serie, con
la etiqueta correcta encima. Así se publicó 0.1.2 reportando la cotización
del euro como reserva internacional.

    BANXICO_TOKEN=... pytest tests/test_series_integration.py
"""

from __future__ import annotations

import os
import unicodedata

import httpx
import pytest

from mcp_banxico.constants import BANXICO_API_BASE_URL, SERIES

# Fragmento que debe aparecer en el título oficial de cada serie.
TITULO_ESPERADO = {
    "TIPO_CAMBIO_FIX": "fix",
    "TIPO_CAMBIO_LIQUIDACION": "tipodecambio",
    "INFLACION_MENSUAL": "variacionmensual",
    "INFLACION_ANUAL": "variacionanual",
    "INDICE_INPC": "indicegeneral",
    "UDIS": "valordeudis",
    "TIIE_28": "tiiea28dias",
    "TASA_OBJETIVO": "tasaobjetivo",
    "RESERVAS_INTERNACIONALES": "reservainternacional",
}


def _normaliza(texto: str) -> str:
    """Minúsculas, sin acentos y sin separadores.

    Banxico devuelve algunos títulos con las letras espaciadas
    ('I n d i c e  G e n e r a l'), así que quitamos todo lo que no sea
    alfanumérico antes de comparar.
    """
    sin_acentos = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return "".join(c for c in sin_acentos.lower() if c.isalnum())


requiere_token = pytest.mark.skipif(
    not os.environ.get("BANXICO_TOKEN"),
    reason="requiere BANXICO_TOKEN para consultar la API real",
)


@requiere_token
@pytest.mark.parametrize("clave", sorted(SERIES))
def test_id_apunta_a_la_serie_declarada(clave: str) -> None:
    info = SERIES[clave]
    respuesta = httpx.get(
        f"{BANXICO_API_BASE_URL}/{info['id']}",
        headers={
            "Bmx-Token": os.environ["BANXICO_TOKEN"],
            "Accept": "application/json",
        },
        timeout=20.0,
    )
    respuesta.raise_for_status()

    titulo = respuesta.json()["bmx"]["series"][0]["titulo"]
    esperado = TITULO_ESPERADO[clave]

    assert esperado in _normaliza(titulo), (
        f"{clave} usa el id {info['id']}, cuyo título oficial en Banxico es "
        f"{titulo!r}. Se esperaba encontrar {esperado!r}."
    )


@requiere_token
@pytest.mark.parametrize("clave", sorted(SERIES))
def test_la_serie_devuelve_un_dato(clave: str) -> None:
    """Un id que existe pero no entrega datos también es un fallo silencioso."""
    info = SERIES[clave]
    respuesta = httpx.get(
        f"{BANXICO_API_BASE_URL}/{info['id']}/datos/oportuno",
        headers={
            "Bmx-Token": os.environ["BANXICO_TOKEN"],
            "Accept": "application/json",
        },
        timeout=20.0,
    )
    assert respuesta.status_code == 200, (
        f"{clave} ({info['id']}) respondió HTTP {respuesta.status_code}"
    )

    datos = respuesta.json()["bmx"]["series"][0].get("datos") or []
    assert datos, f"{clave} ({info['id']}) no devolvió observaciones"


def test_todas_las_series_tienen_expectativa() -> None:
    """No se puede añadir una serie al catálogo sin declarar qué debe ser."""
    assert set(SERIES) == set(TITULO_ESPERADO)
