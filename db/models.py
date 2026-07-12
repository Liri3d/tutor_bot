from datetime import datetime, timedelta
from sqlalchemy import BigInteger, String, DateTime, CheckConstraint, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("role IN ('tutor', 'student')"),
        nullable=False
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now
    )
    invites: Mapped[list["Invite"]] = relationship("Invite", back_populates="tutor")
    relationships_as_tutor: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.tutor_id",
        back_populates="tutor"
    )
    relationships_as_student: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.student_id",
        back_populates="student"
    )

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, role={self.role})>"


class Invite(Base):
    """Модель приглашения"""
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    tutor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Имя ученика
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Связь с репетитором
    tutor: Mapped["User"] = relationship("User", back_populates="invites")

    def __repr__(self):
        return f"<Invite(code={self.code}, tutor_id={self.tutor_id}, is_used={self.is_used})>"


class Relationship(Base):
    """Связь между репетитором и учеником"""
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tutor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('active', 'paused', 'inactive')"),
        default="active"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    # Связи
    tutor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[tutor_id],
        back_populates="relationships_as_tutor"
    )
    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="relationships_as_student"
    )

    def __repr__(self):
        return f"<Relationship(tutor_id={self.tutor_id}, student_id={self.student_id}, status={self.status})>"