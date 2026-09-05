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
  const [nextPage, setNextPage] = useState(null);
  const [previousPage, setPreviousPage] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setLoading(true);
      scannerService.listInspections({ search: query, page: 1 })
        .then((data) => {
          setInspections(data.results || []);
          setNextPage(data.next);
          setPreviousPage(data.previous);
          setError('');
        })
        .catch((requestError) => setError(getApiErrorMessage(requestError, 'Unable to load inspection history.')))
        .finally(() => setLoading(false));
    }, 250);
    return () => window.clearTimeout(timer);
  }, [query]);

  const changePage = async (url) => {
    if (!url) return;
    const requestUrl = new URL(url, window.location.origin);
    setLoading(true);
    try {
      const data = await scannerService.listInspections({ page: requestUrl.searchParams.get('page') || 1, search: query });
      setInspections(data.results || []);
      setNextPage(data.next);
      setPreviousPage(data.previous);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Unable to load inspection history.'));
    } finally {
      setLoading(false);
    }
  };

  const filtered = inspections;

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
                <h1 style={{ fontSize: '22px', fontWeight: '700', color: '#1f2933', margin: 0 }}>
                  Inspection Audit Trail & History
                </h1>
              </div>
              <p style={{ color: '#5b6573', fontSize: '14px', marginTop: '4px', margin: 0 }}>
                Comprehensive log of all commodity verifications, audit records, and violation notices.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                backgroundColor: '#ffffff',
                padding: '8px 16px',
                borderRadius: '6px',
                border: '1px solid #d9dee5'
              }}>
                <Search size={16} color="#6b7280" />
                <input
                  type="text"
                  placeholder="Search inspection ID or product..."
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  style={{ background: 'transparent', border: 'none', color: '#1f2933', outline: 'none', fontSize: '13px' }}
                />
                </div>
            </div>
          </div>
            {error && <div className="scanner-alert" role="alert">{error}</div>}
            {loading && <div className="scanner-alert" role="status">Loading inspection history...</div>}
            {!loading && !error && !filtered.length && <div style={{ padding: '48px 24px', textAlign: 'center', color: '#5b6573' }}><ShieldCheck size={36} color="#356a9a" style={{ margin: '0 auto 12px' }} /><p>No inspections match your filters.</p></div>}
            {filtered.length > 0 && <div className="table-wrapper"><table className="inspections-table"><thead><tr><th>Inspection ID</th><th>Product</th><th>Date</th><th>Images</th><th>Status</th><th /></tr></thead><tbody>{filtered.map((inspection) => <tr key={inspection.inspection_id}><td className="font-mono text-cyan">{inspection.inspection_id}</td><td className="font-medium text-white">{inspection.product_name || 'Unlabelled package'}</td><td className="text-slate">{new Date(inspection.created_at).toLocaleString()}</td><td className="text-slate">{inspection.image_count}</td><td><span className="badge-status badge-review">{inspection.status.replaceAll('_', ' ')}</span></td><td><button className="btn-secondary" onClick={() => navigate(`/inspection/${inspection.inspection_id}`)}><ExternalLink size={14} /> Review</button></td></tr>)}</tbody></table></div>}
            {(nextPage || previousPage) && <div className="scanner-actions" style={{ justifyContent: 'space-between', marginTop: 16 }}><button className="btn-secondary" disabled={!previousPage || loading} onClick={() => changePage(previousPage)}>Previous</button><span aria-live="polite">Page results</span><button className="btn-secondary" disabled={!nextPage || loading} onClick={() => changePage(nextPage)}>Next</button></div>}
        </div>
      </main>
    </div>
  );
};

export default History;
