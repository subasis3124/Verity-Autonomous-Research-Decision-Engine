import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { reportsAPI } from '../api/client';

export default function ReportView() {
  const { queryId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await reportsAPI.get(queryId);
        setReport(response.data);
      } catch (err) {
        setError(
          err.response?.status === 404
            ? 'Report not yet available. The query may still be processing.'
            : 'Failed to load report.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [queryId]);

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container" style={{ maxWidth: '800px' }}>
        <div className="error-message">{error}</div>
        <Link to="/dashboard" className="btn btn-secondary">← Back to Dashboard</Link>
      </div>
    );
  }

  const structured = report?.structured_output || {};

  return (
    <div className="page-container report-container" style={{ maxWidth: '900px' }}>
      {/* Back Navigation */}
      <Link to={`/queries/${queryId}`} style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        ← Back to Query
      </Link>

      {/* Report Header */}
      <div className="card report-header" style={{ marginTop: '1rem' }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📄</div>
        <h1 className="report-title">Research Report</h1>
        <div className="report-meta">
          Generated on {new Date(report.created_at).toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>

      {/* Executive Summary */}
      {structured.executive_summary && (
        <div className="card report-section">
          <h2 className="report-section-title">
            <span>📋</span> Executive Summary
          </h2>
          <div className="report-section-content">
            {structured.executive_summary}
          </div>
        </div>
      )}

      {/* Key Findings */}
      {structured.key_findings?.length > 0 && (
        <div className="card report-section">
          <h2 className="report-section-title">
            <span>🔍</span> Key Findings
          </h2>
          <ul className="report-list">
            {structured.key_findings.map((finding, idx) => (
              <li key={idx}>{finding}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Risks */}
      {structured.risks?.length > 0 && (
        <div className="card report-section">
          <h2 className="report-section-title">
            <span>⚠️</span> Risks & Concerns
          </h2>
          <ul className="report-list">
            {structured.risks.map((risk, idx) => (
              <li key={idx}>{risk}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {structured.recommendations?.length > 0 && (
        <div className="card report-section">
          <h2 className="report-section-title">
            <span>💡</span> Recommendations
          </h2>
          <ul className="report-list">
            {structured.recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Bottom Navigation */}
      <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', marginBottom: '2rem' }}>
        <Link to={`/queries/${queryId}`} className="btn btn-secondary" style={{ flex: 1 }}>
          ← View Query Details
        </Link>
        <Link to="/dashboard" className="btn btn-primary" style={{ flex: 1 }}>
          📊 Dashboard
        </Link>
      </div>
    </div>
  );
}
