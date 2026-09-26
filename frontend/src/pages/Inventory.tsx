import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type Row = {
  product_id: string; name: string; quantity: number; minimum_stock: number
  avg_daily_sales: number; estimated_days_of_cover: number | null; low_stock: boolean; expiry_date: string | null
}
type SlowMoving = { product_name: string; recent_period_units: number; baseline_period_units: number; decline_pct: number; current_stock: number }

export default function Inventory() {
  const { business } = useAuth()
  const [rows, setRows] = useState<Row[]>([])
  const [slowMoving, setSlowMoving] = useState<SlowMoving[]>([])

  useEffect(() => {
    if (!business) return
    api.get(`/api/businesses/${business.id}/inventory`).then(setRows)
    api.get(`/api/businesses/${business.id}/inventory/slow-moving`).then(setSlowMoving)
  }, [business])

  if (!business) return null

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1">Inventory Intelligence</h1>
        <p className="text-gray-500 mb-6">Stock levels, sales velocity, and estimated days of cover.</p>
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 text-left">
              <tr>
                <th className="px-4 py-3">Product</th><th className="px-4 py-3">Stock</th>
                <th className="px-4 py-3">Avg daily sales</th><th className="px-4 py-3">Est. days of cover</th><th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.product_id} className="border-t">
                  <td className="px-4 py-3 font-medium">{r.name}</td>
                  <td className="px-4 py-3">{r.quantity}</td>
                  <td className="px-4 py-3">{r.avg_daily_sales}</td>
                  <td className="px-4 py-3">{r.estimated_days_of_cover ?? '—'}</td>
                  <td className="px-4 py-3">
                    {r.low_stock
                      ? <span className="text-red-600 font-medium">Low stock</span>
                      : <span className="text-green-600">Healthy</span>}
                  </td>
                </tr>
              ))}
              {rows.length === 0 && <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">No products yet.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      {slowMoving.length > 0 && (
        <div>
          <h2 className="font-semibold mb-3">Slow-moving alerts</h2>
          <div className="space-y-2">
            {slowMoving.map((s, i) => (
              <div key={i} className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm">
                <span className="font-medium">{s.product_name}</span> sales are down {s.decline_pct}% vs. the recent baseline.
                You currently have {s.current_stock} units in stock — consider reducing your next order.
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
