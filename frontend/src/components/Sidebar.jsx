import React from 'react'

const steps = [
  'Project Overview',
  'gRPC Service Contracts',
  'Frontend Entry Point',
  'Frontend HTTP Handlers',
  'Product Catalog Service',
  'Cart Service',
  'Checkout Orchestrator',
  'Supporting Microservices'
]

export default function Sidebar(){
  return (
    <aside className="sidebar">
      <div className="panel">
        <h3>Project Tour</h3>
        <button className="btn wide">Start Tour</button>
        <div className="steps">
          {steps.map((s,i)=> (
            <div key={i} className="step">{i+1}. {s}</div>
          ))}
        </div>
      </div>
    </aside>
  )
}
