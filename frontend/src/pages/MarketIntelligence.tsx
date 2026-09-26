import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Trend = {
  area: string; category: string; product_name: string | null
  period_start: string; period_end: string
  demand_change_pct: number; participating_businesses: number
}

export default function MarketIntelligence() {
  const [trends, setTrends] = useState<Trend[]>([])
  const [areas, setAreas] = useState<string[]>([])
  const [areaFilter, setAreaFilter] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/api/market/areas').then(setAreas).catch(() => {})
  }, [])

  useEffect(() => {
    const qs = areaFilter ? `?area=${encodeURIComponent(areaFilter)}` : ''
    api.get(`/api/market/trends${qs}`).then(setTrends).catch((e) => setError(e.message))
  }, [areaFilter])

  const categoryLevel = trends.filter((t) => !t.product_name).sort((a, b) => b.demand_change_pct - a.demand_change_pct)
  const productLevel = trends.filter((t) => t.product_name).sort((a, b) => b.demand_change_pct - a.demand_change_pct)

  const Badge = ({ pct }: { pct: number }) => (
    <span className={`font-semibold ${pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
      {pct >= 0 ? '+' : ''}{pct}%
    </span>
  )

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-1">Market Intelligence</h1>
          <p className="text-gray-500 text-sm">
            Anonymised, aggregated demand trends across participating businesses. No merchant names or individual figures — only area-level and category-level signals.
          </p>
        </div>
        <select value={areaFilter} onChange={(e) => setAreaFilter(e.target.value)} className="border rounded-lg px-3 py-2 text-sm h-fit">
          <option value="">All areas</option>
          {areas.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>

      {error && <div className="text-sm text-red-600 bg-red-50 rounded p-3">{error}</div>}
      {trends.length === 0 && !error && (
        <div className="text-sm text-gray-400 bg-white border rounded-xl p-6 text-center">
          No market data yet. Run <code className="bg-gray-100 px-1 rounded">python seed_market_synthetic.py</code> in the backend to populate demo trends.
        </div>
      )}

      {categoryLevel.length > 0 && (
        <div>
          <h2 className="font-semibold mb-3">Category demand, by area (last 4 weeks vs. prior 4)</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {categoryLevel.map((t, i) => (
              <div key={i} className="bg-white border rounded-xl p-4">
                <div className="text-xs text-gray-400">{t.area}</div>
                <div className="font-medium">{t.category}</div>
                <div className="mt-1"><Badge pct={t.demand_change_pct} /></div>
                <div className="text-xs text-gray-400 mt-1">{t.participating_businesses} businesses</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {productLevel.length > 0 && (
        <div>
          <h2 className="font-semibold mb-3">Product-level trends</h2>
          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-left">
                <tr><th className="px-4 py-3">Product</th><th className="px-4 py-3">Category</th><th className="px-4 py-3">Area</th><th className="px-4 py-3">Demand change</th><th className="px-4 py-3">Businesses</th></tr>
              </thead>
              <tbody>
                {productLevel.slice(0, 20).map((t, i) => (
                  <tr key={i} className="border-t">
                    <td className="px-4 py-3 font-medium">{t.product_name}</td>
                    <td className="px-4 py-3 text-gray-500">{t.category}</td>
                    <td className="px-4 py-3 text-gray-500">{t.area}</td>
                    <td className="px-4 py-3"><Badge pct={t.demand_change_pct} /></td>
                    <td className="px-4 py-3 text-gray-400">{t.participating_businesses}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
