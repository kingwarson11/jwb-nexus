import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type Product = {
  id: string; name: string; category?: string; selling_price: number; cost_price: number
  quantity: number; minimum_stock: number; expiry_date?: string
}

export default function Products() {
  const { business } = useAuth()
  const [products, setProducts] = useState<Product[]>([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', category: '', selling_price: '', cost_price: '', quantity: '', minimum_stock: '5', expiry_date: '' })
  const [error, setError] = useState('')

  const load = () => {
    if (!business) return
    api.get(`/api/businesses/${business.id}/products`).then(setProducts)
  }

  useEffect(load, [business])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!business) return
    setError('')
    try {
      await api.post(`/api/businesses/${business.id}/products`, {
        name: form.name,
        category: form.category || null,
        selling_price: parseFloat(form.selling_price),
        cost_price: parseFloat(form.cost_price),
        quantity: parseInt(form.quantity || '0'),
        minimum_stock: parseInt(form.minimum_stock || '5'),
        expiry_date: form.expiry_date || null,
      })
      setForm({ name: '', category: '', selling_price: '', cost_price: '', quantity: '', minimum_stock: '5', expiry_date: '' })
      setShowForm(false)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save product')
    }
  }

  if (!business) return null

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Products</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-brand-500 text-black rounded-lg text-sm font-semibold hover:bg-brand-600">
          {showForm ? 'Cancel' : '+ Add Product'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border p-5 mb-6 grid grid-cols-2 gap-3">
          {error && <div className="col-span-2 text-sm text-red-600 bg-red-50 rounded p-2">{error}</div>}
          <input required placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
          <input placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
          <input required type="number" step="0.01" placeholder="Selling price" value={form.selling_price} onChange={(e) => setForm({ ...form, selling_price: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
          <input required type="number" step="0.01" placeholder="Cost price" value={form.cost_price} onChange={(e) => setForm({ ...form, cost_price: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
          <input type="number" placeholder="Starting quantity" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
          <input type="number" placeholder="Minimum stock" value={form.minimum_stock} onChange={(e) => setForm({ ...form, minimum_stock: e.target.value })} className="border rounded-lg px-3 py-2 text-sm" />
          <input type="date" placeholder="Expiry date" value={form.expiry_date} onChange={(e) => setForm({ ...form, expiry_date: e.target.value })} className="border rounded-lg px-3 py-2 text-sm col-span-2" />
          <button className="col-span-2 bg-brand-500 text-black rounded-lg py-2 text-sm font-semibold hover:bg-brand-600">Save product</button>
        </form>
      )}

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-left">
            <tr>
              <th className="px-4 py-3">Name</th><th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Price</th><th className="px-4 py-3">Stock</th><th className="px-4 py-3">Expiry</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id} className="border-t">
                <td className="px-4 py-3 font-medium">{p.name}</td>
                <td className="px-4 py-3 text-gray-500">{p.category || '—'}</td>
                <td className="px-4 py-3">{business.currency} {p.selling_price}</td>
                <td className={`px-4 py-3 ${p.quantity <= p.minimum_stock ? 'text-red-600 font-medium' : ''}`}>{p.quantity}</td>
                <td className="px-4 py-3 text-gray-500">{p.expiry_date || '—'}</td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">No products yet — add your first one above.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
