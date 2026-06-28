export interface FileItem {
  id: string;
  name: string;
  type: 'file' | 'folder';
  size?: string;
  updatedAt: string;
  extension?: string;
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
