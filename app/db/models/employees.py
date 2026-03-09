from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import SQLAlchemyBase


if TYPE_CHECKING:
    from .departments import Department


class Employee(SQLAlchemyBase):
    """Employee ORM model"""

    __tablename__ = "employees"

    department_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    position: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    hired_at: Mapped[date | None] = mapped_column(sa.Date, nullable=True)

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="employees",
    )
