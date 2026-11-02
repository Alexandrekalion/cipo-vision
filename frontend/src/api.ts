const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

export type User = { id: number; username: string; display_name: string; role: string; profile_complete: boolean; authorized_profiles: string[] }
export type Profile = { user_id:number; full_name:string|null; employee_number:string|null; department:string|null; authorized_profiles:string[]; profile_completed_at:string|null }
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
export function completeProfile(payload: {full_name:string; employee_number:string; department:string; signature_data:string}) { return call<Profile>('/auth/profile', {method:'PUT', body: JSON.stringify(payload)}) }
export function listRequests() { return call<RequestItem[]>('/requests') }
export function createRequest(payload: object) { return call<RequestItem>('/requests', { method: 'POST', body: JSON.stringify(payload) }) }
export type AuditItem = { id: number; action: string; detail: string; created_at: string }
export function requestHistory(id: number) { return call<AuditItem[]>(`/requests/${id}/history`) }
export type AuthorizedUser = { id: number; username: string; display_name: string; role: string }
export function authorizedWitnesses() { return call<AuthorizedUser[]>('/users/authorized?role=Testemunha') }
export function saveSignature(signatureData: string) { return call('/auth/signature', { method: 'PUT', body: JSON.stringify({ signature_data: signatureData }) }) }
export function resubmitRequest(id: number, payload: object) { return call<RequestItem>(`/requests/${id}/resubmit`, { method: 'POST', body: JSON.stringify(payload) }) }
export function signRequest(id: number, purpose: string, documentHash: string) { return call(`/requests/${id}/sign`, { method: 'POST', body: JSON.stringify({ purpose, document_hash: documentHash, confirmed: true }) }) }
export function decideRequest(id: number, payload: object) { return call<RequestItem>(`/requests/${id}/decision`, { method: 'POST', body: JSON.stringify(payload) }) }
export function startExtraction(id: number, storageReference: string) { return call<RequestItem>(`/requests/${id}/extraction/start`, { method: 'POST', body: JSON.stringify({ storage_reference: storageReference }) }) }
export function finishExtraction(id: number) { return call<RequestItem>(`/requests/${id}/extraction/finish`, { method: 'POST' }) }
export async function logout() { await call('/auth/logout', { method: 'POST' }); csrfToken = '' }
