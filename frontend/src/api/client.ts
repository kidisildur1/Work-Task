import { demoGet, demoPatch, demoPost } from './demoStore';

const API = import.meta.env.VITE_API_URL || '';
const DEMO = !API;

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  if (DEMO) {
    if (!options?.method || options.method === 'GET') return demoGet(path) as Promise<T>;
    const body = options.body ? JSON.parse(String(options.body)) : undefined;
    if (options.method === 'POST') return demoPost(path, body) as Promise<T>;
    if (options.method === 'PATCH') return demoPatch(path, body) as Promise<T>;
  }

  try {
    const res = await fetch(`${API}${path}`, options);
    if (!res.ok) throw new Error('API error');
    return res.json();
  } catch (error) {
    console.warn('API unavailable, switching to demo mode', error);
    if (!options?.method || options.method === 'GET') return demoGet(path) as Promise<T>;
    const body = options?.body ? JSON.parse(String(options.body)) : undefined;
    if (options?.method === 'POST') return demoPost(path, body) as Promise<T>;
    if (options?.method === 'PATCH') return demoPatch(path, body) as Promise<T>;
    throw error;
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  return request<T>(path);
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}
