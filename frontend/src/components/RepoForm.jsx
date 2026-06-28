import React, {useState} from 'react'

export default function RepoForm({onGraphs}){
  const [sourceUrl, setSourceUrl] = useState('')
  const [destination, setDestination] = useState('')
  const [status, setStatus] = useState('')

  function repoNameFromUrl(url){
    try{
      const parts = url.split('/')
      const last = parts.pop() || parts.pop()
      return last?.replace('.git','') || 'repo'
    }catch{ return 'repo' }
  }

  async function handleClone(e){
    e.preventDefault()
    setStatus('Starting clone job...')
    const dest = destination || `./cloned_repos/${repoNameFromUrl(sourceUrl)}`
    try{
      const res = await fetch('/jobs/clone',{
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({source_url: sourceUrl, destination_path: dest})
      })
      if(!res.ok){
        const err = await res.text()
        setStatus(`Job start failed: ${err}`)
        return
      }
      const {job_id} = await res.json()
      setStatus(`Job started: ${job_id}`)
      // attempt websocket for live updates
      const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const wsUrl = `${proto}://${window.location.host}/jobs/ws/${job_id}`
      let ws
      try{
        ws = new WebSocket(wsUrl)
      }catch(e){
        ws = null
      }

      if(ws){
        ws.onopen = ()=> setStatus(s => s + ' (connected)')
        ws.onmessage = (evt)=>{
          try{
            const job = JSON.parse(evt.data)
            setStatus(`Status: ${job.status} - ${job.progress?.join(', ') || ''}`)
            if(job.status === 'completed'){
              setStatus('Done')
              ws.close()
              if(onGraphs) onGraphs(job.result)
            }
            if(job.status === 'failed'){
              setStatus('Job failed: '+(job.error||'unknown'))
              ws.close()
            }
          }catch(err){
            console.error('ws parse', err)
          }
        }
        ws.onerror = (e)=>{
          console.warn('WebSocket error, falling back to polling', e)
          // fallback to polling below
          ws.close()
          pollFallback(job_id)
        }
        // if websocket closes before completion, fallback to polling
        ws.onclose = ()=>{
          // check final status via HTTP
          pollFallback(job_id)
        }
      }else{
        // fallback to polling if WS couldn't be created
        pollFallback(job_id)
      }
    }catch(err){
      console.error(err)
      setStatus('Error: '+String(err))
    }
  }

  async function pollFallback(job_id){
    let finished = false
    while(!finished){
      await new Promise(r=>setTimeout(r,1500))
      try{
        const s = await fetch(`/jobs/${job_id}`)
        if(!s.ok){ setStatus('Failed to fetch job status'); return }
        const js = await s.json()
        setStatus(`Status: ${js.status} - ${js.progress.join(', ')}`)
        if(js.status === 'completed'){
          finished = true
          const graphs = js.result
          setStatus('Done')
          if(onGraphs) onGraphs(graphs)
        }
        if(js.status === 'failed'){
          finished = true
          setStatus('Job failed: '+(js.error||'unknown'))
        }
      }catch(e){
        setStatus('Poll error: '+String(e))
        return
      }
    }
  }

  return (
    <div className="repo-form">
      <form onSubmit={handleClone}>
        <label>GitHub repo URL</label>
        <input value={sourceUrl} onChange={e=>setSourceUrl(e.target.value)} placeholder="https://github.com/owner/repo.git" />
        <label>Destination path (optional)</label>
        <input value={destination} onChange={e=>setDestination(e.target.value)} placeholder="./cloned_repos/myrepo" />
        <div style={{display:'flex',gap:8}}>
          <button className="btn primary" type="submit">Clone & Build Graphs</button>
          <button type="button" className="btn" onClick={()=>{setSourceUrl('');setDestination('');setStatus('')}}>Clear</button>
        </div>
        <div className="status">{status}</div>
      </form>
    </div>
  )
}
