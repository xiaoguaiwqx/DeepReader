'use client';

import { useEffect, useState } from 'react';
import { Paper, PaperListResponse } from '@/types/paper';
import { PaperCard } from '@/components/PaperCard';

export default function Home() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);

  const fetchPapers = async () => {
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const res = await fetch(`${apiUrl}/papers?limit=20`);
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
      await fetch(`${apiUrl}/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category: 'cs.AI', days: 1 })
      });
      alert('Fetch job started in background. Refresh in a moment.');
    } catch (error) {
      alert('Failed to trigger job');
    } finally {
      setTriggering(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, []);

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
              onClick={fetchPapers}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Refresh
            </button>
            <button
              onClick={handleTrigger}
              disabled={triggering}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {triggering ? 'Fetching...' : 'Fetch New Papers'}
            </button>
          </div>
        </div>

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