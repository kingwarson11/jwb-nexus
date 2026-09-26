import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type Product = { id: string; name: string; selling_price: number; quantity: number }
type CartLine = { product: Product; quantity: number }

export default function POS() {
  const { business } = useAuth()
  const [products, setProducts] = useState<Product[]>([])
  const [cart, setCart] = useState<CartLine[]>([])
  const [method, setMethod] = useState('MOMO')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!business) return
    api.get(`/api/businesses/${business.id}/products`).then(setProducts)
  }, [business])

  const addToCart = (product: Product) => {
    setCart((prev) => {
      const existing = prev.find((l) => l.product.id === product.id)
      if (existing) {
        return prev.map((l) => l.product.id === product.id ? { ...l, quantity: l.quantity + 1 } : l)
      }
      return [...prev, { product, quantity: 1 }]
    })
  }

  const updateQty = (id: string, qty: number) => {
    setCart((prev) => prev.map((l) => l.product.id === id ? { ...l, quantity: qty } : l).filter((l) => l.quantity > 0))
  }

  const total = cart.reduce((sum, l) => sum + l.product.selling_price * l.quantity, 0)

  const checkout = async () => {
    if (!business || cart.length === 0) return
    setError(''); setMessage('')
    try {
      const sale = await api.post(`/api/businesses/${business.id}/sales`, {
        items: cart.map((l) => ({ product_id: l.product.id, quantity: l.quantity })),
        discount: 0,
        payment: { method, amount: total },
      })
      setMessage(`Sale completed — ${business.currency} ${sale.total}. Payment via ${method}.`)
      setCart([])
      api.get(`/api/businesses/${business.id}/products`).then(setProducts)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Checkout failed')
    }
  }

  if (!business) return null

  return (
    <div className="p-8 max-w-6xl mx-auto grid grid-cols-3 gap-6">
      <div className="col-span-2">
        <h1 className="text-2xl font-bold mb-4">Point of Sale</h1>
        <div className="grid grid-cols-3 gap-3">
          {products.map((p) => (
            <button key={p.id} onClick={() => addToCart(p)} disabled={p.quantity <= 0}
              className="bg-white border rounded-xl p-4 text-left hover:border-brand-500 disabled:opacity-40 disabled:cursor-not-allowed">
              <div className="font-medium text-sm">{p.name}</div>
              <div className="text-brand-600 font-semibold mt-1">{business.currency} {p.selling_price}</div>
              <div className="text-xs text-gray-400 mt-1">{p.quantity} in stock</div>
            </button>
          ))}
          {products.length === 0 && <p className="text-gray-400 col-span-3">No products yet. Add products first.</p>}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-5 h-fit sticky top-8">
        <h2 className="font-semibold mb-3">Cart</h2>
        {cart.length === 0 && <p className="text-sm text-gray-400">Tap a product to add it.</p>}
        <div className="space-y-2">
          {cart.map((l) => (
            <div key={l.product.id} className="flex items-center justify-between text-sm">
              <span className="flex-1">{l.product.name}</span>
              <input type="number" min={0} value={l.quantity}
                onChange={(e) => updateQty(l.product.id, parseInt(e.target.value || '0'))}
                className="w-14 border rounded px-1 py-0.5 text-center" />
              <span className="w-16 text-right">{(l.product.selling_price * l.quantity).toFixed(2)}</span>
            </div>
          ))}
        </div>
        {cart.length > 0 && (
          <>
            <div className="border-t mt-3 pt-3 flex justify-between font-semibold">
              <span>Total</span><span>{business.currency} {total.toFixed(2)}</span>
            </div>
            <select value={method} onChange={(e) => setMethod(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm mt-3">
              <option value="MOMO">MoMo</option>
              <option value="CASH">Cash</option>
              <option value="BANK">Bank</option>
              <option value="CARD">Card</option>
            </select>
            <button onClick={checkout} className="w-full mt-3 bg-brand-600 text-white rounded-lg py-2 font-medium hover:bg-brand-700">
              Complete Sale
            </button>
          </>
        )}
        {message && <div className="text-sm text-green-700 bg-green-50 rounded p-2 mt-3">{message}</div>}
        {error && <div className="text-sm text-red-600 bg-red-50 rounded p-2 mt-3">{error}</div>}
      </div>
    </div>
  )
}
