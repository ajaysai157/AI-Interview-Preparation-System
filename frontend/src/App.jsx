import { useState } from 'react'
import { API_BASE, api } from './api'
import DashboardPage from './pages/DashboardPage'
import SetupPage from './pages/SetupPage'
import SessionPage from './pages/SessionPage'
import ReportPage from './pages/ReportPage'
import HistoryPage from './pages/HistoryPage'

export default function App() {
  const [screen, setScreen] = useState('dashboard')
  const [interview, setInterview] = useState(null)
  const [start, setStart] = useState(null)
  const [result, setResult] = useState(null)
  const [setupPreset, setSetupPreset] = useState(null)

  function handleCreated(created, started) {
    setInterview(created)
    setStart(started)
    setScreen('session')
  }

  function handleComplete(refreshed, finalResult) {
    setInterview(refreshed)
    setResult(finalResult)
    setScreen('report')
  }

  function handleStartPreset(role, type, difficulty) {
    setSetupPreset({ role, type, difficulty })
    setScreen('setup')
  }

  function handleStartCustom() {
    setSetupPreset(null)
    setScreen('setup')
  }

  function handleOpenHistoryItem(item) {
    if (item.status === 'completed' && item.final_report) {
      setInterview(item)
      setResult(item.final_report)
      setScreen('report')
    } else if (item.current_question) {
      setInterview(item)
      setStart({
        interview_id: item.interview_id,
        current_question_number: item.current_question_number,
        question: item.current_question,
        status: item.status,
      })
      setScreen('session')
    } else {
      api
        .getInterview(item.interview_id)
        .then((detail) => {
          if (detail.status === 'completed' && detail.final_report) {
            setInterview(detail)
            setResult(detail.final_report)
            setScreen('report')
          } else if (detail.current_question) {
            setInterview(detail)
            setStart({
              interview_id: detail.interview_id,
              current_question_number: detail.current_question_number,
              question: detail.current_question,
              status: detail.status,
            })
            setScreen('session')
          } else {
            api.startInterview(detail.interview_id).then((st) => {
              setInterview(detail)
              setStart(st)
              setScreen('session')
            })
          }
        })
        .catch(() => setScreen('history'))
    }
  }

  function openDocs() {
    window.open(`${API_BASE}/docs`, '_blank', 'noopener')
  }

  return (
    <div className="app">
      <header className="app-header">
        <button className="brand" onClick={() => setScreen('dashboard')} type="button">
          <div className="brand-logo">AI</div>
          <div className="brand-text">
            <span>InterviewAI</span>
            <span className="brand-tag">SYSTEM</span>
          </div>
        </button>

        <nav className="nav-links">
          <button
            className={`nav-btn ${screen === 'dashboard' ? 'active' : ''}`}
            onClick={() => setScreen('dashboard')}
            type="button"
          >
            Dashboard
          </button>
          <button
            className={`nav-btn ${screen === 'setup' ? 'active' : ''}`}
            onClick={handleStartCustom}
            type="button"
          >
            + New
          </button>
          <button
            className={`nav-btn ${screen === 'history' ? 'active' : ''}`}
            onClick={() => setScreen('history')}
            type="button"
          >
            Archives
          </button>
          <button className="nav-btn" onClick={openDocs} type="button">
            API
          </button>
        </nav>
      </header>

      {screen === 'dashboard' ? (
        <DashboardPage
          onStartCustom={handleStartCustom}
          onStartPreset={handleStartPreset}
          onOpenReport={handleOpenHistoryItem}
          onOpenHistory={() => setScreen('history')}
        />
      ) : null}

      {screen === 'setup' ? (
        <SetupPage
          initialRole={setupPreset?.role || ''}
          initialType={setupPreset?.type || 'technical'}
          initialDifficulty={setupPreset?.difficulty || 'medium'}
          onCreated={handleCreated}
          onBack={() => setScreen('dashboard')}
        />
      ) : null}

      {screen === 'session' && interview && start ? (
        <SessionPage
          interview={interview}
          start={start}
          onComplete={handleComplete}
          onExit={() => setScreen('dashboard')}
        />
      ) : null}

      {screen === 'history' ? (
        <HistoryPage
          onOpenInterview={handleOpenHistoryItem}
          onNewInterview={handleStartCustom}
        />
      ) : null}

      {screen === 'report' && interview && result ? (
        <ReportPage
          interview={interview}
          result={result}
          onRestart={handleStartCustom}
          onBackToHub={() => setScreen('dashboard')}
        />
      ) : null}
    </div>
  )
}
