import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function CreateBusiness() {
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [area, setArea] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { refreshBusinesses, setBusiness } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const business = await api.post('/api/businesses', { name, category, area, currency: 'GHS' })
      await refreshBusinesses()
      setBusiness(business)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create business')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={handleSubmit} className="w-full max-w-sm bg-white p-8 rounded-xl shadow space-y-4">
        <div className="text-center mb-2">
          <h1 className="text-2xl font-bold text-ink-900">Set up your business</h1>
        </div>
        {error && <div className="text-sm text-red-600 bg-red-50 rounded p-2">{error}</div>}
        <input required placeholder="Business name (e.g. Benjamin's Mini Mart)" value={name}
          onChange={(e) => setName(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" />
        <input placeholder="Category (e.g. Retail / Pharmacy)" value={category}
          onChange={(e) => setCategory(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" />
        <input placeholder="Area (e.g. East Legon)" value={area}
          onChange={(e) => setArea(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" />
        <button disabled={loading}
          className="w-full bg-brand-500 text-black rounded-lg py-2 font-semibold hover:bg-brand-600 disabled:opacity-50">
          {loading ? 'Creating…' : 'Create business'}
        </button>
      </form>
    </div>
  )
}
