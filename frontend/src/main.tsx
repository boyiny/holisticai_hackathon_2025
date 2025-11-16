import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'
import AppLayout from './layouts/AppLayout'
import Overview from './pages/Overview'
import Agents from './pages/Agents'
import Workflow from './pages/Workflow'
import Tools from './pages/Tools'
import Analysis from './pages/Analysis'
import Tests from './pages/Tests'
import RunDetail from './pages/RunDetail'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}> 
          <Route path="/" element={<Navigate to="/overview" replace />} />
          <Route path="/overview" element={<Overview />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/workflow" element={<Workflow />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/tests" element={<Tests />} />
          <Route path="/runs/:id" element={<RunDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)

