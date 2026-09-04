import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { History as HistoryIcon, ArrowLeft, Search, Filter, ShieldCheck } from 'lucide-react';

const History = () => {
  const navigate = useNavigate();

  return (
    <div className="portal-layout">
      <Navbar />

      <main className="dashboard-main gov-container">
        <div style={{ marginBottom: '24px' }}>
          <button onClick={() => navigate('/dashboard')} className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <ArrowLeft size={16} /> Back to Dashboard
          </button>
        </div>

        <div style={{
          backgroundColor: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '12px',
          padding: '32px',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <HistoryIcon className="text-cyan" size={24} />
                <h1 style={{ fontSize: '22px', fontWeight: '700', color: '#f8fafc', margin: 0 }}>
                  Inspection Audit Trail & History
                </h1>
              </div>
              <p style={{ color: '#94a3b8', fontSize: '14px', marginTop: '4px', margin: 0 }}>
                Comprehensive log of all commodity verifications, audit records, and violation notices.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                backgroundColor: '#0f172a',
                padding: '8px 16px',
                borderRadius: '6px',
                border: '1px solid #334155'
              }}>
                <Search size={16} color="#64748b" />
                <input
                  type="text"
                  placeholder="Filter by Session ID or Brand..."
                  style={{ background: 'transparent', border: 'none', color: '#f8fafc', outline: 'none', fontSize: '13px' }}
                  disabled
                />
              </div>
              <button className="btn-secondary" disabled style={{ opacity: 0.6 }}>
                <Filter size={14} /> Filter
              </button>
            </div>
          </div>

          <div style={{
            padding: '48px 24px',
            textAlign: 'center',
            backgroundColor: '#0f172a',
            borderRadius: '8px',
            border: '1px dashed #334155'
          }}>
            <ShieldCheck size={36} color="#38bdf8" style={{ margin: '0 auto 12px' }} />
            <h3 style={{ color: '#f8fafc', fontSize: '16px', marginBottom: '6px' }}>Historical Audits Module Scaffolded</h3>
            <p style={{ color: '#64748b', fontSize: '14px', maxWidth: '500px', margin: '0 auto 20px' }}>
              Historical inspection records with exportable PDF audit sheets will connect to the database in subsequent prompts.
            </p>
            <button onClick={() => navigate('/dashboard')} className="btn-secondary">
              Return to Dashboard
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default History;
