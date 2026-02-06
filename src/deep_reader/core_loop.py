from deep_reader.collector.arxiv_client import ArxivCollector
from deep_reader.storage.db_manager import DatabaseManager
from deep_reader.notifier.email_service import EmailNotifier
from deep_reader.intelligence.llm_client import LLMClient
from datetime import datetime, timedelta, timezone
from typing import Optional

def run_daily_cycle(
    query: Optional[str] = None, 
    category: str = "cs.AI", 
    days: Optional[int] = None, 
    topic: Optional[str] = None,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
    max_results: int = 200,
    job_id: Optional[str] = None
):
    print("Starting fetch cycle...")
    job_update = None
    if job_id:
        from deep_reader.server.job_store import update_job
        job_update = update_job
        job_update(job_id, status="running")
    
    try:
        # ... (components init)
        collector = ArxivCollector()
        db = DatabaseManager()
        notifier = EmailNotifier()
        llm = LLMClient()
        
        # 2. Fetch Papers
        print("Fetching papers...")
        
        actual_query = query
        if not actual_query:
            if start_date_str and end_date_str:
                # Use explicit dates (Expected format: YYYY-MM-DD)
                # ArXiv needs YYYYMMDDHHMM
                s = start_date_str.replace("-", "") + "0000"
                e = end_date_str.replace("-", "") + "2359"
                date_query = f"submittedDate:[{s} TO {e}]"
            else:
                # Fallback to 'days' logic
                fetch_days = days if days is not None else 1
                end_dt = datetime.now(timezone.utc)
                start_dt = end_dt - timedelta(days=fetch_days)
                date_query = f"submittedDate:[{start_dt.strftime('%Y%m%d0000')} TO {end_dt.strftime('%Y%m%d2359')}]"
            
            if topic:
                safe_topic = f'"{topic}"' if " " in topic else topic
                # Use parentheses for category if it contains OR to maintain logic
                safe_cat = f"({category})" if " OR " in category else category
                # Use AND for high precision as requested by user.
                actual_query = f'all:{safe_topic} AND cat:{safe_cat} AND {date_query}'
            else:
                safe_cat = f"({category})" if " OR " in category else category
                actual_query = f"cat:{safe_cat} AND {date_query}"
                
            print(f"Constructed query: {actual_query}")
            
        papers = collector.fetch_papers(query=actual_query, max_results=max_results)
        print(f"Fetched {len(papers)} papers using query: '{actual_query}'.")
        if job_update:
            job_update(job_id, total=len(papers))
        
        if not papers:
            print("No papers found.")
            if job_update:
                job_update(
                    job_id,
                    status="completed",
                    processed=0,
                    new=0,
                    finished_at=datetime.now(timezone.utc)
                )
            return
        
        # 3. Save to DB and Filter new ones
        new_papers = []
        processed_count = 0
        new_count = 0
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
                new_count += 1
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
            processed_count += 1
            if job_update:
                job_update(job_id, processed=processed_count, new=new_count)
                
        print(f"Saved {len(papers)} papers ({len(new_papers)} new).")
        
        # 4. Notify
        if new_papers:
            print("Sending notification...")
            notifier.send_daily_digest(new_papers)
        else:
            print("No new papers to notify.")
        if job_update:
            job_update(
                job_id,
                status="completed",
                processed=processed_count,
                new=new_count,
                finished_at=datetime.now(timezone.utc)
            )
            
        print("Cycle complete.")
    except Exception as e:
        if job_update:
            job_update(
                job_id,
                status="failed",
                error=str(e),
                finished_at=datetime.now(timezone.utc)
            )
        raise
