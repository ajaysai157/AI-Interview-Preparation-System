import { useEffect, useState } from 'react'
import { api } from '../api'
import { scoreColor } from '../components/ScoreRing'
import LoadingOverlay from '../components/LoadingOverlay'

export default function HistoryPage({ onOpenInterview, onNewInterview }) {
  const [interviews, setInterviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => { loadInterviews() }, [])

  function loadInterviews() {
    setLoading(true)
    api.getInterviews()
      .then((data) => { setInterviews(data); setLoading(false) })
      .catch(() => setLoading(false))
  }

  async function handleDelete(e, id) {
    e.stopPropagation()
    if (!confirm('Are you sure you want to remove this interview session?')) return
    try {
      await api.deleteInterview(id)
      setInterviews((prev) => prev.filter((i) => i.interview_id !== id))
    } catch {
      alert('Failed to delete interview.')
    }
  }

  const filtered = interviews.filter((item) => {
    const matchesSearch = item.role.toLowerCase().includes(searchTerm.toLowerCase()) || item.interview_type.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="app-main">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <span className="chip chip-cyan" style={{ marginBottom: 4 }}>ASSESSMENT ARCHIVES</span>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800 }}>Recorded Interview Sessions</h1>
        </div>
        <button className="btn btn-primary" onClick={onNewInterview}>+ New Assessment</button>
      </div>

      <div className="history-toolbar">
        <input className="search-input" placeholder="Search by role (e.g. Python, React)..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ width: 'auto', minWidth: 150 }}>
          <option value="all">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="in_progress">In Progress</option>
          <option value="paused">Paused for Review</option>
        </select>
      </div>

      {loading ? (
        <div style={{ position: 'relative', minHeight: 200 }}>
          <LoadingOverlay message="Loading interview archives…" sub="Connecting to SQLite database." />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card center" style={{ padding: '40px 20px' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📋</div>
          <h3>No matching sessions found</h3>
          <p className="card-sub" style={{ margin: '0 0 16px' }}>
            {searchTerm || statusFilter !== 'all' ? 'Try adjusting your search query or filters.' : 'No mock interview records saved yet. Begin your first session!'}
          </p>
          <button className="btn btn-primary" onClick={onNewInterview}>Start Assessment Now →</button>
        </div>
      ) : (
        <div className="history-list">
          {filtered.map((item) => {
            const hasReport = item.status === 'completed' && item.final_report
            return (
              <div key={item.interview_id} className="history-item" onClick={() => onOpenInterview(item)} style={{ cursor: 'pointer' }}>
                <div className="history-item-main">
                  <h3>{item.role}</h3>
                  <div className="history-meta">
                    <span className="chip chip-indigo">{item.experience_level}</span>
                    <span className="chip">{item.interview_type}</span>
                    <span className="chip">{item.difficulty}</span>
                    <span className="text-dim">{item.total_questions} Questions</span>
                    {item.created_at ? <span className="text-dim">· {new Date(item.created_at).toLocaleDateString()}</span> : null}
                  </div>
                </div>
                <div className="history-actions">
                  {item.overall_score != null ? (
                    <div style={{ textAlign: 'right', marginRight: 10 }}>
                      <div style={{ fontSize: 18, fontWeight: 800, color: scoreColor(item.overall_score), fontFamily: 'var(--font-display)' }}>{item.overall_score.toFixed(1)}%</div>
                      <span className="text-dim" style={{ fontSize: 10.5 }}>Score</span>
                    </div>
                  ) : (
                    <span className={`chip chip-${item.status === 'in_progress' ? 'cyan' : 'amber'}`}>{item.status}</span>
                  )}
                  <button className="btn btn-secondary btn-sm" onClick={(e) => { e.stopPropagation(); onOpenInterview(item) }}>
                    {hasReport ? 'View Report' : 'Resume'}
                  </button>
                  <button className="btn btn-ghost btn-sm" onClick={(e) => handleDelete(e, item.interview_id)} title="Delete session" style={{ color: 'var(--danger)' }}>✕</button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
