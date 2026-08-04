"""Shared HTTP dependencies.

Database session injection is defined in ``dummy_hospital.db.session`` so that
Alembic and non-HTTP callers can use the same infrastructure.
"""

from dummy_hospital.db.session import get_session

__all__ = ["get_session"]
