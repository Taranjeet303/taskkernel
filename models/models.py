from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, Text, String, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# -------------------------
# Execution status
# -------------------------

class ExecutionStatus(str, Enum):
    SUBMITTED = "submitted"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# -------------------------
# Script
# -------------------------

class Script(Base):
    __tablename__ = "scripts"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    executions: Mapped[list["Execution"]] = relationship(
        back_populates="script",
        cascade="all, delete-orphan"
    )


# -------------------------
# Execution
# -------------------------

class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    script_id: Mapped[UUID] = mapped_column(
        ForeignKey("scripts.id"),
        nullable=False
    )

    status: Mapped[ExecutionStatus] = mapped_column(
        SQLEnum(ExecutionStatus),
        nullable=False,
        default=ExecutionStatus.SUBMITTED
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    error_line: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    error_col: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    script: Mapped["Script"] = relationship(
        back_populates="executions"
    )

    logs: Mapped[list["ExecutionLog"]] = relationship(
        back_populates="execution"
    )


# -------------------------
# Execution Log
# -------------------------

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4
    )

    execution_id: Mapped[UUID] = mapped_column(
        ForeignKey("executions.id"),
        nullable=False
    )

    step: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    line: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    col: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    args: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    result_summary: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    execution: Mapped["Execution"] = relationship(
        back_populates="logs"
    )