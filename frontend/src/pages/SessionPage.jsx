import { useState } from 'react'
import { api, ApiError, evaluationFromDraft } from '../api'
import LoadingOverlay from '../components/LoadingOverlay'
import ProgressBar from '../components/ProgressBar'
import ErrorBanner from '../components/ErrorBanner'
import ReviewPanel from '../components/ReviewPanel'
import EvaluationPanel from '../components/EvaluationPanel'
import AiInterviewer from '../components/AiInterviewer'

export default function SessionPage({ interview, start, onComplete, onExit }) {
  const [question, setQuestion] = useState(start.question)
  const [answer, setAnswer] = useState('')
  const [phase, setPhase] = useState('question')
  const [busy, setBusy] = useState(false)
  const [busyMessage, setBusyMessage] = useState('')
  const [error, setError] = useState('')
  const [currentEvaluation, setCurrentEvaluation] = useState(null)
  const [pendingEvaluation, setPendingEvaluation] = useState(null)
  const [nextPendingQuestion, setNextPendingQuestion] = useState(null)
  const [answeredCount, setAnsweredCount] = useState(0)

  const totalQuestions = interview.total_questions

  function setBusyState(message) {
    setBusy(true)
    setBusyMessage(message)
    setError('')
  }

  function handleResponse(response) {
    if (response.needs_human_review || response.status === 'paused') {
      setPhase('review')
      setCurrentEvaluation(null)
      void api.getInterview(interview.interview_id)
        .then((detail) => setPendingEvaluation(detail.current_evaluation))
        .catch(() => setPendingEvaluation(null))
      return
    }

    if (response.evaluation) {
      setCurrentEvaluation(response.evaluation)
      setAnsweredCount((prev) => Math.min(prev + 1, totalQuestions))
      setNextPendingQuestion(response.next_question)
      setPhase('evaluated')
      return
    }

    if (response.next_question) {
      setQuestion(response.next_question)
      setAnswer('')
      setPhase('question')
      return
    }

    if (response.status === 'completed') {
      setAnsweredCount(totalQuestions)
      setPhase('completed')
      void finish()
      return
    }
  }

  function handleError(err) {
    setError(err instanceof ApiError ? err.message : 'Something went wrong with the AI evaluation. Please try again.')
    setBusy(false)
  }

  async function submitAnswer() {
    if (!answer.trim()) return
    setBusyState('Evaluating response & computing rubric scores…')
    try {
      const response = await api.submitAnswer(interview.interview_id, answer)
      handleResponse(response)
      setBusy(false)
    } catch (err) {
      handleError(err)
    }
  }

  function proceedToNext() {
    if (nextPendingQuestion) {
      setQuestion(nextPendingQuestion)
      setNextPendingQuestion(null)
      setCurrentEvaluation(null)
      setAnswer('')
      setPhase('question')
    } else {
      void finish()
    }
  }

  async function resumeReview(approve, modified) {
    setBusyState('Finalizing review decision…')
    try {
      const payload = approve
        ? { approve: true }
        : { approve: false, modified_evaluation: modified ? evaluationFromDraft(modified) : undefined }
      const response = await api.continueInterview(interview.interview_id, payload)
      setPendingEvaluation(null)
      handleResponse(response)
      setBusy(false)
    } catch (err) {
      handleError(err)
    }
  }

  async function finish() {
    setBusyState('Synthesizing performance assessment profile…')
    try {
      const [finalResult, refreshedInterview] = await Promise.all([
        api.getResult(interview.interview_id),
        api.getInterview(interview.interview_id),
      ])
      onComplete(refreshedInterview, finalResult)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load your final report.')
      setPhase('question')
      setBusy(false)
    }
  }

  const isLastQuestion = question.question_number >= totalQuestions
  const wordCount = answer.trim() ? answer.trim().split(/\s+/).length : 0

  let interviewerStatus = 'Awaiting response'
  if (busy) interviewerStatus = 'Analyzing technical reasoning…'
  else if (phase === 'evaluated') interviewerStatus = 'Evaluation complete'
  else if (phase === 'review') interviewerStatus = 'Paused for human oversight'

  return (
    <div className="app-main">
      <div className="session-head">
        <div>
          <div className="muted" style={{ fontSize: 12.5, marginBottom: 3 }}>
            {interview.role} · {interview.experience_level.toUpperCase()} · {interview.interview_type.toUpperCase()}
          </div>
          <div className="session-meta">
            <span className="chip chip-cyan">Question {question.question_number} of {totalQuestions}</span>
            <span className="chip chip-indigo">{question.topic}</span>
            <span className="chip">{question.difficulty}</span>
          </div>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={onExit}>✕ Exit Session</button>
      </div>

      <ProgressBar current={answeredCount} total={totalQuestions} />
      {error ? <ErrorBanner message={error} onRetry={() => setError('')} /> : null}

      <AiInterviewer role={interview.role} difficulty={question.difficulty} statusText={interviewerStatus} isThinking={busy} />

      {phase === 'review' ? (
        <ReviewPanel evaluation={pendingEvaluation} question={question} busy={busy} onApprove={() => void resumeReview(true)} onOverride={(modified) => void resumeReview(false, modified)} />
      ) : (
        <div className="question-stage" style={{ position: 'relative' }}>
          {busy ? <LoadingOverlay message={busyMessage} sub="The LangGraph pipeline is evaluating technical correctness, clarity, and depth." /> : null}

          <div className="question-badge-row">
            <span className="chip chip-cyan" style={{ fontSize: 11 }}>Question #{question.question_number}</span>
            <span className="text-dim" style={{ fontSize: 12.5 }}>Domain: <strong style={{ color: 'var(--text)' }}>{question.topic}</strong></span>
          </div>

          <p className="question-text" onCopy={(e) => e.preventDefault()} onContextMenu={(e) => e.preventDefault()}>{question.question}</p>

          {phase === 'evaluated' && currentEvaluation ? (
            <EvaluationPanel evaluation={currentEvaluation} onNext={proceedToNext} isLastQuestion={isLastQuestion} />
          ) : (
            <div className="answer-card" style={{ marginTop: 20 }}>
              <div className="answer-card-header">
                <label htmlFor="answer-input" style={{ fontWeight: 600, fontSize: 12, color: 'var(--text-muted)' }}>CANDIDATE RESPONSE</label>
                <span className="word-count-badge">{wordCount} words · {answer.length} chars</span>
              </div>
              <textarea id="answer-input" className="answer-input" value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Type your response here. Explain architectural trade-offs, underlying mechanics, and practical considerations…" disabled={busy} rows={6} onPaste={(e) => e.preventDefault()} onDrop={(e) => e.preventDefault()} onCut={(e) => e.preventDefault()} />
              <div className="answer-actions">
                <span className="text-dim" style={{ fontSize: 12.5 }}>
                  {isLastQuestion ? 'Final Question in this session' : `Question ${question.question_number} of ${totalQuestions}`}
                </span>
                <button className="btn btn-primary" onClick={() => void submitAnswer()} disabled={busy || !answer.trim()}>Submit Response →</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
