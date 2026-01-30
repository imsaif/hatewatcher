import axios from 'axios';

// In production, use the full API URL; in development, use proxy
const API_BASE = process.env.REACT_APP_API_URL
  ? `${process.env.REACT_APP_API_URL}/api`
  : '/api';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const getCountries = async () => {
  const response = await client.get('/countries');
  return response.data.countries;
};

export const getStats = async (country = null) => {
  const params = {};
  if (country) params.country = country;
  const response = await client.get('/stats', { params });
  return response.data;
};

export const getAlerts = async (activeOnly = true, country = null) => {
  const params = { active_only: activeOnly };
  if (country) params.country = country;
  const response = await client.get('/alerts', { params });
  return response.data;
};

export const getAlert = async (alertId) => {
  const response = await client.get(`/alerts/${alertId}`);
  return response.data;
};

export const getTimeline = async (channelId = null, country = null, days = 7) => {
  const params = { days };
  if (channelId) params.channel_id = channelId;
  if (country) params.country = country;
  const response = await client.get('/timeline', { params });
  return response.data;
};

export const getPosts = async (channelId = null, hateSpeechOnly = false, limit = 50) => {
  const params = { limit, hate_speech_only: hateSpeechOnly };
  if (channelId) params.channel_id = channelId;
  const response = await client.get('/posts', { params });
  return response.data;
};

export const exportAlert = (alertId) => {
  return `${API_BASE}/export/${alertId}`;
};

export default client;
