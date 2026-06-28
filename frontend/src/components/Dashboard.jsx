import React, {useState} from 'react'
import RepoForm from './RepoForm'
import GraphView from './GraphView'
import ExplainPanel from './ExplainPanel'
import FilePreview from './FilePreview'

export default function Dashboard(){
  const [graphs, setGraphs] = useState(null)
  const [localPath, setLocalPath] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)

  function handleGraphs(result){
    setGraphs(result)
    setLocalPath(result.local_path)
  }

  async function handleNodeSelected({node, impact}){
    // fetch narrative explanation
    try{
      const payload = { local_path: localPath, node_id: node.id, graph_type: graphs?.graphs?.[0]?.graph_type }
      const res = await fetch('/repositories/impact/explain', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
      if(!res.ok) throw new Error('impact explain failed')
      const data = await res.json()
      // show as alert for now or could render in panel
      window.alert(data.narrative)
      // if node has file_path, show preview in side panel
      const fp = node?.data?.file_path
      if(fp) setSelectedFile(fp)
    }catch(e){
      console.error(e)
      window.alert('Impact explanation failed: '+String(e))
    }
  }

  return (
    <div className="dashboard" style={{display:'flex',gap:16}}>
      <div style={{flex:1}}>
        <RepoForm onGraphs={handleGraphs} />
        <div style={{marginTop:12}}>
          {graphs ? <GraphView graphs={graphs} onNodeSelected={handleNodeSelected} /> : <div>Load a repository to view graphs.</div>}
        </div>
      </div>
      <aside style={{width:360}}>
        <ExplainPanel localPath={localPath} />
            <div style={{height:12}} />
            <div className="panel">
              <h4>File Preview</h4>
              <div>
                <FilePreview localPath={localPath} filePath={selectedFile} />
              </div>
            </div>
        <div style={{height:12}} />
        <div className="panel">
          <h4>Onboarding</h4>
          <a href="/ONBOARDING.md" target="_blank">Open Onboarding</a>
        </div>
      </aside>
    </div>
  )
}
