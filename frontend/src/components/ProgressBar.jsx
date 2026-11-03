export default function ProgressBar({ current, total }) {
  const nodes = Array.from({ length: total }, (_, i) => i + 1)

  return (
    <div className="pipeline-wrap">
      <div className="pipeline-header">
        <span style={{ color: 'var(--primary)' }}>Question Pipeline</span>
        <span className="text-dim">{current} of {total} Complete</span>
      </div>
      <div className="pipeline-steps">
        {nodes.map((stepNum) => {
          let stateClass = ''
          if (stepNum <= current) stateClass = 'completed'
          else if (stepNum === current + 1) stateClass = 'active'
          return <div key={stepNum} className={`pipeline-node ${stateClass}`} title={`Question ${stepNum}`} />
        })}
      </div>
    </div>
  )
}
