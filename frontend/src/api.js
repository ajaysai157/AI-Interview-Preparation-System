export const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export class ApiError extends Error {
  constructor(status, detail) {
    super(formatDetail(detail))
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

function formatDetail(detail) {
  if (typeof detail === 'string' && detail.length > 0) return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const loc = Array.isArray(item?.loc) ? item.loc.join('.') : ''
        return loc ? `${loc}: ${item?.msg || 'invalid'}` : (item?.msg || 'invalid input')
      })
      .join('; ')
  }
  return 'Request failed. Please try again.'
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    })
  } catch {
    throw new ApiError(0, `Cannot reach the API at ${API_BASE || 'the backend'}. Is the backend running?`)
  }

  const text = await response.text()
  const body = text ? JSON.parse(text) : null

  if (!response.ok) {
    throw new ApiError(response.status, body?.detail || body || `HTTP ${response.status}`)
  }
  return body
}

export const api = {
  health: () => request('/health'),

  getStats: () => request('/interviews/stats/summary'),

  getInterviews: () => request('/interviews'),

  createInterview: (payload) =>
    request('/interviews', { method: 'POST', body: JSON.stringify(payload) }),

  getInterview: (interviewId) =>
    request(`/interviews/${interviewId}`),

  deleteInterview: (interviewId) =>
    request(`/interviews/${interviewId}`, { method: 'DELETE' }),

  startInterview: (interviewId) =>
    request(`/interviews/${interviewId}/start`, { method: 'POST' }),

  submitAnswer: (interviewId, answer) =>
    request(`/interviews/${interviewId}/answer`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    }),

  continueInterview: (interviewId, payload) =>
    request(`/interviews/${interviewId}/continue`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getResult: (interviewId) =>
    request(`/interviews/${interviewId}/result`),
}

export function evaluationFromDraft(draft) {
  return {
    score: clampScore(draft.score),
    correctness: clampScore(draft.correctness),
    completeness: clampScore(draft.completeness),
    clarity: clampScore(draft.clarity),
    relevance: clampScore(draft.relevance),
    feedback: draft.feedback.trim(),
    improvement_areas: draft.improvement_areas
      .split(',')
      .map((area) => area.trim())
      .filter(Boolean),
  }
}

function clampScore(value) {
  return Math.min(10, Math.max(0, Number(value)))
}
