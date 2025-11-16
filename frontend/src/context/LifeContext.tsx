import React, { createContext, useContext, useState, ReactNode } from 'react'

export type Persona = {
  name: string
  age: number
  summary: string
}

export type FocusArea = {
  title: string
  description: string
}

type LifeState = {
  persona: Persona | null
  focus: FocusArea | null
  setPersona: (p: Persona | null) => void
  setFocus: (f: FocusArea | null) => void
}

const Ctx = createContext<LifeState | null>(null)

export function LifeProvider({ children }: { children: ReactNode }) {
  const [persona, setPersona] = useState<Persona | null>(null)
  const [focus, setFocus] = useState<FocusArea | null>(null)
  return <Ctx.Provider value={{ persona, focus, setPersona, setFocus }}>{children}</Ctx.Provider>
}

export function useLife() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useLife must be used within LifeProvider')
  return ctx
}

