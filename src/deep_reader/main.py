import argparse
import time
import signal
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from deep_reader.core_loop import run_daily_cycle

def main():
    parser = argparse.ArgumentParser(description="DeepReader Agent")
    parser.add_argument("--run-once", action="store_true", help="Run the cycle once and exit")
    parser.add_argument("--schedule", action="store_true", help="Run in scheduled mode (daily)")
    parser.add_argument("--category", type=str, default="cs.AI", help="ArXiv category to fetch")
    
    args = parser.parse_args()
    
    if args.run_once:
        run_daily_cycle(category=args.category)
    elif args.schedule:
        scheduler = BackgroundScheduler()
        # Schedule to run every day at 08:00 AM
        trigger = CronTrigger(hour=8, minute=0)
        
        scheduler.add_job(
            run_daily_cycle,
            trigger=trigger,
            kwargs={"category": args.category},
            id="daily_cycle",
            name="Daily Research Paper Fetch",
            replace_existing=True
        )
        
        print(f"Scheduler started. Job scheduled for {trigger}.")
        scheduler.start()
        
        # Keep the script running
        try:
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            print("Stopping scheduler...")
            scheduler.shutdown()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
