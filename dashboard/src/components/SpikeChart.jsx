import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { format, parseISO } from 'date-fns';

const styles = {
  container: {
    marginBottom: '30px',
    padding: '20px',
    border: '2px solid #000',
  },
  title: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '20px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  chart: {
    width: '100%',
    height: 300,
  },
};

function SpikeChart({ timeline, baselineAvg }) {
  if (!timeline || timeline.length === 0) {
    return (
      <div style={styles.container}>
        <div style={styles.title}>Toxicity Over Time</div>
        <div>No data available</div>
      </div>
    );
  }

  const data = timeline.map((point) => ({
    date: format(parseISO(point.timestamp), 'MMM d'),
    toxicity: point.avg_toxicity ? (point.avg_toxicity * 100).toFixed(1) : null,
    posts: point.post_count,
  }));

  return (
    <div style={styles.container}>
      <div style={styles.title}>Toxicity Over Time (Last 7 Days)</div>
      <div style={styles.chart}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ccc" />
            <XAxis dataKey="date" stroke="#000" />
            <YAxis
              stroke="#000"
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                background: '#fff',
                border: '2px solid #000',
                borderRadius: 0,
              }}
              formatter={(value) => [`${value}%`, 'Toxicity']}
            />
            <Line
              type="monotone"
              dataKey="toxicity"
              stroke="#000"
              strokeWidth={2}
              dot={{ fill: '#000', strokeWidth: 2 }}
              activeDot={{ r: 6, fill: '#000' }}
            />
            {baselineAvg && (
              <ReferenceLine
                y={baselineAvg * 100}
                stroke="#666"
                strokeDasharray="5 5"
                label={{ value: 'Baseline', fill: '#666', fontSize: 12 }}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default SpikeChart;
