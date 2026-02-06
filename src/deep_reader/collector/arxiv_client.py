import arxiv
from typing import List
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
