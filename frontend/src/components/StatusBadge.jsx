export default function StatusBadge({ status }) {
  const statusClass = status?.toLowerCase() || 'pending';

  return (
    <span className={`status-badge ${statusClass}`}>
      <span className="status-dot"></span>
      {status}
    </span>
  );
}
