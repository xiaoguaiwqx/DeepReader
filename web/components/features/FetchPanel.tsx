import React, { useState, useEffect } from 'react';
import { paperService, TriggerFetchParams } from '@/services/paperService';
import toast from 'react-hot-toast';

interface FetchPanelProps {
  onJobStarted: (jobId: string) => void;
}

export function FetchPanel({ onJobStarted }: FetchPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Data State
  const [availableCategories, setAvailableCategories] = useState<string[]>([]);

  // Form State
  const [category, setCategory] = useState('cs.AI OR cs.LG OR cs.CV OR cs.CL');
  const [topic, setTopic] = useState('');
  const [mode, setMode] = useState<'days' | 'range'>('days');
  const [days, setDays] = useState('1');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    // Load categories on mount
    paperService.getCategories()
      .then(res => setAvailableCategories(res.categories))
      .catch(err => console.error('Failed to load categories', err));
  }, []);

  const handleTrigger = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const params: TriggerFetchParams = {
        category,
        topic: topic || undefined,
      };

      if (mode === 'days') {
        params.days = parseInt(days) || 1;
      } else {
        if (!startDate || !endDate) {
          toast.error('Please select both start and end dates.');
          setLoading(false);
          return;
        }
        params.start_date = startDate;
        params.end_date = endDate;
      }

      const res = await paperService.triggerFetch(params);
      toast.success(res.message);
      onJobStarted(res.job_id);
      setIsOpen(false);
    } catch (error: any) {
      console.error(error);
      toast.error(error.message || 'Failed to trigger fetch job.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 inline-flex items-center p-4 border border-transparent rounded-full shadow-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 z-50"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        Fetch New Papers
      </button>
    );
  }

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white shadow-xl border-l border-gray-200 transform transition-transform duration-300 ease-in-out z-50 overflow-y-auto">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">Fetch from ArXiv</h2>
          <button
            onClick={() => setIsOpen(false)}
            className="text-gray-400 hover:text-gray-500"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleTrigger} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ArXiv Categories
            </label>
            <div className="relative">
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
                placeholder="e.g. cs.AI OR cs.LG"
                list="category-suggestions"
              />
              <datalist id="category-suggestions">
                {availableCategories.map(cat => (
                  <option key={cat} value={cat} />
                ))}
              </datalist>
            </div>
            <p className="mt-1 text-xs text-gray-500">Separated by OR/AND. Use dropdown for suggestions.</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Topic / Keyword Filter
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              placeholder="e.g. LLM, RAG (Optional)"
            />
          </div>

          <div className="border-t border-gray-200 pt-4">
            <span className="block text-sm font-medium text-gray-700 mb-2">Time Range</span>
            
            <div className="flex items-center space-x-4 mb-4">
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  checked={mode === 'days'}
                  onChange={() => setMode('days')}
                  className="form-radio text-indigo-600"
                />
                <span className="ml-2 text-sm text-gray-700">Recent Days</span>
              </label>
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  checked={mode === 'range'}
                  onChange={() => setMode('range')}
                  className="form-radio text-indigo-600"
                />
                <span className="ml-2 text-sm text-gray-700">Specific Date</span>
              </label>
            </div>

            {mode === 'days' ? (
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Days to fetch</label>
                <input
                  type="number"
                  min="1"
                  max="30"
                  value={days}
                  onChange={(e) => setDays(e.target.value)}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
                />
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">From</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">To</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
                  />
                </div>
              </div>
            )}
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Triggering Job...
                </>
              ) : (
                'Start Fetch Job'
              )}
            </button>
            <p className="mt-2 text-xs text-gray-500 text-center">
              This will start a background task. You may need to refresh the list later.
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

