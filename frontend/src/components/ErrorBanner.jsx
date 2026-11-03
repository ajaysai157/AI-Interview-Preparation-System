export default function ErrorBanner({ message, onRetry }) {
  return (
    <div className="error-banner">
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 18 }}>⚠️</span>
        <span>{message}</span>
      </div>
      {onRetry ? (
        <button className="btn btn-ghost btn-sm" onClick={onRetry} style={{ color: '#fff', textDecoration: 'underline' }}>Dismiss</button>
      ) : null}
    </div>
  )
}
