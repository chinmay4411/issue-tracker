# Issue Tracker API

A simple and effective issue tracking API built with FastAPI, PostgreSQL, and SQLAlchemy.

## Features

- ✅ Full CRUD operations for issues
- ✅ Advanced filtering (status, priority, assignee, search)
- ✅ CSV import/export functionality
- ✅ Bulk operations (update/delete multiple issues)
- ✅ Analytics and reporting endpoints
- ✅ Optimistic locking for concurrent updates
- ✅ Cloud database support (Render, Neon, Supabase, etc.)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

**Option A: Use Cloud Database (Recommended)**

1. Create a PostgreSQL database on [Render](https://render.com), [Neon](https://neon.tech), or [Supabase](https://supabase.com)
2. Copy `.env.example` to `.env`
3. Set your `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://user:password@host/database
```

**Option B: Use Local PostgreSQL**

1. Create a local database:
```bash
createdb issue_tracker_db
```

2. Create `.env` file (or skip to use default):
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/issue_tracker_db
```

### 3. Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Access API Documentation

Open `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## API Endpoints

### CRUD Operations

- `POST /issues` - Create a new issue
- `GET /issues/{id}` - Get issue by ID
- `GET /issues` - List all issues (with filters)
- `PUT /issues/{id}` - Update an issue
- `DELETE /issues/{id}` - Delete an issue

### Bulk Operations

- `PUT /issues/bulk` - Bulk update multiple issues
- `DELETE /issues/bulk` - Bulk delete issues

### CSV Operations

- `POST /issues/import` - Import issues from CSV
- `GET /issues/export` - Export issues to CSV

### Analytics

- `GET /issues/stats` - Get issue statistics
- `GET /issues/summary` - Get summary report

## CSV Import Format

The CSV file should have the following columns:

```csv
title,description,status,priority,assignee,reporter
"Fix login bug","Login button not working","open","high","John Doe","Jane Smith"
"Add dark mode","Implement dark mode feature","in_progress","medium","Alice","Bob"
```

**Status values**: `open`, `in_progress`, `resolved`, `closed`  
**Priority values**: `low`, `medium`, `high`, `critical`

## Example Usage

### Create an Issue

```bash
curl -X POST "http://localhost:8000/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix bug in login",
    "description": "Users cannot log in with email",
    "status": "open",
    "priority": "high",
    "assignee": "John Doe",
    "reporter": "Jane Smith"
  }'
```

### List Issues with Filters

```bash
# Get all open issues
curl "http://localhost:8000/issues?status=open"

# Get high priority issues
curl "http://localhost:8000/issues?priority=high"

# Search for specific text
curl "http://localhost:8000/issues?search=login"
```

### Import from CSV

```bash
curl -X POST "http://localhost:8000/issues/import" \
  -F "file=@issues.csv"
```

### Export to CSV

```bash
curl "http://localhost:8000/issues/export" -o issues.csv
```

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Project Structure

```
backend/
├── main.py              # FastAPI application & routes
├── database.py          # Database configuration
├── model.py             # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── csv_import.py        # CSV import/export logic
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables example
└── README.md           # This file
```

## Deployment

### Deploy to Render

1. Create a PostgreSQL database on Render
2. Create a new Web Service on Render
3. Set environment variable: `DATABASE_URL`
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## License

MIT
