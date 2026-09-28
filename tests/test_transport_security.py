"""El transporte HTTP valida el header Host contra DNS rebinding.

Detrás de un proxy inverso el Host que llega es el nombre público, así que
hay que declararlo explícitamente o el servidor responde 421 a todo.
"""

from __future__ import annotations

from mcp_banxico.cli import build_transport_security


def test_sin_hosts_declarados_no_fuerza_configuracion():
    # Deja que la librería aplique su default para loopback.
    assert build_transport_security([]) is None


def test_el_host_publico_queda_permitido():
    s = build_transport_security(["banxico-mcp.duckdns.org"])
    assert s is not None
    assert s.enable_dns_rebinding_protection is True
    assert "banxico-mcp.duckdns.org" in s.allowed_hosts


def test_se_aceptan_variantes_con_puerto_y_loopback():
    s = build_transport_security(["ejemplo.org"])
    assert "ejemplo.org:*" in s.allowed_hosts, "el proxy puede incluir el puerto"
    assert "127.0.0.1:*" in s.allowed_hosts, "las pruebas locales deben seguir sirviendo"


def test_el_origin_https_del_host_publico_queda_permitido():
    s = build_transport_security(["ejemplo.org"])
    assert "https://ejemplo.org" in s.allowed_origins


def test_no_se_duplican_entradas():
    s = build_transport_security(["ejemplo.org", "ejemplo.org"])
    assert s.allowed_hosts.count("ejemplo.org") == 1
