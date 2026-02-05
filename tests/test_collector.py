import pytest
from deep_reader.collector.arxiv_client import ArxivCollector
from deep_reader.models import Paper

def test_fetch_papers_integration():
    """
    Integration test to verify ArXiv API connectivity and model conversion.
    This test hits the real ArXiv API.
    """
    collector = ArxivCollector()
    # Fetch just 1 result to be kind to the API and fast
    papers = collector.fetch_papers(query="cat:cs.AI", max_results=1)
    
    assert isinstance(papers, list)
    assert len(papers) > 0
    assert len(papers) <= 1
    
    paper = papers[0]
    assert isinstance(paper, Paper)
    assert paper.arxiv_id is not None
    assert paper.title is not None
    assert "cs.AI" in paper.categories or paper.primary_category.startswith("cs")
