import { useState, useEffect, useRef } from 'react';
import { paperService, JobStatus } from '@/services/paperService';
import toast from 'react-hot-toast';

export function useJobPolling(initialJobId?: string | null) {
  const [jobId, setJobId] = useState<string | null>(initialJobId || null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const pollInterval = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!jobId) {
      setJobStatus(null);
      return;
    }

    const fetchStatus = async () => {
      try {
        const status = await paperService.getJobStatus(jobId);
        setJobStatus(status);

        if (status.status === 'completed' || status.status === 'failed') {
          if (pollInterval.current) {
            clearInterval(pollInterval.current);
            pollInterval.current = null;
          }
          if (status.status === 'completed') {
            toast.success(`Job completed! ${status.new_papers} new papers found.`);
          } else {
            toast.error(`Job failed: ${status.error}`);
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    // Initial fetch
    fetchStatus();

    // Start polling
    pollInterval.current = setInterval(fetchStatus, 2000);

    return () => {
      if (pollInterval.current) {
        clearInterval(pollInterval.current);
      }
    };
  }, [jobId]);

  return { jobId, setJobId, jobStatus };
}
