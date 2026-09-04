import React from 'react';
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

const Dashboard = () => {
  const { officer } = useAuth();
  const navigate = useNavigate();

  // Placeholder inspection metrics for Prompt 1
  const stats = [
    {
      title: 'Total Inspections',
      value: '24',
      subtitle: 'Recorded across jurisdiction',
      icon: FileText,
      badgeColor: '#38bdf8',
      iconBg: 'rgba(56, 189, 248, 0.12)',
    },
    {
      title: 'Passed (Compliant)',
      value: '18',
      subtitle: '75% compliance rate',
      icon: CheckCircle2,
      badgeColor: '#10b981',
      iconBg: 'rgba(16, 185, 129, 0.12)',
    },
    {
      title: 'Failed (Violations)',
      value: '4',
      subtitle: 'Notices generated',
      icon: XCircle,
      badgeColor: '#f43f5e',
      iconBg: 'rgba(244, 63, 94, 0.12)',
    },
    {
      title: 'Needs Review',
      value: '2',
      subtitle: 'Ambiguous packaging labels',
      icon: AlertTriangle,
      badgeColor: '#f59e0b',
      iconBg: 'rgba(245, 158, 11, 0.12)',
    },
  ];

  // Sample recent inspections skeleton
  const recentInspections = [
    {
      id: 'INSP-2024-0104',
      product: 'Fortified Sunflower Oil 1L',
      brand: 'SunPure FMCG Ltd.',
      mrp: '₹185.00',
      status: 'PASSED',
      date: 'Today, 14:32',
      declarations: '7/7 Rules Verified',
    },
    {
      id: 'INSP-2024-0103',
      product: 'Wheat Flour / Atta 5kg',
      brand: 'Kisan Golden Harvest',
      mrp: '₹240.00',
      status: 'NEEDS_REVIEW',
      date: 'Yesterday, 17:15',
      declarations: 'Consumer care contact unreadable',
    },
    {
      id: 'INSP-2024-0102',
      product: 'Almond Kernels 250g Jar',
      brand: 'NutriDelight Imports',
      mrp: '₹450.00',
      status: 'FAILED',
      date: 'Yesterday, 11:20',
      declarations: 'Missing Country of Origin (Rule 6)',
    },
  ];

  const getStatusBadge = (status) => {
    switch (status) {
      case 'PASSED':
        return <span className="badge-status badge-pass"><CheckCircle2 size={13} /> Compliant</span>;
      case 'FAILED':
        return <span className="badge-status badge-fail"><XCircle size={13} /> Violation Found</span>;
      case 'NEEDS_REVIEW':
        return <span className="badge-status badge-review"><AlertTriangle size={13} /> Needs Review</span>;
      default:
        return <span className="badge-status">{status}</span>;
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
                  <th>Session ID</th>
                  <th>Commodity / Product</th>
                  <th>Brand / Manufacturer</th>
                  <th>Declared MRP</th>
                  <th>Compliance Status</th>
                  <th>Inspection Date</th>
                  <th>Audit Findings</th>
                </tr>
              </thead>
              <tbody>
                {recentInspections.map((row) => (
                  <tr key={row.id}>
                    <td>
                      <span className="font-mono text-cyan">{row.id}</span>
                    </td>
                    <td className="font-medium text-white">{row.product}</td>
                    <td className="text-slate">{row.brand}</td>
                    <td className="font-medium text-white">{row.mrp}</td>
                    <td>{getStatusBadge(row.status)}</td>
                    <td className="text-slate">
                      <div className="time-cell">
                        <Clock size={13} /> {row.date}
                      </div>
                    </td>
                    <td className="text-sm text-slate">{row.declarations}</td>
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
