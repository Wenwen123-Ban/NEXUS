import { FileStationResponse, OverviewResponse } from './types';

const BASE = '/api';

async function parseJson<T>(res: Response): Promise<T> {
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.error || data?.message || `Request failed with ${res.status}`);
  }
  return data;
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

export async function uploadFile(file: File): Promise<{ message: string; path: string; size: number }> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form });
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
