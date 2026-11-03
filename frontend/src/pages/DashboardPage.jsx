import { useEffect, useState } from 'react'
import { api } from '../api'
import { scoreColor } from '../components/ScoreRing'

const rolePresets = [
  { icon: '⚡', title: 'Python Backend Engineer', desc: 'GIL, asyncio, concurrency, data models, RESTful architecture.', role: 'Python Backend Engineer', type: 'technical', difficulty: 'medium' },
  { icon: '⚛', title: 'Full Stack React Engineer', desc: 'State patterns, rendering optimization, hooks, clean APIs.', role: 'Full Stack React Engineer', type: 'technical', difficulty: 'medium' },
  { icon: '🏗', title: 'Distributed System Design', desc: 'Microservices, caching, sharding, CAP trade-offs, resilience.', role: 'System Design Architect', type: 'technical', difficulty: 'hard' },
  { icon: '🧠', title: 'AI / ML Engineer', desc: 'Model training, LangChain/LangGraph, RAG, embeddings.', role: 'AI / ML Engineer', type: 'technical', difficulty: 'medium' },
  { icon: '☁', title: 'Cloud & Infrastructure SRE', desc: 'Kubernetes, CI/CD pipelines, container security, observability.', role: 'DevOps & Cloud Engineer', type: 'technical', difficulty: 'medium' },
  { icon: '💬', title: 'Behavioral & Leadership', desc: 'Conflict resolution, agile decisions, mentorship, impact.', role: 'Engineering Team Lead', type: 'hr', difficulty: 'medium' },
]

export default function DashboardPage({ onStartCustom, onStartPreset, onOpenReport, onOpenHistory }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    api.getStats()
      .then((data) => { if (mounted) { setStats(data); setLoading(false) } })
      .catch(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [])

  const completedCount = stats?.completed_interviews || 0
  const avgScore = stats?.average_score || 0
  const topicList = stats?.topic_breakdown ? Object.entries(stats.topic_breakdown) : []

  return (
    <div className="app-main">
      <section className="arena-hero">
        <span className="arena-badge">AI INTERVIEW LABORATORY · GEMMA2:2B / OLLAMA</span>
        <h1>AI Interview <span className="text-gradient">System</span></h1>
        <p className="card-sub" style={{ maxWidth: 640, margin: 0 }}>
          Structured, stateful mock interviews orchestrated by LangGraph. Receive deterministic,
          metric-driven evaluations with adaptive difficulty calibration.
        </p>
        <div style={{ display: 'flex', gap: 10, marginTop: 6, flexWrap: 'wrap' }}>
          <button className="btn btn-primary" onClick={onStartCustom}>Configure Interview →</button>
          <button className="btn btn-secondary" onClick={onOpenHistory}>
            Review Archives ({stats?.total_interviews || 0})
          </button>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-header"><span>Interviews Completed</span><span>📋</span></div>
          <div className="stat-num">{loading ? '—' : completedCount}</div>
          <div className="stat-footer">
            {stats?.total_interviews ? `${stats.total_interviews} registered sessions` : 'No sessions completed yet'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-header"><span>Average Score</span><span>📊</span></div>
          <div className="stat-num" style={{ color: avgScore ? scoreColor(avgScore) : 'inherit' }}>
            {loading ? '—' : completedCount > 0 ? `${avgScore}%` : 'N/A'}
          </div>
          <div className="stat-footer">
            {completedCount > 0 ? 'Aggregated composite score' : 'Computed after completion'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-header"><span>Top Competency</span><span>✓</span></div>
          <div className="stat-num" style={{ fontSize: 20, color: 'var(--primary)' }}>
            {loading ? '—' : stats?.strongest_areas?.[0] || 'Pending Evaluation'}
          </div>
          <div className="stat-footer">
            {stats?.strongest_areas?.[1] ? `Secondary: ${stats.strongest_areas[1]}` : 'Highest scoring technical topic'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-header"><span>Development Area</span><span>📈</span></div>
          <div className="stat-num" style={{ fontSize: 20, color: 'var(--warning)' }}>
            {loading ? '—' : stats?.improvement_areas?.[0] || 'All Passing'}
          </div>
          <div className="stat-footer">
            {stats?.improvement_areas?.[0] ? 'Target for reinforcement' : 'No low-scoring topics detected'}
          </div>
        </div>
      </section>

      {topicList.length > 0 ? (
        <section className="card mb-20">
          <h2>Topic Competency Profile</h2>
          <p className="card-sub">Real performance breakdown aggregated across completed evaluations.</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 14 }}>
            {topicList.map(([topic, score]) => (
              <div className="topic-bar" key={topic}>
                <div className="topic-row">
                  <span>{topic}</span>
                  <span style={{ color: scoreColor(score) }}>{score.toFixed(1)}%</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${Math.min(100, score)}%`, background: scoreColor(score) }} />
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      <section>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
          <div>
            <h2 style={{ margin: '0 0 2px', fontSize: 19 }}>Curated Interview Tracks</h2>
            <p className="text-dim" style={{ margin: 0, fontSize: 13 }}>Select a specialized domain track or configure custom parameters.</p>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onStartCustom}>Custom Config →</button>
        </div>
        <div className="presets-grid">
          {rolePresets.map((preset) => (
            <div key={preset.title} className="preset-card" onClick={() => onStartPreset(preset.role, preset.type, preset.difficulty)}>
              <div>
                <div className="preset-icon">{preset.icon}</div>
                <h3 className="preset-title">{preset.title}</h3>
                <p className="preset-desc">{preset.desc}</p>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="chip chip-cyan">{preset.difficulty}</span>
                <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--primary)' }}>Launch Track →</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {stats?.recent_interviews && stats.recent_interviews.length > 0 ? (
        <section className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <div>
              <h2 style={{ margin: 0, fontSize: 17 }}>Recent Assessment Sessions</h2>
              <p className="text-dim" style={{ margin: 0, fontSize: 12.5 }}>Your latest recorded interviews and performance evaluations</p>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={onOpenHistory}>View All Archives →</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {stats.recent_interviews.slice(0, 3).map((item) => (
              <div key={item.interview_id} className="history-item" onClick={() => onOpenReport(item)} style={{ cursor: 'pointer' }}>
                <div>
                  <strong style={{ fontSize: 14.5 }}>{item.role}</strong>
                  <div style={{ display: 'flex', gap: 6, marginTop: 3 }}>
                    <span className="chip chip-indigo" style={{ fontSize: 11 }}>{item.interview_type}</span>
                    <span className="chip" style={{ fontSize: 11 }}>{item.difficulty}</span>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  {item.overall_score != null ? (
                    <span style={{ fontSize: 15, fontWeight: 700, color: scoreColor(item.overall_score) }}>{item.overall_score}%</span>
                  ) : (
                    <span className="chip chip-amber" style={{ fontSize: 11 }}>{item.status}</span>
                  )}
                  <span style={{ color: 'var(--primary)', fontSize: 12.5, fontWeight: 600 }}>Report →</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}
