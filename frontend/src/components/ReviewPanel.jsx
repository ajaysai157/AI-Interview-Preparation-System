import { useState } from 'react'
import LoadingOverlay from './LoadingOverlay'

const scoreFields = [
  { key: 'score', label: 'Overall' },
  { key: 'correctness', label: 'Correctness' },
  { key: 'completeness', label: 'Completeness' },
  { key: 'clarity', label: 'Clarity' },
  { key: 'relevance', label: 'Relevance' },
]

function toDraft(evaluation) {
  if (!evaluation) return null
  return {
    score: evaluation.score,
    correctness: evaluation.correctness,
    completeness: evaluation.completeness,
    clarity: evaluation.clarity,
    relevance: evaluation.relevance,
    feedback: evaluation.feedback,
    improvement_areas: evaluation.improvement_areas.join(', '),
  }
}

export default function ReviewPanel({ evaluation, question, busy, onApprove, onOverride }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(() => toDraft(evaluation))

  function update(field, value) {
    setDraft((previous) => {
      if (!previous) return previous
      const next = { ...previous }
      if (field === 'feedback') {
        next.feedback = value
      } else if (field === 'improvement_areas') {
        next.improvement_areas = value
      } else {
        const parsed = Number(value)
        next[field] = Number.isNaN(parsed) ? 0 : Math.min(10, Math.max(0, parsed))
      }
      return next
    })
  }

  return (
    <div className="card" style={{ position: 'relative' }}>
      {busy ? <LoadingOverlay message="Resuming interview…" sub="Finalizing the reviewer decision." /> : null}

      <div className="review-banner">
        <div style={{ fontSize: 26 }}>🛡️</div>
        <div className="review-msg">
          <h3>Human review required</h3>
          <p>The AI scored the answer below the review threshold. A reviewer must approve the evaluation or provide a corrected one before the interview can continue.</p>
        </div>
      </div>

      <div className="question-label">Reviewed answer</div>
      <p className="question-text" style={{ fontSize: 16, marginBottom: 18 }}>{question.question}</p>

      {!editing ? (
        <>
          {evaluation ? (
            <div className="eval-feedback">
              <strong>AI evaluation · score {evaluation.score.toFixed(1)}/10</strong>
              <div className="mt-16">{evaluation.feedback}</div>
              {evaluation.improvement_areas.length > 0 ? (
                <ul className="improve-list">
                  {evaluation.improvement_areas.map((area, index) => (<li key={index}>{area}</li>))}
                </ul>
              ) : null}
            </div>
          ) : <p className="muted">Loading the AI evaluation…</p>}

          <div className="answer-actions">
            <button className="btn btn-secondary" onClick={() => { setDraft(toDraft(evaluation)); setEditing(true) }}>Edit & override</button>
            <button className="btn btn-success" onClick={onApprove} disabled={busy}>Approve AI evaluation</button>
          </div>
        </>
      ) : (
        <>
          <div className="score-input-row">
            {scoreFields.map(({ key, label }) => (
              <div className="field" key={key}>
                <label htmlFor={`review-${key}`}>{label}</label>
                <input id={`review-${key}`} type="number" min={0} max={10} step={0.1} value={draft ? Number(draft[key]).toFixed(1) : '0.0'} onChange={(e) => update(key, e.target.value)} disabled={busy} />
              </div>
            ))}
          </div>

          <div className="field mt-16">
            <label htmlFor="review-feedback">Feedback</label>
            <textarea id="review-feedback" value={draft?.feedback || ''} onChange={(e) => update('feedback', e.target.value)} disabled={busy} style={{ minHeight: 90 }} />
          </div>

          <div className="field">
            <label htmlFor="review-areas">Improvement areas (comma separated)</label>
            <input id="review-areas" value={draft?.improvement_areas || ''} onChange={(e) => update('improvement_areas', e.target.value)} disabled={busy} />
          </div>

          <div className="answer-actions">
            <button className="btn btn-ghost" onClick={() => setEditing(false)} disabled={busy}>Cancel</button>
            <button className="btn btn-primary" onClick={() => draft && onOverride(draft)} disabled={busy || !draft}>Save review & continue</button>
          </div>
        </>
      )}
    </div>
  )
}
