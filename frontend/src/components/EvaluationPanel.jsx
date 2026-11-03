import { scoreColor } from './ScoreRing'

const metricKeys = [
  { key: 'correctness', label: 'Technical Correctness' },
  { key: 'completeness', label: 'Completeness' },
  { key: 'clarity', label: 'Communication Clarity' },
  { key: 'relevance', label: 'Target Relevance' },
]

export default function EvaluationPanel({ evaluation, onNext, isLastQuestion }) {
  const overallColor = scoreColor(evaluation.score * 10)

  return (
    <div className="eval-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <span className="chip chip-cyan" style={{ marginBottom: 6 }}>✦ Instant AI Evaluation</span>
          <h3 style={{ margin: 0, fontSize: 18, fontWeight: 800 }}>Answer Performance Breakdown</h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Score:</span>
          <span style={{ fontSize: 26, fontWeight: 900, color: overallColor, fontFamily: 'var(--font-display)' }}>
            {evaluation.score.toFixed(1)}
            <span style={{ fontSize: 14, color: 'var(--text-dim)', fontWeight: 600 }}>/10</span>
          </span>
        </div>
      </div>

      <div className="eval-grid">
        {metricKeys.map(({ key, label }) => {
          const val = evaluation[key]
          const color = scoreColor(val * 10)
          return (
            <div className="metric" key={key}>
              <div className="metric-label">{label}</div>
              <div className="metric-value" style={{ color }}>
                {val.toFixed(1)}
                <span className="text-dim" style={{ fontSize: 13, fontWeight: 500 }}>/10</span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="eval-feedback"><strong style={{ color: 'var(--primary)' }}>AI Feedback: </strong>{evaluation.feedback}</div>

      {evaluation.improvement_areas && evaluation.improvement_areas.length > 0 ? (
        <ul className="improve-list">
          {evaluation.improvement_areas.map((area, index) => (<li key={index}><span>{area}</span></li>))}
        </ul>
      ) : null}

      {onNext ? (
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 20 }}>
          <button className="btn btn-primary" onClick={onNext}>
            {isLastQuestion ? 'View Final Performance Profile →' : 'Proceed to Next Challenge →'}
          </button>
        </div>
      ) : null}
    </div>
  )
}
