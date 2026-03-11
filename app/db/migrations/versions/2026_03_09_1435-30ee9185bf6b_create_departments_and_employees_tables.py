"""create departments and employees tables

Revision ID: 30ee9185bf6b
Revises:
Create Date: 2026-03-09 14:35:50.655158+00:00

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "30ee9185bf6b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_departments_parent_id"), "departments", ["parent_id"], unique=False)

    op.create_table(
        "employees",
        sa.Column("department_id", sa.UUID(), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("position", sa.String(length=200), nullable=False),
        sa.Column("hired_at", sa.Date(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_employees_department_id"), "employees", ["department_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_employees_department_id"), table_name="employees")
    op.drop_table("employees")

    op.drop_index(op.f("ix_departments_parent_id"), table_name="departments")
    op.drop_table("departments")
