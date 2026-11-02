# Unidad 5 CLN · Pruebas, integración y calidad

Proyecto de pedidos con dominio, servicio de cobro, repositorio SQLAlchemy y política de
autorización, validado con pruebas unitarias, de integración y con mocks, cobertura y CI.

## Instalación

**Windows (PowerShell)**
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt

**macOS / Linux**
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt

## Comandos

    python -m pytest -v                                  # todas las pruebas
    python -m ruff check src tests                       # estilo
    python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80

El reporte HTML queda en `htmlcov/index.html`. El umbral mínimo de cobertura es 80%.

## Arquitectura

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Dominio | `src/domain.py` | `Order`: descuento VIP 15%, total positivo, deuda, no confirmar dos veces |
| Aplicación | `src/application.py` | `OrderService.checkout`: confirma y cobra mediante una pasarela inyectada |
| Persistencia | `src/repository.py` | `SqlOrderRepository` con SQLAlchemy; sesión como límite transaccional |
| Seguridad | `src/security.py` | `can_cancel`: reglas por rol, propietario, estado y antigüedad |

## Estrategia de pruebas

| Tipo | Archivos | Qué demuestra |
|---|---|---|
| Unitarias (AAA) | `test_order.py`, `test_order_aaa.py` | Reglas de negocio sin BD ni red |
| TDD | `test_order.py::test_cannot_confirm_twice` | Ciclo Red, Green, Refactor |
| Integración | `test_repository*.py` | Commit y rollback con SQLite en memoria |
| Mocks | `test_service*.py` | Pasarela aprobada, rechazada y timeout, sin cobros reales |
| Seguridad | `test_security*.py` | Matriz de autorización con fechas fijas |

La matriz completa de 16 casos está en `matriz_casos_pruebas.csv`.

## Integración continua

`.github/workflows/ci.yml` ejecuta en cada push y pull request: Ruff, pytest con
`--cov-fail-under=80` y `compileall`. Para que bloquee merges hay que activar
branch protection o rulesets en GitHub.

## Decisiones de diseño y riesgos conocidos

- `pythonpath = ["."]` en `pyproject.toml`: el primer CI falló porque `pytest` a secas no
  encontraba `src`, aunque `python -m pytest` sí funcionaba en local.
- **Riesgo:** `checkout()` confirma el pedido antes de cobrar; si el pago es rechazado el
  pedido queda `CONFIRMED`. Está documentado con una prueba de caracterización. Mejora
  propuesta: cobrar primero y confirmar solo si la pasarela aprueba.
- `checkout()` no pasa la deuda del cliente a `confirm()`, por lo que esa regla no se aplica
  por esa vía.
- SQLite en memoria no sustituye pruebas contra el motor de producción (por ejemplo PostgreSQL).
- La cobertura mide líneas ejecutadas, no defectos detectados: por ejemplo, el valor por
  defecto de `now` en `can_cancel` cuenta como cubierto sin que ninguna prueba lo use.

## Adaptación al PIA

Pendiente: documentar al menos tres reglas de la empresa con un caso de éxito, uno de error
y uno límite cada una (mínimo nueve casos).
