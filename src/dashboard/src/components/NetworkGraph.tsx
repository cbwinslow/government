import React, { useRef, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

// Mock data for the network graph visualization
const graphData = {
  nodes: [
    { id: 'politician', name: 'Kathleen Kauth', val: 20, color: '#ff3b3b' },
    { id: 'donor1', name: 'NRA', val: 10, color: '#3b82f6' },
    { id: 'donor2', name: 'Koch Industries', val: 15, color: '#3b82f6' },
    { id: 'bill1', name: 'LB 574 (Co-Sponsor)', val: 5, color: '#10b981' },
    { id: 'news1', name: 'Fox News Appearance', val: 8, color: '#a855f7' }
  ],
  links: [
    { source: 'politician', target: 'donor1' },
    { source: 'politician', target: 'donor2' },
    { source: 'politician', target: 'bill1' },
    { source: 'politician', target: 'news1' }
  ]
};

export const NetworkGraph: React.FC = () => {
  const fgRef = useRef<any>();

  useEffect(() => {
    // Slight animation on load
    if (fgRef.current) {
      fgRef.current.d3Force('charge').strength(-400);
    }
  }, []);

  return (
    <div className="graph-container animate-fade-in">
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeLabel="name"
        nodeColor={(node: any) => node.color}
        nodeRelSize={6}
        linkColor={() => 'rgba(255,255,255,0.2)'}
        width={600}
        height={600}
        backgroundColor="transparent"
      />
    </div>
  );
};
