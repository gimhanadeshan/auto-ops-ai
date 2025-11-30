// API utility for backend integration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

export async function fetchBackendStatus(options = {}) {
  const { signal, timeout = 5000 } = options;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(`${API_BASE_URL}/status`, { signal: signal || controller.signal });
    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(`Backend responded with ${response.status} ${response.statusText} ${text}`);
    }
    return response.json();
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Request timed out');
    }
    throw new Error(err.message || 'Network error');
  } finally {
    clearTimeout(timer);
  }
}
