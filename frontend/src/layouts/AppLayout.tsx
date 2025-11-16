import { Outlet } from 'react-router-dom'
import { useState } from 'react'
import Sidebar from '../shared/Sidebar'
import Topbar from '../shared/Topbar'
import ThemeToggle from '../shared/ThemeToggle'
import { SpiralDemo } from '../components/ui/demo'

export default function AppLayout() {
  const [showIntro, setShowIntro] = useState(true)

  return (
    <div className="relative min-h-screen flex">
      {showIntro && (
        <div className="fixed inset-0 z-50">
          <SpiralDemo onEnter={() => setShowIntro(false)} />
        </div>
      )}
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />
        <main className="p-6 space-y-6">
          <Outlet />
        </main>
      </div>
      <ThemeToggle />
    </div>
  )
}
