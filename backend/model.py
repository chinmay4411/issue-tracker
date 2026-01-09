from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum


class StatusEnum(str, enum.Enum):
    """Issue status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class PriorityEnum(str, enum.Enum):
    """Issue priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Issue(Base):
    """
    Issue model representing a single issue in the tracker.
    
    Attributes:
        id: Unique identifier (primary key)
        title: Issue title (required, max 200 chars)
        description: Detailed description (optional)
        status: Current status of the issue
        priority: Priority level
        assignee: Person assigned to the issue
        reporter: Person who reported the issue
        created_at: Timestamp when the issue was created
        updated_at: Timestamp when the issue was last updated
        version: Version number for optimistic locking
    """
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.OPEN, index=True)
    priority = Column(Enum(PriorityEnum), nullable=False, default=PriorityEnum.MEDIUM, index=True)
    assignee = Column(String(100), nullable=True, index=True)
    reporter = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    version = Column(Integer, default=1, nullable=False)

    def __repr__(self):
        return f"<Issue(id={self.id}, title='{self.title}', status='{self.status}', priority='{self.priority}')>"
