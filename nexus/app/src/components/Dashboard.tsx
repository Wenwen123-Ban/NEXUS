import React from 'react';
import { 
  Cpu, 
  HardDrive, 
  Activity, 
  ArrowUp, 
  ArrowDown, 
  Thermometer, 
  Server, 
  CheckCircle2, 
  AlertTriangle 
} from 'lucide-react';
import { SystemStats } from '../types';

interface DashboardProps {
  stats: SystemStats;
  uptime: string;
}

export default function Dashboard({ stats, uptime }: DashboardProps) {
  // Calculate total used and total capacity across all disks
  const totalUsed = stats.disks.reduce((acc, disk) => acc + disk.used, 0);
  const totalCap = stats.disks.reduce((acc, disk) => acc + disk.total, 0);
  const storagePercentage = totalCap > 0 ? Math.round((totalUsed / totalCap) * 100) : 0;

  // Format network speeds for humans
  const formatSpeed = (kbps: number) => {
    if (kbps > 1024) {
      return `${(kbps / 1024).toFixed(1)} MB/s`;
    }
    return `${kbps.toFixed(0)} KB/s`;
  };

  return (
    <div className="space-y-6" id="nas-dashboard">
      {/* System Status Banner */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-4 flex items-center justify-between shadow-lg backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
            <Server className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-sm">{stats.serverName || 'NAS-Server-01'}</h3>
            <p className="text-xs text-slate-400">{stats.platform || 'NAS'} • Uptime: {uptime}</p>
          </div>
        </div>
        <div className="flex items-center space-x-1.5 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-xs font-medium text-emerald-400">Healthy</span>
        </div>
      </div>

      {/* Main Grid: CPU, RAM, Temp, Network */}
      <div className="grid grid-cols-2 gap-3">
        {/* CPU Panel */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-4 flex flex-col justify-between h-32 hover:border-slate-700/60 transition-all duration-300 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">CPU Load</span>
            <Cpu className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-2">
            <span className="text-3xl font-bold text-slate-100 tracking-tight">{Math.round(stats.cpu)}%</span>
            <div className="w-full bg-slate-850 h-1.5 rounded-full mt-2 overflow-hidden">
              <div 
                className="bg-blue-400 h-full rounded-full transition-all duration-1000"
                style={{ width: `${stats.cpu}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* RAM Panel */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-4 flex flex-col justify-between h-32 hover:border-slate-700/60 transition-all duration-300 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">RAM Usage</span>
            <Activity className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2">
            <span className="text-3xl font-bold text-slate-100 tracking-tight">{Math.round(stats.ram)}%</span>
            <div className="w-full bg-slate-850 h-1.5 rounded-full mt-2 overflow-hidden">
              <div 
                className="bg-indigo-400 h-full rounded-full transition-all duration-1000"
                style={{ width: `${stats.ram}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Temp Panel */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-4 flex flex-col justify-between h-32 hover:border-slate-700/60 transition-all duration-300 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">System Temp</span>
            <Thermometer className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2">
            <span className="text-3xl font-bold text-slate-100 tracking-tight">{stats.temp}°C</span>
            <div className="w-full bg-slate-850 h-1.5 rounded-full mt-2 overflow-hidden">
              <div 
                className="bg-amber-400 h-full rounded-full transition-all duration-1000"
                style={{ width: `${Math.min((stats.temp / 85) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Live Network Rates */}
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-4 flex flex-col justify-between h-32 hover:border-slate-700/60 transition-all duration-300 shadow-sm">
          <span className="text-xs font-medium text-slate-400">Network Rates</span>
          <div className="space-y-1.5 mt-2">
            <div className="flex items-center justify-between text-xs text-emerald-400 font-mono">
              <span className="flex items-center"><ArrowDown className="w-3.5 h-3.5 mr-0.5" /> DL</span>
              <span className="font-semibold">{formatSpeed(stats.networkDown)}</span>
            </div>
            <div className="flex items-center justify-between text-xs text-blue-400 font-mono">
              <span className="flex items-center"><ArrowUp className="w-3.5 h-3.5 mr-0.5" /> UL</span>
              <span className="font-semibold">{formatSpeed(stats.networkUp)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Storage Pools */}
      <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-4 space-y-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold text-slate-200 flex items-center">
            <HardDrive className="w-4 h-4 mr-2 text-blue-400" /> Storage Pools
          </h4>
          <span className="text-xs text-slate-400 font-medium">RAID-5 Array</span>
        </div>

        {/* Combined Storage Gauge */}
        <div className="space-y-2">
          <div className="flex justify-between items-baseline">
            <span className="text-2xl font-bold text-slate-100">{storagePercentage}% <span className="text-xs text-slate-400 font-normal">used</span></span>
            <span className="text-xs font-mono text-slate-300">
              {totalUsed.toLocaleString()} GB / {totalCap.toLocaleString()} GB
            </span>
          </div>
          <div className="w-full bg-slate-850 h-3 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-1000 ${
                storagePercentage > 85 ? 'bg-rose-500' : storagePercentage > 70 ? 'bg-amber-400' : 'bg-blue-500'
              }`}
              style={{ width: `${storagePercentage}%` }}
            ></div>
          </div>
        </div>

        {/* Drive Health List */}
        <div className="border-t border-slate-800/60 pt-3 mt-3 space-y-2.5">
          <span className="text-xs font-medium text-slate-400">Physical Disks</span>
          {stats.disks.map((disk, idx) => (
            <div key={idx} className="flex items-center justify-between text-xs bg-slate-950/45 p-2.5 rounded-xl border border-slate-900">
              <div className="flex items-center space-x-2">
                {disk.status === 'healthy' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                )}
                <span className="font-medium text-slate-300">{disk.name}</span>
                <span className="text-[10px] text-slate-500 font-mono">{(disk.total / 1024).toFixed(1)} TB</span>
              </div>
              <div className="flex items-center space-x-3 font-mono text-slate-400">
                <span>{disk.total > 0 ? Math.round((disk.used / disk.total) * 100) : 0}% full</span>
                <span className="flex items-center text-slate-400 border-l border-slate-800 pl-2.5">
                  <Thermometer className="w-3 h-3 text-amber-500/80 mr-0.5" />
                  {disk.temp}°C
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
