const API_BASE_URL = 'http://localhost:8000';

export const api = {
    // Issues CRUD
    async getIssues(filters = {}) {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        if (filters.priority) params.append('priority', filters.priority);
        if (filters.assignee) params.append('assignee', filters.assignee);
        if (filters.search) params.append('search', filters.search);

        const response = await fetch(`${API_BASE_URL}/issues?${params}`);
        if (!response.ok) throw new Error('Failed to fetch issues');
        return response.json();
    },

    async getIssue(id) {
        const response = await fetch(`${API_BASE_URL}/issues/${id}`);
        if (!response.ok) throw new Error('Failed to fetch issue');
        return response.json();
    },

    async createIssue(issue) {
        const response = await fetch(`${API_BASE_URL}/issues`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(issue),
        });
        if (!response.ok) throw new Error('Failed to create issue');
        return response.json();
    },

    async updateIssue(id, issue) {
        const response = await fetch(`${API_BASE_URL}/issues/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(issue),
        });
        if (!response.ok) throw new Error('Failed to update issue');
        return response.json();
    },

    async deleteIssue(id) {
        const response = await fetch(`${API_BASE_URL}/issues/${id}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Failed to delete issue');
    },

    // Bulk Operations
    async bulkUpdate(issue_ids, updates) {
        const response = await fetch(`${API_BASE_URL}/issues/bulk`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ issue_ids, ...updates }),
        });
        if (!response.ok) throw new Error('Failed to bulk update');
        return response.json();
    },

    async bulkDelete(issue_ids) {
        const response = await fetch(`${API_BASE_URL}/issues/bulk`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ issue_ids }),
        });
        if (!response.ok) throw new Error('Failed to bulk delete');
        return response.json();
    },

    // CSV Operations
    async importCSV(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/issues/import`, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) throw new Error('Failed to import CSV');
        return response.json();
    },

    async exportCSV(filters = {}) {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        if (filters.priority) params.append('priority', filters.priority);
        if (filters.assignee) params.append('assignee', filters.assignee);

        const response = await fetch(`${API_BASE_URL}/issues/export?${params}`);
        if (!response.ok) throw new Error('Failed to export CSV');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'issues_export.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    },

    // Analytics
    async getStats() {
        const response = await fetch(`${API_BASE_URL}/issues/stats`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        return response.json();
    },

    async getSummary() {
        const response = await fetch(`${API_BASE_URL}/issues/summary`);
        if (!response.ok) throw new Error('Failed to fetch summary');
        return response.json();
    },
};
