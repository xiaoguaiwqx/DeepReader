import sqlite3
import json
from typing import Optional, List, Dict
from datetime import datetime

from deep_reader.models import Paper

class DatabaseManager:
    def __init__(self, db_path: str = "deep_reader.db"):
        self.db_path = db_path
        self._fts_enabled = False
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Papers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    arxiv_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    summary TEXT,
                    published_date TIMESTAMP,
                    updated_date TIMESTAMP,
                    primary_category TEXT,
                    categories TEXT,  -- Stored as JSON list
                    pdf_url TEXT
                )
            """)

            # Index to speed up date range filters
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_papers_published_date ON papers(published_date)"
            )

            # Migration: Add new columns if they don't exist
            try:
                cursor.execute("ALTER TABLE papers ADD COLUMN llm_summary TEXT")
            except sqlite3.OperationalError:
                pass 
            
            try:
                cursor.execute("ALTER TABLE papers ADD COLUMN key_insights TEXT")
            except sqlite3.OperationalError:
                pass

            # Optional FTS for topic search performance
            try:
                cursor.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts USING fts5(
                        title, summary, primary_category, categories,
                        content='papers', content_rowid='rowid'
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TRIGGER IF NOT EXISTS papers_ai AFTER INSERT ON papers BEGIN
                        INSERT INTO papers_fts(rowid, title, summary, primary_category, categories)
                        VALUES (new.rowid, new.title, new.summary, new.primary_category, new.categories);
                    END;
                    """
                )
                cursor.execute(
                    """
                    CREATE TRIGGER IF NOT EXISTS papers_ad AFTER DELETE ON papers BEGIN
                        INSERT INTO papers_fts(papers_fts, rowid, title, summary, primary_category, categories)
                        VALUES('delete', old.rowid, old.title, old.summary, old.primary_category, old.categories);
                    END;
                    """
                )
                cursor.execute(
                    """
                    CREATE TRIGGER IF NOT EXISTS papers_au AFTER UPDATE ON papers BEGIN
                        INSERT INTO papers_fts(papers_fts, rowid, title, summary, primary_category, categories)
                        VALUES('delete', old.rowid, old.title, old.summary, old.primary_category, old.categories);
                        INSERT INTO papers_fts(rowid, title, summary, primary_category, categories)
                        VALUES (new.rowid, new.title, new.summary, new.primary_category, new.categories);
                    END;
                    """
                )
                self._fts_enabled = True
            except sqlite3.OperationalError:
                # FTS5 might be unavailable in some builds; fallback to LIKE
                self._fts_enabled = False
            
            # Authors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS authors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            
            # Junction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paper_authors (
                    paper_id TEXT,
                    author_id INTEGER,
                    FOREIGN KEY(paper_id) REFERENCES papers(arxiv_id),
                    FOREIGN KEY(author_id) REFERENCES authors(id),
                    PRIMARY KEY (paper_id, author_id)
                )
            """)
            conn.commit()

    def _parse_date(self, date_val):
        """Parses a date value which might be a string or datetime object."""
        if isinstance(date_val, str):
            try:
                # Try simple ISO format
                return datetime.fromisoformat(date_val)
            except ValueError:
                # Fallback for formats like "2026-02-04 18:59:52+00:00" if standard parser fails
                # Often separating space and timezone can be tricky manually if fromisoformat is strict
                # In Python 3.11+ fromisoformat is very good. In 3.10 it handles most.
                # If it fails, let's try to strip timezone or handle space
                try:
                    return datetime.strptime(date_val, "%Y-%m-%d %H:%M:%S%z")
                except ValueError:
                     pass
                return date_val # Return as is or raise
        return date_val

    def _build_fts_query(self, topic: str) -> str:
        keywords = [kw.strip().replace('"', '') for kw in topic.lower().split() if kw.strip()]
        if not keywords:
            return ""
        return " AND ".join(keywords)

    def save_paper(self, paper: Paper):
        """Saves a paper and its authors to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Insert Paper
            # Convert list categories to JSON
            categories_json = json.dumps(paper.categories)
            
            cursor.execute("""
                INSERT OR REPLACE INTO papers 
                (arxiv_id, title, summary, published_date, updated_date, primary_category, categories, pdf_url, llm_summary, key_insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.arxiv_id,
                paper.title,
                paper.summary,
                paper.published_date,
                paper.updated_date,
                paper.primary_category,
                categories_json,
                paper.pdf_url,
                paper.llm_summary,
                paper.key_insights
            ))
            
            # 2. Insert Authors and Link
            for author_name in paper.authors:
                # Insert author if not exists
                cursor.execute("INSERT OR IGNORE INTO authors (name) VALUES (?)", (author_name,))
                
                # Get author ID (whether inserted or existed)
                cursor.execute("SELECT id FROM authors WHERE name = ?", (author_name,))
                author_id = cursor.fetchone()[0]
                
                # Link
                cursor.execute("INSERT OR IGNORE INTO paper_authors (paper_id, author_id) VALUES (?, ?)", 
                               (paper.arxiv_id, author_id))
            
            conn.commit()

    def get_paper(self, arxiv_id: str) -> Optional[Paper]:
        """Retrieves a paper by its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM papers WHERE arxiv_id = ?", (arxiv_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Unpack row (order must match INSERT/Schema)
            # Schema: arxiv_id, title, summary, published_date, updated_date, primary_category, categories, pdf_url, llm_summary, key_insights
            # Note: We added columns via ALTER, so they are at the end.
            # But "SELECT *" order depends on schema.
            # To be safe, let's explicitly select columns or trust the order if ALTER appends.
            # SQLite appends.
            
            (pid, title, summary, pub_date, upd_date, prim_cat, cats_json, pdf, llm_summ, insights) = row
            
            # Fetch authors
            cursor.execute("""
                SELECT a.name FROM authors a
                JOIN paper_authors pa ON a.id = pa.author_id
                WHERE pa.paper_id = ?
            """, (pid,))
            author_rows = cursor.fetchall()
            authors = [r[0] for r in author_rows]
            
            return Paper(
                arxiv_id=pid,
                title=title,
                authors=authors,
                summary=summary,
                published_date=self._parse_date(pub_date),
                updated_date=self._parse_date(upd_date),
                primary_category=prim_cat,
                categories=json.loads(cats_json),
                pdf_url=pdf,
                llm_summary=llm_summ,
                key_insights=insights
            )
            
    def count_papers(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM papers")
            return cursor.fetchone()[0]

    def get_stats(self) -> Dict[str, object]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*), MAX(updated_date) FROM papers")
            total, last_fetch = cursor.fetchone()

            last_fetch_dt = self._parse_date(last_fetch) if last_fetch else None
            last_fetch_time = (
                last_fetch_dt.isoformat() if isinstance(last_fetch_dt, datetime) else None
            )

            cursor.execute(
                "SELECT primary_category, COUNT(*) FROM papers GROUP BY primary_category"
            )
            categories = {row[0]: row[1] for row in cursor.fetchall() if row[0]}

            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN llm_summary IS NOT NULL AND llm_summary != '' THEN 1 ELSE 0 END),
                    COUNT(*)
                FROM papers
                """
            )
            with_summary, summary_total = cursor.fetchone()
            with_summary = with_summary or 0
            summary_total = summary_total or 0

            return {
                "total": total,
                "last_fetch_time": last_fetch_time,
                "categories": categories,
                "with_summary": with_summary,
                "without_summary": summary_total - with_summary,
            }

    def get_categories(self) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT primary_category FROM papers WHERE primary_category IS NOT NULL GROUP BY primary_category"
            )
            return [row[0] for row in cursor.fetchall() if row[0]]

    def count_papers_filtered(
        self,
        topic: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            clauses = []
            params: List[str] = []

            if topic:
                if self._fts_enabled:
                    fts_query = self._build_fts_query(topic)
                    if fts_query:
                        clauses.append("papers_fts MATCH ?")
                        params.append(fts_query)
                else:
                    # Split topic into individual keywords and ensure all of them are present
                    # This increases robustness against minor title variations
                    keywords = topic.lower().split()
                    for kw in keywords:
                        like = f"%{kw}%"
                        clauses.append(
                            "(LOWER(title) LIKE ? OR LOWER(summary) LIKE ? OR LOWER(primary_category) LIKE ? OR LOWER(categories) LIKE ?)"
                        )
                        params.extend([like, like, like, like])

            if start_date:
                # Use strftime style to ensure clean date comparison
                clauses.append("strftime('%Y-%m-%d', published_date) >= ?")
                params.append(start_date)

            if end_date:
                clauses.append("strftime('%Y-%m-%d', published_date) <= ?")
                params.append(end_date)

            where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

            if topic and self._fts_enabled:
                cursor.execute(
                    f"SELECT COUNT(*) FROM papers JOIN papers_fts ON papers_fts.rowid = papers.rowid {where_sql}",
                    params,
                )
            else:
                cursor.execute(
                    f"SELECT COUNT(*) FROM papers {where_sql}",
                    params,
                )
            return cursor.fetchone()[0]

    def get_recent_papers(
        self,
        limit: int = 20,
        offset: int = 0,
        topic: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Paper]:
        """Retrieves a list of papers ordered by published date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            clauses = []
            params: List[str] = []

            if topic:
                if self._fts_enabled:
                    fts_query = self._build_fts_query(topic)
                    if fts_query:
                        clauses.append("papers_fts MATCH ?")
                        params.append(fts_query)
                else:
                    # Split topic into individual keywords and ensure all of them are present
                    # This increases robustness against minor title variations
                    keywords = topic.lower().split()
                    for kw in keywords:
                        like = f"%{kw}%"
                        clauses.append(
                            "(LOWER(title) LIKE ? OR LOWER(summary) LIKE ? OR LOWER(primary_category) LIKE ? OR LOWER(categories) LIKE ?)"
                        )
                        params.extend([like, like, like, like])

            if start_date:
                # Use strftime style to ensure clean date comparison
                clauses.append("strftime('%Y-%m-%d', published_date) >= ?")
                params.append(start_date)

            if end_date:
                clauses.append("strftime('%Y-%m-%d', published_date) <= ?")
                params.append(end_date)

            where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

            if topic and self._fts_enabled:
                cursor.execute(
                    f"""
                    SELECT papers.* FROM papers
                    JOIN papers_fts ON papers_fts.rowid = papers.rowid
                    {where_sql}
                    ORDER BY published_date DESC
                    LIMIT ? OFFSET ?
                    """,
                    (*params, limit, offset),
                )
            else:
                cursor.execute(
                    f"""
                    SELECT * FROM papers 
                    {where_sql}
                    ORDER BY published_date DESC 
                    LIMIT ? OFFSET ?
                    """,
                    (*params, limit, offset),
                )
            
            rows = cursor.fetchall()
            papers = []
            
            for row in rows:
                (pid, title, summary, pub_date, upd_date, prim_cat, cats_json, pdf, llm_summ, insights) = row
                
                # Fetch authors (This effectively causes N+1 query problem, acceptable for small MVP limits)
                cursor.execute("""
                    SELECT a.name FROM authors a
                    JOIN paper_authors pa ON a.id = pa.author_id
                    WHERE pa.paper_id = ?
                """, (pid,))
                author_rows = cursor.fetchall()
                authors = [r[0] for r in author_rows]
                
                papers.append(Paper(
                    arxiv_id=pid,
                    title=title,
                    authors=authors,
                    summary=summary,
                    published_date=self._parse_date(pub_date),
                    updated_date=self._parse_date(upd_date),
                    primary_category=prim_cat,
                    categories=json.loads(cats_json),
                    pdf_url=pdf,
                    llm_summary=llm_summ,
                    key_insights=insights
                ))
                
            return papers
