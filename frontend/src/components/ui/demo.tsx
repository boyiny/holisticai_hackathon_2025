'use client'

import { useEffect, useState } from 'react'
import { SpiralAnimation } from '@/components/ui/spiral-animation'

type SpiralDemoProps = {
  onEnter?: () => void
}

export function SpiralDemo({ onEnter }: SpiralDemoProps) {
  const [startVisible, setStartVisible] = useState(false)

  const handleEnter = () => {
    if (onEnter) {
      onEnter()
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      setStartVisible(true)
    }, 2000)

    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden bg-black">
      <div className="absolute inset-0">
        <SpiralAnimation />
      </div>

      <div
        className={`absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10 transition-all duration-1500 ease-out ${
          startVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}
      >
        <button
          onClick={handleEnter}
          className="text-white text-center text-3xl tracking-[0.25em] uppercase font-extralight transition-all duration-700 hover:tracking-[0.35em] animate-pulse"
        >
          <div className="text-5xl mb-3 tracking-[0.35em]">Life 2.0</div>
          <div className="text-lg tracking-[0.4em]">Enter</div>
        </button>
      </div>
    </div>
  )
}


