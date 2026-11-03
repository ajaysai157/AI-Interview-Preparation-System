export default function AiInterviewer({ statusText, role = 'Technical Interviewer', difficulty = 'medium', isThinking = false }) {
  return (
    <div className={`ai-interviewer-card ${isThinking ? 'is-thinking' : ''}`}>
      <div className="ai-avatar-wrap">
        <div className="ai-avatar" title="AI Assessment Model">AI</div>
        <div className="ai-info">
          <h4>{role} Assessment</h4>
          <div className="ai-status">
            <span className="status-dot" />
            <span>{statusText}</span>
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <div className="sound-wave" title="Neural activity monitor">
          <div className="wave-bar" /><div className="wave-bar" /><div className="wave-bar" /><div className="wave-bar" /><div className="wave-bar" />
        </div>
        <span className="chip chip-cyan">Difficulty: {difficulty}</span>
      </div>
    </div>
  )
}
