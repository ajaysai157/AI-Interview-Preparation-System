export default function LoadingOverlay({ message = 'AI Interviewer is processing…', sub = 'Analyzing response and generating next adaptive challenge.' }) {
  return (
    <div className="loading-overlay">
      <div className="arena-spinner" />
      <div className="loading-message">{message}</div>
      <div className="loading-sub">{sub}</div>
    </div>
  )
}
