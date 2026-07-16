from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import BigInteger, String, DateTime, CheckConstraint, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Это поле теперь опциональное
    # telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, unique=True, nullable=True)
    
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
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

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": "role",
    }

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, role={self.role})>"

class Tutor(User):
    """Репетитор — регистрация через логин/пароль"""
    __tablename__ = "tutors"

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Дополнительные поля репетитора
    work_start: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # "09:00"
    work_end: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)    # "18:00"
    working_days: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "1,2,3,4,5"

    __mapper_args__ = {
        "polymorphic_identity": "tutor",
    }

class Student(User):
    """Ученик — регистрация через Telegram"""
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    
    # Дополнительные поля ученика
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    parent_contact: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "student",
    }

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