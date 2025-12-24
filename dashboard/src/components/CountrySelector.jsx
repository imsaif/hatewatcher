import React from 'react';

const styles = {
  container: {
    marginBottom: '20px',
  },
  label: {
    fontSize: '12px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    marginRight: '10px',
  },
  select: {
    padding: '10px 15px',
    fontSize: '14px',
    border: '2px solid #000',
    background: '#fff',
    cursor: 'pointer',
    minWidth: '200px',
  },
};

function CountrySelector({ countries, selectedCountry, onCountryChange }) {
  return (
    <div style={styles.container}>
      <label style={styles.label}>Region:</label>
      <select
        style={styles.select}
        value={selectedCountry || ''}
        onChange={(e) => onCountryChange(e.target.value || null)}
      >
        <option value="">All Countries (Global)</option>
        {countries.map((country) => (
          <option key={country} value={country}>
            {country}
          </option>
        ))}
      </select>
    </div>
  );
}

export default CountrySelector;
