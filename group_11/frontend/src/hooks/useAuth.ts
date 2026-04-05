import { useEffect, useState } from 'react'
import type { User } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    void supabase.auth
      .getSession()
      .then(({ data, error }) => {
        if (cancelled) return
        if (error) {
          console.warn('getSession:', error.message)
        }
        setUser(data.session?.user ?? null)
        setLoading(false)
      })
      .catch((err: unknown) => {
        console.warn('getSession failed:', err)
        if (!cancelled) {
          setUser(null)
          setLoading(false)
        }
      })

    const { data } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
    })
    const subscription = data?.subscription

    return () => {
      cancelled = true
      subscription?.unsubscribe()
    }
  }, [])

  return { user, loading }
}
