import { useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type Income = { revenue: number; cost_of_goods_sold: number; gross_profit: number; operating_expenses: number; net_profit: number }
type CashFlow = { opening_balance: number; cash_in: number; cash_out: number; closing_balance: number; net_cash_flow: number }

function firstOfMonth() {
  const d = new Date(); d.setDate(1)
  return d.toISOString().slice(0, 10)
}
function today() { return new Date().toISOString().slice(0, 10) }

export default function Reports() {
  const { business } = useAuth()
  const [start, setStart] = useState(firstOfMonth())
  const [end, setEnd] = useState(today())
  const [opening, setOpening] = useState('0')
  const [income, setIncome] = useState<Income | null>(null)
  const [cashFlow, setCashFlow] = useState<CashFlow | null>(null)
  const [error, setError] = useState('')

  const runReports = async () => {
    if (!business) return
    setError('')
    try {
      const [inc, cf] = await Promise.all([
        api.get(`/api/businesses/${business.id}/reports/income-statement?start=${start}&end=${end}`),
        api.get(`/api/businesses/${business.id}/reports/cash-flow?start=${start}&end=${end}&opening_balance=${opening}`),
      ])
      setIncome(inc); setCashFlow(cf)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load reports')
    }
  }

  if (!business) return null

  const Row = ({ label, value, bold = false }: { label: string; value: number; bold?: boolean }) => (
    <div className={`flex justify-between py-1.5 ${bold ? 'font-semibold border-t mt-1 pt-2' : 'text-gray-600'}`}>
      <span>{label}</span><span>{business.currency} {value.toLocaleString()}</span>
    </div>
  )

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Financial Reports</h1>

      <div className="bg-white rounded-xl shadow-sm border p-5 mb-6 flex gap-3 items-end flex-wrap">
        <div><label className="block text-xs text-gray-500 mb-1">Start</label>
          <input type="date" value={start} onChange={(e) => setStart(e.target.value)} className="border rounded-lg px-3 py-2 text-sm" /></div>
        <div><label className="block text-xs text-gray-500 mb-1">End</label>
          <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} className="border rounded-lg px-3 py-2 text-sm" /></div>
        <div><label className="block text-xs text-gray-500 mb-1">Opening cash balance</label>
          <input type="number" value={opening} onChange={(e) => setOpening(e.target.value)} className="border rounded-lg px-3 py-2 text-sm w-32" /></div>
        <button onClick={runReports} className="bg-brand-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-brand-700">Run</button>
      </div>

      {error && <div className="text-sm text-red-600 bg-red-50 rounded p-3 mb-4">{error}</div>}

      <div className="grid grid-cols-2 gap-6">
        {income && (
          <div className="bg-white rounded-xl shadow-sm border p-5">
            <h2 className="font-semibold mb-2">Income Statement</h2>
            <Row label="Revenue" value={income.revenue} />
            <Row label="Cost of goods sold" value={-income.cost_of_goods_sold} />
            <Row label="Gross profit" value={income.gross_profit} bold />
            <Row label="Operating expenses" value={-income.operating_expenses} />
            <Row label="Net profit" value={income.net_profit} bold />
          </div>
        )}
        {cashFlow && (
          <div className="bg-white rounded-xl shadow-sm border p-5">
            <h2 className="font-semibold mb-2">Cash Flow Statement</h2>
            <Row label="Opening balance" value={cashFlow.opening_balance} />
            <Row label="Cash in (revenue)" value={cashFlow.cash_in} />
            <Row label="Cash out (expenses)" value={-cashFlow.cash_out} />
            <Row label="Closing balance" value={cashFlow.closing_balance} bold />
          </div>
        )}
      </div>
    </div>
  )
}
