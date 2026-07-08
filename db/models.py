from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, String, Boolean, DateTime, 
    Integer, Numeric, JSON, CheckConstraint, 
    Index, UniqueConstraint, text, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        String(20), 
        CheckConstraint("role IN ('tutor', 'student')"),
        nullable=False
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now()
    )
    settings: Mapped[dict] = mapped_column(
        JSON, 
        server_default='{}',
        nullable=False
    )
    
    # Связи
    tutor_relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship", 
        foreign_keys="Relationship.tutor_id",
        back_populates="tutor"
    )
    student_relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.student_id", 
        back_populates="student"
    )
    invites: Mapped[list["Invite"]] = relationship(
        "Invite",
        back_populates="tutor",
        foreign_keys="Invite.tutor_id"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, role={self.role})>"


class Invite(Base):
    __tablename__ = 'invites'
    
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    tutor_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Связи
    tutor: Mapped["User"] = relationship(
        "User",
        back_populates="invites",
        foreign_keys=[tutor_id]
    )
    
    __table_args__ = (
        Index('idx_invites_code', 'code'),
        Index('idx_invites_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<Invite(id={self.id}, code={self.code}, is_used={self.is_used})>"


class Relationship(Base):
    __tablename__ = 'relationships'
    
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    tutor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('active', 'paused', 'inactive')"),
        server_default='active',
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Связи
    tutor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[tutor_id],
        back_populates="tutor_relationships"
    )
    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="student_relationships"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="relationship",
        cascade="all, delete-orphan"
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="relationship",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        # Защита от дублирования активной связи через уникальный индекс с условием
        Index(
            'idx_relationships_unique_active',
            'tutor_id', 'student_id',
            unique=True,
            postgresql_where=text("status = 'active'")
        ),
        Index('idx_relationships_tutor_student', 'tutor_id', 'student_id'),
    )
    
    def __repr__(self):
        return f"<Relationship(id={self.id}, tutor_id={self.tutor_id}, student_id={self.student_id}, status={self.status})>"


class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    relationship_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('relationships.id', ondelete='CASCADE'),
        nullable=False
    )
    total_lessons: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("total_lessons > 0"),
        nullable=False
    )
    used_lessons: Mapped[int] = mapped_column(
        Integer,
        server_default='0',
        nullable=False
    )
    price_per_lesson: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Связи
    relationship: Mapped["Relationship"] = relationship(
        "Relationship",
        back_populates="subscriptions"
    )
    
    @property
    def balance(self) -> int:
        """Остаток занятий по абонементу"""
        return self.total_lessons - self.used_lessons
    
    @property
    def is_active(self) -> bool:
        """Активен ли абонемент"""
        if self.expires_at is None:
            return True
        return datetime.now() < self.expires_at
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, balance={self.balance}, total={self.total_lessons})>"


class Lesson(Base):
    __tablename__ = 'lessons'
    
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    relationship_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('relationships.id', ondelete='CASCADE'),
        nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("duration_minutes BETWEEN 10 AND 180"),
        nullable=False
    )
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(30),
        CheckConstraint("status IN ('scheduled', 'completed', 'cancelled', 'missed', 'failed_to_notify')"),
        server_default='scheduled',
        nullable=False
    )
    paid: Mapped[bool] = mapped_column(Boolean, server_default='true', nullable=False)
    notified: Mapped[bool] = mapped_column(Boolean, server_default='false', nullable=False)
    notify_attempts: Mapped[int] = mapped_column(Integer, server_default='0', nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    
    # Связи
    relationship: Mapped["Relationship"] = relationship(
        "Relationship",
        back_populates="lessons"
    )
    
    @property
    def end_time(self) -> datetime:
        """Время окончания занятия"""
        from datetime import timedelta
        return self.start_time + timedelta(minutes=self.duration_minutes)
    
    __table_args__ = (
        Index('idx_lessons_start_time', 'start_time'),
        Index('idx_lessons_status', 'status'),
        Index('idx_lessons_notified', 'notified'),
    )
    
    def __repr__(self):
        return f"<Lesson(id={self.id}, start_time={self.start_time}, status={self.status})>"