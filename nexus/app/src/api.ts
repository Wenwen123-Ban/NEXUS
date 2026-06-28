import type { FileStationResponse, OverviewResponse } from './types';

const BASE = '/api';

async function parseJson<T>(res: Response): Promise<T> {
  const contentType = res.headers.get('content-type') ?? '';
  const body = contentType.includes('application/json') ? await res.json() : await res.text();

  if (!res.ok) {
    const message = typeof body === 'object' && body !== null
      ? (body as { error?: string; message?: string }).error || (body as { message?: string }).message
      : body;
    throw new Error(message || `Request failed with ${res.status}`);
  }

  if (!contentType.includes('application/json')) {
    throw new Error('Expected a JSON response from the NAS API');
  }

  return body as T;
}

export async function getOverview(): Promise<OverviewResponse> {
  const res = await fetch(`${BASE}/overview`);
  return parseJson<OverviewResponse>(res);
}

export async function getFiles(path?: string | null): Promise<FileStationResponse> {
  const url = path ? `${BASE}/files?path=${encodeURIComponent(path)}` : `${BASE}/files`;
  const res = await fetch(url);
  return parseJson<FileStationResponse>(res);
}

export async function uploadFile(file: File, path?: string | null): Promise<{ message: string; path: string; size: number }> {
  const form = new FormData();
  form.append('file', file);
  const url = path ? `${BASE}/upload?path=${encodeURIComponent(path)}` : `${BASE}/upload`;
  const res = await fetch(url, { method: 'POST', body: form });
  return parseJson<{ message: string; path: string; size: number }>(res);
}

export function downloadFile(path: string): void {
  window.location.href = `${BASE}/download?path=${encodeURIComponent(path)}`;
}

export async function deleteFile(path: string): Promise<{ message: string }> {
  const res = await fetch(`${BASE}/delete?path=${encodeURIComponent(path)}`, { method: 'DELETE' });
  return parseJson<{ message: string }>(res);
}

export async function getLogs(): Promise<{ lines: string[] }> {
  const res = await fetch(`${BASE}/logs`);
  return parseJson<{ lines: string[] }>(res);
}
