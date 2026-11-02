const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

export type User = { id: number; username: string; display_name: string; role: string }
export type RequestItem = { id: number; protocol: string; status: string; employee: string; occurrence_type: string; occurred_at: string; location: string; camera_area?: string; reason: string; requester_id: number; manager_id: number }

let csrfToken = ''
async function call<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Content-Type', 'application/json')
  if (csrfToken && init.method && init.method !== 'GET') headers.set('X-CSRF-Token', csrfToken)
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers, credentials: 'include' })
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Erro HTTP ${response.status}`)
  return response.json()
}

export async function login(username: string, password: string) {
  const result = await call<{ access_token: string }>('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
  csrfToken = result.access_token
  return me()
}
export function me() { return call<User>('/auth/me') }
export function listRequests() { return call<RequestItem[]>('/requests') }
export function createRequest(payload: object) { return call<RequestItem>('/requests', { method: 'POST', body: JSON.stringify(payload) }) }
export async function logout() { await call('/auth/logout', { method: 'POST' }); csrfToken = '' }
