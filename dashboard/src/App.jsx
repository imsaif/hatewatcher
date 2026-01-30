import React, { useState, useEffect, useCallback } from 'react';
import StatsBar from './components/StatsBar';
import SpikeChart from './components/SpikeChart';
import AlertFeed from './components/AlertFeed';
import CountrySelector from './components/CountrySelector';
import { getStats, getAlerts, getTimeline, getCountries } from './api/client';

const styles = {
  app: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    paddingBottom: '20px',
    borderBottom: '3px solid #000',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    letterSpacing: '2px',
    textTransform: 'uppercase',
  },
  refreshBtn: {
    background: '#fff',
    color: '#000',
    border: '2px solid #000',
    padding: '10px 20px',
    cursor: 'pointer',
    fontSize: '14px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  refreshBtnHover: {
    background: '#000',
    color: '#fff',
  },
  error: {
    padding: '20px',
    border: '2px solid #000',
    background: '#f5f5f5',
    marginBottom: '20px',
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '18px',
  },
  footer: {
    marginTop: '40px',
    paddingTop: '20px',
    borderTop: '1px solid #ccc',
    textAlign: 'center',
    fontSize: '12px',
    color: '#666',
  },
};

function App() {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [countries, setCountries] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshHover, setRefreshHover] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [statsData, alertsData, timelineData] = await Promise.all([
        getStats(selectedCountry),
        getAlerts(true, selectedCountry),
        getTimeline(null, selectedCountry, 7),
      ]);
      setStats(statsData);
      setAlerts(alertsData);
      setTimeline(timelineData.timeline || []);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data. Make sure the API server is running.');
    } finally {
      setLoading(false);
    }
  }, [selectedCountry]);

  const fetchCountries = useCallback(async () => {
    try {
      const countriesData = await getCountries();
      setCountries(countriesData);
    } catch (err) {
      console.error('Error fetching countries:', err);
    }
  }, []);

  useEffect(() => {
    fetchCountries();
  }, [fetchCountries]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleRefresh = () => {
    setLoading(true);
    fetchData();
  };

  const handleCountryChange = (country) => {
    setSelectedCountry(country);
    setLoading(true);
  };

  if (loading && !stats) {
    return (
      <div style={styles.app}>
        <div style={styles.loading}>Loading...</div>
      </div>
    );
  }

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <div style={styles.title}>HateWatch</div>
        <button
          style={{
            ...styles.refreshBtn,
            ...(refreshHover ? styles.refreshBtnHover : {}),
          }}
          onClick={handleRefresh}
          onMouseEnter={() => setRefreshHover(true)}
          onMouseLeave={() => setRefreshHover(false)}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </header>

      <CountrySelector
        countries={countries}
        selectedCountry={selectedCountry}
        onCountryChange={handleCountryChange}
      />

      {error && <div style={styles.error}>{error}</div>}

      <StatsBar stats={stats} />
      <SpikeChart timeline={timeline} baselineAvg={stats?.avg_toxicity_24h} />
      <AlertFeed alerts={alerts} />

      <footer style={styles.footer}>
        {lastUpdated && (
          <div style={{ marginBottom: '8px' }}>
            Last updated: {lastUpdated.toLocaleString()}
          </div>
        )}
        HateWatch MVP | Data updates every 60 seconds
      </footer>
    </div>
  );
}

export default App;
