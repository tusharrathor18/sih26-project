import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Lock, AlertCircle, KeyRound, UserCheck, Info } from 'lucide-react';
import { getApiErrorMessage } from '../services/api';
import '../styles/login.css';

const Login = () => {
  const [officerId, setOfficerId] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (!officerId.trim()) {
      setErrorMessage('Please enter your designated Officer ID.');
      return;
    }
    if (!password) {
      setErrorMessage('Please enter your password.');
      return;
    }

    setIsSubmitting(true);
    try {
      await login(officerId, password);
      navigate(from, { replace: true });
    } catch (err) {
      setErrorMessage(err.response?.data?.message || getApiErrorMessage(err, 'Invalid Officer ID or password.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-wrapper">
      {/* Background ambient accents */}
      <div className="login-bg-glow" />

      <div className="login-card-container">
        <div className="login-card">
          {/* Official Emblem & Portal Title */}
          <div className="login-header">
            <div className="emblem-circle">
              <ShieldCheck size={36} className="emblem-svg" />
            </div>
            <div className="header-national">GOVERNMENT OF INDIA</div>
            <div className="header-department">Department of Consumer Affairs</div>
            <h1 className="header-portal-title">Legal Metrology</h1>
            <p className="header-portal-sub">Compliance Inspection System</p>
          </div>

          <div className="card-divider" />

          {/* Error Message Box */}
          {errorMessage && (
            <div className="alert-box alert-error" role="alert">
              <AlertCircle size={18} className="alert-icon" />
              <div className="alert-text">{errorMessage}</div>
            </div>
          )}

          {/* Officer Login Form */}
          <form onSubmit={handleSubmit} className="login-form" noValidate>
            <div className="form-group">
              <label htmlFor="officer-id" className="form-label">
                Officer ID
              </label>
              <div className="input-wrapper">
                <UserCheck size={18} className="input-icon" />
                <input
                  id="officer-id"
                  type="text"
                  className="form-input"
                  placeholder="e.g. OFF-DEL-2024-001"
                  value={officerId}
                  onChange={(e) => setOfficerId(e.target.value)}
                  autoComplete="username"
                  autoFocus
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <div className="input-wrapper">
                <Lock size={18} className="input-icon" />
                <input
                  id="password"
                  type="password"
                  className="form-input"
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="btn-loading">
                  <span className="spinner" /> Authenticating...
                </span>
              ) : (
                <>
                  <KeyRound size={18} />
                  <span>Officer Login</span>
                </>
              )}
            </button>
          </form>

          {/* Statutory Enforcement Notice */}
          <div className="security-notice">
            <Info size={16} className="notice-icon" />
            <div className="notice-text">
              <strong>Official Restricted System:</strong> No public registration is permitted.
              Officer accounts are issued exclusively by Department Administrators.
            </div>
          </div>

        </div>

        {/* Footer info */}
        <div className="login-footer">
          Legal Metrology (Packaged Commodities) Rules, 2011 &bull; Automated Verification Suite
        </div>
      </div>
    </div>
  );
};

export default Login;
