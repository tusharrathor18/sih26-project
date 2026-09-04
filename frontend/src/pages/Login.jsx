import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Lock, AlertCircle, KeyRound, UserCheck, Info } from 'lucide-react';
import '../styles/login.css';

const Login = () => {
  const [officerId, setOfficerId] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDemoCredentials, setShowDemoCredentials] = useState(false);

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
      // Extract specific backend error messages
      if (err.response && err.response.data) {
        const data = err.response.data;
        if (data.errors) {
          if (data.errors.officer_id) {
            setErrorMessage(Array.isArray(data.errors.officer_id) ? data.errors.officer_id[0] : data.errors.officer_id);
          } else if (data.errors.password) {
            setErrorMessage(Array.isArray(data.errors.password) ? data.errors.password[0] : data.errors.password);
          } else if (data.errors.non_field_errors) {
            setErrorMessage(Array.isArray(data.errors.non_field_errors) ? data.errors.non_field_errors[0] : data.errors.non_field_errors);
          } else {
            setErrorMessage(data.message || 'Authentication failed. Please check credentials.');
          }
        } else {
          setErrorMessage(data.message || 'Access denied. Please verify your Officer ID and password.');
        }
      } else {
        setErrorMessage('Unable to connect to backend service. Ensure Django server is running.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const fillTestCredentials = (id, pwd) => {
    setOfficerId(id);
    setPassword(pwd);
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

          {/* Quick Credential Guide for Testing / Prompt 1 Evaluation */}
          <div className="demo-credentials-toggle">
            <button
              type="button"
              onClick={() => setShowDemoCredentials(!showDemoCredentials)}
              className="btn-toggle-demo"
            >
              {showDemoCredentials ? '▲ Hide Test Credentials' : '▼ Pre-authorized Test Accounts (Prompt 1)'}
            </button>

            {showDemoCredentials && (
              <div className="demo-credentials-box">
                <div className="demo-row" onClick={() => fillTestCredentials('OFF-DEL-2024-001', 'Inspector@123')}>
                  <div>
                    <strong>OFF-DEL-2024-001</strong> (Inspector Delhi)
                  </div>
                  <span className="fill-pill">Click to fill</span>
                </div>
                <div className="demo-row" onClick={() => fillTestCredentials('OFF-MUM-2024-042', 'Inspector@123')}>
                  <div>
                    <strong>OFF-MUM-2024-042</strong> (Inspector Mumbai)
                  </div>
                  <span className="fill-pill">Click to fill</span>
                </div>
                <div className="demo-row" onClick={() => fillTestCredentials('OFF-INACT-2024-099', 'Inspector@123')}>
                  <div>
                    <strong>OFF-INACT-2024-099</strong> (Inactive Test)
                  </div>
                  <span className="fill-pill text-warn">Test Inactive</span>
                </div>
                <div className="demo-subnote">Password for all test officers: <code>Inspector@123</code></div>
              </div>
            )}
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
