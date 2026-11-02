"""Servicio de checkout con pasarela simulada (Mock): no se hace ningún cobro real."""
from unittest.mock import Mock

import pytest

from src.application import OrderService
from src.domain import Order


def test_approved_payment_charges_170_for_vip_order_of_200():
    """CP-08 · Éxito · pasarela aprueba."""
    # Arrange
    gateway = Mock()
    gateway.charge.return_value = True
    service = OrderService(gateway)

    # Act
    amount = service.checkout(Order(200, vip=True))

    # Assert
    assert amount == 170
    gateway.charge.assert_called_once_with(170)


def test_rejected_payment_raises_runtime_error_after_charging_170():
    """CP-09 · Error · pasarela rechaza (actividad E5)."""
    gateway = Mock()
    gateway.charge.return_value = False
    service = OrderService(gateway)

    with pytest.raises(RuntimeError, match="payment rejected"):
        service.checkout(Order(200, vip=True))

    gateway.charge.assert_called_once_with(170)


def test_gateway_timeout_propagates_to_the_caller():
    """CP-10 · Límite · la pasarela no responde: el servicio no oculta el error."""
    gateway = Mock()
    gateway.charge.side_effect = TimeoutError("gateway timeout")
    service = OrderService(gateway)

    with pytest.raises(TimeoutError):
        service.checkout(Order(100))

    gateway.charge.assert_called_once_with(100)


def test_known_risk_order_stays_confirmed_when_payment_is_rejected():
    """RIESGO CONOCIDO (E5): hoy se confirma ANTES de cobrar. Prueba de caracterización.

    Cuando se corrija checkout() (cobrar primero, confirmar después), esta prueba debe
    invertirse: el pedido debe quedar en NEW si el pago es rechazado.
    """
    gateway = Mock()
    gateway.charge.return_value = False
    order = Order(100)

    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(order)

    assert order.status == "CONFIRMED"
