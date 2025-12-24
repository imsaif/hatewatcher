import React, { useState } from 'react';
import { format, parseISO } from 'date-fns';
import { exportAlert } from '../api/client';

const styles = {
  container: {
    marginBottom: '30px',
  },
  title: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '20px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  alert: {
    border: '2px solid #000',
    marginBottom: '15px',
    padding: '15px',
    cursor: 'pointer',
  },
  alertHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '10px',
  },
  severity: {
    display: 'inline-block',
    padding: '2px 8px',
    border: '2px solid #000',
    fontWeight: 'bold',
    fontSize: '12px',
    textTransform: 'uppercase',
    marginRight: '10px',
  },
  severityCritical: {
    background: '#000',
    color: '#fff',
  },
  severityHigh: {
    background: '#333',
    color: '#fff',
  },
  severityMedium: {
    background: '#666',
    color: '#fff',
  },
  severityLow: {
    background: '#fff',
    color: '#000',
  },
  mainInfo: {
    flex: 1,
  },
  location: {
    fontWeight: 'bold',
    fontSize: '16px',
  },
  percentage: {
    fontSize: '24px',
    fontWeight: 'bold',
  },
  meta: {
    fontSize: '14px',
    color: '#333',
    marginTop: '5px',
  },
  exportBtn: {
    background: '#000',
    color: '#fff',
    border: 'none',
    padding: '8px 16px',
    cursor: 'pointer',
    fontSize: '12px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  samplePosts: {
    marginTop: '15px',
    paddingTop: '15px',
    borderTop: '1px solid #ccc',
  },
  sampleTitle: {
    fontSize: '12px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    marginBottom: '10px',
    color: '#666',
  },
  post: {
    padding: '10px',
    background: '#f5f5f5',
    marginBottom: '10px',
    fontSize: '14px',
  },
  postMeta: {
    fontSize: '12px',
    color: '#666',
    marginTop: '5px',
  },
  empty: {
    padding: '40px',
    textAlign: 'center',
    border: '2px dashed #ccc',
    color: '#666',
  },
};

function getSeverityStyle(severity) {
  switch (severity) {
    case 'critical':
      return { ...styles.severity, ...styles.severityCritical };
    case 'high':
      return { ...styles.severity, ...styles.severityHigh };
    case 'medium':
      return { ...styles.severity, ...styles.severityMedium };
    default:
      return { ...styles.severity, ...styles.severityLow };
  }
}

function AlertCard({ alert }) {
  const [expanded, setExpanded] = useState(false);

  const handleExport = (e) => {
    e.stopPropagation();
    window.open(exportAlert(alert.id), '_blank');
  };

  return (
    <div style={styles.alert} onClick={() => setExpanded(!expanded)}>
      <div style={styles.alertHeader}>
        <div style={styles.mainInfo}>
          <span style={getSeverityStyle(alert.severity)}>{alert.severity}</span>
          <span style={styles.location}>
            {alert.country || 'Unknown'} | {alert.channel_username || 'Channel'}
          </span>
          <div style={styles.meta}>
            {alert.post_count} posts | Started {format(parseISO(alert.started_at), 'MMM d, h:mm a')}
          </div>
        </div>
        <div>
          <div style={styles.percentage}>+{alert.spike_percentage.toFixed(0)}%</div>
          <button style={styles.exportBtn} onClick={handleExport}>
            Export
          </button>
        </div>
      </div>

      {expanded && alert.sample_posts && alert.sample_posts.length > 0 && (
        <div style={styles.samplePosts}>
          <div style={styles.sampleTitle}>Sample Posts</div>
          {alert.sample_posts.map((post, idx) => (
            <div key={idx} style={styles.post}>
              {post.text}
              <div style={styles.postMeta}>
                Toxicity: {(post.toxicity_score * 100).toFixed(1)}% |{' '}
                {format(parseISO(post.posted_at), 'MMM d, h:mm a')}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AlertFeed({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div style={styles.container}>
        <div style={styles.title}>Active Alerts</div>
        <div style={styles.empty}>No active alerts</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.title}>Active Alerts ({alerts.length})</div>
      {alerts.map((alert) => (
        <AlertCard key={alert.id} alert={alert} />
      ))}
    </div>
  );
}

export default AlertFeed;
