"""Autorización de cancelación: roles, propietario, estado y antigüedad (fechas fijas)."""
from datetime import UTC, datetime, timedelta

import pytest

from src.security import can_cancel

NOW = datetime(2026, 11, 1, 12, 0, 0, tzinfo=UTC)  # fecha fija: resultados reproducibles


def test_admin_can_cancel_new_order_of_another_user():
    """CP-13 · Éxito · el administrador cancela un pedido NEW ajeno."""
    # Arrange
    created_at = NOW - timedelta(hours=1)

    # Act
    allowed = can_cancel("NEW", owner_id=1, user_id=99, is_admin=True, created_at=created_at, now=NOW)

    # Assert
    assert allowed is True


def test_owner_cannot_cancel_at_exactly_24_hours():
    """CP-14 · Límite · a las 24h exactas se rechaza (la regla usa < 24h)."""
    created_at = NOW - timedelta(hours=24)

    allowed = can_cancel("NEW", owner_id=1, user_id=1, is_admin=False, created_at=created_at, now=NOW)

    assert allowed is False


def test_owner_can_cancel_one_second_before_24_hours():
    """CP-16 · Límite · 23h 59m 59s todavía se permite."""
    created_at = NOW - timedelta(hours=23, minutes=59, seconds=59)

    allowed = can_cancel("NEW", owner_id=1, user_id=1, is_admin=False, created_at=created_at, now=NOW)

    assert allowed is True


@pytest.mark.parametrize(
    ("status", "is_admin", "is_owner", "age_hours", "expected"),
    [
        ("NEW", False, True, 1, True),         # propietario dentro de 24h
        ("NEW", False, True, 24, False),       # propietario, límite exacto
        ("NEW", False, True, 25, False),       # propietario, vencido
        ("NEW", False, False, 1, False),       # usuario ajeno
        ("NEW", True, False, 100, True),       # admin ajeno, aunque sea antiguo
        ("CONFIRMED", True, False, 1, True),   # admin sobre pedido confirmado
        ("SHIPPED", True, False, 1, False),    # SHIPPED nunca, ni admin
        ("SHIPPED", False, True, 1, False),    # SHIPPED nunca, ni propietario
    ],
)
def test_authorization_matrix(status, is_admin, is_owner, age_hours, expected):
    """CP-15 y matriz E6: rol x propietario x estado x antigüedad."""
    user_id = 1 if is_owner else 2
    created_at = NOW - timedelta(hours=age_hours)

    allowed = can_cancel(status, owner_id=1, user_id=user_id, is_admin=is_admin,
                         created_at=created_at, now=NOW)

    assert allowed is expected
