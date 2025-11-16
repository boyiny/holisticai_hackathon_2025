import { Outlet, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Sidebar from '../shared/Sidebar'
import Topbar from '../shared/Topbar'
import ThemeToggle from '../shared/ThemeToggle'
import { LifeProvider } from '../context/LifeContext'
import { SpiralDemo } from '../components/ui/demo'
import { useTheme } from '../hooks/useTheme'

export default function AppLayout() {
  const [showIntro, setShowIntro] = useState(true)
  const { theme, setTheme } = useTheme()
  const location = useLocation()
  const inLifeFlow = location.pathname.startsWith('/life')

  // Force dark theme while in Life 2.0 flow
  useEffect(() => {
    if (inLifeFlow && theme !== 'dark') {
      setTheme('dark')
    }
  }, [inLifeFlow, theme, setTheme])

  return (
    <div className="relative min-h-screen flex">
      {showIntro && (
        <div className="fixed inset-0 z-50">
          <SpiralDemo onEnter={() => setShowIntro(false)} />
        </div>
      )}
      {!inLifeFlow && <Sidebar />}
      <div className="flex-1 flex flex-col">
        <Topbar />
        <main className="p-6 space-y-6">
          <LifeProvider>
            <Outlet />
          </LifeProvider>
        </main>
      </div>
      {!inLifeFlow && <ThemeToggle />}
    </div>
  )
}
