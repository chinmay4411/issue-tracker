import csv
import io
from typing import List, Dict
from sqlalchemy.orm import Session
from model import Issue, StatusEnum, PriorityEnum
from schemas import IssueCreate, CSVImportResult


def parse_csv_row(row: Dict[str, str], row_number: int) -> tuple[IssueCreate | None, dict | None]:
    """
    Parse a single CSV row into an IssueCreate object.
    
    Args:
        row: Dictionary representing a CSV row
        row_number: Row number for error reporting
    
    Returns:
        Tuple of (IssueCreate object or None, error dict or None)
    """
    try:
        # Parse status enum
        status_str = row.get('status', 'open').strip().lower()
        if status_str == 'in progress' or status_str == 'in_progress':
            status = StatusEnum.IN_PROGRESS
        elif status_str == 'open':
            status = StatusEnum.OPEN
        elif status_str == 'resolved':
            status = StatusEnum.RESOLVED
        elif status_str == 'closed':
            status = StatusEnum.CLOSED
        else:
            status = StatusEnum.OPEN  # Default
        
        # Parse priority enum
        priority_str = row.get('priority', 'medium').strip().lower()
        if priority_str == 'low':
            priority = PriorityEnum.LOW
        elif priority_str == 'medium':
            priority = PriorityEnum.MEDIUM
        elif priority_str == 'high':
            priority = PriorityEnum.HIGH
        elif priority_str == 'critical':
            priority = PriorityEnum.CRITICAL
        else:
            priority = PriorityEnum.MEDIUM  # Default
        
        # Create issue object
        issue = IssueCreate(
            title=row.get('title', '').strip(),
            description=row.get('description', '').strip() or None,
            status=status,
            priority=priority,
            assignee=row.get('assignee', '').strip() or None,
            reporter=row.get('reporter', '').strip() or None
        )
        
        # Validate title is not empty
        if not issue.title:
            return None, {
                "row": row_number,
                "error": "Title is required and cannot be empty"
            }
        
        return issue, None
    
    except Exception as e:
        return None, {
            "row": row_number,
            "error": f"Parsing error: {str(e)}"
        }


def import_issues_from_csv(file_content: bytes, db: Session) -> CSVImportResult:
    """
    Import issues from a CSV file.
    
    Expected CSV columns: title, description, status, priority, assignee, reporter
    
    Args:
        file_content: CSV file content as bytes
        db: Database session
    
    Returns:
        CSVImportResult with statistics and errors
    """
    # Decode file content
    text_content = file_content.decode('utf-8')
    csv_file = io.StringIO(text_content)
    
    # Parse CSV
    reader = csv.DictReader(csv_file)
    
    total_rows = 0
    successful = 0
    failed = 0
    errors = []
    
    for row_number, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
        total_rows += 1
        
        # Parse row
        issue_data, error = parse_csv_row(row, row_number)
        
        if error:
            failed += 1
            errors.append(error)
            continue
        
        try:
            # Create database object
            db_issue = Issue(**issue_data.model_dump())
            db.add(db_issue)
            db.commit()
            successful += 1
        except Exception as e:
            db.rollback()
            failed += 1
            errors.append({
                "row": row_number,
                "error": f"Database error: {str(e)}"
            })
    
    return CSVImportResult(
        total_rows=total_rows,
        successful=successful,
        failed=failed,
        errors=errors
    )


def export_issues_to_csv(issues: List[Issue]) -> str:
    """
    Export issues to CSV format.
    
    Args:
        issues: List of Issue objects
    
    Returns:
        CSV content as string
    """
    output = io.StringIO()
    
    fieldnames = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'reporter', 'created_at', 'updated_at']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    # Write header
    writer.writeheader()
    
    # Write rows
    for issue in issues:
        writer.writerow({
            'id': issue.id,
            'title': issue.title,
            'description': issue.description or '',
            'status': issue.status.value,
            'priority': issue.priority.value,
            'assignee': issue.assignee or '',
            'reporter': issue.reporter or '',
            'created_at': issue.created_at.isoformat(),
            'updated_at': issue.updated_at.isoformat()
        })
    
    return output.getvalue()
