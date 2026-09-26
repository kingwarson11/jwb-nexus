import { Routes, Route } from 'react-router-dom'
import Login from './pages/Login'
import Signup from './pages/Signup'
import CreateBusiness from './pages/CreateBusiness'
import Dashboard from './pages/Dashboard'
import POS from './pages/POS'
import Products from './pages/Products'
import Inventory from './pages/Inventory'
import Expenses from './pages/Expenses'
import Reports from './pages/Reports'
import AIAnalyst from './pages/AIAnalyst'
import MarketIntelligence from './pages/MarketIntelligence'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/create-business" element={<CreateBusiness />} />
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/pos" element={<POS />} />
          <Route path="/products" element={<Products />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/expenses" element={<Expenses />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/ai" element={<AIAnalyst />} />
          <Route path="/market" element={<MarketIntelligence />} />
        </Route>
      </Route>
    </Routes>
  )
}
