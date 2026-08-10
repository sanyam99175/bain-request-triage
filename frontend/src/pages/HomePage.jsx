import { useAuth } from '../context/auth'
import IntakePage from './IntakePage'
import ReviewerQueuePage from './ReviewerQueuePage'

function HomePage() {
  const { session } = useAuth()
  return session.user.role === 'requestor' ? <IntakePage /> : <ReviewerQueuePage />
}

export default HomePage
