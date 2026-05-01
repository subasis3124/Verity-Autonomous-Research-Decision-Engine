import { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { queriesAPI } from '../api/client';
import StatusBadge from '../components/StatusBadge';

export default function Dashboard() {
  const navigate = useNavigate();
  const [queries, setQueries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchQueries = useCallback(async () => {
    try {
      const response = await queriesAPI.list();
      setQueries(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load queries.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load + auto-refresh every 5 seconds
  useEffect(() => {
    fetchQueries();
    const interval = setInterval(fetchQueries, 5000);
    return () => clearInterval(interval);
  }, [fetchQueries]);

  const handleDelete = async (e, queryId) => {
    e.stopPropagation();
    if (!confirm('Delete this query and all its research data?')) return;

    try {
      await queriesAPI.delete(queryId);
      setQueries((prev) => prev.filter((q) => q.id !== queryId));
    } catch {
      setError('Failed to delete query.');
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Research Dashboard</h1>
          <p className="page-subtitle">Your AI-powered research queries</p>
        </div>
        <Link to="/submit" className="btn btn-primary">
          ✨ New Query
        </Link>
      </div>

      {error && <div className="error-message">{error}</div>}

      {queries.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🔍</div>
          <h3 className="empty-state-title">No queries yet</h3>
          <p>Submit your first research question to get started.</p>
          <Link to="/submit" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Submit a Query
          </Link>
        </div>
      ) : (
        <div className="query-list">
          {queries.map((query) => (
            <div
              key={query.id}
              className="card card-clickable query-card"
              onClick={() => navigate(`/queries/${query.id}`)}
            >
              <div className="query-card-content">
                <div className="query-card-text">{query.raw_query}</div>
                <div className="query-card-meta">
                  <span>{formatDate(query.created_at)}</span>
                </div>
              </div>
              <div className="query-card-actions">
                <StatusBadge status={query.status} />
                <button
                  className="btn btn-danger btn-sm"
                  onClick={(e) => handleDelete(e, query.id)}
                  title="Delete query"
                >
                  🗑
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
