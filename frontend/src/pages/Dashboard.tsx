import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type Summary = {
  today_revenue: number
  today_sales_count: number
  gross_profit_today: number
  inventory_value: number
  low_stock_count: number
  expiring_soon_count: number
  slow_moving_count: number
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-bold text-gray-900 mt-1">{value}</div>
    </div>
  )
}

export default function Dashboard() {
  const { business } = useAuth()
  const [summary, setSummary] = useState<Summary | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!business) return
    api.get(`/api/businesses/${business.id}/reports/dashboard`)
      .then(setSummary)
      .catch((e) => setError(e.message))
  }, [business])

  if (!business) return null

  const insights: string[] = []
  if (summary) {
    if (summary.low_stock_count > 0) insights.push(`${summary.low_stock_count} product(s) are running low on stock.`)
    if (summary.expiring_soon_count > 0) insights.push(`${summary.expiring_soon_count} product(s) expire within 7 days.`)
    if (summary.slow_moving_count > 0) insights.push(`${summary.slow_moving_count} product(s) are becoming slow-moving.`)
    if (insights.length === 0) insights.push('No urgent issues detected today — inventory and cash flow look healthy.')
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-1">{business.name}</h1>
      <p className="text-gray-500 mb-6">Today's overview</p>

      {error && <div className="text-sm text-red-600 bg-red-50 rounded p-3 mb-4">{error}</div>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Today's Revenue" value={summary ? `${business.currency} ${summary.today_revenue.toLocaleString()}` : '—'} />
        <StatCard label="Today's Sales" value={summary?.today_sales_count ?? '—'} />
        <StatCard label="Gross Profit (today)" value={summary ? `${business.currency} ${summary.gross_profit_today.toLocaleString()}` : '—'} />
        <StatCard label="Inventory Value" value={summary ? `${business.currency} ${summary.inventory_value.toLocaleString()}` : '—'} />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h2 className="font-semibold mb-3">AI Insights</h2>
        <ul className="space-y-2">
          {insights.map((line, i) => (
            <li key={i} className="text-sm text-gray-700 flex gap-2">
              <span className="text-brand-600">•</span> {line}
            </li>
          ))}
          {!summary && <li className="text-sm text-gray-400">Loading…</li>}
        </ul>
      </div>
    </div>
  )
}
