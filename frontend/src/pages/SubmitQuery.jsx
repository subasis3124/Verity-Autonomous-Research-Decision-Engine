import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { queriesAPI } from '../api/client';

export default function SubmitQuery() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (query.trim().length < 10) {
      setError('Please enter a more detailed research question (at least 10 characters).');
      return;
    }

    setLoading(true);

    try {
      const response = await queriesAPI.submit(query.trim());
      navigate(`/queries/${response.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit query. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const exampleQueries = [
    "What are the biggest risks in investing in Indian EV startups in 2025?",
    "How is AI transforming drug discovery and what are the key players?",
    "What are the geopolitical implications of semiconductor supply chain disruptions?",
    "Analyze the future of remote work and its impact on commercial real estate.",
  ];

  return (
    <div className="page-container" style={{ maxWidth: '800px' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">New Research Query</h1>
          <p className="page-subtitle">
            Ask any complex question — Verity will autonomously research, analyze, and generate a structured report.
          </p>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="query-input">
            Your Research Question
          </label>
          <textarea
            id="query-input"
            className="form-input"
            placeholder="e.g. What are the biggest risks in investing in Indian EV startups in 2025?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
            autoFocus
            style={{ minHeight: '160px' }}
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-lg"
          style={{ width: '100%' }}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></span>
              Submitting...
            </>
          ) : (
            <>🚀 Start Research</>
          )}
        </button>
      </form>

      <div style={{ marginTop: '2.5rem' }}>
        <p className="form-label" style={{ marginBottom: '0.75rem' }}>
          💡 Try one of these examples:
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {exampleQueries.map((eq, idx) => (
            <div
              key={idx}
              className="card card-clickable"
              onClick={() => setQuery(eq)}
              style={{ padding: '0.75rem 1rem', cursor: 'pointer' }}
            >
              <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                {eq}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
