export function scoreColor(value) {
  if (value >= 80) return '#10b981'
  if (value >= 60) return '#38bdf8'
  if (value >= 40) return '#f59e0b'
  return '#f43f5e'
}

export default function ScoreRing({ value, size = 140, stroke = 10, label }) {
  const clamped = Math.min(100, Math.max(0, value))
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (clamped / 100) * circumference
  const color = scoreColor(clamped)

  return (
    <div className="score-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(255, 255, 255, 0.07)" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset} style={{ transition: 'stroke-dashoffset 0.7s ease, stroke 0.2s ease' }} />
      </svg>
      <div className="score-value" style={{ color }}>{Math.round(clamped)}</div>
      {label ? <div className="score-label">{label}</div> : null}
    </div>
  )
}
