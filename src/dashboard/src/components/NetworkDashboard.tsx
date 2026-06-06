import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell
} from 'recharts';
import { ShieldAlert, Network, ArrowRightCircle } from 'lucide-react';

interface EpsteinOverlap {
  filing_year: number;
  first_name: string;
  last_name: string;
  epstein_associate_name: string;
  associate_role: string;
  filingtype: string;
}

interface FinanceStat {
  filing_year: number;
  disclosure_count: number;
}

export function NetworkDashboard() {
  const [overlapData, setOverlapData] = useState<EpsteinOverlap[]>([]);
  const [financeStats, setFinanceStats] = useState<FinanceStat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const epsteinRes = await axios.get('http://localhost:8000/api/network/epstein');
        const financeRes = await axios.get('http://localhost:8000/api/finance/stats');
        setOverlapData(epsteinRes.data.data);
        setFinanceStats(financeRes.data.data.reverse()); // Chronological order
      } catch (error) {
        console.error('Error fetching dashboard data', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex-center" style={{ height: '50vh' }}>
        <div className="gradient-text">Loading Data Pipeline...</div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="dashboard-header" style={{ marginBottom: '40px' }}>
        <h1 className="gradient-text" style={{ fontSize: '3rem', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <Network size={40} color="var(--accent-color)" />
          Corruption Mapping
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', marginTop: '8px' }}>
          Real-time ingestion of Financial Disclosures and Network Correspondences.
        </p>
      </div>

      <div className="grid-2">
        {/* Financial Disclosures Chart */}
        <motion.div className="glass-panel" whileHover={{ scale: 1.01 }}>
          <h3 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ActivityIcon /> Total Financial Disclosures
          </h3>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={financeStats}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="filing_year" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}
                  itemStyle={{ color: 'var(--text-primary)' }}
                />
                <Bar dataKey="disclosure_count" fill="var(--accent-color)" radius={[4, 4, 0, 0]}>
                  {
                    financeStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index % 2 === 0 ? 'var(--accent-color)' : '#ff6b6b'} />
                    ))
                  }
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Epstein Correlation Alert Box */}
        <motion.div className="glass-panel" style={{ borderLeft: '4px solid var(--accent-color)' }}>
          <h3 className="danger-text" style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={24} /> Epstein Flight Log Overlaps
          </h3>
          <div style={{ maxHeight: '300px', overflowY: 'auto', paddingRight: '8px' }}>
            {overlapData.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>No direct overlaps found in the current dataset.</p>
            ) : (
              overlapData.map((item, index) => (
                <div key={index} className="glass-card" style={{ marginBottom: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong style={{ color: '#fff' }}>{item.first_name} {item.last_name}</strong>
                      <span style={{ margin: '0 8px', color: 'var(--text-secondary)' }}>
                        <ArrowRightCircle size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
                      </span>
                      <strong className="danger-text">{item.epstein_associate_name}</strong>
                    </div>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {item.filing_year} ({item.filingtype})
                    </span>
                  </div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    Role: {item.associate_role}
                  </div>
                </div>
              ))
            )}
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}

function ActivityIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  );
}
