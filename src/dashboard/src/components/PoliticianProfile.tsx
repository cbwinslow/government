import React from 'react';
import { ShieldAlert, FileText, Mic, Briefcase } from 'lucide-react';
import { NetworkGraph } from './NetworkGraph';

export const PoliticianProfile: React.FC = () => {
  return (
    <div className="container">
      {/* Header Section */}
      <div className="glass-panel animate-fade-in" style={{ display: 'flex', gap: '40px', alignItems: 'center', marginBottom: '40px' }}>
        <img 
          src="https://www.nebraskalegislature.gov/media/images/senators/dist31/highres/dist31.jpg" 
          alt="Kathleen Kauth" 
          style={{ width: '150px', height: '150px', borderRadius: '50%', objectFit: 'cover', border: '2px solid var(--accent-color)' }}
        />
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '8px' }}>Kathleen Kauth</h1>
          <div style={{ display: 'flex', gap: '16px', color: 'var(--text-secondary)' }}>
            <span className="flex-center" style={{ gap: '6px' }}><Briefcase size={16} /> State Senator, NE-31</span>
            <span className="issue-tag" style={{ background: 'rgba(255,59,59,0.2)', color: 'var(--accent-color)' }}>Republican</span>
          </div>
          <p style={{ marginTop: '16px', color: 'var(--text-secondary)' }}>
            Overall consistency analysis based on 145 public statements, 32 legislative votes, and $450,000 in campaign contributions.
          </p>
        </div>
        
        {/* The Honesty Score Ring */}
        <div className="score-circle-wrapper" style={{ '--score': 45 } as React.CSSProperties}>
          <div className="score-circle-inner">
            <span className="score-value danger-text">45</span>
            <span className="score-label">Score</span>
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* Left Column: Timeline of Words vs Votes */}
        <div>
          <h3 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={20} className="danger-text" /> 
            Critical Discrepancies
          </h3>
          
          <div className="timeline">
            {/* Timeline Item 1 */}
            <div className="timeline-item animate-fade-in" style={{ animationDelay: '0.1s' }}>
              <div className="timeline-content">
                <div className="timeline-header">
                  <span className="issue-tag">Corporate Taxation</span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Severity: 8/10</span>
                </div>
                
                <div className="timeline-split">
                  <div>
                    <h4><Mic size={14} style={{ display: 'inline', marginRight: '4px' }}/> The Words</h4>
                    <p style={{ fontSize: '0.9rem' }}>"I will always fight to ensure massive corporations pay their fair share and protect the middle class."</p>
                  </div>
                  <div>
                    <h4><FileText size={14} style={{ display: 'inline', marginRight: '4px' }}/> The Actions</h4>
                    <p style={{ fontSize: '0.9rem' }}>Voted YES on LB 754, drastically reducing the top corporate tax rate from 7.25% to 3.99%.</p>
                  </div>
                </div>
                
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
                  <strong>Analysis:</strong> Direct contradiction between stated campaign promises regarding corporate taxation and actual legislative voting record.
                </p>
              </div>
            </div>
            
            {/* Timeline Item 2 */}
            <div className="timeline-item animate-fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="timeline-content">
                <div className="timeline-header">
                  <span className="issue-tag">Public Education</span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Severity: 6/10</span>
                </div>
                <div className="timeline-split">
                  <div>
                    <h4><Mic size={14} style={{ display: 'inline', marginRight: '4px' }}/> The Words</h4>
                    <p style={{ fontSize: '0.9rem' }}>"Public schools are the bedrock of our communities."</p>
                  </div>
                  <div>
                    <h4><FileText size={14} style={{ display: 'inline', marginRight: '4px' }}/> The Actions</h4>
                    <p style={{ fontSize: '0.9rem' }}>Co-sponsored LB 753 (Opportunity Scholarships Act), diverting public funds to private school scholarships.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Network Graph */}
        <div>
          <h3 style={{ marginBottom: '24px' }}>Influence Network</h3>
          <NetworkGraph />
        </div>
      </div>
    </div>
  );
};
