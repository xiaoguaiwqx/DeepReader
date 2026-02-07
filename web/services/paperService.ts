import { Paper, PaperListResponse } from '@/types/paper';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://10.102.136.54:8000/api';

export interface FetchPapersParams {
  limit?: number;
  offset?: number;
  topic?: string;
  start_date?: string;
  end_date?: string;
}

export interface TriggerFetchParams {
  category?: string;
  days?: number;
  topic?: string;
  query?: string;
  start_date?: string;
  end_date?: string;
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  processed: number;
  total: number;
  new_papers: number;
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface StatsResponse {
  total: number;
  last_fetch_time: string | null;
  categories: Record<string, number>;
  with_summary: number;
  without_summary: number;
}

export interface CategoriesResponse {
  categories: string[];
}

export const paperService = {
  async getPapers(params: FetchPapersParams): Promise<PaperListResponse> {
    const query = new URLSearchParams();
    if (params.limit) query.set('limit', params.limit.toString());
    if (params.offset) query.set('offset', params.offset.toString());
    if (params.topic) query.set('topic', params.topic);
    if (params.start_date) query.set('start_date', params.start_date);
    if (params.end_date) query.set('end_date', params.end_date);

    const res = await fetch(`${API_URL}/papers?${query.toString()}`);
    if (!res.ok) {
      throw new Error(`Failed to fetch papers: ${res.statusText}`);
    }
    return res.json();
  },

  async triggerFetch(params: TriggerFetchParams): Promise<{ status: string; job_id: string; message: string }> {
    const res = await fetch(`${API_URL}/trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.message || `Failed to trigger fetch: ${res.statusText}`);
    }
    return res.json();
  },

  async getJobStatus(jobId: string): Promise<JobStatus> {
    const res = await fetch(`${API_URL}/jobs/${jobId}`);
    if (!res.ok) {
      throw new Error(`Failed to get job status: ${res.statusText}`);
    }
    return res.json();
  },

  async getStats(): Promise<StatsResponse> {
    const res = await fetch(`${API_URL}/stats`);
    if (!res.ok) {
      throw new Error(`Failed to get stats: ${res.statusText}`);
    }
    return res.json();
  },

  async getCategories(): Promise<CategoriesResponse> {
    const res = await fetch(`${API_URL}/categories`);
    if (!res.ok) {
      throw new Error(`Failed to get categories: ${res.statusText}`);
    }
    return res.json();
  }
};
