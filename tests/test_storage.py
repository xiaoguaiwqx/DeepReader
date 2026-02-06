import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from deep_reader.storage.db_manager import DatabaseManager
from deep_reader.models import Paper

@pytest.fixture
def db(tmp_path):
    # Use a temporary file database for testing
    db_file = tmp_path / "test_deep_reader.db"
    return DatabaseManager(db_path=str(db_file))

def test_save_and_get_paper(db):
    paper = Paper(
        arxiv_id="2301.00001",
        title="Test Paper",
        authors=["Author One", "Author Two"],
        summary="This is a test summary.",
        published_date=datetime.now(timezone.utc),
        updated_date=datetime.now(timezone.utc),
        primary_category="cs.AI",
        categories=["cs.AI", "cs.LG"],
        pdf_url="http://example.com/pdf"
    )
    
    # Save
    db.save_paper(paper)
    
    # Verify count
    assert db.count_papers() == 1
    
    # Retrieve
    retrieved = db.get_paper("2301.00001")
    assert retrieved is not None
    assert retrieved.arxiv_id == paper.arxiv_id
    assert retrieved.title == paper.title
    assert len(retrieved.authors) == 2
    assert "Author One" in retrieved.authors
    assert retrieved.categories == paper.categories
    # Note: Pydantic handles datetime, but SQLite might return naive or different precision.
    # We might need to handle timezone awareness if strict equality fails.
    # But let's see.

def test_save_duplicate_paper(db):
    """Test that saving the same paper twice updates it (upsert) and doesn't crash."""
    paper = Paper(
        arxiv_id="2301.00002",
        title="Original Title",
        authors=["Me"],
        summary="Summary",
        published_date=datetime.now(timezone.utc),
        updated_date=datetime.now(timezone.utc),
        primary_category="cs.SE",
        categories=["cs.SE"],
    )
    
    db.save_paper(paper)
    
    # Update title
    paper2 = paper.model_copy(update={"title": "Updated Title"})
    db.save_paper(paper2)
    
    assert db.count_papers() == 1
    retrieved = db.get_paper("2301.00002")
    assert retrieved.title == "Updated Title"


def test_topic_search_fallback_to_like(db):
    paper = Paper(
        arxiv_id="2301.00003",
        title="Deep Learning for Vision",
        authors=["Tester"],
        summary="A paper about deep learning and vision.",
        published_date=datetime.now(timezone.utc),
        updated_date=datetime.now(timezone.utc),
        primary_category="cs.CV",
        categories=["cs.CV"],
    )

    db.save_paper(paper)
    db._fts_enabled = False

    with patch.object(DatabaseManager, "_build_fts_query", side_effect=AssertionError("FTS used")):
        assert db.count_papers_filtered(topic="deep vision") == 1
        results = db.get_recent_papers(topic="deep vision")
        assert len(results) == 1
