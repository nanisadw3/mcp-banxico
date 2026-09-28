"""Cliente HTTP asíncrono para consumir la API oficial del Banco de México (SIE)."""

from __future__ import annotations

import asyncio
import os
from time import monotonic
from typing import Any

import httpx

from .constants import (
    BANXICO_API_BASE_URL,
    BANXICO_TOKEN_HELP_URL,
    PACKAGE_VERSION,
    SERIES,
)


class BanxicoAPIError(Exception):
    """Excepción para errores al consultar la API de Banxico."""



class BanxicoClient:
    """Cliente para interactuar con la API SIE de Banxico."""

    #: TTL por defecto de la caché, en segundos. Las series del SIE se
    #: actualizan una vez al día como mucho, así que una hora es conservador.
    DEFAULT_CACHE_TTL = 3600.0

    #: Cota de entradas. `consultar_serie_sie` acepta IDs arbitrarios, así que
    #: sin límite un cliente hostil podría hacer crecer la memoria a voluntad.
    DEFAULT_CACHE_MAX_ENTRIES = 512

    def __init__(
        self,
        token: str | None = None,
        timeout: float = 10.0,
        cache_ttl: float | None = None,
        cache_max_entries: int | None = None,
    ):
        self.token = token or os.environ.get("BANXICO_TOKEN", "")
        self.timeout = timeout
        if cache_ttl is None:
            cache_ttl = float(os.environ.get("BANXICO_CACHE_TTL", self.DEFAULT_CACHE_TTL))
        self.cache_ttl = cache_ttl
        if cache_max_entries is None:
            cache_max_entries = int(
                os.environ.get("BANXICO_CACHE_MAX_ENTRIES", self.DEFAULT_CACHE_MAX_ENTRIES)
            )
        self.cache_max_entries = cache_max_entries
        # clave -> (momento de expiración, resultado)
        self._cache: dict[tuple[str, str, str], tuple[float, dict[str, Any]]] = {}
        # Un lock por clave evita que N peticiones simultáneas en frío se
        # conviertan en N consultas al SIE; solo la primera va a la red.
        self._locks: dict[tuple[str, str, str], asyncio.Lock] = {}

    def _cache_get(self, key: tuple[str, str, str]) -> dict[str, Any] | None:
        entrada = self._cache.get(key)
        if entrada is None:
            return None
        expira_en, valor = entrada
        if monotonic() >= expira_en:
            self._cache.pop(key, None)
            return None
        return valor

    def _cache_put(self, key: tuple[str, str, str], valor: dict[str, Any]) -> None:
        if self.cache_ttl <= 0:
            return
        self._cache[key] = (monotonic() + self.cache_ttl, valor)
        self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        """Mantiene caché y locks dentro de la cota, tirando lo más viejo primero."""
        if len(self._cache) > self.cache_max_entries:
            # dict conserva orden de inserción: el frente es lo más antiguo.
            for key in list(self._cache)[: len(self._cache) - self.cache_max_entries]:
                self._cache.pop(key, None)
        if len(self._locks) > self.cache_max_entries:
            for key in list(self._locks):
                if len(self._locks) <= self.cache_max_entries:
                    break
                lock = self._locks.get(key)
                # Nunca tiramos un lock en uso: quien lo espera quedaría suelto.
                if lock is not None and not lock.locked():
                    self._locks.pop(key, None)

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": f"mcp-banxico/{PACKAGE_VERSION} (https://github.com/nanisadw3/mcp-banxico)",
        }
        if self.token:
            headers["Bmx-Token"] = self.token
        return headers

    async def get_series_data(
        self,
        series_id: str,
        fecha_inicio: str | None = None,
        fecha_fin: str | None = None,
    ) -> dict[str, Any]:
        """Consulta observaciones para una serie de Banxico.

        Si no se especifican fechas, consulta el dato oportuno (más reciente).
        """
        if not self.token:
            raise BanxicoAPIError(
                "No se encontró el token de Banxico. "
                f"Obtén tu token gratuito en {BANXICO_TOKEN_HELP_URL} "
                "y configúralo en la variable de entorno BANXICO_TOKEN."
            )

        key = (series_id, fecha_inicio or "", fecha_fin or "")

        en_cache = self._cache_get(key)
        if en_cache is not None:
            return en_cache

        if self.cache_ttl <= 0:
            return await self._fetch_series_data(series_id, fecha_inicio, fecha_fin)

        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            # Otra corrutina pudo haberla poblado mientras esperábamos el lock.
            en_cache = self._cache_get(key)
            if en_cache is not None:
                return en_cache

            resultado = await self._fetch_series_data(series_id, fecha_inicio, fecha_fin)
            # Solo llegamos aquí si no hubo excepción: los errores no se cachean.
            self._cache_put(key, resultado)
            return resultado

    async def _fetch_series_data(
        self,
        series_id: str,
        fecha_inicio: str | None = None,
        fecha_fin: str | None = None,
    ) -> dict[str, Any]:
        """Consulta la API de Banxico sin pasar por la caché."""
        if fecha_inicio and fecha_fin:
            url = f"{BANXICO_API_BASE_URL}/{series_id}/datos/{fecha_inicio}/{fecha_fin}"
        elif fecha_inicio:
            url = f"{BANXICO_API_BASE_URL}/{series_id}/datos/{fecha_inicio}/{fecha_inicio}"
        else:
            url = f"{BANXICO_API_BASE_URL}/{series_id}/datos/oportuno"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=self._get_headers())
            except httpx.RequestError as e:
                raise BanxicoAPIError(f"Error de red al conectar con Banxico: {e}") from e

            if response.status_code == 401 or response.status_code == 403:
                raise BanxicoAPIError(
                    "Token de Banxico inválido o no autorizado. "
                    f"Verifica tu clave en {BANXICO_TOKEN_HELP_URL}."
                )
            if response.status_code != 200:
                raise BanxicoAPIError(
                    f"Banxico respondió con código HTTP {response.status_code}: {response.text}"
                )

            try:
                data = response.json()
            except Exception as e:
                raise BanxicoAPIError(f"Error al decodificar respuesta JSON de Banxico: {e}") from e

        series_list = data.get("bmx", {}).get("series", [])
        if not series_list:
            raise BanxicoAPIError(f"No se encontraron datos para la serie '{series_id}'.")

        serie = series_list[0]
        return {
            "id_serie": serie.get("idSerie"),
            "titulo": serie.get("titulo"),
            "datos": serie.get("datos", []),
        }

    async def get_latest_value(self, series_key: str) -> dict[str, Any]:
        """Obtiene el último valor registrado de una serie del catálogo."""
        if series_key not in SERIES:
            raise BanxicoAPIError(f"Serie '{series_key}' no reconocida en el catálogo.")

        info = SERIES[series_key]
        raw = await self.get_series_data(info["id"])
        datos = raw.get("datos", [])
        ultimo = datos[-1] if datos else {}

        return {
            "serie": series_key,
            "id_serie": info["id"],
            "nombre": info["nombre"],
            "unidad": info["unidad"],
            "descripcion": info["descripcion"],
            "fecha": ultimo.get("fecha", "N/D"),
            "valor": ultimo.get("dato", "N/D"),
        }
