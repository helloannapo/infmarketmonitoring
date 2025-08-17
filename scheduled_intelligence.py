#!/usr/bin/env python3
"""
Infineon Competitive Intelligence Scheduler
Runs the main intelligence scraper at specified intervals
"""

import schedule
import time
import subprocess
import sys
import os
import logging
from datetime import datetime
from pathlib import Path
import argparse

# Setup logging for the scheduler
def setup_scheduler_logging():
    """Setup logging for the scheduler"""
    os.makedirs('logs', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'logs/scheduler_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_intelligence_job():
    """Run the main intelligence scraper"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("STARTING SCHEDULED INTELLIGENCE JOB")
    logger.info("=" * 60)
    
    try:
        # Get the directory of this script
        script_dir = Path(__file__).parent.absolute()
        
        # Activate virtual environment and run the main script
        if os.name == 'nt':  # Windows
            activate_script = script_dir / "venv" / "Scripts" / "activate.bat"
            python_exe = script_dir / "venv" / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            activate_script = script_dir / "venv" / "bin" / "activate"
            python_exe = script_dir / "venv" / "bin" / "python"
        
        # Check if virtual environment exists
        if not python_exe.exists():
            logger.error(f"Virtual environment not found at {python_exe}")
            logger.error("Please run setup_venv.sh first to create the virtual environment")
            return False
        
        # Run the main intelligence scraper
        main_script = script_dir / "infineon_intelligence_scraper.py"
        
        if not main_script.exists():
            logger.error(f"Main script not found at {main_script}")
            return False
        
        logger.info(f"Running intelligence scraper: {main_script}")
        
        # Execute the main script
        result = subprocess.run(
            [str(python_exe), str(main_script)],
            capture_output=True,
            text=True,
            cwd=script_dir
        )
        
        if result.returncode == 0:
            logger.info("Intelligence job completed successfully")
            logger.info("Output:")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"Intelligence job failed with return code {result.returncode}")
            logger.error("Error output:")
            logger.error(result.stderr)
            logger.error("Standard output:")
            logger.error(result.stdout)
            return False
            
    except Exception as e:
        logger.error(f"Error running intelligence job: {e}")
        return False

def setup_schedule(interval_hours=24):
    """Setup the schedule for running the intelligence job"""
    logger = logging.getLogger(__name__)
    
    # Schedule the job to run every X hours
    schedule.every(interval_hours).hours.do(run_intelligence_job)
    
    logger.info(f"Intelligence job scheduled to run every {interval_hours} hours")
    logger.info("Available schedule commands:")
    logger.info("  - schedule.every().hour.do(run_intelligence_job)")
    logger.info("  - schedule.every().day.at('10:30').do(run_intelligence_job)")
    logger.info("  - schedule.every().monday.do(run_intelligence_job)")
    logger.info("  - schedule.every().wednesday.at('13:15').do(run_intelligence_job)")

def run_scheduler(interval_hours=24, run_once=False):
    """Run the scheduler"""
    logger = logging.getLogger(__name__)
    
    if run_once:
        logger.info("Running intelligence job once...")
        success = run_intelligence_job()
        return success
    else:
        setup_schedule(interval_hours)
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        logger.info(f"Next run in {interval_hours} hours")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            return True

def main():
    """Main function for the scheduler"""
    parser = argparse.ArgumentParser(
        description="Infineon Competitive Intelligence Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run every 24 hours (default)
  python scheduled_intelligence.py
  
  # Run every 6 hours
  python scheduled_intelligence.py --interval 6
  
  # Run every 12 hours
  python scheduled_intelligence.py --interval 12
  
  # Run once and exit
  python scheduled_intelligence.py --once
  
  # Run every 8 hours with verbose logging
  python scheduled_intelligence.py --interval 8 --verbose
        """
    )
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=24,
        help='Interval in hours between runs (default: 24)'
    )
    
    parser.add_argument(
        '--once', 
        action='store_true',
        help='Run once and exit (do not schedule)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger = setup_scheduler_logging()
    
    logger.info("=" * 60)
    logger.info("INFINEON COMPETITIVE INTELLIGENCE SCHEDULER")
    logger.info("=" * 60)
    logger.info(f"Interval: {args.interval} hours")
    logger.info(f"Run once: {args.once}")
    logger.info(f"Verbose: {args.verbose}")
    logger.info("=" * 60)
    
    # Validate interval
    if args.interval < 1:
        logger.error("Interval must be at least 1 hour")
        sys.exit(1)
    
    # Run the scheduler
    success = run_scheduler(args.interval, args.once)
    
    if success:
        logger.info("Scheduler completed successfully")
        sys.exit(0)
    else:
        logger.error("Scheduler failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
