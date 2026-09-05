import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import StatCard from '../components/StatCard';
import {
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  PlusCircle,
  ArrowRight,
  ShieldCheck,
  Building2,
  MapPin,
  Clock
} from 'lucide-react';
import '../styles/dashboard.css';
import { scannerService } from '../services/scannerService';

const Dashboard = () => {
  const { officer } = useAuth();
  const navigate = useNavigate();
  const [inspections, setInspections] = useState([]);

  useEffect(() => {
    scannerService.listInspections().then(setInspections).catch(() => setInspections([]));
  }, []);

  const stats = [
    {
      title: 'Total Inspections',
      value: String(inspections.length),
      subtitle: 'Recorded under your account',
      icon: FileText,
      badgeColor: '#38bdf8',
      iconBg: 'rgba(56, 189, 248, 0.12)',
    },
    {
      title: 'Ready for Compliance',
      value: String(inspections.filter((item) => item.status === 'READY_FOR_COMPLIANCE').length),
      subtitle: 'Verified extraction records',
      icon: CheckCircle2,
      badgeColor: '#10b981',
      iconBg: 'rgba(16, 185, 129, 0.12)',
    },
    {
      title: 'Awaiting Verification',
      value: String(inspections.filter((item) => item.status === 'AWAITING_VERIFICATION').length),
      subtitle: 'Officer review required',
      icon: XCircle,
      badgeColor: '#f43f5e',
      iconBg: 'rgba(244, 63, 94, 0.12)',
    },
    {
      title: 'Needs Review',
      value: String(inspections.filter((item) => ['PROCESSING', 'FAILED'].includes(item.status)).length),
      subtitle: 'Processing or needs retry',
      icon: AlertTriangle,
      badgeColor: '#f59e0b',
      iconBg: 'rgba(245, 158, 11, 0.12)',
    },
  ];

  const recentInspections = inspections.slice(0, 5);

  const getStatusBadge = (status) => {
    switch (status) {
      default:
        return <span className="badge-status badge-review"><AlertTriangle size={13} /> {status.replaceAll('_', ' ')}</span>;
    }
  };

  return (
    <div className="portal-layout">
      <Navbar />

      <main className="dashboard-main gov-container">
        {/* Officer Welcome Banner */}
        <section className="welcome-banner">
          <div className="welcome-info">
            <div className="welcome-tag">
              <ShieldCheck size={16} />
              <span>OFFICIAL ENFORCEMENT DESK</span>
            </div>
            <h1 className="welcome-heading">
              Welcome, {officer?.name || 'Inspector'}
            </h1>
            <div className="officer-detail-bar">
              <span className="officer-meta-item">
                <strong>ID:</strong> {officer?.officer_id || 'N/A'}
              </span>
              <span className="meta-sep">&bull;</span>
              <span className="officer-meta-item">
                <Building2 size={14} className="meta-icon" />
                {officer?.designation || 'Inspector of Legal Metrology'}
              </span>
              <span className="meta-sep">&bull;</span>
              <span className="officer-meta-item">
                <MapPin size={14} className="meta-icon" />
                {officer?.jurisdiction || 'All Zones'}
              </span>
            </div>
          </div>

          <div className="welcome-action">
            <button
              onClick={() => navigate('/scan')}
              className="btn-primary-action"
            >
              <PlusCircle size={20} />
              <span>Start New Inspection</span>
            </button>
          </div>
        </section>

        {/* Statistics Cards Grid */}
        <section className="stats-grid">
          {stats.map((stat, idx) => (
            <StatCard key={idx} {...stat} />
          ))}
        </section>

        {/* Action & Guidelines Banner */}
        <section className="rules-overview-card">
          <div className="rules-card-content">
            <h3>Legal Metrology (Packaged Commodities) Rules, 2011</h3>
            <p>
              Rule 6 mandates 7 essential packaging declarations: Name & Address of Manufacturer/Packer/Importer, Common Generic Name, Net Quantity, Month & Year of Manufacture/Packing/Import, Retail Sale Price (MRP incl. of all taxes), Consumer Care details, and Unit Sale Price.
            </p>
          </div>
          <button onClick={() => navigate('/scan')} className="btn-link-action">
            Open Scanner Engine <ArrowRight size={16} />
          </button>
        </section>

        {/* Recent Inspections Table */}
        <section className="inspections-section">
          <div className="section-header">
            <div>
              <h2 className="section-title">Recent Inspections</h2>
              <p className="section-desc">Commodity inspection sessions logged under your jurisdiction</p>
            </div>
            <button onClick={() => navigate('/history')} className="btn-secondary">
              View Complete Audit Trail
            </button>
          </div>

          <div className="table-wrapper">
            <table className="inspections-table">
              <thead>
                <tr>
                  <th>Inspection ID</th>
                  <th>Product</th>
                  <th>Images</th>
                  <th>Status</th>
                  <th>Inspection Date</th>
                  <th>Next step</th>
                </tr>
              </thead>
              <tbody>
                {recentInspections.map((row) => (
                  <tr key={row.id}>
                    <td><span className="font-mono text-cyan">{row.inspection_id}</span></td>
                    <td className="font-medium text-white">{row.product_name || 'Unlabelled package'}</td>
                    <td className="text-slate">{row.image_count}</td>
                    <td>{getStatusBadge(row.status)}</td>
                    <td className="text-slate">
                      <div className="time-cell">
                        <Clock size={13} /> {new Date(row.created_at).toLocaleString()}
                      </div>
                    </td>
                    <td><button className="btn-secondary" onClick={() => navigate(`/scan/${row.inspection_id}/review`)}>Review extraction</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
