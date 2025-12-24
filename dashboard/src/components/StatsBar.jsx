import React from 'react';

const styles = {
  container: {
    display: 'flex',
    gap: '20px',
    marginBottom: '30px',
    flexWrap: 'wrap',
  },
  card: {
    flex: '1',
    minWidth: '150px',
    padding: '20px',
    border: '2px solid #000',
    textAlign: 'center',
  },
  value: {
    fontSize: '32px',
    fontWeight: 'bold',
    marginBottom: '5px',
  },
  label: {
    fontSize: '14px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
};

function StatsBar({ stats }) {
  if (!stats) {
    return <div style={styles.container}>Loading stats...</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.value}>{stats.total_posts_24h.toLocaleString()}</div>
        <div style={styles.label}>Posts / 24h</div>
      </div>
      <div style={styles.card}>
        <div style={styles.value}>{stats.active_spikes}</div>
        <div style={styles.label}>Active Alerts</div>
      </div>
      <div style={styles.card}>
        <div style={styles.value}>{stats.channels_monitored}</div>
        <div style={styles.label}>Channels</div>
      </div>
      <div style={styles.card}>
        <div style={styles.value}>
          {stats.avg_toxicity_24h ? (stats.avg_toxicity_24h * 100).toFixed(1) + '%' : 'N/A'}
        </div>
        <div style={styles.label}>Avg Toxicity</div>
      </div>
    </div>
  );
}

export default StatsBar;
