import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { logout } from '../api/client'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/pos', label: 'POS' },
  { to: '/products', label: 'Products' },
  { to: '/inventory', label: 'Inventory' },
  { to: '/expenses', label: 'Expenses' },
  { to: '/reports', label: 'Reports' },
  { to: '/ai', label: 'AI Analyst' },
  { to: '/market', label: 'Market Intelligence' },
]

export default function Layout() {
  const { business, businesses, setBusiness } = useAuth()
  const navigate = useNavigate()

  if (businesses.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center space-y-3">
          <p className="text-gray-600">You don't have a business set up yet.</p>
          <button
            onClick={() => navigate('/create-business')}
            className="px-4 py-2 bg-brand-500 text-black font-semibold rounded-lg hover:bg-brand-600"
          >
            Create your business
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex">
      <aside className="w-56 bg-ink-900 text-white flex flex-col">
        <div className="px-5 py-5 border-b border-ink-700">
          <div className="font-bold text-lg tracking-tight">
            JWB <span className="text-brand-500">NEXUS</span>
          </div>
          <div className="text-xs text-gray-400 mt-1 truncate">{business?.name}</div>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === '/'}
              className={({ isActive }) =>
                `block px-3 py-2 rounded-lg text-sm font-medium ${
                  isActive ? 'bg-brand-500 text-black' : 'text-gray-300 hover:bg-ink-700'
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-ink-700 space-y-2">
          {businesses.length > 1 && (
            <select
              className="w-full text-xs rounded bg-ink-700 text-white px-2 py-1 border border-ink-600"
              value={business?.id}
              onChange={(e) => {
                const b = businesses.find((x) => x.id === e.target.value)
                if (b) setBusiness(b)
              }}
            >
              {businesses.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          )}
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="w-full text-xs text-gray-400 hover:text-brand-500 text-left"
          >
            Log out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
