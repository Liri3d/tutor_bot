# db/models.py
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, DateTime, CheckConstraint, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class Tutor(Base):
    """Репетитор — регистрация через логин/пароль"""
    __tablename__ = "tutors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Связи
    invites: Mapped[list["Invite"]] = relationship(
        "Invite",
        foreign_keys="Invite.tutor_id",
        back_populates="tutor"
    )
    relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.tutor_id",
        back_populates="tutor"
    )

    def __repr__(self):
        return f"<Tutor(id={self.id}, login={self.login})>"


class Student(Base):
    """Ученик — регистрация через Telegram"""
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Связи
    relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.student_id",
        back_populates="student"
    )

    def __repr__(self):
        return f"<Student(id={self.id}, telegram_id={self.telegram_id})>"


class Invite(Base):
    """Модель приглашения"""
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    tutor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tutors.id", ondelete="CASCADE"),  # ← теперь ссылается на tutors
        nullable=False
    )
    student_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="SET NULL"),  # ← теперь ссылается на students
        nullable=True
    )
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Invite(code={self.code}, tutor_id={self.tutor_id}, is_used={self.is_used})>"


class Relationship(Base):
    """Связь между репетитором и учеником"""
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tutor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tutors.id", ondelete="CASCADE"),  # ← теперь ссылается на tutors
        nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="CASCADE"),  # ← теперь ссылается на students
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
    tutor: Mapped["Tutor"] = relationship(
        "Tutor",
        foreign_keys=[tutor_id],
        back_populates="relationships"
    )
    student: Mapped["Student"] = relationship(
        "Student",
        foreign_keys=[student_id],
        back_populates="relationships"
    )

    def __repr__(self):
        return f"<Relationship(tutor_id={self.tutor_id}, student_id={self.student_id}, status={self.status})>"