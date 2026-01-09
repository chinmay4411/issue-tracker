import { useState, useEffect } from 'react';
import { api } from './api';
import './index.css';

function App() {
  const [issues, setIssues] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [selectedIssues, setSelectedIssues] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingIssue, setEditingIssue] = useState(null);
  const [showImportModal, setShowImportModal] = useState(false);

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [issuesData, statsData] = await Promise.all([
        api.getIssues(filters),
        api.getStats(),
      ]);
      setIssues(issuesData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load data:', error);
      alert('Failed to load data. Make sure the backend is running on http://localhost:8000');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateIssue = () => {
    setEditingIssue(null);
    setShowModal(true);
  };

  const handleEditIssue = (issue) => {
    setEditingIssue(issue);
    setShowModal(true);
  };

  const handleDeleteIssue = async (id) => {
    if (!confirm('Are you sure you want to delete this issue?')) return;
    try {
      await api.deleteIssue(id);
      loadData();
    } catch (error) {
      alert('Failed to delete issue');
    }
  };

  const handleBulkUpdate = async (updates) => {
    if (selectedIssues.length === 0) return;
    try {
      await api.bulkUpdate(selectedIssues, updates);
      setSelectedIssues([]);
      loadData();
    } catch (error) {
      alert('Failed to bulk update issues');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIssues.length === 0) return;
    if (!confirm(`Delete ${selectedIssues.length} selected issue(s)?`)) return;
    try {
      await api.bulkDelete(selectedIssues);
      setSelectedIssues([]);
      loadData();
    } catch (error) {
      alert('Failed to bulk delete issues');
    }
  };

  const handleExport = async () => {
    try {
      await api.exportCSV(filters);
    } catch (error) {
      alert('Failed to export CSV');
    }
  };

  const toggleIssueSelection = (id) => {
    setSelectedIssues(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelectedIssues(issues.map(i => i.id));
  };

  const clearSelection = () => {
    setSelectedIssues([]);
  };

  return (
    <div className="container">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon"></span>
            Issue Tracker
          </div>
          <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
            <button className="btn btn-primary" onClick={handleCreateIssue}>
              New Issue
            </button>
            <button className="btn btn-secondary" onClick={() => setShowImportModal(true)}>
              Import CSV
            </button>
            <button className="btn btn-secondary" onClick={handleExport}>
              Export CSV
            </button>
          </div>
        </div>
      </header>

      {stats && <StatsGrid stats={stats} />}

      <div className="main-content">
        <Toolbar
          filters={filters}
          onFilterChange={setFilters}
          selectedCount={selectedIssues.length}
          onSelectAll={selectAll}
          onClearSelection={clearSelection}
          onBulkUpdate={handleBulkUpdate}
          onBulkDelete={handleBulkDelete}
        />

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading issues...</p>
          </div>
        ) : issues.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon"></div>
            <h3>No issues found</h3>
            <p>Create your first issue or adjust filters</p>
          </div>
        ) : (
          <IssuesList
            issues={issues}
            selectedIssues={selectedIssues}
            onToggleSelection={toggleIssueSelection}
            onEdit={handleEditIssue}
            onDelete={handleDeleteIssue}
          />
        )}
      </div>

      {showModal && (
        <IssueModal
          issue={editingIssue}
          onClose={() => setShowModal(false)}
          onSave={() => {
            setShowModal(false);
            loadData();
          }}
        />
      )}

      {showImportModal && (
        <ImportModal
          onClose={() => setShowImportModal(false)}
          onImport={() => {
            setShowImportModal(false);
            loadData();
          }}
        />
      )}
    </div>
  );
}

function StatsGrid({ stats }) {
  return (
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-header">
          <span className="stat-label">Total Issues</span>
          <span className="stat-icon"></span>
        </div>
        <div className="stat-value">{stats.total_issues}</div>
      </div>
      <div className="stat-card">
        <div className="stat-header">
          <span className="stat-label">Open</span>
          <span className="stat-icon"></span>
        </div>
        <div className="stat-value">{stats.by_status.open || 0}</div>
      </div>
      <div className="stat-card">
        <div className="stat-header">
          <span className="stat-label">In Progress</span>
          <span className="stat-icon"></span>
        </div>
        <div className="stat-value">{stats.by_status.in_progress || 0}</div>
      </div>
      <div className="stat-card">
        <div className="stat-header">
          <span className="stat-label">Resolved</span>
          <span className="stat-icon"></span>
        </div>
        <div className="stat-value">{stats.by_status.resolved || 0}</div>
      </div>
    </div>
  );
}

