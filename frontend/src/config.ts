const normalizeBaseUrl = (url?: string): string => {
  const fallback = 'http://localhost:8000';
  const base = (url || fallback).trim();
  return base.replace(/\/$/, '');
};

const apiBaseUrl = normalizeBaseUrl(process.env.REACT_APP_API_BASE_URL);
const wsProtocol = apiBaseUrl.startsWith('https://') ? 'wss' : 'ws';
const wsBase = apiBaseUrl.replace(/^https?/, wsProtocol);

export const API_BASE_URL = apiBaseUrl;
export const WS_URL = `${wsBase}/ws`;
