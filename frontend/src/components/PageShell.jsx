import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/auth'

function PageShell({ children }) {
  const { session, signOut } = useAuth()
  const navigate = useNavigate()

  function handleSignOut() {
    signOut()
    navigate('/login')
  }

  return (
    <main className="page-shell">
      <div className="session-bar">
        <span>{session.user.email} · {session.user.role}</span>
        <button type="button" onClick={handleSignOut}>Sign out</button>
      </div>
      {children}
    </main>
  )
}

export default PageShell