function Toolbar({ filters, onFilterChange, selectedCount, onSelectAll, onClearSelection, onBulkUpdate, onBulkDelete }) {
  return (
    <div className="toolbar">
      <div className="toolbar-group">
        <input
          type="text"
          className="input"
          placeholder=" Search issues..."
          value={filters.search || ''}
          onChange={(e) => onFilterChange({ ...filters, search: e.target.value })}
        />
        <select
          className="select"
          value={filters.status || ''}
          onChange={(e) => onFilterChange({ ...filters, status: e.target.value || undefined })}
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
        <select
          className="select"
          value={filters.priority || ''}
          onChange={(e) => onFilterChange({ ...filters, priority: e.target.value || undefined })}
        >
          <option value="">All Priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      {selectedCount > 0 && (
        <div className="toolbar-group">
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            {selectedCount} selected
          </span>
          <button className="btn btn-sm btn-secondary" onClick={onClearSelection}>
            Clear
          </button>
          <button className="btn btn-sm btn-secondary" onClick={onSelectAll}>
            Select All
          </button>
          <select
            className="select"
            onChange={(e) => {
              if (e.target.value) {
                onBulkUpdate({ status: e.target.value });
                e.target.value = '';
              }
            }}
          >
            <option value="">Bulk Status...</option>
            <option value="open">Set Open</option>
            <option value="in_progress">Set In Progress</option>
            <option value="resolved">Set Resolved</option>
            <option value="closed">Set Closed</option>
          </select>
          <button className="btn btn-sm btn-danger" onClick={onBulkDelete}>
            Delete Selected
          </button>
        </div>
      )}
    </div>
  );
}

function IssuesList({ issues, selectedIssues, onToggleSelection, onEdit, onDelete }) {
  return (
    <div className="issues-grid">
      {issues.map(issue => (
        <div key={issue.id} className="issue-card">
          <div className="issue-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', flex: 1 }}>
              <input
                type="checkbox"
                className="checkbox"
                checked={selectedIssues.includes(issue.id)}
                onChange={() => onToggleSelection(issue.id)}
                onClick={(e) => e.stopPropagation()}
              />
              <h3 className="issue-title" onClick={() => onEdit(issue)}>
                {issue.title}
              </h3>
            </div>
            <div className="issue-badges">
              <span className={`badge badge-${issue.status}`}>{issue.status.replace('_', ' ')}</span>
              <span className={`badge badge-${issue.priority}`}>{issue.priority}</span>
            </div>
          </div>
          {issue.description && (
            <p className="issue-description">{issue.description}</p>
          )}
          <div className="issue-footer">
            <div className="issue-meta">
              {issue.assignee && <span> {issue.assignee}</span>}
              {issue.reporter && <span> {issue.reporter}</span>}
              <span>{new Date(issue.created_at).toLocaleDateString()}</span>
            </div>
            <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
              <button className="btn btn-sm btn-secondary" onClick={() => onEdit(issue)}>
                Edit
              </button>
              <button className="btn btn-sm btn-danger" onClick={() => onDelete(issue.id)}>

              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function IssueModal({ issue, onClose, onSave }) {
  const [formData, setFormData] = useState({
    title: issue?.title || '',
    description: issue?.description || '',
    status: issue?.status || 'open',
    priority: issue?.priority || 'medium',
    assignee: issue?.assignee || '',
    reporter: issue?.reporter || '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (issue) {
        await api.updateIssue(issue.id, formData);
      } else {
        await api.createIssue(formData);
      }
      onSave();
    } catch (error) {
      alert(`Failed to ${issue ? 'update' : 'create'} issue`);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{issue ? 'Edit Issue' : 'Create New Issue'}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label className="form-label">Title *</label>
              <input
                type="text"
                className="form-input"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                maxLength={200}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className="form-textarea"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Status</label>
              <select
                className="form-select"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Priority</label>
              <select
                className="form-select"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Assignee</label>
              <input
                type="text"
                className="form-input"
                value={formData.assignee}
                onChange={(e) => setFormData({ ...formData, assignee: e.target.value })}
                maxLength={100}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Reporter</label>
              <input
                type="text"
                className="form-input"
                value={formData.reporter}
                onChange={(e) => setFormData({ ...formData, reporter: e.target.value })}
                maxLength={100}
              />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              {issue ? 'Update' : 'Create'} Issue
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ImportModal({ onClose, onImport }) {
  const [file, setFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);

  const handleImport = async () => {
    if (!file) return;
    try {
      setImporting(true);
      const importResult = await api.importCSV(file);
      setResult(importResult);
      if (importResult.failed === 0) {
        setTimeout(() => onImport(), 1500);
      }
    } catch (error) {
      alert('Failed to import CSV');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Import CSV</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <div className="file-upload" onClick={() => document.getElementById('csv-file').click()}>
            <div className="file-upload-icon"></div>
            <p>{file ? file.name : 'Click to select CSV file'}</p>
            <input
              id="csv-file"
              type="file"
              accept=".csv"
              style={{ display: 'none' }}
              onChange={(e) => setFile(e.target.files[0])}
            />
          </div>
          {result && (
            <div style={{ marginTop: 'var(--spacing-lg)', padding: 'var(--spacing-md)', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <p><strong>Import Results:</strong></p>
              <p> Successful: {result.successful}</p>
              <p>Failed: {result.failed}</p>
              <p>Total: {result.total_rows}</p>
              {result.errors.length > 0 && (
                <details style={{ marginTop: 'var(--spacing-sm)' }}>
                  <summary>View Errors</summary>
                  <ul style={{ marginTop: 'var(--spacing-sm)' }}>
                    {result.errors.map((err, i) => (
                      <li key={i}>Row {err.row}: {err.error}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            {result && result.failed === 0 ? 'Done' : 'Cancel'}
          </button>
          {!result && (
            <button
              className="btn btn-primary"
              onClick={handleImport}
              disabled={!file || importing}
            >
              {importing ? 'Importing...' : 'Import'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
