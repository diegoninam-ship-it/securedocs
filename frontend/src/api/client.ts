const TOKEN_KEY = 'securedocs_token'
const SIM_UBICACION_KEY = 'securedocs_sim_ubicacion'
const SIM_DISPOSITIVO_KEY = 'securedocs_sim_dispositivo'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

let onUnauthorized: (() => void) | null = null

export function setOnUnauthorized(fn: () => void) {
  onUnauthorized = fn
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function getSimulador() {
  return {
    ubicacion: localStorage.getItem(SIM_UBICACION_KEY) ?? 'PE',
    dispositivo: localStorage.getItem(SIM_DISPOSITIVO_KEY) ?? 'CORPORATIVO',
  }
}

export function setSimulador(ubicacion: string, dispositivo: string) {
  localStorage.setItem(SIM_UBICACION_KEY, ubicacion)
  localStorage.setItem(SIM_DISPOSITIVO_KEY, dispositivo)
}

interface ApiFetchOptions {
  method?: string
  body?: unknown
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const headers: Record<string, string> = {}
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const { ubicacion, dispositivo } = getSimulador()
  headers['X-Sim-Ubicacion'] = ubicacion
  headers['X-Sim-Dispositivo'] = dispositivo

  let body: string | undefined
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(options.body)
  }

  const response = await fetch(`/api${path}`, {
    method: options.method ?? 'GET',
    headers,
    body,
  })

  if (response.status === 401) {
    clearToken()
    onUnauthorized?.()
    throw new ApiError(401, 'Sesión expirada, vuelve a iniciar sesión')
  }

  if (response.status === 204) {
    return undefined as T
  }

  let payload: unknown = null
  const text = await response.text()
  if (text) {
    try {
      payload = JSON.parse(text)
    } catch {
      payload = text
    }
  }

  if (!response.ok) {
    const detail =
      payload && typeof payload === 'object' && 'detail' in payload
        ? String((payload as { detail: unknown }).detail)
        : `Error ${response.status}`
    throw new ApiError(response.status, detail)
  }

  return payload as T
}
