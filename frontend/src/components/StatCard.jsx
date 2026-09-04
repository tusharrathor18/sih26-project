import React from 'react';

const StatCard = ({ title, value, subtitle, icon: Icon, badgeColor, iconBg }) => {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <span className="stat-title">{title}</span>
        <div className="stat-icon-wrapper" style={{ backgroundColor: iconBg || '#1e293b' }}>
          {Icon && <Icon size={22} style={{ color: badgeColor || '#38bdf8' }} />}
        </div>
      </div>
      <div className="stat-value">{value}</div>
      {subtitle && (
        <div className="stat-footer">
          <span className="stat-pill" style={{ color: badgeColor, backgroundColor: `${badgeColor}18` }}>
            {subtitle}
          </span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
