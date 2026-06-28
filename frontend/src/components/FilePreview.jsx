import React, {useEffect, useState} from 'react'

export default function FilePreview({localPath, filePath}){
  const [content, setContent] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(()=>{
    if(!localPath || !filePath) return
    let cancelled = false
    async function load(){
      setLoading(true)
      try{
        const res = await fetch('/repositories/file', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({local_path: localPath, file_path: filePath})})
        if(!res.ok) throw new Error('file fetch failed')
        const data = await res.json()
        if(!cancelled) setContent(data.content)
      }catch(e){
        if(!cancelled) setContent('Error loading file: '+String(e))
      }finally{if(!cancelled) setLoading(false)}
    }
    load()
    return ()=>{ cancelled = true }
  },[localPath,filePath])

  if(!filePath) return <div>No file selected</div>
  return (
    <div style={{background:'#fff',padding:10,borderRadius:8,border:'1px solid #eef2f5',height:400,overflow:'auto'}}>
      <div style={{fontSize:12,color:'#666',marginBottom:8}}>Preview: {filePath}</div>
      {loading && <div>Loading...</div>}
      {content && <pre style={{whiteSpace:'pre-wrap'}}>{content}</pre>}
    </div>
  )
}
