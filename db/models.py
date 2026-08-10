# db/models.py
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class Tutor(Base):
    """Репетитор — регистрация через Telegram"""
    __tablename__ = "tutors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
     
    # Связи
    students: Mapped[list["Student"]] = relationship(
        "Student",
        secondary="tutor_student_links",
        back_populates="tutors"
    )
    invites: Mapped[list["Invite"]] = relationship(
        "Invite",
        foreign_keys="Invite.tutor_id",
        back_populates="tutor"
    )
   
    def __repr__(self):
        return f"<Tutor(id={self.id}, username={self.username}, first_name={self.first_name})>"


class Student(Base):
    """Ученик — регистрация через Telegram"""
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[Optional[str]] = mapped_column(BigInteger, unique=True, nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Связи
    tutors: Mapped[list["Tutor"]] = relationship(
        "Tutor",
        secondary="tutor_student_links",
        back_populates="students"
    )

    def __repr__(self):
        return f"<Student(id={self.id}, first_name={self.first_name}, telegram_id={self.telegram_id})>"


class TutorStudentLink(Base):
    """Связь репетитор-ученик (многие-ко-многим)"""
    __tablename__ = "tutor_student_links"

    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("tutors.id", ondelete="CASCADE"),
        primary_key=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active"  # active, paused, inactive
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    def __repr__(self):
        return f"<Link(tutor={self.tutor_id}, student={self.student_id}, status={self.status})>"


class Invite(Base):
    """Приглашение для ученика"""
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("tutors.id", ondelete="CASCADE"),
        nullable=False
    )
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)  # имя, которое указал репетитор
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now() + timedelta(days=7)
    )
        
    tutor: Mapped["Tutor"] = relationship("Tutor", back_populates="invites")

    def __repr__(self):
        return f"<Invite(code={self.code}, tutor_id={self.tutor_id}, used={self.is_used})>"