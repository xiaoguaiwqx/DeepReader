from deep_reader.collector.arxiv_client import ArxivCollector
from deep_reader.storage.db_manager import DatabaseManager
from deep_reader.notifier.email_service import EmailNotifier
from deep_reader.models import Paper

def run_daily_cycle(category: str = "cs.AI", days: int = 1):
    print(f"Starting daily cycle for {category}...")
    
    # 1. Initialize Components
    collector = ArxivCollector()
    db = DatabaseManager()
    notifier = EmailNotifier()
    
    # 2. Fetch Papers
    print("Fetching papers...")
    papers = collector.get_recent_papers(category=category, days=days)
    print(f"Fetched {len(papers)} papers.")
    
    if not papers:
        print("No papers found.")
        return

    # 3. Save to DB and Filter new ones
    new_papers = []
    for paper in papers:
        existing = db.get_paper(paper.arxiv_id)
        if not existing:
            new_papers.append(paper)
            db.save_paper(paper)
        else:
            # We might want to update existing papers too?
            # For now, just save (upsert handled by DB)
            db.save_paper(paper)
            
    print(f"Saved {len(papers)} papers ({len(new_papers)} new).")
    
    # 4. Notify
    if new_papers:
        print("Sending notification...")
        notifier.send_daily_digest(new_papers)
    else:
        print("No new papers to notify.")
        
    print("Cycle complete.")
