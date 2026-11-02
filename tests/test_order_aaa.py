"""Pruebas unitarias del dominio (sin BD, sin red) con estructura Arrange-Act-Assert."""
import pytest

from src.domain import CustomerHasDebt, Order


def test_vip_order_of_200_is_charged_170_and_confirmed():
    """CP-01 · Éxito · Regla: pedido VIP recibe 15% de descuento."""
    # Arrange
    order = Order(total=200, vip=True)

    # Act
    amount_to_charge = order.confirm()

    # Assert
    assert amount_to_charge == 170
    assert order.discount == 30
    assert order.status == "CONFIRMED"


def test_regular_order_of_200_has_no_discount():
    """CP-02 · Éxito · Regla: cliente regular no recibe descuento."""
    order = Order(total=200)

    amount_to_charge = order.confirm()

    assert amount_to_charge == 200
    assert order.discount == 0


def test_customer_with_debt_cannot_confirm_and_order_stays_new():
    """CP-04 · Error · Regla: deuda pendiente bloquea la confirmación."""
    order = Order(total=100)

    with pytest.raises(CustomerHasDebt):
        order.confirm(customer_debt=50)

    assert order.status == "NEW"  # el fallo no debe mutar el estado


def test_vip_minimum_amount_boundary_keeps_one_cent():
    """CP-05 · Límite · 0.01 VIP: el descuento redondeado es 0.00."""
    order = Order(total=0.01, vip=True)

    amount_to_charge = order.confirm()

    assert amount_to_charge == pytest.approx(0.01)
    assert order.discount == 0.0
