// src/lib/apiClient.ts
export async function getCsrfToken(): Promise<string> {
  // 1) Получаем/обновляем CSRF-cookie
  await fetch('/api/auth/csrf/', { credentials: 'include' });
  // 2) Читаем csrftoken из document.cookie
  const match = document.cookie.match(/(^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[2]) : '';
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
    let detail = 'Request failed';
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
