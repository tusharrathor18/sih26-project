import React, { useEffect, useState } from 'react';
import { ArrowLeft, CheckCircle2, Save } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { getApiErrorMessage } from '../services/api';
import { scannerService } from '../services/scannerService';
import { complianceService } from '../services/complianceService';
import '../styles/scanner.css';

const InspectionReview = () => {
  const { inspectionId } = useParams();
  const navigate = useNavigate();
  const [inspection, setInspection] = useState(null);
  const [values, setValues] = useState({});
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    scannerService.getInspection(inspectionId).then((data) => {
      setInspection(data);
      setValues(data.extracted_data?.values || {});
    }).catch((requestError) => setError(getApiErrorMessage(requestError, 'Unable to load inspection review.')));
  }, [inspectionId]);

  const saveVerification = async () => {
    setSaving(true);
    setError('');
    try {
      const updated = await scannerService.verifyInspection(inspectionId, values);
      setInspection(updated);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Unable to save verification.'));
    } finally {
      setSaving(false);
    }
  };

  const runComplianceCheck = async () => {
    setEvaluating(true);
    setError('');
    try {
      const data = await complianceService.evaluate(inspectionId);
      setEvaluation(data.evaluation);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Unable to evaluate this inspection.'));
    } finally {
      setEvaluating(false);
    }
  };

  if (!inspection) return <div className="portal-layout"><Navbar /><main className="dashboard-main gov-container"><div className="scanner-panel">{error || 'Loading inspection review...'}</div></main></div>;
  const fields = Object.keys(values);

  return <div className="portal-layout"><Navbar /><main className="dashboard-main gov-container"><div className="scanner-shell"><button onClick={() => navigate('/history')} className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 24 }}><ArrowLeft size={16} /> Back to history</button><div className="scanner-header"><div><div className="scanner-kicker">{inspection.inspection_id}</div><h1 className="scanner-title">Officer Review</h1><p className="scanner-copy">Review the OCR draft, correct uncertain values, and verify the information before it reaches the compliance engine.</p></div><div className="scanner-meta"><span>{inspection.status}</span><span>{inspection.images?.length || 0} images</span></div></div>{error && <div className="scanner-alert">{error}</div>}<div style={{ display: 'grid', gridTemplateColumns: 'minmax(260px, .9fr) minmax(320px, 1.1fr)', gap: 20 }}><section className="scanner-panel"><h2 style={{ color: '#f8fafc', fontSize: 18, marginTop: 0 }}>Evidence images</h2>{inspection.images?.map((image) => <figure key={image.id} style={{ margin: '0 0 16px' }}><img src={image.image_url} alt={image.original_filename} style={{ width: '100%', borderRadius: 7, display: 'block' }} /><figcaption style={{ color: '#94a3b8', fontSize: 12, marginTop: 7 }}>{image.image_type} {image.quality_warning && `• ${image.quality_warning}`}</figcaption>{image.ocr_result?.raw_text && <pre style={{ color: '#cbd5e1', whiteSpace: 'pre-wrap', fontSize: 12, lineHeight: 1.5 }}>{image.ocr_result.raw_text}</pre>}</figure>)}</section><section className="scanner-panel"><h2 style={{ color: '#f8fafc', fontSize: 18, marginTop: 0 }}>Extracted information</h2><p style={{ color: '#94a3b8', fontSize: 13 }}>Values are assistive OCR output. Empty fields mean information was not detected.</p>{fields.map((field) => <div className="scanner-field" key={field}><label htmlFor={`field-${field}`}>{field.replaceAll('_', ' ')}</label><input id={`field-${field}`} value={values[field] || ''} onChange={(event) => setValues((current) => ({ ...current, [field]: event.target.value }))} /></div>)}<div className="scanner-actions" style={{ justifyContent: 'flex-start' }}><button type="button" className="scanner-button primary" onClick={saveVerification} disabled={saving}><Save size={16} /> {saving ? 'Saving...' : 'Verify information'}</button><button type="button" className="scanner-button" onClick={runComplianceCheck} disabled={evaluating || inspection.status !== 'READY_FOR_COMPLIANCE'}>{evaluating ? 'Evaluating...' : 'Run Compliance Check'}</button></div>{inspection.status === 'READY_FOR_COMPLIANCE' && <div className="scanner-success"><CheckCircle2 size={16} /> Verified and ready for the compliance engine.</div>}</section></div>{evaluation && <section className="scanner-panel" style={{ marginTop: 20 }}><h2 style={{ color: '#1f2933', marginTop: 0 }}>Automated preliminary compliance assessment</h2><p className="scanner-copy">Results should be verified by the authorized Legal Metrology Officer.</p><div className="scanner-meta" style={{ margin: '14px 0' }}><strong>Overall status: {evaluation.overall_status}</strong><span>Pass {evaluation.passed} · Fail {evaluation.failed} · Manual review {evaluation.manual_review} · Not applicable {evaluation.not_applicable}</span></div>{evaluation.results.map((result) => <article key={result.id} className="scanner-result"><div><strong>{result.rule_reference.source_reference || `Rule ${result.rule_reference.rule_number}`}</strong><span className={`result-status result-${result.status.toLowerCase()}`}>{result.status.replaceAll('_', ' ')}</span></div><h3>{result.rule_reference.title}</h3><p>{result.explanation}</p>{result.detected_value && <p><strong>Detected:</strong> {result.detected_value}</p>}{result.recommendation && <p><strong>Recommendation:</strong> {result.recommendation}</p>}<small>Source PDF page {result.rule_reference.source_page || 'not recorded'}</small></article>)}</section>}</div></main></div>;
};

export default InspectionReview;
