export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function apiFetch(path: string, token?: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {})
  }
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API_URL}${path}`, { ...options, headers, cache: 'no-store' })
  if (!res.ok) {
    let message = 'Request failed'
    try {
      const data = await res.json()
      message = data.detail || message
    } catch {}
    throw new Error(message)
  }
  return res.json()
}

export function exportUrl(path: string, token: string) {
  return `${API_URL}${path}?token=${encodeURIComponent(token)}`
}
