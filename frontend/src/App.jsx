import { useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from './store/authStore.js'
import Layout from './components/ui/Layout.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Learn from './pages/Learn.jsx'
import Practice from './pages/Practice.jsx'
import ExamSetup from './pages/ExamSetup.jsx'
import ExamRunner from './pages/ExamRunner.jsx'
import ExamResults from './pages/ExamResults.jsx'
import WrongQuestions from './pages/WrongQuestions.jsx'
import AITutor from './pages/AITutor.jsx'
import Analytics from './pages/Analytics.jsx'
import Dumps from './pages/Dumps.jsx'

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuthStore()

  if (loading) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
          <p className="text-sm text-muted">Loading CertMind...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default function App() {
  const { init, isAuthenticated } = useAuthStore()
  const location = useLocation()

  useEffect(() => {
    init()
  }, [])

  // Redirect authenticated users away from login
  if (isAuthenticated && location.pathname === '/login') {
    return <Navigate to="/" replace />
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/learn" element={<Learn />} />
                <Route path="/practice" element={<Practice />} />
                <Route path="/exam" element={<ExamSetup />} />
                <Route path="/exam/run/:sessionId" element={<ExamRunner />} />
                <Route path="/exam/results/:sessionId" element={<ExamResults />} />
                <Route path="/wrong-questions" element={<WrongQuestions />} />
                <Route path="/tutor" element={<AITutor />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/dumps" element={<Dumps />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
