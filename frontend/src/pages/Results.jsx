import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { FileCheck2, ArrowLeft } from 'lucide-react';
import { complianceService } from '../services/complianceService';
import { getApiErrorMessage } from '../services/api';
import '../styles/scanner.css';

const Results = () => {
  const navigate = useNavigate();
  const { inspectionId } = useParams();
  const [evaluation, setEvaluation] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!inspectionId) return;
    complianceService.get(inspectionId).then(setEvaluation).catch((requestError) => setError(getApiErrorMessage(requestError, 'Unable to load compliance results.')));
  }, [inspectionId]);

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
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <FileCheck2 className="text-cyan" size={24} />
            <h1 style={{ fontSize: '22px', fontWeight: '700', color: '#1f2933', margin: 0 }}>
              Compliance Evaluation Reports
            </h1>
          </div>

          <p style={{ color: '#5b6573', fontSize: '14px', marginBottom: '32px' }}>
            Automated preliminary compliance assessment. Results must be verified by the authorized officer.
          </p>
          {error && <div className="scanner-alert">{error}</div>}
          {!inspectionId && <div className="scanner-alert">Open an inspection from History to view its results.</div>}
          {evaluation && <><div className="scanner-success"><strong>Overall status: {evaluation.overall_status}</strong><br />Passed {evaluation.passed} · Failed {evaluation.failed} · Manual review {evaluation.manual_review} · Not applicable {evaluation.not_applicable}</div>{evaluation.results.map((result) => <article key={result.id} className="scanner-result"><div><strong>{result.rule_reference.source_reference || `Rule ${result.rule_reference.rule_number}`}</strong><span className={`result-status result-${result.status.toLowerCase()}`}>{result.status.replaceAll('_', ' ')}</span></div><h3>{result.rule_reference.title}</h3><p>{result.explanation}</p>{result.detected_value && <p><strong>Detected:</strong> {result.detected_value}</p>}<p><strong>Requirement:</strong> {result.expected_requirement}</p>{result.recommendation && <p><strong>Recommendation:</strong> {result.recommendation}</p>}<small>Source PDF page {result.rule_reference.source_page || 'not recorded'}</small></article>)}</>}
        </div>
      </main>
    </div>
  );
};

export default Results;
