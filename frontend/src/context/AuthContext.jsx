import { useState } from 'react'
import { readSession, saveSession, clearSession } from '../auth/session'
import { AuthContext } from './auth'

function AuthProvider({ children }) {
  const [session, setSession] = useState(readSession)

  function signIn(nextSession) {
    saveSession(nextSession)
    setSession(nextSession)
  }

  function signOut() {
    clearSession()
    setSession(null)
  }

  return <AuthContext value={{ session, signIn, signOut }}>{children}</AuthContext>
}

export { AuthProvider }
