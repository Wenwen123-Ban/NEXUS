import React, { useState, useEffect } from 'react';
import { 
  LayoutGrid, 
  FolderClosed, 
  Layers, 
  DownloadCloud, 
  Wifi, 
  Signal, 
  Battery, 
  Sliders, 
  Bell, 
  Info, 
  Power,
  Shield, 
  Fan, 
  Activity,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';
import Dashboard from './components/Dashboard';
import FileExplorer from './components/FileExplorer';
import ServicesManager from './components/ServicesManager';
import TaskList from './components/TaskList';
import { SystemStats, FileItem, NasService, NasTask } from './types';
import { deleteFile, downloadFile, getFiles, getOverview, uploadFile } from './api';

// Mock initial files structure (dict path -> items)
const INITIAL_FILES: Record<string, FileItem[]> = {
  'root': [
    { id: 'f1', name: 'Media', type: 'folder', updatedAt: '2026-06-25' },
    { id: 'f2', name: 'Backups', type: 'folder', updatedAt: '2026-06-20' },
    { id: 'f3', name: 'DockerConfigs', type: 'folder', updatedAt: '2026-06-27' },
    { id: 'f4', name: 'nas_manual.pdf', type: 'file', size: '2.4 MB', updatedAt: '2026-05-12', extension: 'pdf' },
  ],
  'Media': [
    { id: 'm1', name: 'Movies', type: 'folder', updatedAt: '2026-06-24' },
    { id: 'm2', name: 'Music', type: 'folder', updatedAt: '2026-06-23' },
    { id: 'm3', name: 'family_photo.jpg', type: 'file', size: '4.8 MB', updatedAt: '2026-06-15', extension: 'jpg' }
  ],
  'Media/Movies': [
    { id: 'mov1', name: 'Big_Buck_Bunny.mp4', type: 'file', size: '245 MB', updatedAt: '2026-06-10', extension: 'mp4' },
    { id: 'mov2', name: 'Sintel_4K.mkv', type: 'file', size: '1.2 GB', updatedAt: '2026-06-11', extension: 'mkv' }
  ],
  'Media/Music': [
    { id: 'mus1', name: 'lofi_study_chill.mp3', type: 'file', size: '8.2 MB', updatedAt: '2026-06-22', extension: 'mp3' }
  ],
  'Backups': [
    { id: 'b1', name: 'MacBook_Backup.sparseimage', type: 'file', size: '124 GB', updatedAt: '2026-06-20', extension: 'sparseimage' },
    { id: 'b2', name: 'database_dump.sql', type: 'file', size: '42 MB', updatedAt: '2026-06-26', extension: 'sql' }
  ],
  'DockerConfigs': [
    { id: 'd1', name: 'docker-compose.yml', type: 'file', size: '4.1 KB', updatedAt: '2026-06-27', extension: 'yml' },
    { id: 'd2', name: 'plex_config', type: 'folder', updatedAt: '2026-06-27' }
  ],
  'DockerConfigs/plex_config': [
    { id: 'plex1', name: 'Preferences.xml', type: 'file', size: '1.8 KB', updatedAt: '2026-06-27', extension: 'xml' }
  ]
};

// Initial docker container services
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / Math.pow(1024, index)).toFixed(1)} ${units[index]}`;
};

const INITIAL_SERVICES: NasService[] = [
  { id: 's1', name: 'Plex Media Server', category: 'media', status: 'running', port: 32400, uptime: '12d 4h', cpuUsage: 4.2, ramUsage: 184 },
  { id: 's2', name: 'Pi-hole DNS', category: 'network', status: 'running', port: 8080, uptime: '32d 18h', cpuUsage: 0.8, ramUsage: 45 },
  { id: 's3', name: 'Transmission Torrent', category: 'utility', status: 'running', port: 9091, uptime: '4d 2h', cpuUsage: 1.5, ramUsage: 68 },
  { id: 's4', name: 'Home Assistant', category: 'utility', status: 'running', port: 8123, uptime: '12d 4h', cpuUsage: 3.1, ramUsage: 142 },
  { id: 's5', name: 'Portainer', category: 'system', status: 'running', port: 9443, uptime: '12d 4h', cpuUsage: 0.2, ramUsage: 32 },
  { id: 's6', name: 'Samba Share Engine', category: 'system', status: 'running', port: 445, uptime: '45d 1h', cpuUsage: 0.5, ramUsage: 24 }
];

// Initial running downloads and system tasks
const INITIAL_TASKS: NasTask[] = [
  { id: 't1', name: 'RAID scrubbing array_0', type: 'raid', progress: 34, speed: '145 MB/s', eta: '1h 42m', status: 'active' },
  { id: 't2', name: 'Cloud sync: Google Drive', type: 'sync', progress: 85, speed: '4.5 MB/s', eta: '1m 20s', status: 'active' },
  { id: 't3', name: 'ubuntu-26.04-desktop-amd64.iso', type: 'download', progress: 12, speed: '18.4 MB/s', eta: '2m 15s', status: 'active' }
];

export default function App() {
  // Mobile app tabs: 'dashboard', 'files', 'apps', 'tasks'
  const [activeTab, setActiveTab] = useState<'dashboard' | 'files' | 'apps' | 'tasks'>('dashboard');
  
  // App States
  const [currentTime, setCurrentTime] = useState<string>('12:00 PM');
  const [uptimeSeconds, setUptimeSeconds] = useState<number>(382894); // ~4.4 days in seconds
  const [isControlCenterOpen, setIsControlCenterOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'info' | 'success' | 'warn' } | null>(null);

  // Storage / Health values
  const [stats, setStats] = useState<SystemStats>({
    cpu: 18,
    ram: 42,
    temp: 41,
    networkUp: 84, // KB/s
    networkDown: 1420, // KB/s
    serverName: 'NAS-Server-01',
    platform: 'NAS',
    nasRoot: 'root',
    disks: [
      { name: 'Drive 1 (WD Red Pro)', used: 2840, total: 3726, temp: 36, status: 'healthy' },
      { name: 'Drive 2 (WD Red Pro)', used: 2840, total: 3726, temp: 37, status: 'healthy' },
      { name: 'Drive 3 (WD Red Pro)', used: 2840, total: 3726, temp: 35, status: 'healthy' },
      { name: 'Drive 4 (WD Red Pro)', used: 0, total: 3726, temp: 34, status: 'healthy' } // Spare/unassigned in raid
    ]
  });

  const [files, setFiles] = useState<Record<string, FileItem[]>>(INITIAL_FILES);
  const [services, setServices] = useState<NasService[]>(INITIAL_SERVICES);
  const [tasks, setTasks] = useState<NasTask[]>(INITIAL_TASKS);

  // 1. Time ticking
  useEffect(() => {
    const updateTime = () => {
      const date = new Date();
      let hours = date.getHours();
      const minutes = date.getMinutes();
      const ampm = hours >= 12 ? 'PM' : 'AM';
      hours = hours % 12;
      hours = hours ? hours : 12; // the hour '0' should be '12'
      const strMinutes = minutes < 10 ? '0'+minutes : minutes;
      setCurrentTime(`${hours}:${strMinutes} ${ampm}`);
    };
    updateTime();
    const interval = setInterval(updateTime, 15000);
    return () => clearInterval(interval);
  }, []);

  const mapApiFiles = (entries: Awaited<ReturnType<typeof getFiles>>['entries']): FileItem[] => entries.map((entry) => ({
    id: entry.path,
    name: entry.name,
    path: entry.path,
    type: entry.is_dir ? 'folder' : 'file',
    size: entry.is_dir ? undefined : formatBytes(entry.size),
    updatedAt: entry.mtime ? new Date(entry.mtime * 1000).toISOString().split('T')[0] : 'unknown',
    extension: entry.name.includes('.') ? entry.name.split('.').pop() : undefined
  }));

  const refreshFiles = async (path?: string | null) => {
    const data = await getFiles(path);
    const key = data.current;
    setFiles(prev => ({
      ...prev,
      root: key === data.root ? mapApiFiles(data.entries) : prev.root,
      [key]: mapApiFiles(data.entries)
    }));
    return data;
  };

  useEffect(() => {
    let cancelled = false;
    const loadOverview = async () => {
      try {
        const overview = await getOverview();
        if (cancelled) return;
        setStats({
          serverName: overview.server_name,
          platform: overview.platform,
          nasRoot: overview.nas_root,
          cpu: overview.cpu_percent,
          ram: overview.ram_percent,
          temp: overview.temp_c ?? 0,
          networkUp: overview.net_ul_kbs,
          networkDown: overview.net_dl_kbs,
          disks: (overview.drives.length ? overview.drives : [{
            device: overview.nas_root,
            mountpoint: overview.nas_root,
            fstype: 'nas',
            percent: overview.disk_percent,
            used_gb: overview.disk_used_gb,
            total_gb: overview.disk_total_gb,
            free_gb: overview.disk_free_gb
          }]).map((drive) => ({
            name: drive.device || drive.mountpoint,
            used: drive.used_gb,
            total: drive.total_gb,
            temp: overview.temp_c ?? 0,
            status: drive.percent > 90 ? 'critical' : drive.percent > 75 ? 'warning' : 'healthy'
          }))
        });
      } catch (error) {
        console.warn('Failed to load NAS overview', error);
      }
    };
    loadOverview();
    const interval = setInterval(loadOverview, 10000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    refreshFiles().catch((error) => console.warn('Failed to load NAS files', error));
  }, []);

  // 2. Active system simulation loops
  useEffect(() => {
    const interval = setInterval(() => {
      // Tick uptime
      setUptimeSeconds(prev => prev + 1);

      // Fluctuate Base stats depending on running services
      setStats(prev => {
        const runningApps = services.filter(s => s.status === 'running');
        const runningCpuOverhead = runningApps.reduce((acc, app) => acc + app.cpuUsage, 0);
        const runningRamOverhead = runningApps.reduce((acc, app) => acc + app.ramUsage, 0);

        // Convert memory overhead (MB) to percentage of 16GB total RAM
        const ramPctOverhead = (runningRamOverhead / 16384) * 100;

        // Base Idle stats + Service overhead + slight variance
        const cpuVariance = Math.sin(Date.now() / 5000) * 4;
        const targetCpu = Math.max(5, Math.min(95, 8 + runningCpuOverhead + cpuVariance));

        const ramVariance = Math.cos(Date.now() / 7000) * 1;
        const targetRam = Math.max(15, Math.min(90, 20 + ramPctOverhead + ramVariance));

        const networkDownVariance = Math.random() > 0.5 ? Math.random() * 800 : -Math.random() * 500;
        const activeDownloadTasks = tasks.filter(t => t.type === 'download' && t.status === 'active');
        const downloadSpeedContribution = activeDownloadTasks.reduce((sum, d) => {
          if (d.speed?.includes('MB/s')) {
            return sum + (parseFloat(d.speed) * 1024);
          }
          return sum + parseFloat(d.speed || '0');
        }, 0);

        const targetNetDown = Math.max(10, 120 + downloadSpeedContribution + networkDownVariance);
        const targetNetUp = Math.max(5, 45 + (Math.random() > 0.5 ? Math.random() * 80 : -Math.random() * 30));

        // Slightly vary temperatures
        const targetTemp = Math.round(38 + (targetCpu / 10) + (Math.sin(Date.now() / 20000) * 1.5));
        
        return {
          ...prev,
          cpu: targetCpu,
          ram: targetRam,
          temp: targetTemp,
          networkDown: targetNetDown,
          networkUp: targetNetUp,
          disks: prev.disks.map(disk => ({
            ...disk,
            temp: Math.round(34 + Math.random() * 3)
          }))
        };
      });

      // Update service uptimes and metric fluctuations
      setServices(prev => prev.map(srv => {
        if (srv.status !== 'running') return srv;
        // Slightly vary container metrics
        const cpuFluct = (Math.random() - 0.5) * 0.4;
        return {
          ...srv,
          cpuUsage: Math.max(0.1, parseFloat((srv.cpuUsage + cpuFluct).toFixed(1)))
        };
      }));

      // Update Tasks download progress
      setTasks(prev => {
        let completionToast: string | null = null;
        let fileToInstall: { name: string; size: string } | null = null;

        const updated = prev.map(task => {
          if (task.status !== 'active') return task;

          // Increment progress
          let rate = 0.5;
          if (task.type === 'download') rate = 2.4; // Downloads finish faster for simulation excitement
          if (task.type === 'raid') rate = 0.08; // RAID takes a long time

          const nextProgress = Math.min(100, task.progress + rate);
          
          if (nextProgress >= 100) {
            completionToast = `${task.name} has completed!`;
            if (task.type === 'download') {
              fileToInstall = {
                name: task.name,
                size: '4.2 GB'
              };
            }
            return {
              ...task,
              progress: 100,
              status: 'completed',
              speed: undefined,
              eta: undefined
            };
          }

          // Generate dynamic remaining speeds and ETAs
          let speedStr = task.speed;
          let etaStr = task.eta;

          if (task.type === 'download') {
            const currentSpeedVal = 12 + Math.sin(Date.now() / 3000) * 4;
            speedStr = `${currentSpeedVal.toFixed(1)} MB/s`;
            const secondsLeft = Math.round(((100 - nextProgress) / rate) * 1);
            etaStr = secondsLeft > 60 ? `${Math.floor(secondsLeft / 60)}m ${secondsLeft % 60}s` : `${secondsLeft}s`;
          } else if (task.type === 'sync') {
            const currentSpeedVal = 2.1 + Math.cos(Date.now() / 4000) * 0.5;
            speedStr = `${currentSpeedVal.toFixed(1)} MB/s`;
            const secondsLeft = Math.round(((100 - nextProgress) / rate) * 1);
            etaStr = secondsLeft > 60 ? `${Math.floor(secondsLeft / 60)}m ${secondsLeft % 60}s` : `${secondsLeft}s`;
          } else if (task.type === 'raid') {
            const secondsLeft = Math.round(((100 - nextProgress) / rate) * 1);
            etaStr = `${Math.floor(secondsLeft / 60)}h ${secondsLeft % 60}m`;
          }

          return {
            ...task,
            progress: nextProgress,
            speed: speedStr,
            eta: etaStr
          };
        });

        // Trigger toast completion banner
        if (completionToast) {
          triggerToast(completionToast, 'success');
        }

        // Add file to root directory if downloaded
        if (fileToInstall) {
          const fileObj = fileToInstall as { name: string; size: string };
          const fileExt = fileObj.name.split('.').pop() || 'zip';
          setFiles(current => {
            const rootItems = current['root'] || [];
            // Avoid duplicate additions
            if (rootItems.find(item => item.name === fileObj.name)) return current;

            const newItem: FileItem = {
              id: 'dld-' + Math.random().toString(36).substring(2, 9),
              name: fileObj.name,
              type: 'file',
              size: fileObj.size,
              updatedAt: new Date().toISOString().split('T')[0],
              extension: fileExt
            };
            return {
              ...current,
              'root': [newItem, ...rootItems]
            };
          });
        }

        return updated;
      });

    }, 2000);

    return () => clearInterval(interval);
  }, [services, tasks]);

  // Helper to trigger alert toast
  const triggerToast = (text: string, type: 'info' | 'success' | 'warn' = 'info') => {
    setToastMessage({ text, type });
    // Soundless physical feedback vibration API check
    if (navigator.vibrate) {
      navigator.vibrate(50);
    }
    setTimeout(() => {
      setToastMessage(null);
    }, 4500);
  };

  // 3. Format dynamic human-readable uptime
  const getFormattedUptime = () => {
    const days = Math.floor(uptimeSeconds / (3600 * 24));
    const hours = Math.floor((uptimeSeconds % (3600 * 24)) / 3600);
    const minutes = Math.floor((uptimeSeconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  // 4. File Manager Handlers
  const handleCreateFolder = (_path: string, folderName: string) => {
    triggerToast(`Folder creation is not exposed by the NAS API yet (${folderName})`, 'warn');
  };

  const handleUploadFile = async (_path: string, file: File) => {
    try {
      const result = await uploadFile(file);
      await refreshFiles();
      triggerToast(result.message, 'success');
    } catch (error) {
      triggerToast(error instanceof Error ? error.message : 'Upload failed', 'warn');
    }
  };

  const handleDeleteFile = async (path: string, fileId: string) => {
    const parentFiles = files[path] || [];
    const itemToDelete = parentFiles.find(f => f.id === fileId);
    if (!itemToDelete?.path) return;

    try {
      await deleteFile(itemToDelete.path);
      await refreshFiles(path === 'root' ? null : path);
      triggerToast(`Deleted "${itemToDelete.name}"`, 'info');
    } catch (error) {
      triggerToast(error instanceof Error ? error.message : 'Delete failed', 'warn');
    }
  };

  const handleDownloadFile = (file: FileItem) => {
    if (!file.path) {
      triggerToast(`Cannot download "${file.name}" without a NAS path`, 'warn');
      return;
    }
    downloadFile(file.path);
    triggerToast(`Downloading "${file.name}"`, 'info');
  };

  const handleOpenFolder = async (path: string) => {
    try {
      const data = await refreshFiles(path === 'root' ? null : path);
      return data.current;
    } catch (error) {
      triggerToast(error instanceof Error ? error.message : 'Unable to open folder', 'warn');
      return path;
    }
  };

  // 5. Service Switcheboard Handlers
  const handleToggleService = (serviceId: string) => {
    setServices(prev => prev.map(srv => {
      if (srv.id !== serviceId) return srv;
      
      if (srv.status === 'running') {
        triggerToast(`${srv.name} stopped`, 'warn');
        return {
          ...srv,
          status: 'stopped',
          uptime: undefined,
          cpuUsage: 0,
          ramUsage: 0
        };
      } else {
        triggerToast(`Starting ${srv.name}...`, 'info');
        
        // Transition immediately to starting
        setTimeout(() => {
          setServices(current => current.map(c => {
            if (c.id !== serviceId) return c;
            // Generate some random metrics
            const initialCpu = parseFloat((2.5 + Math.random() * 4).toFixed(1));
            const initialRam = Math.round(50 + Math.random() * 120);
            triggerToast(`${c.name} is now running online`, 'success');
            return {
              ...c,
              status: 'running',
              uptime: '0s',
              cpuUsage: initialCpu,
              ramUsage: initialRam
            };
          }));
        }, 1800);

        return {
          ...srv,
          status: 'starting'
        };
      }
    }));
  };

  // 6. Task Manager Handlers
  const handleAddTask = (link: string) => {
    // Generate a file name from link
    let filename = 'downloaded_package.zip';
    if (link.includes('ubuntu')) {
      filename = 'ubuntu-26.04-desktop-amd64.iso';
    } else if (link.includes('debian')) {
      filename = 'debian-netinst.iso';
    } else if (link.startsWith('magnet:')) {
      // Pick a simulated show
      filename = 'The_Matrix_4K_HDR.mkv';
    } else {
      const parts = link.split('/');
      const last = parts[parts.length - 1];
      if (last && last.includes('.')) filename = last;
    }

    const newTask: NasTask = {
      id: 'task-added-' + Math.random().toString(36).substring(2, 9),
      name: filename,
      type: 'download',
      progress: 0,
      speed: '25.6 MB/s',
      eta: '35s',
      status: 'active'
    };

    setTasks(prev => [newTask, ...prev]);
    triggerToast(`Added magnet download task: ${filename}`, 'info');
  };

  const handlePauseTask = (id: string) => {
    setTasks(prev => prev.map(t => {
      if (t.id !== id) return t;
      return { ...t, status: 'paused', speed: undefined, eta: undefined };
    }));
    triggerToast('Download paused', 'info');
  };

  const handleResumeTask = (id: string) => {
    setTasks(prev => prev.map(t => {
      if (t.id !== id) return t;
      return { ...t, status: 'active', speed: '20 MB/s', eta: 'Calculating...' };
    }));
    triggerToast('Download resumed', 'info');
  };

  const handleCancelTask = (id: string) => {
    const taskObj = tasks.find(t => t.id === id);
    setTasks(prev => prev.filter(t => t.id !== id));
    if (taskObj) {
      triggerToast(`Cancelled and deleted "${taskObj.name}"`, 'warn');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-0 md:p-6 select-none font-sans overflow-hidden">
      
      {/* Absolute Backdrop Graphics for immersive depth */}
      <div className="absolute top-[-10%] left-[-20%] w-[80%] h-[60%] bg-blue-900/15 rounded-full filter blur-[120px] pointer-events-none animate-pulse" style={{ animationDuration: '10s' }}></div>
      <div className="absolute bottom-[-10%] right-[-20%] w-[80%] h-[60%] bg-indigo-950/20 rounded-full filter blur-[120px] pointer-events-none animate-pulse" style={{ animationDuration: '15s' }}></div>

      {/* Responsive Smartphone Container Shell */}
      <div className="relative w-full max-w-md h-screen md:h-[860px] bg-slate-950 md:rounded-[48px] md:border-[10px] md:border-slate-800 md:shadow-2xl md:ring-4 md:ring-slate-900/40 overflow-hidden flex flex-col">
        
        {/* Notch / Speaker representation on desktop */}
        <div className="hidden md:block absolute top-0 left-1/2 transform -translate-x-1/2 w-36 h-6 bg-slate-800 rounded-b-2xl z-50">
          <div className="w-12 h-1.5 bg-slate-950 rounded-full mx-auto mt-1"></div>
        </div>

        {/* Live Notification Toast Overlay */}
        {toastMessage && (
          <div className="absolute top-16 left-4 right-4 z-50 animate-bounce">
            <div className={`p-3.5 rounded-2xl shadow-2xl flex items-center space-x-3 border text-xs font-semibold backdrop-blur-xl ${
              toastMessage.type === 'success' 
                ? 'bg-emerald-950/95 text-emerald-300 border-emerald-500/20 shadow-emerald-500/5' 
                : toastMessage.type === 'warn'
                ? 'bg-rose-950/95 text-rose-300 border-rose-500/20 shadow-rose-500/5'
                : 'bg-slate-900/95 text-blue-300 border-blue-500/20 shadow-blue-500/5'
            }`}>
              <div className="shrink-0">
                {toastMessage.type === 'success' ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : toastMessage.type === 'warn' ? (
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                ) : (
                  <Info className="w-4 h-4 text-blue-400" />
                )}
              </div>
              <p className="flex-1 leading-tight">{toastMessage.text}</p>
            </div>
          </div>
        )}

        {/* 1. Mobile Top Status Bar */}
        <div className="h-12 bg-slate-950 shrink-0 px-6 flex items-center justify-between text-[11px] font-semibold text-slate-300 z-40 select-none border-b border-slate-900/20">
          {/* Time */}
          <span className="font-bold tracking-tight text-slate-100">{currentTime.split(' ')[0]}</span>
          
          {/* Hardware status mini dots */}
          <div className="flex items-center space-x-1">
            <span className="text-[10px] font-mono text-blue-400/90 font-bold bg-blue-500/10 px-1.5 py-0.5 rounded leading-none">
              NAS {Math.round(stats.cpu)}%
            </span>
          </div>

          {/* Icons: Signal, WiFi, Battery */}
          <div className="flex items-center space-x-2">
            <Signal className="w-3.5 h-3.5 text-slate-300" />
            <span className="text-[9px] font-black">5G</span>
            <Wifi className="w-3.5 h-3.5 text-slate-300" />
            <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 px-1 py-0.5 rounded">
              <span className="text-[8px] font-mono leading-none">88%</span>
              <Battery className="w-3 h-3 text-emerald-400 fill-emerald-400/20" />
            </div>
          </div>
        </div>

        {/* 2. Interactive Navigation Drawer (Control Center Drawer) */}
        {isControlCenterOpen && (
          <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md z-40 flex flex-col justify-end">
            {/* Click outside to close */}
            <div className="flex-1" onClick={() => setIsControlCenterOpen(false)}></div>
            <div className="bg-slate-950 border-t border-slate-900 rounded-t-[32px] p-6 space-y-5 animate-slide-up max-h-[85%] overflow-y-auto">
              <div className="flex justify-between items-center pb-2 border-b border-slate-900">
                <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center">
                  <Sliders className="w-4 h-4 mr-2 text-blue-400" /> System Control Center
                </h4>
                <button 
                  onClick={() => setIsControlCenterOpen(false)}
                  className="text-xs bg-slate-900 border border-slate-800 px-3 py-1 rounded-full text-slate-400 hover:text-slate-200"
                >
                  Close
                </button>
              </div>

              {/* Server Information */}
              <div className="space-y-3">
                <div className="flex justify-between items-center text-xs bg-slate-900/40 p-3 rounded-xl border border-slate-900">
                  <span className="text-slate-400">Hardware Platform:</span>
                  <span className="font-mono text-slate-200">QNAP x64/Celeron</span>
                </div>
                <div className="flex justify-between items-center text-xs bg-slate-900/40 p-3 rounded-xl border border-slate-900">
                  <span className="text-slate-400">Internal Network IP:</span>
                  <span className="font-mono text-slate-200">192.168.1.100</span>
                </div>
                <div className="flex justify-between items-center text-xs bg-slate-900/40 p-3 rounded-xl border border-slate-900">
                  <span className="text-slate-400">UPS Battery Status:</span>
                  <span className="font-mono text-emerald-400 flex items-center">
                    <Shield className="w-3.5 h-3.5 mr-1" /> 100% (Online)
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs bg-slate-900/40 p-3 rounded-xl border border-slate-900">
                  <span className="text-slate-400">Cooling Fan Rate:</span>
                  <span className="font-mono text-slate-200 flex items-center">
                    <Fan className="w-3.5 h-3.5 mr-1 animate-spin text-slate-500" style={{ animationDuration: '3s' }} /> 1450 RPM
                  </span>
                </div>
              </div>

              {/* Danger Actions */}
              <div className="pt-2 grid grid-cols-2 gap-3">
                <button 
                  onClick={() => {
                    setIsControlCenterOpen(false);
                    triggerToast("Rebooting server... Web interface will reconnect in 45 seconds.", "warn");
                  }}
                  className="py-3 bg-slate-900 hover:bg-slate-850 rounded-xl text-xs font-semibold text-amber-400 border border-slate-800 flex items-center justify-center space-x-1.5 active:scale-95 transition"
                >
                  <Activity className="w-4 h-4" />
                  <span>Reboot Host</span>
                </button>
                <button 
                  onClick={() => {
                    setIsControlCenterOpen(false);
                    triggerToast("Shutting down host immediately... Connection lost.", "warn");
                  }}
                  className="py-3 bg-slate-900 hover:bg-slate-850 rounded-xl text-xs font-semibold text-rose-400 border border-slate-800 flex items-center justify-center space-x-1.5 active:scale-95 transition"
                >
                  <Power className="w-4 h-4" />
                  <span>Shut Down</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 3. Top Banner App Bar */}
        <div className="px-6 py-3.5 bg-slate-950 border-b border-slate-900 flex items-center justify-between shrink-0 z-10">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-blue-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <span className="font-black text-white text-xs tracking-wider">NAS</span>
            </div>
            <div>
              <h1 className="text-sm font-bold text-slate-100">Nexus NAS</h1>
              <p className="text-[9px] text-slate-500 font-medium">Remote Portal • 192.168.1.100</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Toggle system control drawer */}
            <button 
              onClick={() => setIsControlCenterOpen(!isControlCenterOpen)}
              className="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 flex items-center justify-center hover:text-white hover:bg-slate-850 active:scale-95 transition-all"
            >
              <Sliders className="w-4 h-4 text-slate-400" />
            </button>
            <button 
              onClick={() => triggerToast("System Logs: All security tokens are running healthy", 'info')}
              className="relative w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 flex items-center justify-center hover:text-white hover:bg-slate-850 active:scale-95 transition-all"
            >
              <Bell className="w-4 h-4 text-slate-400" />
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
            </button>
          </div>
        </div>

        {/* 4. Active Main View Screen Area (scrollable wrapper) */}
        <div className="flex-1 overflow-y-auto px-5 py-4 scrollbar-none pb-24">
          {activeTab === 'dashboard' && (
            <Dashboard stats={stats} uptime={getFormattedUptime()} />
          )}

          {activeTab === 'files' && (
            <FileExplorer 
              files={files}
              onCreateFolder={handleCreateFolder}
              onUploadFile={handleUploadFile}
              onDeleteFile={handleDeleteFile}
              onOpenFolder={handleOpenFolder}
              onDownloadFile={handleDownloadFile}
            />
          )}

          {activeTab === 'apps' && (
            <ServicesManager 
              services={services}
              onToggleService={handleToggleService}
            />
          )}

          {activeTab === 'tasks' && (
            <TaskList 
              tasks={tasks}
              onAddTask={handleAddTask}
              onPauseTask={handlePauseTask}
              onResumeTask={handleResumeTask}
              onCancelTask={handleCancelTask}
            />
          )}
        </div>

        {/* 5. Mobile Native Bottom Navigation Bar */}
        <div className="absolute bottom-4 inset-x-4 h-16 bg-slate-900/90 border border-slate-800/80 backdrop-blur-xl flex items-center justify-around px-2 z-35 rounded-2xl shadow-xl shadow-blue-950/40 select-none">
          {/* Dashboard */}
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`flex flex-col items-center justify-center w-16 h-12 rounded-xl transition ${
              activeTab === 'dashboard' ? 'text-blue-500' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <LayoutGrid className="w-5 h-5" />
            <span className="text-[9px] font-bold mt-1 tracking-tight">Overview</span>
          </button>

          {/* Files */}
          <button 
            onClick={() => setActiveTab('files')}
            className={`flex flex-col items-center justify-center w-16 h-12 rounded-xl transition ${
              activeTab === 'files' ? 'text-blue-500' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <FolderClosed className="w-5 h-5" />
            <span className="text-[9px] font-bold mt-1 tracking-tight">File Station</span>
          </button>

          {/* Services */}
          <button 
            onClick={() => setActiveTab('apps')}
            className={`flex flex-col items-center justify-center w-16 h-12 rounded-xl transition ${
              activeTab === 'apps' ? 'text-blue-500' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <Layers className="w-5 h-5" />
            <span className="text-[9px] font-bold mt-1 tracking-tight">App Center</span>
          </button>

          {/* Downloads / Tasks */}
          <button 
            onClick={() => setActiveTab('tasks')}
            className={`relative flex flex-col items-center justify-center w-16 h-12 rounded-xl transition ${
              activeTab === 'tasks' ? 'text-blue-500' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <DownloadCloud className="w-5 h-5" />
            <span className="text-[9px] font-bold mt-1 tracking-tight">Downloads</span>
            
            {/* Active task badge counter */}
            {tasks.filter(t => t.status === 'active').length > 0 && (
              <span className="absolute top-0.5 right-2 w-4 h-4 rounded-full bg-blue-650 border border-slate-950 flex items-center justify-center text-[8px] font-bold text-white font-mono scale-90">
                {tasks.filter(t => t.status === 'active').length}
              </span>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
