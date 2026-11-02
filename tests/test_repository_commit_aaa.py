"""Integración con SQLite en memoria: commit y rollback (cada prueba crea su propio motor)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain import Order
from src.repository import OrderRow, SqlOrderRepository, make_engine


def test_committed_order_is_persisted_with_id_total_and_status():
    """CP-11 · Éxito · E4: guardar id=2, total=250 y hacer commit."""
    # Arrange
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(2, Order(250))

        # Act
        session.commit()

    # Assert: se lee desde una sesión NUEVA, así se prueba que realmente persistió
    with Session(engine) as new_session:
        row = new_session.scalar(select(OrderRow).where(OrderRow.id == 2))
        assert row is not None
        assert row.id == 2
        assert row.total == 250
        assert row.status == "NEW"


def test_rolled_back_order_is_not_persisted_in_a_new_session():
    """CP-12 · Error · rollback descarta el pedido aunque se consulte desde otra sesión."""
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(3, Order(80))

        session.rollback()

    with Session(engine) as new_session:
        assert new_session.scalar(select(OrderRow).where(OrderRow.id == 3)) is None
