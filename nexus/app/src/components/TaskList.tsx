// ✅ Fixed imports
  // ← now works after Step 1
import { useState, FormEvent } from 'react';
import {
  Download,
  Play,
  Pause,
  X,
  Plus,
  CheckCircle,
  AlertCircle,
  TrendingDown,
  TrendingUp,
  Clock,
  RefreshCw,    // ← replaces FolderSync if needed
  Heart,
  TaskListProps,
} from 'lucide-react';
import { NasTask } from '../types'; 

interface TaskListProps {
  tasks:          NasTask[];
  onAddTask:      (link: string) => void;
  onPauseTask:    (id: string) => void;
  onResumeTask:   (id: string) => void;
  onCancelTask:   (id: string) => void;
}

export default function TaskList({
  tasks,
  onAddTask,
  onPauseTask,
  onResumeTask,
  onCancelTask,
}: TaskListProps) {
  const [downloadLink, setDownloadLink] = useState('');
  const [isAddOpen, setIsAddOpen]       = useState(false);

  // ✅ FormEvent properly typed
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!downloadLink.trim()) return;
    onAddTask(downloadLink.trim());
    setDownloadLink('');
    setIsAddOpen(false);
  };

  // ✅ RefreshCw replaces FolderSync
  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'download': return <Download   className="w-5 h-5 text-blue-400" />;
      case 'backup':   return <CheckCircle className="w-5 h-5 text-emerald-400" />;
      case 'raid':     return <AlertCircle className="w-5 h-5 text-amber-400 animate-pulse" />;
      case 'sync':     return <RefreshCw   className="w-5 h-5 text-indigo-400" />;
      default:         return <Download   className="w-5 h-5 text-slate-400" />;
    }
  };
  return (
    <div className="space-y-4" id="nas-tasks-list">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-100 text-lg">Downloads & Tasks</h3>
        <button
          onClick={() => setIsAddOpen(true)}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold active:scale-95 transition shadow-lg shadow-blue-600/15"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Download</span>
        </button>
      </div>

      {/* Add Download Form Toggle */}
      {isAddOpen && (
        <form onSubmit={handleSubmit} className="bg-slate-950 border border-slate-850 p-4 rounded-3xl space-y-3 shadow-inner">
          <div className="flex justify-between items-center">
            <span className="text-xs font-semibold text-slate-300">Add Torrent / HTTP Download Link</span>
            <button 
              type="button" 
              onClick={() => setIsAddOpen(false)}
              className="text-slate-500 hover:text-slate-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-2">
            <input
              type="text"
              required
              value={downloadLink}
              onChange={(e) => setDownloadLink(e.target.value)}
              placeholder="Paste magnet:?xt=urn:... or http://..."
              className="w-full px-3.5 py-2.5 text-sm bg-slate-900 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-650 focus:outline-none focus:border-blue-500"
            />
            <div className="flex space-x-2 pt-1">
              <button
                type="button"
                onClick={() => setIsAddOpen(false)}
                className="flex-1 py-2 text-xs font-semibold text-slate-400 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-850 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 py-2 text-xs font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition shadow-lg shadow-blue-600/10"
              >
                Add Link
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Tasks Queue List */}
      <div className="space-y-3">
        {tasks.map((task) => (
          <div 
            key={task.id}
            className={`bg-slate-900/40 border rounded-3xl p-4 space-y-3 transition duration-300 ${
              task.status === 'active' ? 'border-slate-800/80' : 'border-slate-900/40 opacity-60'
            }`}
          >
            {/* Metadata Section */}
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3 pr-1">
                <div className="p-2 bg-slate-950 rounded-xl border border-slate-900 shrink-0">
                  {getTaskIcon(task.type)}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-slate-200 truncate leading-tight pr-1">{task.name}</p>
                  <div className="flex items-center space-x-2 mt-1.5 text-[10px] font-mono text-slate-500">
                    <span className="uppercase">{task.type}</span>
                    {task.speed && (
                      <>
                        <span>•</span>
                        <span className="text-slate-400 flex items-center">
                          <TrendingDown className="w-3 h-3 mr-0.5 text-blue-400" />
                          {task.speed}
                        </span>
                      </>
                    )}
                    {task.eta && (
                      <>
                        <span>•</span>
                        <span className="text-slate-400 flex items-center">
                          <Clock className="w-3 h-3 mr-0.5 text-indigo-400" />
                          {task.eta}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Task Controls */}
              {task.type === 'download' && (
                <div className="flex items-center space-x-1 shrink-0">
                  {task.status === 'active' ? (
                    <button
                      onClick={() => onPauseTask(task.id)}
                      className="p-1.5 text-slate-400 hover:text-amber-400 hover:bg-slate-800 rounded-lg active:scale-90 transition"
                      title="Pause"
                    >
                      <Pause className="w-4 h-4" />
                    </button>
                  ) : task.status === 'paused' ? (
                    <button
                      onClick={() => onResumeTask(task.id)}
                      className="p-1.5 text-slate-400 hover:text-emerald-400 hover:bg-slate-800 rounded-lg active:scale-90 transition"
                      title="Resume"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  ) : null}
                  <button
                    onClick={() => onCancelTask(task.id)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-slate-850 rounded-lg active:scale-90 transition"
                    title="Cancel"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>

            {/* Progress Gauge */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs font-mono font-semibold">
                <span className={task.status === 'completed' ? 'text-emerald-400' : 'text-slate-400'}>
                  {task.status === 'active' ? 'Downloading...' : task.status === 'paused' ? 'Paused' : task.status === 'completed' ? 'Completed' : 'Queued'}
                </span>
                <span className="text-slate-300">{Math.round(task.progress)}%</span>
              </div>
              <div className="w-full bg-slate-850 h-2 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${
                    task.status === 'completed' 
                      ? 'bg-emerald-500' 
                      : task.status === 'paused' 
                      ? 'bg-slate-600' 
                      : 'bg-gradient-to-r from-blue-500 to-indigo-500'
                  }`}
                  style={{ width: `${task.progress}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
