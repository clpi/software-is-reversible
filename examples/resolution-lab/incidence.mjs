// Two incidence bits preserve a node's two possible roles on the same edge.
// A signed subtraction would confuse a dual-role node with absence.
export function incidence(graph) {
  return graph.edges.map(edge => {
    const prem=new Set(edge.premises), conc=new Set(edge.conclusions);
    return {action:edge.action,bits:graph.nodes.map(n=>
      Number(prem.has(n.digest)) + 2*Number(conc.has(n.digest)))};
  });
}
