import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api/requests'
import { useAuth } from '../context/auth'

function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { signIn } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    setIsSubmitting(true)
    try {
      const session = await login(email, password)
      signIn(session)
      navigate('/')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <p className="eyebrow">Business request triage</p>
        <h1>Sign in</h1>
        <p className="intro-copy">Sign in to continue to your requestor or reviewer workflow.</p>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
        </label>
        <label>
          Password
          <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required />
        </label>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in…' : 'Sign in'}
        </button>
        {errorMessage && <p className="error-message" role="alert">{errorMessage}</p>}
        <p className="auth-link">New here? <Link to="/signup">Create an account</Link></p>
      </form>
    </main>
  )
}

export default LoginPage
