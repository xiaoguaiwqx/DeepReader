import React from 'react';
import { JobStatus } from '@/services/paperService';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

interface JobStatusBannerProps {
  status: JobStatus | null;
}

export function JobStatusBanner({ status }: JobStatusBannerProps) {
  if (!status) return null;

  if (status.status === 'completed') {
    // We might not want to show a permanent banner for completion if we use Toast,
    // but a small temporary one or auto-dismiss logic is good. 
    // For now, let's show it if it's recent, but maybe the parent clears it.
    // Actually, let's focus on "Running" state mainly.
    return null; 
  }

  if (status.status === 'failed') {
    return (
      <div className="bg-red-50 border-b border-red-200 p-4">
        <div className="flex items-center justify-center gap-2 text-red-700 text-sm">
          <XCircle className="h-4 w-4" />
          <span>Job Failed: {status.error}</span>
        </div>
      </div>
    );
  }

  const progress = status.total > 0 ? Math.round((status.processed / status.total) * 100) : 0;

  return (
    <div className="bg-indigo-600 text-white p-3 shadow-md transition-all duration-500 ease-in-out">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-indigo-200" />
          <div className="flex flex-col">
            <span className="font-medium text-sm">Fetching & Analyzing Papers...</span>
            <span className="text-xs text-indigo-200">
              Processed {status.processed} of {status.total} papers ({status.new_papers} new)
            </span>
          </div>
        </div>
        
        <div className="w-full sm:w-64 bg-indigo-800 rounded-full h-2.5 overflow-hidden">
          <div 
            className="bg-white h-2.5 rounded-full transition-all duration-500 ease-out" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
