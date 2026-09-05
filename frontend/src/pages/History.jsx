import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { History as HistoryIcon, ArrowLeft, Search, ShieldCheck, ExternalLink } from 'lucide-react';
import { getApiErrorMessage } from '../services/api';
import { scannerService } from '../services/scannerService';
import '../styles/scanner.css';

const History = () => {
  const navigate = useNavigate();
  const [inspections, setInspections] = useState([]);
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    scannerService.listInspections().then(setInspections).catch((requestError) => setError(getApiErrorMessage(requestError, 'Unable to load inspection history.')));
  }, []);

  const filtered = inspections.filter((inspection) => inspection.inspection_id.toLowerCase().includes(query.toLowerCase()) || inspection.product_name.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="portal-layout">
      <Navbar />

      <main className="dashboard-main gov-container">
        <div style={{ marginBottom: '24px' }}>
          <button onClick={() => navigate('/dashboard')} className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <ArrowLeft size={16} /> Back to Dashboard
          </button>
        </div>

        <div className="scanner-panel">
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
                  placeholder="Search inspection ID or product..."
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  style={{ background: 'transparent', border: 'none', color: '#f8fafc', outline: 'none', fontSize: '13px' }}
                />
                </div>
            </div>
          </div>
            {error && <div className="scanner-alert">{error}</div>}
            {!error && !filtered.length && <div style={{ padding: '48px 24px', textAlign: 'center', color: '#94a3b8' }}><ShieldCheck size={36} color="#38bdf8" style={{ margin: '0 auto 12px' }} /><p>No inspections found.</p></div>}
            {filtered.length > 0 && <div className="table-wrapper"><table className="inspections-table"><thead><tr><th>Inspection ID</th><th>Product</th><th>Date</th><th>Images</th><th>Status</th><th /></tr></thead><tbody>{filtered.map((inspection) => <tr key={inspection.inspection_id}><td className="font-mono text-cyan">{inspection.inspection_id}</td><td className="font-medium text-white">{inspection.product_name || 'Unlabelled package'}</td><td className="text-slate">{new Date(inspection.created_at).toLocaleString()}</td><td className="text-slate">{inspection.image_count}</td><td><span className="badge-status badge-review">{inspection.status.replaceAll('_', ' ')}</span></td><td><button className="btn-secondary" onClick={() => navigate(`/scan/${inspection.inspection_id}/review`)}><ExternalLink size={14} /> Review</button></td></tr>)}</tbody></table></div>}
        </div>
      </main>
    </div>
  );
};

export default History;
