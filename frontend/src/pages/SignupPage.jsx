import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signup } from '../api/requests'
import { useAuth } from '../context/auth'

function SignupPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('requestor')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { signIn } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    setIsSubmitting(true)
    try {
      const session = await signup(email, password, role)
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
        <h1>Create an account</h1>
        <p className="intro-copy">Choose the workspace you need, then get started right away.</p>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
        </label>
        <label>
          Password
          <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" minLength="8" required />
        </label>
        <label>
          Role
          <select value={role} onChange={(event) => setRole(event.target.value)}>
            <option value="requestor">Requestor</option>
            <option value="reviewer">Reviewer</option>
          </select>
        </label>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Creating account…' : 'Create account'}
        </button>
        {errorMessage && <p className="error-message" role="alert">{errorMessage}</p>}
        <p className="auth-link">Already have an account? <Link to="/login">Sign in</Link></p>
      </form>
    </main>
  )
}

export default SignupPage
