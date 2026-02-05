from deep_reader.collector.arxiv_client import ArxivCollector
from deep_reader.storage.db_manager import DatabaseManager
from deep_reader.notifier.email_service import EmailNotifier
from deep_reader.intelligence.llm_client import LLMClient

def run_daily_cycle(category: str = "cs.AI", days: int = 1):
    print(f"Starting daily cycle for {category}...")
    
    # 1. Initialize Components
    collector = ArxivCollector()
    db = DatabaseManager()
    notifier = EmailNotifier()
    llm = LLMClient()
    
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
            # New Paper
            print(f"New paper found: {paper.title[:50]}... Generating summary...")
            try:
                summary = llm.generate_summary(paper.summary)
                paper_to_save = paper.model_copy(update={"llm_summary": summary})
            except Exception as e:
                print(f"Failed to generate summary for {paper.arxiv_id}: {e}")
                paper_to_save = paper
                
            new_papers.append(paper_to_save)
            db.save_paper(paper_to_save)
            
        else:
            # Existing Paper
            # 1. Preserve existing intelligence data (so we don't overwrite with None)
            # 2. Optional: Backfill if missing
            
            updates = {
                "llm_summary": existing.llm_summary,
                "key_insights": existing.key_insights
            }
            
            if not existing.llm_summary:
                print(f"Backfilling summary for existing paper: {paper.arxiv_id}")
                try:
                    summary = llm.generate_summary(paper.summary)
                    updates["llm_summary"] = summary
                except Exception as e:
                    print(f"Failed to backfill summary: {e}")

            paper_to_save = paper.model_copy(update=updates)
            db.save_paper(paper_to_save)
            
    print(f"Saved {len(papers)} papers ({len(new_papers)} new).")
    
    # 4. Notify
    if new_papers:
        print("Sending notification...")
        notifier.send_daily_digest(new_papers)
    else:
        print("No new papers to notify.")
        
    print("Cycle complete.")
