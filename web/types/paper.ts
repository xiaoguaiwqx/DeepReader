export interface Paper {
  arxiv_id: string;
  title: string;
  authors: string[];
  summary: string;
  published_date: string;
  updated_date: string;
  primary_category: string;
  categories: string[];
  pdf_url?: string;
  llm_summary?: string;
  key_insights?: string;
}

export interface PaperListResponse {
  items: Paper[];
  total: number;
  limit: number;
  offset: number;
}
