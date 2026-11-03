import { useState } from 'react'
import { api, ApiError } from '../api'
import ErrorBanner from '../components/ErrorBanner'

const experienceOptions = [
  { value: 'entry', label: 'Entry Level', desc: 'Core fundamentals & syntax basics' },
  { value: 'junior', label: 'Junior (1–3 yrs)', desc: 'Applied engineering & code trade-offs' },
  { value: 'mid', label: 'Mid / Senior (3+ yrs)', desc: 'System architecture, scale & mechanics' },
]

const typeOptions = [
  { value: 'technical', label: 'Technical Assessment', hint: 'Algorithms, engineering, design' },
  { value: 'hr', label: 'Behavioral & Leadership', hint: 'Situations, communication, impact' },
  { value: 'mixed', label: 'Comprehensive Hybrid', hint: 'Balanced technical + behavioral' },
]

const difficultyOptions = [
  { value: 'easy', label: 'Easy (Baseline fundamentals)' },
  { value: 'medium', label: 'Medium (Industry standard)' },
  { value: 'hard', label: 'Hard (In-depth engineering)' },
]

const popularRoles = [
  'Python Backend Engineer', 'Full Stack React Developer', 'System Design Engineer',
  'Data Scientist / ML Engineer', 'DevOps & Cloud SRE', 'Engineering Team Lead',
]

export default function SetupPage({ initialRole = '', initialType = 'technical', initialDifficulty = 'medium', onCreated, onBack }) {
  const [role, setRole] = useState(initialRole)
  const [experienceLevel, setExperienceLevel] = useState('junior')
  const [interviewType, setInterviewType] = useState(initialType)
  const [difficulty, setDifficulty] = useState(initialDifficulty)
  const [totalQuestions, setTotalQuestions] = useState(5)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const roleError = role.trim().length < 2 ? 'Please specify a target role (at least 2 characters).' : ''

  async function handleSubmit(event) {
    event.preventDefault()
    if (roleError) return
    setError('')
    setLoading(true)
    try {
      const interview = await api.createInterview({
        role: role.trim(),
        experience_level: experienceLevel,
        interview_type: interviewType,
        difficulty,
        total_questions: totalQuestions,
      })
      const start = await api.startInterview(interview.interview_id)
      onCreated(interview, start)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not initialize interview session.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-main">
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
        <button className="btn btn-ghost" onClick={onBack} type="button">← Back to Hub</button>
        <span className="chip chip-cyan">Interview Configuration</span>
      </div>

      <div className="setup-grid">
        <form className="card" onSubmit={handleSubmit}>
          <h2>Configure Session Parameters</h2>
          <p className="card-sub">Tailor the AI interviewer's evaluation rubric and target role domain.</p>

          {error ? <ErrorBanner message={error} /> : null}

          <div className="field">
            <label htmlFor="role">
              <span>Target Role</span>
              <span className="text-dim">{role.length}/100</span>
            </label>
            <input id="role" placeholder="e.g. Python Backend Engineer, React Architect..." value={role} onChange={(e) => setRole(e.target.value)} disabled={loading} maxLength={100} />
            {roleError && role.length > 0 ? <div className="field-error">{roleError}</div> : null}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
              {popularRoles.map((r) => (
                <button key={r} type="button" className="chip" style={{ cursor: 'pointer', background: role === r ? 'var(--primary-subtle)' : undefined, borderColor: role === r ? 'var(--primary)' : undefined, color: role === r ? 'var(--primary)' : undefined }} onClick={() => setRole(r)}>
                  + {r}
                </button>
              ))}
            </div>
          </div>

          <div className="field">
            <label>Experience Level</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 8 }}>
              {experienceOptions.map((opt) => (
                <button key={opt.value} type="button" className="card" style={{ padding: '12px', textAlign: 'left', cursor: 'pointer', borderColor: experienceLevel === opt.value ? 'var(--primary)' : 'var(--border)', background: experienceLevel === opt.value ? 'var(--primary-subtle)' : 'var(--bg-subtle)' }} onClick={() => setExperienceLevel(opt.value)}>
                  <strong style={{ display: 'block', fontSize: 13.5, color: experienceLevel === opt.value ? 'var(--primary)' : 'inherit' }}>{opt.label}</strong>
                  <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>{opt.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="field">
            <label>Interview Format</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 8 }}>
              {typeOptions.map((opt) => (
                <button key={opt.value} type="button" className="card" style={{ padding: '12px', textAlign: 'left', cursor: 'pointer', borderColor: interviewType === opt.value ? 'var(--primary)' : 'var(--border)', background: interviewType === opt.value ? 'var(--primary-subtle)' : 'var(--bg-subtle)' }} onClick={() => setInterviewType(opt.value)}>
                  <strong style={{ display: 'block', fontSize: 13.5, color: interviewType === opt.value ? 'var(--primary)' : 'inherit' }}>{opt.label}</strong>
                  <span style={{ fontSize: 11, color: 'var(--text-dim)', display: 'block', marginTop: 2 }}>{opt.hint}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="form-row">
            <div className="field">
              <label>Starting Difficulty</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} disabled={loading}>
                {difficultyOptions.map((opt) => (<option key={opt.value} value={opt.value}>{opt.label}</option>))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="questions">
                <span>Number of Questions</span>
                <span className="text-dim">{totalQuestions} questions</span>
              </label>
              <input id="questions" type="number" min={1} max={20} value={totalQuestions} onChange={(e) => setTotalQuestions(Math.min(20, Math.max(1, Number(e.target.value) || 1)))} disabled={loading} />
            </div>
          </div>

          <button className="btn btn-primary btn-block" type="submit" disabled={loading || !role.trim()} style={{ marginTop: 6 }}>
            {loading ? 'Initializing LangGraph Engine…' : 'Begin Assessment Session →'}
          </button>
        </form>

        <div className="card setup-side">
          <span className="chip chip-cyan" style={{ marginBottom: 10 }}>Session Summary</span>
          <h3 style={{ margin: '0 0 14px', fontSize: 17, fontWeight: 700 }}>Assessment Specifications</h3>
          <div className="summary-line"><span>Target Role</span><strong>{role.trim() || '—'}</strong></div>
          <div className="summary-line"><span>Experience Tier</span><strong>{experienceLevel.toUpperCase()}</strong></div>
          <div className="summary-line"><span>Format</span><strong>{interviewType.toUpperCase()}</strong></div>
          <div className="summary-line"><span>Initial Difficulty</span><strong>{difficulty.toUpperCase()}</strong></div>
          <div className="summary-line"><span>Length</span><strong>{totalQuestions} Questions</strong></div>
          <div style={{ background: 'var(--panel-surface)', padding: '14px', borderRadius: '10px', marginTop: 18, border: '1px solid var(--border)' }}>
            <strong style={{ fontSize: 12.5, color: 'var(--primary)', display: 'block', marginBottom: 4 }}>Adaptive Calibration Active</strong>
            <p className="text-dim" style={{ fontSize: 12, lineHeight: 1.5, margin: 0 }}>
              The LangGraph engine assesses your depth per question. Scoring &gt;= 8.0 advances difficulty to Hard,
              while weaker responses reinforce core engineering fundamentals.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
