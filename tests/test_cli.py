"""Pruebas para la CLI de mcp-banxico."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from mcp_banxico.cli import test_connection as run_test_connection


def test_test_connection_without_token(capsys):
    with patch.dict("os.environ", {}, clear=True):
        ret = run_test_connection(token=None)
        captured = capsys.readouterr()
        assert ret == 1
        assert "No se detectó la variable de entorno BANXICO_TOKEN" in captured.out


def test_test_connection_success(capsys):
    mock_data = {
        "serie": "TIPO_CAMBIO_FIX",
        "id_serie": "SF43718",
        "nombre": "Tipo de cambio FIX",
        "descripcion": "FIX",
        "fecha": "18/09/2026",
        "valor": "19.95",
    }

    with patch(
        "mcp_banxico.client.BanxicoClient.get_latest_value", new_callable=AsyncMock
    ) as mock_val:
        mock_val.return_value = mock_data
        ret = run_test_connection(token="valid_token")
        captured = capsys.readouterr()
        assert ret == 0
        assert "Éxito: Fecha 18/09/2026, Valor: $19.95 MXN por USD" in captured.out
