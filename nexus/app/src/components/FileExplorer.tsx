import React, { useState } from 'react';
import { 
  Folder, 
  File, 
  ChevronRight, 
  ArrowLeft, 
  Plus, 
  Search, 
  Trash2, 
  Download, 
  FileText, 
  Image, 
  Video, 
  Music, 
  X,
  Upload
} from 'lucide-react';
import { FileItem } from '../types';

interface FileExplorerProps {
  files: Record<string, FileItem[]>; // Map of path -> files
  onCreateFolder: (path: string, folderName: string) => void;
  onUploadFile: (path: string, fileName: string, size: string) => void;
  onDeleteFile: (path: string, fileId: string) => void;
  onDownloadFile: (file: FileItem) => void;
}

export default function FileExplorer({ 
  files, 
  onCreateFolder, 
  onUploadFile, 
  onDeleteFile, 
  onDownloadFile 
}: FileExplorerProps) {
  const [currentPath, setCurrentPath] = useState<string>('root');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [uploadFileName, setUploadFileName] = useState('');
  const [uploadFileSize, setUploadFileSize] = useState('14.2 MB');

  // Breadcrumbs parsing
  const getBreadcrumbs = () => {
    if (currentPath === 'root') return [{ label: 'NAS Storage', path: 'root' }];
    const parts = currentPath.split('/');
    const crumbs = [{ label: 'NAS Storage', path: 'root' }];
    let accum = '';
    parts.forEach((part) => {
      accum = accum ? `${accum}/${part}` : part;
      crumbs.push({ label: part, path: accum });
    });
    return crumbs;
  };

  const handleNavigate = (path: string) => {
    setCurrentPath(path);
    setSearchQuery('');
  };

  const currentFiles = files[currentPath] || [];

  const filteredFiles = currentFiles.filter(f => 
    f.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateFolderSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFolderName.trim()) return;
    onCreateFolder(currentPath, newFolderName.trim());
    setNewFolderName('');
    setIsCreateModalOpen(false);
  };

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFileName.trim()) return;
    // Add extension if missing
    let finalName = uploadFileName.trim();
    if (!finalName.includes('.')) {
      finalName += '.zip';
    }
    onUploadFile(currentPath, finalName, uploadFileSize);
    setUploadFileName('');
    setIsUploadModalOpen(false);
  };

  // Get matching icons for file extensions
  const getFileIcon = (file: FileItem) => {
    if (file.type === 'folder') {
      return <Folder className="w-5 h-5 text-amber-400 fill-amber-400/20" />;
    }
    
    const ext = file.extension?.toLowerCase() || '';
    if (['mp4', 'mkv', 'mov'].includes(ext)) {
      return <Video className="w-5 h-5 text-indigo-400" />;
    }
    if (['mp3', 'wav', 'flac'].includes(ext)) {
      return <Music className="w-5 h-5 text-emerald-400" />;
    }
    if (['jpg', 'png', 'svg', 'gif'].includes(ext)) {
      return <Image className="w-5 h-5 text-pink-400" />;
    }
    if (['pdf', 'docx', 'txt', 'json'].includes(ext)) {
      return <FileText className="w-5 h-5 text-sky-400" />;
    }
    return <File className="w-5 h-5 text-zinc-400" />;
  };

  return (
    <div className="space-y-4" id="nas-file-explorer">
      {/* Header and Toolbar */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-100 text-lg">File Station</h3>
        <div className="flex space-x-2">
          {/* Create Folder Trigger */}
          <button 
            onClick={() => setIsCreateModalOpen(true)}
            className="w-9 h-9 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300 flex items-center justify-center hover:bg-slate-800 active:scale-95 transition-all"
            title="New Folder"
          >
            <Plus className="w-4 h-4" />
          </button>
          {/* Upload File Trigger */}
          <button 
            onClick={() => setIsUploadModalOpen(true)}
            className="w-9 h-9 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300 flex items-center justify-center hover:bg-slate-800 active:scale-95 transition-all"
            title="Upload File"
          >
            <Upload className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search Input */}
      <div className="relative">
        <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <Search className="h-4 w-4 text-slate-500" />
        </span>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search files and folders..."
          className="w-full pl-9 pr-4 py-2 text-sm bg-slate-900/40 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-slate-700"
        />
      </div>

      {/* Navigation Breadcrumbs */}
      <div className="flex items-center space-x-1.5 overflow-x-auto py-1 scrollbar-none text-xs">
        {currentPath !== 'root' && (
          <button 
            onClick={() => {
              const parts = currentPath.split('/');
              parts.pop();
              setCurrentPath(parts.length ? parts.join('/') : 'root');
            }}
            className="p-1 rounded-md bg-slate-900 border border-slate-800 text-slate-400 mr-1 active:scale-95 transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
          </button>
        )}
        {getBreadcrumbs().map((crumb, idx) => (
          <React.Fragment key={crumb.path}>
            {idx > 0 && <ChevronRight className="w-3 h-3 text-slate-600 shrink-0" />}
            <button
              onClick={() => handleNavigate(crumb.path)}
              className={`hover:text-slate-250 truncate max-w-[120px] font-medium transition ${
                idx === getBreadcrumbs().length - 1 ? 'text-slate-100' : 'text-slate-500'
              }`}
            >
              {crumb.label === 'root' ? 'Storage' : crumb.label}
            </button>
          </React.Fragment>
        ))}
      </div>

      {/* Files List */}
      <div className="bg-slate-900/20 border border-slate-800/60 rounded-3xl overflow-hidden min-h-[300px] flex flex-col">
        {filteredFiles.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
            <Folder className="w-12 h-12 text-slate-700 mb-2 stroke-[1.5]" />
            <p className="text-sm text-slate-400 font-medium">No items found</p>
            <p className="text-xs text-slate-600 mt-1">This directory is empty or matchless</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-900/60">
            {filteredFiles.map((file) => (
              <div 
                key={file.id} 
                className="flex items-center justify-between p-3.5 hover:bg-slate-900/40 transition active:bg-slate-900/20"
              >
                {/* File Click Handler */}
                <div 
                  onClick={() => file.type === 'folder' ? handleNavigate(currentPath === 'root' ? file.name : `${currentPath}/${file.name}`) : null}
                  className={`flex items-center space-x-3 flex-1 min-w-0 ${file.type === 'folder' ? 'cursor-pointer' : ''}`}
                >
                  <div className="shrink-0">{getFileIcon(file)}</div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-slate-200 truncate">{file.name}</p>
                    <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                      {file.type === 'folder' ? 'Folder' : file.size} • {file.updatedAt}
                    </p>
                  </div>
                </div>

                {/* Operations Toolbar */}
                <div className="flex items-center space-x-1.5 ml-2">
                  {file.type === 'file' && (
                    <button
                      onClick={() => onDownloadFile(file)}
                      className="p-2 text-slate-450 hover:text-emerald-450 hover:bg-slate-800/40 rounded-lg active:scale-90 transition"
                      title="Download"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => onDeleteFile(currentPath, file.id)}
                    className="p-2 text-slate-500 hover:text-rose-450 hover:bg-slate-800/40 rounded-lg active:scale-90 transition"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Folder Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-950 border border-slate-800 rounded-3xl w-full max-w-sm overflow-hidden shadow-2xl">
            <div className="px-4 py-3 border-b border-slate-900 flex justify-between items-center bg-slate-900/40">
              <span className="font-semibold text-slate-200 text-sm">Create Folder</span>
              <button onClick={() => setIsCreateModalOpen(false)} className="text-slate-500 hover:text-slate-300">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleCreateFolderSubmit} className="p-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Folder Name</label>
                <input
                  type="text"
                  required
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="e.g., Photos, Movies, Temp"
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 text-sm"
                  autoFocus
                />
              </div>
              <div className="flex space-x-2 pt-1">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="flex-1 py-2 text-sm font-medium text-slate-400 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-850 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition shadow-lg shadow-blue-600/10"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Upload File Modal */}
      {isUploadModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-950 border border-slate-800 rounded-3xl w-full max-w-sm overflow-hidden shadow-2xl">
            <div className="px-4 py-3 border-b border-slate-900 flex justify-between items-center bg-slate-900/40">
              <span className="font-semibold text-slate-200 text-sm">Upload File Simulator</span>
              <button onClick={() => setIsUploadModalOpen(false)} className="text-slate-500 hover:text-slate-300">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleUploadSubmit} className="p-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">File Name</label>
                <input
                  type="text"
                  required
                  value={uploadFileName}
                  onChange={(e) => setUploadFileName(e.target.value)}
                  placeholder="e.g., invoice.pdf, avatar.png"
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 text-sm"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">File Size Preset</label>
                <select
                  value={uploadFileSize}
                  onChange={(e) => setUploadFileSize(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-200 focus:outline-none focus:border-blue-500 text-sm"
                >
                  <option value="1.2 MB">Small document (1.2 MB)</option>
                  <option value="14.5 MB">High-Res Photo (14.5 MB)</option>
                  <option value="320 MB">Home Video (320 MB)</option>
                  <option value="1.4 GB">Full HD Movie (1.4 GB)</option>
                </select>
              </div>
              <div className="flex space-x-2 pt-1">
                <button
                  type="button"
                  onClick={() => setIsUploadModalOpen(false)}
                  className="flex-1 py-2 text-sm font-medium text-slate-400 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-850 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-500 transition shadow-lg shadow-blue-600/10"
                >
                  Upload File
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
