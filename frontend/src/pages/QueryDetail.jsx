import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { queriesAPI } from '../api/client';
import StatusBadge from '../components/StatusBadge';

export default function QueryDetail() {
  const { id } = useParams();
  const [query, setQuery] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDetail = useCallback(async () => {
    try {
      const response = await queriesAPI.detail(id);
      setQuery(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load query details.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  // Auto-refresh while processing
  useEffect(() => {
    fetchDetail();
    const interval = setInterval(() => {
      fetchDetail();
    }, 3000);
    return () => clearInterval(interval);
  }, [fetchDetail]);

  // Stop refreshing when completed or failed
  useEffect(() => {
    if (query?.status === 'completed' || query?.status === 'failed') {
      // One final fetch already happened, no need for more
    }
  }, [query?.status]);

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error || !query) {
    return (
      <div className="page-container">
        <div className="error-message">{error || 'Query not found.'}</div>
        <Link to="/dashboard" className="btn btn-secondary">← Back to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <Link to="/dashboard" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            ← Back to Dashboard
          </Link>
          <h1 className="page-title" style={{ marginTop: '0.5rem' }}>Query Detail</h1>
        </div>
        <StatusBadge status={query.status} />
      </div>

      {/* Original Query */}
      <div className="card detail-section" style={{ marginBottom: '1.5rem' }}>
        <div className="detail-section-title">📝 Original Query</div>
        <p style={{ fontSize: '1.05rem', lineHeight: '1.7' }}>{query.raw_query}</p>
        {query.error_message && (
          <div className="error-message" style={{ marginTop: '1rem' }}>
            ❌ Error: {query.error_message}
          </div>
        )}
      </div>

      {/* Processing State */}
      {(query.status === 'pending' || query.status === 'processing') && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem 2rem', marginBottom: '1.5rem' }}>
          <div className="loading-spinner" style={{ padding: '0 0 1rem 0' }}>
            <div className="spinner"></div>
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            {query.status === 'pending' ? 'Queued for Research' : 'Researching...'}
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            {query.status === 'pending'
              ? 'Your query is in the queue. Research will begin shortly.'
              : `Analyzing sub-questions and generating insights... (${query.research_steps?.length || 0} steps completed)`}
          </p>
        </div>
      )}

      {/* Sub-Questions */}
      {query.sub_questions?.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">🧩 Sub-Questions ({query.sub_questions.length})</div>
          {query.sub_questions.map((sq) => (
            <div key={sq.id} className="card sub-question-card">
              <span className="sub-question-number">{sq.order_index}</span>
              {sq.question_text}
            </div>
          ))}
        </div>
      )}

      {/* Research Steps */}
      {query.research_steps?.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">🔬 Research Steps ({query.research_steps.length})</div>
          {query.research_steps.map((step) => {
            const matchingSQ = query.sub_questions?.find(sq => sq.id === step.sub_question_id);
            return (
              <div key={step.id} className="card research-step">
                <div className="research-step-question">
                  Step {step.step_number}: {matchingSQ?.question_text || 'Research Analysis'}
                </div>
                <div className="research-step-response">{step.llm_response}</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Final Report Link */}
      {query.final_report && (
        <div className="detail-section">
          <Link
            to={`/reports/${query.id}`}
            className="btn btn-primary btn-lg"
            style={{ width: '100%' }}
          >
            📄 View Full Report
          </Link>
        </div>
      )}
    </div>
  );
}
