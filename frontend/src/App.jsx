import { Navigate, Route, Routes } from 'react-router-dom'
import RequireAuth from './components/RequireAuth'
import HomePage from './pages/HomePage'
import IntakePage from './pages/IntakePage'
import LoginPage from './pages/LoginPage'
import ReviewerDetailPage from './pages/ReviewerDetailPage'
import ReviewerQueuePage from './pages/ReviewerQueuePage'
import SignupPage from './pages/SignupPage'
import TriageHistoryPage from './pages/TriageHistoryPage'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/" element={<RequireAuth><HomePage /></RequireAuth>} />
      <Route path="/requests" element={<RequireAuth requiredRole="reviewer"><ReviewerQueuePage /></RequireAuth>} />
      <Route path="/requests/new" element={<RequireAuth requiredRole="requestor"><IntakePage /></RequireAuth>} />
      <Route path="/requests/:requestId/history" element={<RequireAuth requiredRole="reviewer"><TriageHistoryPage /></RequireAuth>} />
      <Route path="/requests/:requestId" element={<RequireAuth requiredRole="reviewer"><ReviewerDetailPage /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
