import React, { createContext, useContext, useEffect, useState } from 'react'
import { api, getToken } from '../api/client'

type Business = { id: string; name: string; category?: string; area?: string; currency: string }

type AuthContextType = {
  isAuthenticated: boolean
  business: Business | null
  businesses: Business[]
  setBusiness: (b: Business) => void
  refreshBusinesses: () => Promise<void>
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [businesses, setBusinesses] = useState<Business[]>([])
  const [business, setBusinessState] = useState<Business | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshBusinesses = async () => {
    if (!getToken()) {
      setLoading(false)
      return
    }
    try {
      const list = await api.get('/api/businesses')
      setBusinesses(list)
      const savedId = localStorage.getItem('jwb_business_id')
      const match = list.find((b: Business) => b.id === savedId)
      setBusinessState(match || list[0] || null)
    } catch {
      /* token likely invalid/expired */
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshBusinesses()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const setBusiness = (b: Business) => {
    setBusinessState(b)
    localStorage.setItem('jwb_business_id', b.id)
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!getToken(),
        business,
        businesses,
        setBusiness,
        refreshBusinesses,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
