import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, LayoutDashboard, Camera, History, LogOut, UserCheck } from 'lucide-react';

const Navbar = () => {
  const { officer, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/scan', label: 'Scan Commodity', icon: Camera },
    { path: '/history', label: 'Audit History', icon: History },
  ];

  return (
    <header className="gov-header">
      {/* Top National Branding Bar */}
      <div className="gov-topbar">
        <div className="gov-container topbar-content">
          <div className="emblem-group">
            <ShieldCheck className="emblem-icon" size={20} />
            <span className="gov-agency">GOVERNMENT OF INDIA &bull; DEPARTMENT OF CONSUMER AFFAIRS</span>
          </div>
          <div className="portal-sub">Legal Metrology (Packaged Commodities) Enforcement Division</div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <nav className="gov-nav">
        <div className="gov-container nav-content">
          <Link to="/dashboard" className="brand-logo">
            <div className="brand-badge">LM</div>
            <div className="brand-text">
              <span className="brand-title">LEGAL METROLOGY</span>
              <span className="brand-subtitle">Compliance Inspection System</span>
            </div>
          </Link>

          <div className="nav-links">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-link ${isActive ? 'active' : ''}`}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Officer Profile & Logout */}
          <div className="officer-actions">
            {officer && (
              <div className="officer-badge">
                <div className="officer-avatar">
                  <UserCheck size={18} />
                </div>
                <div className="officer-meta">
                  <div className="officer-name">{officer.name}</div>
                  <div className="officer-sub">
                    <span className="badge-id">{officer.officer_id}</span>
                    <span className="badge-sep">&bull;</span>
                    <span className="badge-jur">{officer.jurisdiction}</span>
                  </div>
                </div>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="btn-logout"
              title="End session and log out"
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Navbar;
