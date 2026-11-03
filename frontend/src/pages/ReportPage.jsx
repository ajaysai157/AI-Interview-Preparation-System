import ScoreRing, { scoreColor } from '../components/ScoreRing'

function getScoreGrade(score) {
  if (score >= 90) return { label: 'Distinguished Mastery', color: 'var(--success)', badge: 'Grade A+' }
  if (score >= 80) return { label: 'High Proficiency', color: 'var(--success)', badge: 'Grade A' }
  if (score >= 70) return { label: 'Solid Competency', color: 'var(--primary)', badge: 'Grade B+' }
  if (score >= 60) return { label: 'Developing Foundation', color: 'var(--warning)', badge: 'Grade B' }
  return { label: 'Target Focus Required', color: 'var(--danger)', badge: 'Grade C' }
}

export default function ReportPage({ interview, result, onRestart, onBackToHub }) {
  const topics = Object.entries(result.topic_performance)
  const overall = result.overall_score
  const grade = getScoreGrade(overall)

  return (
    <div className="app-main">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18, flexWrap: 'wrap', gap: 10 }}>
        <button className="btn btn-ghost" onClick={onBackToHub} type="button">← Back to Hub</button>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => window.print()}>Print / Export PDF</button>
          <button className="btn btn-primary btn-sm" onClick={onRestart}>New Assessment →</button>
        </div>
      </div>

      <div className="report-head">
        <ScoreRing value={overall} size={160} stroke={12} label="Score" />
        <div className="report-title" style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 6 }}>
            <span className="chip chip-cyan" style={{ fontSize: 12, fontWeight: 700 }}>{grade.badge}</span>
            <span className="chip" style={{ color: grade.color }}>{grade.label}</span>
          </div>
          <h2>Performance Assessment Profile</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 14, margin: '0 0 12px' }}>
            Target: <strong>{interview.role}</strong> · Experience: <strong>{interview.experience_level.toUpperCase()}</strong> · Format: <strong>{interview.interview_type.toUpperCase()}</strong>
          </p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <span className="chip chip-green">Composite Score: {overall.toFixed(1)} / 100</span>
            <span className="chip chip-indigo">Calibrated Difficulty: {interview.difficulty.toUpperCase()}</span>
            <span className="chip">{interview.total_questions} Questions Evaluated</span>
          </div>
        </div>
      </div>

      <div className="report-grid">
        <div className="card report-section">
          <h3>Topic Competency Breakdown</h3>
          {topics.length > 0 ? topics.map(([topic, value]) => {
            const color = scoreColor(value)
            return (
              <div className="topic-bar" key={topic}>
                <div className="topic-row">
                  <span>{topic}</span>
                  <span style={{ color, fontFamily: 'var(--font-mono)' }}>{value.toFixed(1)}%</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${Math.min(100, value)}%`, background: color }} />
                </div>
              </div>
            )
          }) : <p className="muted">No specific topic metrics recorded.</p>}
        </div>

        <div className="card report-section">
          <h3>Executive Evaluation Summary</h3>
          <div style={{ lineHeight: 1.6, fontSize: 13.5, color: 'var(--text)', background: 'var(--bg-subtle)', border: '1px solid var(--border)', borderRadius: '8px', padding: '16px' }}>
            {result.interview_summary}
          </div>
        </div>

        <div className="card report-section">
          <h3 style={{ color: 'var(--success)' }}>Demonstrated Competencies</h3>
          <ul className="list-clean list-strengths">
            {result.strengths.map((item, index) => (<li key={index}>{item}</li>))}
          </ul>
        </div>

        <div className="card report-section">
          <h3 style={{ color: 'var(--danger)' }}>Target Growth Areas</h3>
          {result.weaknesses.length > 0 ? (
            <ul className="list-clean list-weaknesses">
              {result.weaknesses.map((item, index) => (<li key={index}>{item}</li>))}
            </ul>
          ) : <p className="muted">No significant structural gaps identified.</p>}
        </div>
      </div>

      <div className="card report-section mt-20">
        <h3>Recommended Next Steps & Technical Focus</h3>
        <ul className="list-clean list-recs">
          {result.recommendations.map((item, index) => (<li key={index}><span>{item}</span></li>))}
        </ul>
      </div>

      {interview.history && interview.history.length > 0 ? (
        <div className="card report-section mt-20">
          <h3>Detailed Question Log</h3>
          <div style={{ marginTop: 16 }}>
            {interview.history.map((item, index) => {
              if (!item.question) return null
              const score = item.evaluation?.score ?? 0
              const color = scoreColor(score * 10)
              return (
                <div className="timeline-item" key={index}>
                  <div className="timeline-dot" style={{ background: color }} />
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8, marginBottom: 4 }}>
                    <strong style={{ fontSize: 15 }}>Q{item.question.question_number}: {item.question.question}</strong>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <span className="chip chip-indigo" style={{ fontSize: 11 }}>{item.question.topic}</span>
                      <span className="chip" style={{ fontSize: 11 }}>{item.question.difficulty}</span>
                      {item.evaluation ? <span style={{ fontSize: 13, fontWeight: 700, color, alignSelf: 'center' }}>{item.evaluation.score.toFixed(1)} / 10</span> : null}
                    </div>
                  </div>
                  {item.answer ? (
                    <div style={{ background: 'var(--bg-subtle)', padding: '10px 14px', borderRadius: '8px', fontSize: 13, margin: '8px 0', border: '1px solid var(--border)' }}>
                      <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Your Answer: </span>{item.answer.answer}
                    </div>
                  ) : null}
                  {item.evaluation ? (
                    <div style={{ fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                      <strong>AI Review: </strong>{item.evaluation.feedback}
                    </div>
                  ) : null}
                </div>
              )
            })}
          </div>
        </div>
      ) : null}

      <div className="center mt-20">
        <button className="btn btn-primary" onClick={onRestart}>Begin New Assessment →</button>
      </div>
    </div>
  )
}
