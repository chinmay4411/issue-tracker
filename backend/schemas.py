from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from model import StatusEnum, PriorityEnum


# Schema for creating a new issue
class IssueCreate(BaseModel):
    """Schema for creating a new issue"""
    title: str = Field(..., min_length=1, max_length=200, description="Issue title")
    description: Optional[str] = Field(None, description="Detailed description")
    status: StatusEnum = Field(StatusEnum.OPEN, description="Issue status")
    priority: PriorityEnum = Field(PriorityEnum.MEDIUM, description="Priority level")
    assignee: Optional[str] = Field(None, max_length=100, description="Assigned person")
    reporter: Optional[str] = Field(None, max_length=100, description="Reporter name")


# Schema for updating an existing issue
class IssueUpdate(BaseModel):
    """Schema for updating an issue (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    assignee: Optional[str] = Field(None, max_length=100)
    reporter: Optional[str] = Field(None, max_length=100)
    version: Optional[int] = Field(None, description="Current version for optimistic locking")


# Schema for API responses
class IssueResponse(BaseModel):
    """Schema for issue responses"""
    id: int
    title: str
    description: Optional[str]
    status: StatusEnum
    priority: PriorityEnum
    assignee: Optional[str]
    reporter: Optional[str]
    created_at: datetime
    updated_at: datetime
    version: int

    model_config = ConfigDict(from_attributes=True)


# Schema for bulk updates
class IssueBulkUpdate(BaseModel):
    """Schema for bulk updating multiple issues"""
    issue_ids: List[int] = Field(..., description="List of issue IDs to update")
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    assignee: Optional[str] = Field(None, max_length=100)


# Schema for bulk delete
class IssueBulkDelete(BaseModel):
    """Schema for bulk deleting issues"""
    issue_ids: List[int] = Field(..., description="List of issue IDs to delete")


# Schema for filtering/searching
class IssueFilter(BaseModel):
    """Schema for filtering issues"""
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    assignee: Optional[str] = None
    search: Optional[str] = Field(None, description="Search in title and description")


# Schema for CSV import results
class CSVImportResult(BaseModel):
    """Schema for CSV import results"""
    total_rows: int
    successful: int
    failed: int
    errors: List[dict] = Field(default_factory=list, description="List of errors with row numbers")


# Schema for issue statistics
class IssueStats(BaseModel):
    """Schema for issue statistics"""
    total_issues: int
    by_status: dict
    by_priority: dict
    by_assignee: dict


# Schema for summary report
class IssueSummary(BaseModel):
    """Schema for issue summary"""
    total_issues: int
    open_issues: int
    in_progress_issues: int
    resolved_issues: int
    closed_issues: int
    critical_priority: int
    high_priority: int
    medium_priority: int
    low_priority: int
