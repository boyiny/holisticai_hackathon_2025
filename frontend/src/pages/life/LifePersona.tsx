import { useNavigate } from 'react-router-dom'
import { useLife, Persona, FocusArea } from '../../context/LifeContext'
import { useState } from 'react'

const personas: Persona[] = [
  { name: 'Jordan Dubois', age: 35, summary: 'Ambitious product leader prioritizing energy, metabolic balance, and long-term vitality' },
  { name: 'Alex Sharma', age: 63, summary: 'Older adult committed to staying active, mobile, and resilient.' },
  { name: 'Sacha Silva', age: 24, summary: 'High-stress young professional seeking better rest, energy, and recovery.' },
]

// Default images that persist from the public folder
const defaultPersonaImages: Record<string, string> = {
  'Jordan Dubois': '/personas/Jordan.jpg',
  'Alex Sharma': '/personas/Alex.jpg',
  'Sacha Silva': '/personas/Sacha.jpg',
}

const focusAreas: FocusArea[] = [
  { title: 'Metabolic Health', description: 'Weight, energy, blood sugar stability, sustainable nutrition.' },
  { title: 'Sleep & Recovery', description: 'Improve sleep quality, circadian rhythm, and daytime energy.' },
  { title: 'Strength & Movement', description: 'Build aerobic capacity and functional strength.' },
  { title: 'Cognitive Resilience', description: 'Protect focus, mood, and long term brain function.' },
]

export default function LifePersona() {
  const nav = useNavigate()
  const { persona, focus, setPersona, setFocus } = useLife()
  const [images, setImages] = useState<Record<string, string>>({})
  const canLaunch = !!persona && !!focus

  const onUpload = (name: string, file: File | null) => {
    if (!file) return
    const url = URL.createObjectURL(file)
    setImages(prev => ({ ...prev, [name]: url }))
  }

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <div className="font-display font-bold text-xl mb-4">Select a Persona</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {personas.map(p => {
            const active = persona?.name === p.name
            // Use uploaded image if available, otherwise fall back to default image
            const img = images[p.name] || defaultPersonaImages[p.name]
            const inputId = `upload-${p.name.replace(/\s+/g,'-')}`
            return (
              <div key={p.name} className={`card p-4 transition border-2 ${active ? 'border-accent' : 'border-transparent'}`}>
                <div className="aspect-[3/4] rounded-xl overflow-hidden bg-slate-100 dark:bg-white/10 border border-slate-200 dark:border-white/10 mb-3 flex items-center justify-center">
                  {img ? (
                    <img 
                      src={img} 
                      alt={p.name} 
                      className="w-full h-full object-cover"
                      loading="lazy"
                      decoding="async"
                    />
                  ) : (
                    <span className="text-xs text-slate-500">Upload photo</span>
                  )}
                </div>
                <div className="font-semibold">{p.name} · {p.age}</div>
                <div className="text-sm text-slate-600 dark:text-slate-300 mt-1">{p.summary}</div>
                <div className="mt-3 flex gap-2">
                  <button onClick={() => setPersona(p)} className={`btn-ghost border text-xs ${active ? 'border-accent' : 'border-slate-200 dark:border-white/10'}`}>Select</button>
                  <label htmlFor={inputId} className="btn-ghost border border-slate-200 dark:border-white/10 text-xs cursor-pointer">Upload</label>
                  <input id={inputId} type="file" accept="image/*" className="hidden" onChange={(e) => onUpload(p.name, e.target.files?.[0] || null)} />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="card p-6">
        <div className="font-display font-bold text-xl mb-4">Choose a Longevity Focus</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {focusAreas.map(f => {
            const active = focus?.title === f.title
            return (
              <button key={f.title} onClick={() => setFocus(f)} className={`text-left card p-4 transition border-2 ${active ? 'border-accent' : 'border-transparent'}`}>
                <div className="font-semibold">{f.title}</div>
                <div className="text-sm text-slate-600 dark:text-slate-300 mt-1">{f.description}</div>
              </button>
            )
          })}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <button className="btn-ghost border border-slate-200 dark:border-white/10" onClick={() => nav('/life')}>Back</button>
        <button className="btn disabled:opacity-50" disabled={!canLaunch} onClick={() => nav('/life/explain')}>Launch Simulation</button>
      </div>
    </div>
  )
}