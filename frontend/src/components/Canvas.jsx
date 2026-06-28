import React, {useEffect, useState} from 'react'

function NodeCard({title, subtitle}){
  return (
    <div className="node-card">
      <div className="node-title">{title}</div>
      <div className="node-sub">{subtitle}</div>
    </div>
  )
}

export default function Canvas(){
  const [nodes, setNodes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load(){
      try{
        const res = await fetch('/api/visualization/nodes')
        if(!res.ok) throw new Error('Network error')
        const data = await res.json()
        if(!cancelled){
          setNodes(data.nodes || [])
        }
      }catch(e){
        console.error('Failed to load nodes', e)
      }finally{
        if(!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  return (
    <div className="canvas">
      <div className="project-overview">PROJECT OVERVIEW</div>
      <div className="nodes">
        {loading && <div>Loading nodes...</div>}
        {!loading && nodes.length === 0 && <div>No nodes found.</div>}
        {nodes.map((n, i) => (
          <NodeCard key={n.id || i} title={n.title} subtitle={n.meta} />
        ))}
      </div>
    </div>
  )
}
