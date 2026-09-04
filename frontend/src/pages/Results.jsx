import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { FileCheck2, ArrowLeft, ShieldAlert } from 'lucide-react';

const Results = () => {
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <FileCheck2 className="text-cyan" size={24} />
            <h1 style={{ fontSize: '22px', fontWeight: '700', color: '#f8fafc', margin: 0 }}>
              Compliance Evaluation Reports
            </h1>
          </div>

          <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '32px' }}>
            Detailed rule-by-rule evaluation logs based on the Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>

          <div style={{
            padding: '48px 24px',
            textAlign: 'center',
            backgroundColor: '#0f172a',
            borderRadius: '8px',
            border: '1px dashed #334155'
          }}>
            <ShieldAlert size={36} color="#fbbf24" style={{ margin: '0 auto 12px' }} />
            <h3 style={{ color: '#f8fafc', fontSize: '16px', marginBottom: '6px' }}>Rule Engine Reporting Scaffolded</h3>
            <p style={{ color: '#64748b', fontSize: '14px', maxWidth: '500px', margin: '0 auto 20px' }}>
              The Legal Metrology rule engine outputs (PASS, FAIL, WARNING, and statutory citations) will be rendered here upon completing inspection scans.
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

export default Results;
