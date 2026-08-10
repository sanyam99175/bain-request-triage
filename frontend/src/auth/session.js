const SESSION_STORAGE_KEY = 'request-triage-session'

function readSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_STORAGE_KEY))
  } catch {
    return null
  }
}

function saveSession(session) {
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
}

function clearSession() {
  localStorage.removeItem(SESSION_STORAGE_KEY)
}

export { clearSession, readSession, saveSession }
