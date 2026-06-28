import React, {useMemo, useCallback, useState} from 'react'
import ReactFlow, {MiniMap, Controls, Background, useNodesState, useEdgesState} from 'reactflow'
import 'reactflow/dist/style.css'
import 'reactflow/dist/style.css'
import dagre from 'dagre'

function layoutNodes(nodes){
  // dagre layout
  const g = new dagre.graphlib.Graph()
  g.setGraph({rankdir: 'LR', nodesep: 50, ranksep: 100})
  g.setDefaultEdgeLabel(() => ({}))

  nodes.forEach((n) => {
    g.setNode(n.node_id, {width: 180, height: 60})
  })

  nodes.forEach((n) => {
    // no explicit edges provided here; dagre will still place nodes reasonably
    // if edges are needed, GraphView's initialEdges can be used to add edges to the layout
  })

  dagre.layout(g)

  return nodes.map((n) => {
    const pos = g.node(n.node_id)
    return { id: n.node_id, data: {label: n.label, file_path: n.file_path}, position: { x: pos.x - 90, y: pos.y - 30 } }
  })
}

export default function GraphView({graphs, onNodeSelected}){
  const first = graphs?.graphs?.[0]
  const initialNodes = useMemo(()=>{
    if(!first) return []
    return layoutNodes(first.nodes)
  },[first])
  const initialEdges = useMemo(()=>{
    if(!first) return []
    return first.edges.map((e, i)=>({id:`e${i}`, source:e.source, target:e.target, animated:true}))
  },[first])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [highlighted, setHighlighted] = useState({nodes:new Set(), edges:new Set()})

  const onNodeClick = useCallback(async (evt, node) => {
    // call impact API
    try{
      const payload = { local_path: graphs.local_path || graphs?.graphs?.[0]?.repository_local_path || graphs.local_path, node_id: node.id, graph_type: first.graph_type, direction: 'both' }
      const res = await fetch('/repositories/impact', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
      if(!res.ok) throw new Error('impact call failed')
      const data = await res.json()
      const impacted = new Set(data.impacted_nodes.map(n=>n.node_id))
      setHighlighted({nodes: impacted, edges: new Set(data.impacted_edges.map(e=>`${e.source}->${e.target}`))})
      // mark node styles
      setNodes(ns => ns.map(n => ({...n, style: impacted.has(n.id) ? {border:'2px solid #ff7f50', boxShadow:'0 6px 18px rgba(255,127,80,0.12)'} : {}})))
      setEdges(es => es.map(e => ({...e, animated: highlighted.edges.has(`${e.source}->${e.target}`)})))
      if(onNodeSelected) onNodeSelected({node, impact: data})
    }catch(err){
      console.error('impact error', err)
    }
  }, [first, graphs, highlighted.edges, setEdges, setNodes])

  if(!first) return <div>No graph data</div>

  return (
    <div style={{height:'600px', borderRadius:8, overflow:'hidden'}}>
      <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} fitView onNodeClick={onNodeClick}>
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  )
}
