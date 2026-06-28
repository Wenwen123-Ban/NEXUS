export interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  size?: string;
  updatedAt: string;
  extension?: string;
  path?: string;
}

export interface FileStationEntry {
  name: string;
  path: string;
  is_dir: boolean;
  size: number;
  mtime: number;
}

export interface FileStationResponse {
  current: string;
  root: string;
  parent: string | null;
  entries: FileStationEntry[];
}

export interface OverviewResponse {
  server_name: string;
  platform: string;
  cpu_percent: number;
  ram_percent: number;
  ram_used_gb: number;
  ram_total_gb: number;
  temp_c: number | null;
  net_dl_kbs: number;
  net_ul_kbs: number;
  disk_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  disk_free_gb: number;
  nas_root: string;
  drives: {
    device: string;
    mountpoint: string;
    fstype: string;
    percent: number;
    used_gb: number;
    total_gb: number;
    free_gb: number;
  }[];
}

export interface NasService {
  id: string;
  name: string;
  category: 'media' | 'utility' | 'network' | 'system';
  status: 'running' | 'stopped' | 'starting';
  port: number;
  uptime?: string;
  cpuUsage: number;
  ramUsage: number;
}

export interface NasTask {
  id: string;
  name: string;
  type: 'download' | 'backup' | 'raid' | 'sync';
  progress: number; // 0 to 100
  speed?: string; // e.g. "12.4 MB/s"
  eta?: string; // e.g. "4m 12s"
  status: 'active' | 'paused' | 'completed' | 'queued';
}

export interface SystemStats {
  cpu: number;
  ram: number;
  temp: number;
  networkUp: number; // KB/s
  networkDown: number; // KB/s
  serverName?: string;
  platform?: string;
  nasRoot?: string;
  disks: {
    name: string;
    used: number; // GB
    total: number; // GB
    temp: number; // Celsius
    status: 'healthy' | 'warning' | 'critical';
  }[];
}

export interface SystemLog {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
}
