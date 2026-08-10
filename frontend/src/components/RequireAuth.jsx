import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/auth'

function RequireAuth({ children, requiredRole }) {
  const { session } = useAuth()
  if (!session) return <Navigate to="/login" replace />
  if (requiredRole && session.user.role !== requiredRole) return <Navigate to="/" replace />
  return children
}

export default RequireAuth
