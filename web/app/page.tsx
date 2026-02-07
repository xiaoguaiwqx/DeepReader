'use client';

import { useEffect, useState } from 'react';
import { Paper } from '@/types/paper';
import { paperService } from '@/services/paperService';
import { BrowseFilterBar } from '@/components/features/BrowseFilterBar';
import { FetchPanel } from '@/components/features/FetchPanel';
import { PaperList } from '@/components/features/PaperList';
import { Pagination } from '@/components/common/Pagination';
import { useJobPolling } from '@/hooks/useJobPolling';
import { JobStatusBanner } from '@/components/features/JobStatusBanner';
import { Toaster } from 'react-hot-toast';

export default function Home() {
  // Browsing State
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const LIMIT = 20;
  
  // Filter State
  const [topic, setTopic] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Job Polling State
  const { jobId, setJobId, jobStatus } = useJobPolling();

  const fetchPapers = async (currentOffset: number = offset) => {
    setLoading(true);
    try {
      const data = await paperService.getPapers({
        topic: topic || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        limit: LIMIT,
        offset: currentOffset
      });
      setPapers(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load papers:', error);
      // In Phase 4 we will add a Toast here
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, [offset]); // Re-fetch when offset changes

  // Auto-refresh when job completes
  useEffect(() => {
    if (jobStatus?.status === 'completed') {
      fetchPapers(0);
      setOffset(0);
    }
  }, [jobStatus?.status]);

  // Reset offset when applying new filters
  const handleApplyFilters = () => {
    setOffset(0);
    fetchPapers(0);
  };

  const handleClearFilters = () => {
    setTopic('');
    setStartDate('');
    setEndDate('');
    setOffset(0);
    // Explicitly call fetch with default params to avoid stale state issues
    setLoading(true);
    paperService.getPapers({ limit: LIMIT, offset: 0 })
      .then(data => {
        setPapers(data.items);
        setTotal(data.total);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <span className="text-indigo-600">Deep</span>Reader
              </h1>
            </div>
            <div>
              <button
                onClick={() => fetchPapers(offset)}
                className="text-sm text-gray-500 hover:text-indigo-600 font-medium"
              >
                Refresh List
              </button>
            </div>
          </div>
        </div>
        {/* Job Status Banner placed immediately under header */}
        <JobStatusBanner status={jobStatus} />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Main Content Area */}
        <div className="flex flex-col gap-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
            <div>
              <h2 className="text-lg font-medium text-gray-900">Your Library</h2>
              <p className="text-sm text-gray-500">Browse and manage your collected papers.</p>
            </div>
          </div>

          <BrowseFilterBar
            topic={topic}
            startDate={startDate}
            endDate={endDate}
            onTopicChange={setTopic}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
            onApply={handleApplyFilters}
            onClear={handleClearFilters}
          />

          <PaperList 
            papers={papers} 
            loading={loading} 
            total={total}
          />

          <Pagination
            total={total}
            limit={LIMIT}
            offset={offset}
            onPageChange={setOffset}
          />
        </div>
      </div>

      {/* Floating Fetch Panel (Sidebar) */}
      <FetchPanel onJobStarted={setJobId} />
    </main>
  );
}
