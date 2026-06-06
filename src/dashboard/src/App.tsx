import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Activity } from 'lucide-react';
import { NetworkDashboard } from './components/NetworkDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        {/* Global Navigation */}
        <nav className="navbar">
          <div className="container">
            <Link to="/" className="logo">
              <Activity size={24} color="var(--accent-color)" />
              Open<span>Discourse</span>
            </Link>
            <div style={{ display: 'flex', gap: '24px' }}>
              <Link to="/" style={{ color: 'var(--text-primary)', textDecoration: 'none' }}>Dashboard</Link>
              <a href="#" style={{ color: 'var(--text-primary)', textDecoration: 'none' }}>Methodology</a>
            </div>
          </div>
        </nav>

        {/* Main Content Router */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<NetworkDashboard />} />
            {/* Future routes: <Route path="/politician/:id" element={<PoliticianProfile />} /> */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
