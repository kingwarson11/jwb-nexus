import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type Expense = { id: string; category: string; description?: string; amount: number; date: string }

const CATEGORIES = ['rent', 'electricity', 'transport', 'suppliers', 'salaries', 'internet', 'other']

export default function Expenses() {
  const { business } = useAuth()
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [form, setForm] = useState({ category: 'rent', description: '', amount: '' })
  const [error, setError] = useState('')

  const load = () => {
    if (!business) return
    api.get(`/api/businesses/${business.id}/expenses`).then(setExpenses)
  }
  useEffect(load, [business])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!business) return
    setError('')
    try {
      await api.post(`/api/businesses/${business.id}/expenses`, {
        category: form.category, description: form.description || null, amount: parseFloat(form.amount),
      })
      setForm({ category: 'rent', description: '', amount: '' })
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save expense')
    }
  }

  if (!business) return null

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Expenses</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border p-5 mb-6 grid grid-cols-4 gap-3 items-end">
        {error && <div className="col-span-4 text-sm text-red-600 bg-red-50 rounded p-2">{error}</div>}
        <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="border rounded-lg px-3 py-2 text-sm">
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <input placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
        <input required type="number" step="0.01" placeholder="Amount" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
        <button className="bg-brand-500 text-black rounded-lg py-2 text-sm font-semibold hover:bg-brand-600">Add expense</button>
      </form>

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-left">
            <tr><th className="px-4 py-3">Date</th><th className="px-4 py-3">Category</th><th className="px-4 py-3">Description</th><th className="px-4 py-3">Amount</th></tr>
          </thead>
          <tbody>
            {expenses.map((e) => (
              <tr key={e.id} className="border-t">
                <td className="px-4 py-3 text-gray-500">{e.date}</td>
                <td className="px-4 py-3 capitalize">{e.category}</td>
                <td className="px-4 py-3 text-gray-500">{e.description || '—'}</td>
                <td className="px-4 py-3">{business.currency} {e.amount}</td>
              </tr>
            ))}
            {expenses.length === 0 && <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-400">No expenses recorded yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
