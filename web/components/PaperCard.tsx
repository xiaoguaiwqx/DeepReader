import React from 'react';
import { Paper } from '@/types/paper';

interface PaperCardProps {
  paper: Paper;
}

export const PaperCard: React.FC<PaperCardProps> = ({ paper }) => {
  return (
    <div className="bg-white shadow-md rounded-lg p-6 mb-4 border border-gray-200 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            <a href={paper.pdf_url || '#'} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600 hover:underline">
              {paper.title}
            </a>
          </h2>
          <p className="text-sm text-gray-600 mb-2">
            {paper.authors.join(', ')} • {new Date(paper.published_date).toLocaleDateString()}
          </p>
          <div className="flex flex-wrap gap-2 mb-3">
            <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
              {paper.primary_category}
            </span>
            {paper.categories.filter(c => c !== paper.primary_category).map(cat => (
              <span key={cat} className="bg-gray-100 text-gray-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                {cat}
              </span>
            ))}
          </div>
        </div>
      </div>

      {paper.llm_summary ? (
        <div className="mt-4 bg-indigo-50 p-4 rounded-md border-l-4 border-indigo-500">
          <h3 className="text-sm font-bold text-indigo-900 mb-1">AI Insight</h3>
          <p className="text-gray-700 text-sm whitespace-pre-line leading-relaxed">
            {paper.llm_summary}
          </p>
        </div>
      ) : (
        <div className="mt-4">
           <h3 className="text-sm font-bold text-gray-700 mb-1">Abstract</h3>
           <p className="text-gray-600 text-sm line-clamp-3">
            {paper.summary}
          </p>
        </div>
      )}
    </div>
  );
};
