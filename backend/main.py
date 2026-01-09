from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
import io

from database import engine, get_db, Base
from model import Issue, StatusEnum, PriorityEnum
from schemas import (
    IssueCreate, IssueUpdate, IssueResponse, IssueBulkUpdate, IssueBulkDelete,
    CSVImportResult, IssueStats, IssueSummary
)
from csv_import import import_issues_from_csv, export_issues_to_csv

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Issue Tracker API",
    description="A simple and effective issue tracking API with full CRUD operations, CSV import/export, and analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== CRUD Operations ====================

# ==================== CRUD Operations ====================

@app.post("/issues", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    """
    Create a new issue.
    
    - **title**: Issue title (required, max 200 chars)
    - **description**: Detailed description (optional)
    - **status**: Issue status (default: open)
    - **priority**: Priority level (default: medium)
    - **assignee**: Assigned person (optional)
    - **reporter**: Reporter name (optional)
    """
    db_issue = Issue(**issue.model_dump())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


# ==================== Analytics/Reporting (MUST BE BEFORE /issues/{issue_id}) ====================

@app.get("/issues/stats", response_model=IssueStats)
def get_issue_stats(db: Session = Depends(get_db)):
    """
    Get issue statistics.
    
    Returns counts by status, priority, and assignee.
    """
    # Total issues
    total_issues = db.query(Issue).count()
    
    # Count by status
    by_status = {}
    for status_enum in StatusEnum:
        count = db.query(Issue).filter(Issue.status == status_enum).count()
        by_status[status_enum.value] = count
    
    # Count by priority
    by_priority = {}
    for priority_enum in PriorityEnum:
        count = db.query(Issue).filter(Issue.priority == priority_enum).count()
        by_priority[priority_enum.value] = count
    
    # Count by assignee
    assignee_counts = db.query(
        Issue.assignee,
        func.count(Issue.id).label('count')
    ).filter(
        Issue.assignee.isnot(None)
    ).group_by(Issue.assignee).all()
    
    by_assignee = {assignee: count for assignee, count in assignee_counts}
    by_assignee['unassigned'] = db.query(Issue).filter(Issue.assignee.is_(None)).count()
    
    return IssueStats(
        total_issues=total_issues,
        by_status=by_status,
        by_priority=by_priority,
        by_assignee=by_assignee
    )


@app.get("/issues/summary", response_model=IssueSummary)
def get_issue_summary(db: Session = Depends(get_db)):
    """
    Get a summary report of all issues.
    
    Returns counts for different statuses and priorities.
    """
    return IssueSummary(
        total_issues=db.query(Issue).count(),
        open_issues=db.query(Issue).filter(Issue.status == StatusEnum.OPEN).count(),
        in_progress_issues=db.query(Issue).filter(Issue.status == StatusEnum.IN_PROGRESS).count(),
        resolved_issues=db.query(Issue).filter(Issue.status == StatusEnum.RESOLVED).count(),
        closed_issues=db.query(Issue).filter(Issue.status == StatusEnum.CLOSED).count(),
        critical_priority=db.query(Issue).filter(Issue.priority == PriorityEnum.CRITICAL).count(),
        high_priority=db.query(Issue).filter(Issue.priority == PriorityEnum.HIGH).count(),
        medium_priority=db.query(Issue).filter(Issue.priority == PriorityEnum.MEDIUM).count(),
        low_priority=db.query(Issue).filter(Issue.priority == PriorityEnum.LOW).count()
    )


# ==================== CSV Operations (MUST BE BEFORE /issues/{issue_id}) ====================

@app.post("/issues/import", response_model=CSVImportResult)
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import issues from a CSV file.
    
    Expected CSV columns: title, description, status, priority, assignee, reporter
    
    Returns statistics about successful and failed imports.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Read file content
    content = await file.read()
    
    # Import issues
    result = import_issues_from_csv(content, db)
    
    return result


@app.get("/issues/export")
def export_csv(
    status_filter: Optional[StatusEnum] = Query(None, alias="status"),
    priority: Optional[PriorityEnum] = Query(None),
    assignee: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Export issues to a CSV file.
    
    Supports the same filters as the list endpoint.
    """
    # Build query with filters
    query = db.query(Issue)
    
    if status_filter:
        query = query.filter(Issue.status == status_filter)
    if priority:
        query = query.filter(Issue.priority == priority)
    if assignee:
        query = query.filter(Issue.assignee == assignee)
    
    issues = query.order_by(Issue.created_at.desc()).all()
    
    # Generate CSV
    csv_content = export_issues_to_csv(issues)
    
    # Return as streaming response
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=issues_export.csv"}
    )


# ==================== Bulk Operations (MUST BE BEFORE /issues/{issue_id}) ====================

@app.put("/issues/bulk", response_model=dict)
def bulk_update_issues(bulk_update: IssueBulkUpdate, db: Session = Depends(get_db)):
    """
    Bulk update multiple issues.
    
    - **issue_ids**: List of issue IDs to update
    - **status**: New status (optional)
    - **priority**: New priority (optional)
    - **assignee**: New assignee (optional)
    """
    # Get issues
    issues = db.query(Issue).filter(Issue.id.in_(bulk_update.issue_ids)).all()
    
    if not issues:
        raise HTTPException(status_code=404, detail="No issues found with the provided IDs")
    
    # Update fields
    updated_count = 0
    for issue in issues:
        if bulk_update.status is not None:
            issue.status = bulk_update.status
        if bulk_update.priority is not None:
            issue.priority = bulk_update.priority
        if bulk_update.assignee is not None:
            issue.assignee = bulk_update.assignee
        issue.version += 1
        updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully updated {updated_count} issue(s)",
        "updated_count": updated_count,
        "updated_ids": [issue.id for issue in issues]
    }


@app.delete("/issues/bulk", status_code=status.HTTP_200_OK)
def bulk_delete_issues(bulk_delete: IssueBulkDelete, db: Session = Depends(get_db)):
    """
    Bulk delete multiple issues.
    
    - **issue_ids**: List of issue IDs to delete
    """
    # Get issues
    issues = db.query(Issue).filter(Issue.id.in_(bulk_delete.issue_ids)).all()
    
    if not issues:
        raise HTTPException(status_code=404, detail="No issues found with the provided IDs")
    
    deleted_count = len(issues)
    deleted_ids = [issue.id for issue in issues]
    
    # Delete issues
    for issue in issues:
        db.delete(issue)
    
    db.commit()
    
    return {
        "message": f"Successfully deleted {deleted_count} issue(s)",
        "deleted_count": deleted_count,
        "deleted_ids": deleted_ids
    }


# ==================== Single Issue Operations (Parameterized route) ====================

@app.get("/issues/{issue_id}", response_model=IssueResponse)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    """
    Get a single issue by ID.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue with ID {issue_id} not found")
    return issue


@app.get("/issues", response_model=List[IssueResponse])
def list_issues(
    status_filter: Optional[StatusEnum] = Query(None, alias="status", description="Filter by status"),
    priority: Optional[PriorityEnum] = Query(None, description="Filter by priority"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List all issues with optional filters.
    
    - **status**: Filter by status (open, in_progress, resolved, closed)
    - **priority**: Filter by priority (low, medium, high, critical)
    - **assignee**: Filter by assignee name
    - **search**: Search in title and description
    - **skip**: Pagination offset
    - **limit**: Maximum number of results (default: 100, max: 1000)
    """
    query = db.query(Issue)
    
    # Apply filters
    if status_filter:
        query = query.filter(Issue.status == status_filter)
    if priority:
        query = query.filter(Issue.priority == priority)
    if assignee:
        query = query.filter(Issue.assignee == assignee)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Issue.title.ilike(search_pattern),
                Issue.description.ilike(search_pattern)
            )
        )
    
    # Apply pagination and order
    issues = query.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()
    return issues


@app.put("/issues/{issue_id}", response_model=IssueResponse)
def update_issue(issue_id: int, issue_update: IssueUpdate, db: Session = Depends(get_db)):
    """
    Update an existing issue.
    
    Supports optimistic locking via the version field.
    All fields are optional - only provided fields will be updated.
    """
    # Get existing issue
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail=f"Issue with ID {issue_id} not found")
    
    # Check version for optimistic locking
    if issue_update.version is not None:
        if db_issue.version != issue_update.version:
            raise HTTPException(
                status_code=409,
                detail=f"Version conflict: expected version {issue_update.version}, but current version is {db_issue.version}"
            )
    
    # Update fields
    update_data = issue_update.model_dump(exclude_unset=True, exclude={'version'})
    for field, value in update_data.items():
        setattr(db_issue, field, value)
    
    # Increment version
    db_issue.version += 1
    
    db.commit()
    db.refresh(db_issue)
    return db_issue


@app.delete("/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    """
    Delete an issue by ID.
    """
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail=f"Issue with ID {issue_id} not found")
    
    db.delete(db_issue)
    db.commit()
    return None


# ==================== Health Check ====================

@app.get("/")
def root():
    """
    Root endpoint - API health check.
    """
    return {
        "message": "Issue Tracker API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "service": "issue-tracker-api"}
