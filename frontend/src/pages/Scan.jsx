import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { Camera, Upload, ArrowLeft, Layers, ShieldCheck, Sparkles } from 'lucide-react';

const Scan = () => {
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
          padding: '40px',
          textAlign: 'center',
          maxWidth: '800px',
          margin: '0 auto'
        }}>
          <div style={{
            display: 'inline-flex',
            padding: '16px',
            backgroundColor: 'rgba(56, 189, 248, 0.1)',
            borderRadius: '50%',
            color: '#38bdf8',
            marginBottom: '20px'
          }}>
            <Camera size={44} />
          </div>

          <div style={{
            display: 'inline-block',
            padding: '4px 12px',
            backgroundColor: 'rgba(217, 119, 6, 0.15)',
            border: '1px solid rgba(217, 119, 6, 0.4)',
            color: '#fbbf24',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: '600',
            marginBottom: '16px'
          }}>
            PIPELINE READY &bull; PROMPT 2/15 TARGET
          </div>

          <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f8fafc', marginBottom: '12px' }}>
            Packaged Commodity Scanner Module
          </h1>

          <p style={{ color: '#94a3b8', fontSize: '15px', lineHeight: '1.6', maxWidth: '600px', margin: '0 auto 30px' }}>
            The scanning pipeline architecture is scaffolded. In upcoming prompts, this screen will provide live camera image capture, multi-image package label uploads, image preprocessing, and high-accuracy OCR text extraction.
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '16px',
            textAlign: 'left',
            marginBottom: '32px'
          }}>
            <div style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38bdf8', fontWeight: '600', marginBottom: '6px' }}>
                <Camera size={18} /> Camera Capture
              </div>
              <p style={{ color: '#64748b', fontSize: '13px', margin: 0 }}>Real-time camera feed to capture front, back, and nutritional panels.</p>
            </div>

            <div style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981', fontWeight: '600', marginBottom: '6px' }}>
                <Upload size={18} /> Batch Label Upload
              </div>
              <p style={{ color: '#64748b', fontSize: '13px', margin: 0 }}>High-resolution image uploads with automated enhancement.</p>
            </div>

            <div style={{ padding: '16px', backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#a855f7', fontWeight: '600', marginBottom: '6px' }}>
                <Layers size={18} /> OCR Text Engine
              </div>
              <p style={{ color: '#64748b', fontSize: '13px', margin: 0 }}>PaddleOCR integration for curved text and small-print labels.</p>
            </div>
          </div>

          <button onClick={() => navigate('/dashboard')} className="btn-primary-action" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', margin: '0 auto' }}>
            <ShieldCheck size={18} /> Return to Officer Dashboard
          </button>
        </div>
      </main>
    </div>
  );
};

export default Scan;
