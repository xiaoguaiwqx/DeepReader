import arxiv
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from deep_reader.models import Paper

class ArxivCollector:
    """
    Collector for fetching papers from ArXiv API.
    """
    
    def __init__(self, page_size: int = 100, delay_seconds: float = 3.0):
        """
        Args:
            page_size: Number of results to fetch per page (though python lib handles pagination).
            delay_seconds: Delay between requests (handled by lib, but good to note).
        """
        self.client = arxiv.Client(
            page_size=page_size,
            delay_seconds=delay_seconds,
            num_retries=3
        )

    def fetch_papers(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Fetch papers based on a search query.

        Args:
            query: The search query string (e.g., "cat:cs.AI AND submittedDate:[20240101 TO 20240131]").
            max_results: Maximum number of papers to return.

        Returns:
            List[Paper]: A list of validated Paper objects.
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers = []
        # Using the generator provided by the client
        for result in self.client.results(search):
            try:
                paper = self._convert_to_model(result)
                papers.append(paper)
            except Exception as e:
                # Log error but continue processing other results
                print(f"Error processing result {result.entry_id}: {e}")
                continue
        
        return papers

    def get_recent_papers(self, category: str, days: int = 1, max_results: int = 20) -> List[Paper]:
        """
        Convenience method to fetch papers from the last N days in a specific category.
        """
        # ArXiv API date format: YYYYMMDDHHMM
        # We generally search via submittedDate. Note that ArXiv dates can be tricky.
        # Constructing a broad query for simplicity in MVP.
        # "cat:cs.AI" is usually sufficient for testing. 
        # For precise date filtering, we might need post-filtering or precise query syntax.
        # Here we use the query syntax.
        
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Format dates for query (YYYYMMDD) - ArXiv search syntax is a bit specific
        # actually ArXiv uses 'submittedDate:[YYYYMMDD0000 TO YYYYMMDD2359]'
        start_str = start_date.strftime("%Y%m%d0000")
        end_str = end_date.strftime("%Y%m%d2359")
        
        # NOTE: Date filtering in ArXiv API query can be flaky. 
        # For Phase 1 MVP, we will fetch recent by sort order and filter in Python if strictness is needed.
        # But let's try the query first.
        query = f"cat:{category}" 
        
        # Fetch a bit more to ensure we cover the range if we were to post-filter
        # But here we rely on sort_by=SubmittedDate Descending in fetch_papers
        
        return self.fetch_papers(query=query, max_results=max_results)

    def _convert_to_model(self, result: arxiv.Result) -> Paper:
        """Converts an arxiv.Result to our Paper model."""
        return Paper(
            arxiv_id=result.get_short_id(),
            title=result.title,
            authors=[a.name for a in result.authors],
            summary=result.summary,
            published_date=result.published,
            updated_date=result.updated,
            primary_category=result.primary_category,
            categories=result.categories,
            pdf_url=result.pdf_url
        )
