import { readSession } from '../auth/session'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

async function requestJson(path, options) {
  const session = readSession()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...options?.headers,
      ...(session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {}),
    },
  })
  const body = await response.json().catch(() => ({}))

  if (!response.ok) {
    const detail = body.detail
    const error = new Error(
      typeof detail === 'string' ? detail : detail?.message ?? 'The request could not be completed.',
    )
    error.status = response.status
    error.code = typeof detail === 'object' ? detail?.code : undefined
    throw error
  }

  return body
}

export function login(email, password) {
  return requestJson('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
}

export function signup(email, password, role) {
  return requestJson('/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, role }),
  })
}

export function createRequest(rawRequest, generationMode, allowSimilar = false) {
  return requestJson('/requests', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      raw_request: rawRequest,
      generation_mode: generationMode,
      allow_similar: allowSimilar,
    }),
  })
}

export function fetchRequests(cursor) {
  const query = new URLSearchParams({ limit: '5' })
  if (cursor) query.set('cursor', cursor)
  return requestJson(`/requests?${query}`)
}

export function fetchRequest(requestId) {
  return requestJson(`/requests/${requestId}`)
}

export function fetchTriageHistory(requestId) {
  return requestJson(`/requests/${requestId}/triage-history`)
}

export function updateTriage(requestId, status, priority, notes, version) {
  return requestJson(`/requests/${requestId}/triage`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, priority, notes, version }),
  })
}
