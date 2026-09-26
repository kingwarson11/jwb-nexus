import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, login } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Signup() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { refreshBusinesses } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/api/auth/signup', { full_name: fullName, email, password })
      await login(email, password)
      await refreshBusinesses()
      navigate('/create-business')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={handleSubmit} className="w-full max-w-sm bg-white p-8 rounded-xl shadow space-y-4">
        <div className="text-center mb-2">
          <h1 className="text-2xl font-bold text-brand-700">JWB NEXUS</h1>
          <p className="text-sm text-gray-500">Create your account</p>
        </div>
        {error && <div className="text-sm text-red-600 bg-red-50 rounded p-2">{error}</div>}
        <input required placeholder="Full name" value={fullName}
          onChange={(e) => setFullName(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" />
        <input type="email" required placeholder="Email" value={email}
          onChange={(e) => setEmail(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" />
        <input type="password" required placeholder="Password" value={password}
          onChange={(e) => setPassword(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" />
        <button disabled={loading}
          className="w-full bg-brand-600 text-white rounded-lg py-2 font-medium hover:bg-brand-700 disabled:opacity-50">
          {loading ? 'Creating account…' : 'Sign up'}
        </button>
        <p className="text-sm text-center text-gray-500">
          Already have an account? <Link to="/login" className="text-brand-600 font-medium">Log in</Link>
        </p>
      </form>
    </div>
  )
}
