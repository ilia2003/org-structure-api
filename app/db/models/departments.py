from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import SQLAlchemyBase


if TYPE_CHECKING:
    from .employees import Employee


class Department(SQLAlchemyBase):
    """Department ORM model"""

    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        sa.ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    parent: Mapped[Department | None] = relationship(
        "Department",
        remote_side="Department.id",
        back_populates="children",
    )
    children: Mapped[list[Department]] = relationship(
        "Department",
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
