import React, {useState} from 'react'

export default function ExplainPanel({localPath}){
  const [explain, setExplain] = useState(null)
  const [loading, setLoading] = useState(false)

  async function load(){
    setLoading(true)
    try{
      const res = await fetch('/repositories/explain', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({local_path: localPath})})
      if(!res.ok) throw new Error('explain failed')
      const data = await res.json()
      setExplain(data)
    }catch(e){
      console.error(e)
      setExplain({error: String(e)})
    }finally{setLoading(false)}
  }

  return (
    <div className="explain-panel">
      <div style={{display:'flex',gap:8,alignItems:'center'}}>
        <h4>Explain</h4>
        <button className="btn" onClick={load}>Refresh</button>
      </div>
      {loading && <div>Loading...</div>}
      {explain && explain.error && <div style={{color:'red'}}>Error: {explain.error}</div>}
      {explain && !explain.error && (
        <div>
          <div><strong>Repo:</strong> {explain.local_path}</div>
          <div><strong>Remote:</strong> {explain.remote_url || 'N/A'}</div>
          <div><strong>Graph:</strong> {explain.graph_type}</div>
          <div><strong>Nodes:</strong> {explain.total_nodes} <strong>Edges:</strong> {explain.total_edges}</div>
          <h5>Top modules</h5>
          <ul>
            {explain.top_modules.map((m,i)=>(<li key={i}>{m.label} {m.file_path ? ` — ${m.file_path}` : ''}</li>))}
          </ul>
          <h5>Sample edges</h5>
          <ul>
            {explain.sample_edges.map((e,i)=>(<li key={i}>{e.source} —[{e.relation}]-> {e.target}</li>))}
          </ul>
        </div>
      )}
    </div>
  )
}
