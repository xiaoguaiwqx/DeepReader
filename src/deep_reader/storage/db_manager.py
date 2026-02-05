import sqlite3
import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from deep_reader.models import Paper

class DatabaseManager:
    def __init__(self, db_path: str = "deep_reader.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)

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

    def save_paper(self, paper: Paper):
        """Saves a paper and its authors to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Insert Paper
            # Convert list categories to JSON
            categories_json = json.dumps(paper.categories)
            
            cursor.execute("""
                INSERT OR REPLACE INTO papers 
                (arxiv_id, title, summary, published_date, updated_date, primary_category, categories, pdf_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.arxiv_id,
                paper.title,
                paper.summary,
                paper.published_date,
                paper.updated_date,
                paper.primary_category,
                categories_json,
                paper.pdf_url
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
                
            # Unpack row (order must match INSERT)
            # arxiv_id, title, summary, published, updated, primary_cat, categories_json, pdf_url
            (pid, title, summary, pub_date, upd_date, prim_cat, cats_json, pdf) = row
            
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
                published_date=pub_date,
                updated_date=upd_date,
                primary_category=prim_cat,
                categories=json.loads(cats_json),
                pdf_url=pdf
            )
            
    def count_papers(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM papers")
            return cursor.fetchone()[0]
