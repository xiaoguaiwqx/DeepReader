'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { Paper, PaperListResponse } from '@/types/paper';
import { PaperCard } from '@/components/PaperCard';

export default function Home() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [topic, setTopic] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [daysToFetch, setDaysToFetch] = useState('1');

  const buildParams = (overrides?: {
    topic?: string;
    startDate?: string;
    endDate?: string;
  }) => {
    const effective = {
      topic,
      startDate,
      endDate,
      ...overrides
    };

    const params = new URLSearchParams({ limit: '20' });
    if (effective.topic) params.set('topic', effective.topic);
    if (effective.startDate) params.set('start_date', effective.startDate);
    if (effective.endDate) params.set('end_date', effective.endDate);
    return params.toString();
  };

  const fetchPapers = async (overrides?: {
    topic?: string;
    startDate?: string;
    endDate?: string;
  }) => {
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const query = buildParams(overrides);
      const res = await fetch(`${apiUrl}/papers?${query}`);
      if (!res.ok) throw new Error('Failed to fetch data');
      const data: PaperListResponse = await res.json();
      setPapers(data.items);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrigger = async () => {
    setTriggering(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      
      // If user has set dates in the view, use them for fetching too
      const body: any = { 
        category: 'cs.AI OR cs.LG OR cs.CV OR cs.CL', 
        topic: topic || undefined
      };

      if (startDate && endDate) {
        body.start_date = startDate;
        body.end_date = endDate;
      } else {
        body.days = parseInt(daysToFetch) || 1;
      }

      const res = await fetch(`${apiUrl}/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      alert(data.message || 'Fetch job started in background.');
    } catch (error) {
      alert('Failed to trigger job');
    } finally {
      setTriggering(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, []);

  const handleApplyFilters = (event: FormEvent) => {
    event.preventDefault();
    fetchPapers();
  };

  const handleClearFilters = () => {
    setTopic('');
    setStartDate('');
    setEndDate('');
    setDaysToFetch('1');
    fetchPapers({ topic: '', startDate: '', endDate: '' });
  };

  return (
    <main className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900">DeepReader</h1>
            <p className="mt-2 text-sm text-gray-600">
              AI-Powered Research Assistant & Knowledge Manager
            </p>
          </div>
          <div className="flex gap-2">
             <button
              onClick={() => fetchPapers()}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Refresh View
            </button>
            <button
              onClick={handleTrigger}
              disabled={triggering}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {triggering ? 'Triggering...' : 'Fetch & Analyze New Papers'}
            </button>
          </div>
        </div>

        <form
          onSubmit={handleApplyFilters}
          className="bg-white border border-gray-200 rounded-lg p-4 mb-6 shadow-sm"
        >
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Topic / Keyword (Search & Fetch)
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., MLLM, RAG, diffusion"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date (View)</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date (View)</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Days to Fetch</label>
              <input
                type="number"
                min="1"
                max="30"
                value={daysToFetch}
                onChange={(e) => setDaysToFetch(e.target.value)}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              />
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="submit"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Apply Filters
            </button>
            <button
              type="button"
              onClick={handleClearFilters}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Clear
            </button>
          </div>
        </form>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : (
          <div className="space-y-6">
            {papers.length === 0 ? (
              <p className="text-center text-gray-500">No papers found. Try triggering a fetch.</p>
            ) : (
              papers.map((paper) => (
                <PaperCard key={paper.arxiv_id} paper={paper} />
              ))
            )}
          </div>
        )}
      </div>
    </main>
  );
}