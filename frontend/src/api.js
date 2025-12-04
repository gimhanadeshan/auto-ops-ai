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

export async function sendChatMessage(messages, userEmail, ticketId = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages.map(m => ({
          role: m.role,
          content: m.content
        })),
        user_email: userEmail,
        ticket_id: ticketId
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Server error: ${response.status}`);
    }

    return response.json();
  } catch (err) {
    throw new Error(err.message || 'Failed to send message');
  }
}

export async function resetChatConversation(userEmail) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_email: userEmail
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Server error: ${response.status}`);
    }

    return response.json();
  } catch (err) {
    console.warn('Failed to reset conversation:', err.message);
    // Don't throw - this is a background operation
    return null;
  }
}
