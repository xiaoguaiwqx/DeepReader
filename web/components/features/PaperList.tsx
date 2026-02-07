import React from 'react';
import { Paper } from '@/types/paper';
import { PaperCard } from '@/components/PaperCard';

interface PaperListProps {
  papers: Paper[];
  loading: boolean;
  total: number;
}

export function PaperList({ papers, loading, total }: PaperListProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow-md border border-gray-200 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          </div>
        ))}
      </div>
    );
  }

  if (papers.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg border border-gray-200 border-dashed">
        <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No papers found</h3>
        <p className="mt-1 text-sm text-gray-500">Try adjusting your filters or fetch new papers from ArXiv.</p>
      </div>
    );
  }

  return (
    <div>
       <div className="mb-4 text-sm text-gray-500 flex justify-between items-center">
        <span>Found {total} papers</span>
      </div>
      <div className="space-y-6">
        {papers.map((paper) => (
          <PaperCard key={paper.arxiv_id} paper={paper} />
        ))}
      </div>
    </div>
  );
}
