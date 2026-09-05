import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { ArrowLeft, Camera, CheckCircle2, ImagePlus, Play, Trash2, Upload } from 'lucide-react';
import { getApiErrorMessage } from '../services/api';
import { scannerService } from '../services/scannerService';
import '../styles/scanner.css';

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const IMAGE_TYPES = ['FRONT', 'BACK', 'SIDE', 'TOP', 'BOTTOM', 'OTHER'];

const Scan = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [productName, setProductName] = useState('');
  const [selectedImages, setSelectedImages] = useState([]);
  const [error, setError] = useState('');
  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => () => streamRef.current?.getTracks().forEach((track) => track.stop()), []);

  const addFiles = (files) => {
    const next = [];
    for (const file of files) {
      if (!ACCEPTED_TYPES.includes(file.type)) {
        setError('Unsupported image format. Use JPEG, PNG, or WEBP.');
        continue;
      }
      if (file.size > MAX_FILE_SIZE) {
        setError('Image is too large. Maximum allowed size is 10 MB.');
        continue;
      }
      next.push({ file, preview: URL.createObjectURL(file), imageType: 'OTHER' });
    }
    setSelectedImages((current) => [...current, ...next]);
  };

  const removeImage = (index) => {
    setSelectedImages((current) => {
      URL.revokeObjectURL(current[index].preview);
      return current.filter((_, itemIndex) => itemIndex !== index);
    });
  };

  const openCamera = async () => {
    setCameraError('');
    try {
      streamRef.current = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      setCameraOpen(true);
      requestAnimationFrame(() => { if (videoRef.current) videoRef.current.srcObject = streamRef.current; });
    } catch {
      setCameraError('Camera access is unavailable. You can continue by choosing image files.');
    }
  };

  const captureImage = () => {
    const video = videoRef.current;
    if (!video) return;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      if (blob) addFiles([new File([blob], `camera-${Date.now()}.jpg`, { type: 'image/jpeg' })]);
    }, 'image/jpeg', 0.92);
  };

  const closeCamera = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setCameraOpen(false);
  };

  const startInspection = async () => {
    if (!selectedImages.length) {
      setError('Choose at least one package image before starting.');
      return;
    }
    setError('');
    setIsSubmitting(true);
    try {
      const inspection = await scannerService.createInspection(productName);
      for (const [index, item] of selectedImages.entries()) {
        await scannerService.uploadImage(inspection.inspection_id, item.file, item.imageType, index);
      }
      await scannerService.processInspection(inspection.inspection_id);
      navigate(`/scan/${inspection.inspection_id}/review`);
    } catch (requestError) {
      setError(requestError.response?.data?.message || getApiErrorMessage(requestError, 'Inspection processing failed. Please try again.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="portal-layout">
      <Navbar />

      <main className="dashboard-main gov-container">
        <div className="scanner-shell">
        <div style={{ marginBottom: '24px' }}>
          <button onClick={() => navigate('/dashboard')} className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <ArrowLeft size={16} /> Back to Dashboard
          </button>
        </div>

        <div className="scanner-header">
          <div><div className="scanner-kicker">INSPECTION WORKSPACE</div><h1 className="scanner-title">New Product Inspection</h1><p className="scanner-copy">Capture the package from each relevant side. The original evidence is preserved while OCR prepares a draft for officer verification.</p></div>
          <div className="scanner-meta"><span>{selectedImages.length} image{selectedImages.length === 1 ? '' : 's'}</span><span>10 MB max each</span></div>
        </div>
        <section className="scanner-panel">
          <div className="scanner-field"><label htmlFor="product-name">Product label (optional)</label><input id="product-name" value={productName} onChange={(event) => setProductName(event.target.value)} placeholder="e.g. packaged tea, flour, oil" /></div>
          {error && <div className="scanner-alert" role="alert">{error}</div>}
          {cameraError && <div className="scanner-alert" role="alert">{cameraError}</div>}
          <div className="scanner-dropzone"><ImagePlus size={34} color="#38bdf8" /><h2 style={{ color: '#f8fafc', margin: '12px 0 6px' }}>Add package images</h2><p style={{ color: '#94a3b8', margin: 0 }}>Front, back, side, top, and bottom views are supported.</p><div className="scanner-actions"><label className="scanner-button primary"><Upload size={17} /> Choose images<input ref={fileInputRef} className="scanner-file-input" type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={(event) => addFiles(Array.from(event.target.files || []))} /></label><button type="button" className="scanner-button" onClick={openCamera}><Camera size={17} /> Capture with camera</button></div></div>
          {cameraOpen && <div className="scanner-camera"><video ref={videoRef} autoPlay playsInline /><div className="scanner-actions"><button type="button" className="scanner-button primary" onClick={captureImage}><Camera size={17} /> Capture image</button><button type="button" className="scanner-button" onClick={closeCamera}>Close camera</button></div></div>}
          {selectedImages.length > 0 && <div className="scanner-grid">{selectedImages.map((item, index) => <div className="scanner-preview" key={item.preview}><img src={item.preview} alt={`Selected package view ${index + 1}`} /><div className="scanner-preview-body"><div className="scanner-meta"><span>Image {index + 1}</span><button type="button" className="scanner-button danger" onClick={() => removeImage(index)} title="Remove image"><Trash2 size={14} /></button></div><select value={item.imageType} onChange={(event) => setSelectedImages((current) => current.map((entry, itemIndex) => itemIndex === index ? { ...entry, imageType: event.target.value } : entry))}>{IMAGE_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}</select></div></div>)}</div>}
          <div className="scanner-actions" style={{ justifyContent: 'flex-end', marginTop: 26 }}><button type="button" className="scanner-button primary" disabled={isSubmitting || !selectedImages.length} onClick={startInspection}>{isSubmitting ? 'Uploading and processing...' : <><Play size={17} /> Start inspection</>}</button></div>
        </section>
        </div>
      </main>
    </div>
  );
};

export default Scan;
