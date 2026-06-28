import React, { useState } from 'react';
import { 
  Play, 
  Square, 
  Cpu, 
  Activity, 
  Search, 
  ExternalLink,
  Cpu as CpuIcon,
  Layers,
  Settings
} from 'lucide-react';
import { NasService } from '../types';

interface ServicesManagerProps {
  services: NasService[];
  onToggleService: (serviceId: string) => void;
}

type FilterCategory = 'all' | 'media' | 'utility' | 'network' | 'system';

export default function ServicesManager({ services, onToggleService }: ServicesManagerProps) {
  const [activeTab, setActiveTab] = useState<FilterCategory>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [connectingServiceId, setConnectingServiceId] = useState<string | null>(null);

  const categories: { label: string; value: FilterCategory }[] = [
    { label: 'All', value: 'all' },
    { label: 'Media', value: 'media' },
    { label: 'Network', value: 'network' },
    { label: 'Utilities', value: 'utility' },
    { label: 'System', value: 'system' }
  ];

  const filteredServices = services.filter(service => {
    const matchesCategory = activeTab === 'all' || service.category === activeTab;
    const matchesSearch = service.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // Calculate container stats
  const runningCount = services.filter(s => s.status === 'running').length;
  const totalCpuUsage = services
    .filter(s => s.status === 'running')
    .reduce((sum, s) => sum + s.cpuUsage, 0);
  const totalRamUsage = services
    .filter(s => s.status === 'running')
    .reduce((sum, s) => sum + s.ramUsage, 0);

  const handleWebUiClick = (e: React.MouseEvent, serviceId: string) => {
    e.preventDefault();
    setConnectingServiceId(serviceId);
    setTimeout(() => {
      setConnectingServiceId(null);
    }, 1500);
  };

  return (
    <div className="space-y-4" id="nas-services-manager">
      {/* Services Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-100 text-lg">App Center</h3>
        <span className="text-xs bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-full text-slate-400 font-medium">
          Docker Engine Active
        </span>
      </div>

      {/* Resource summary for Docker containers */}
      <div className="grid grid-cols-3 gap-2.5 bg-slate-950/40 p-3 rounded-2xl border border-slate-900">
        <div className="text-center py-1">
          <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">Containers</p>
          <p className="text-lg font-bold text-slate-200 mt-0.5">{runningCount}/{services.length}</p>
        </div>
        <div className="text-center py-1 border-x border-slate-900">
          <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">Total CPU</p>
          <p className="text-lg font-bold text-blue-400 mt-0.5">{totalCpuUsage.toFixed(1)}%</p>
        </div>
        <div className="text-center py-1">
          <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">Total Memory</p>
          <p className="text-lg font-bold text-indigo-400 mt-0.5">{(totalRamUsage * 1024 * 0.12).toFixed(0)} MB</p>
        </div>
      </div>

      {/* Filter Category Tabs */}
      <div className="flex items-center space-x-1.5 overflow-x-auto py-1 scrollbar-none">
        {categories.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setActiveTab(cat.value)}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all duration-200 ${
              activeTab === cat.value
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/10'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-250 border border-slate-800/60'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Search Bar */}
      <div className="relative">
        <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <Search className="h-4 w-4 text-slate-500" />
        </span>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Filter applications..."
          className="w-full pl-9 pr-4 py-2 text-sm bg-slate-900/40 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-slate-750"
        />
      </div>

      {/* Services List */}
      <div className="space-y-3">
        {filteredServices.length === 0 ? (
          <div className="bg-slate-900/20 border border-slate-800/60 rounded-3xl p-8 text-center flex flex-col items-center justify-center">
            <Layers className="w-10 h-10 text-slate-700 mb-2 stroke-[1.5]" />
            <p className="text-xs text-slate-500">No applications match filter</p>
          </div>
        ) : (
          filteredServices.map((service) => (
            <div 
              key={service.id}
              className={`bg-slate-900/40 border transition-all duration-300 rounded-3xl p-4 space-y-3.5 ${
                service.status === 'running' 
                  ? 'border-slate-800/80 shadow-md' 
                  : 'border-slate-900/40 opacity-60'
              }`}
            >
              {/* Header: Name, Status, Switch */}
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-slate-100 text-sm leading-none">{service.name}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-bold leading-none ${
                      service.status === 'running'
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                        : service.status === 'starting'
                        ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20 animate-pulse'
                        : 'bg-slate-800 text-slate-500 border border-slate-700'
                    }`}>
                      {service.status.toUpperCase()}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 block mt-1.5">
                    Port: <span className="text-slate-400 font-medium">{service.port}</span> 
                    {service.status === 'running' && ` • Up: ${service.uptime}`}
                  </span>
                </div>

                {/* Switch Toggle */}
                <button
                  onClick={() => onToggleService(service.id)}
                  className={`w-11 h-6 rounded-full p-0.5 transition-colors duration-300 focus:outline-none ${
                    service.status === 'running' ? 'bg-emerald-500' : 'bg-slate-800 border border-slate-700'
                  }`}
                >
                  <div className={`bg-white w-5 h-5 rounded-full shadow-md transform duration-300 ${
                    service.status === 'running' ? 'translate-x-5' : 'translate-x-0'
                  }`}></div>
                </button>
              </div>

              {/* Resource Metrics & Action (if running) */}
              {service.status === 'running' && (
                <div className="flex items-center justify-between border-t border-slate-900/80 pt-3.5 text-xs text-slate-400">
                  <div className="flex space-x-4">
                    <div className="flex items-center space-x-1 font-mono">
                      <CpuIcon className="w-3.5 h-3.5 text-blue-400" />
                      <span>{service.cpuUsage}%</span>
                    </div>
                    <div className="flex items-center space-x-1 font-mono">
                      <Activity className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{service.ramUsage} MB</span>
                    </div>
                  </div>
                  
                  {/* Simulate Open WebUI link */}
                  <a 
                    href={`http://192.168.1.100:${service.port}`} 
                    target="_blank" 
                    rel="noreferrer"
                    onClick={(e) => handleWebUiClick(e, service.id)}
                    className="flex items-center space-x-1 text-blue-400 hover:text-blue-300 font-medium active:scale-95 transition"
                  >
                    <span>{connectingServiceId === service.id ? 'Connecting...' : 'Web UI'}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
