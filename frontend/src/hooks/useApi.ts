import { useEffect, useState } from 'react'

export function useApi<T>(path: string, fallback?: string) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    async function run() {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(path)
        if (!res.ok) throw new Error(`${res.status}`)
        const js = await res.json()
        if (alive) setData(js)
      } catch (e) {
        if (fallback) {
          try {
            const res2 = await fetch(fallback)
            const js2 = await res2.json()
            if (alive) setData(js2)
          } catch (e2) {
            if (alive) setError(String(e2))
          }
        } else {
          if (alive) setError(String(e))
        }
      } finally {
        if (alive) setLoading(false)
      }
    }
    run()
    return () => { alive = false }
  }, [path, fallback])

  return { data, loading, error }
}

