import React from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'

export default function App(){
  return (
    <div className="app-root">
      <header className="topbar">
        <div className="brand">microservices-demo</div>
        <div className="controls">
          <button className="btn ghost">Overview</button>
          <button className="btn ghost active">Learn</button>
          <button className="btn ghost">Deep Dive</button>
        </div>
        <div className="right-actions">
          <button className="btn">Filter</button>
          <button className="btn primary">Export</button>
        </div>
      </header>

      <main className="main-area">
        <Dashboard />
        <Sidebar />
      </main>
    </div>
  )
}
