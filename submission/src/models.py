from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Time, Table, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from .database import Base

class RoleEnum(str, enum.Enum):
    student = "student"
    trainer = "trainer"
    institution = "institution"
    programme_manager = "programme_manager"
    monitoring_officer = "monitoring_officer"

class AttendanceStatusEnum(str, enum.Enum):
    present = "present"
    absent = "absent"
    late = "late"

batch_trainers = Table(
    "batch_trainers",
    Base.metadata,
    Column("batch_id", Integer, ForeignKey("batches.id"), primary_key=True),
    Column("trainer_id", Integer, ForeignKey("users.id"), primary_key=True)
)

batch_students = Table(
    "batch_students",
    Base.metadata,
    Column("batch_id", Integer, ForeignKey("batches.id"), primary_key=True),
    Column("student_id", Integer, ForeignKey("users.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    institution_id = Column(Integer, nullable=True) # Could refer to an Institution entity if there was one, but we use institution user id for now.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    institution_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trainers = relationship("User", secondary=batch_trainers, backref="trainer_batches")
    students = relationship("User", secondary=batch_students, backref="student_batches")
    sessions = relationship("Session", back_populates="batch")

class BatchInvite(Base):
    __tablename__ = "batch_invites"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    batch = relationship("Batch", back_populates="sessions")
    attendance = relationship("Attendance", back_populates="session")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AttendanceStatusEnum), nullable=False)
    marked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("Session", back_populates="attendance")
