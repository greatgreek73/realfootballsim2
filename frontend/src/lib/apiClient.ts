// src/lib/apiClient.ts

// Берём CSRF-токен из JSON-ответа /api/auth/csrf/.
// Если JSON не пришёл (редкий случай) — пробуем из cookie как запасной вариант.
export async function getCsrfToken(): Promise<string> {
  const res = await fetch('/api/auth/csrf/', { credentials: 'include' });
  try {
    const data = await res.json();
    if (data && data.csrfToken) return String(data.csrfToken);
  } catch {
    // ignore
  }
  const m = document.cookie.match(/(^|;\s*)csrftoken=([^;]+)/);
  return m ? decodeURIComponent(m[2]) : '';
}

export async function postJSON<T = any>(url: string, data: any): Promise<T> {
  const csrftoken = await getCsrfToken();
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    credentials: 'include',
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    // Пытаемся вытащить деталь из JSON; если пришла HTML-страница (403 CSRF) — дадим общий текст
    let detail = 'Login failed';
    try {
      const j = await res.json();
      detail = j.detail ?? JSON.stringify(j);
    } catch {}
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function getJSON<T = any>(url: string): Promise<T> {
  const res = await fetch(url, { credentials: 'include' });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}
