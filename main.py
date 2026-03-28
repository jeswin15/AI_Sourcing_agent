import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from src.engine.processor import ProcessOrchestrator
from src.utils.logger import setup_logging
from src.utils.config import Config
from dotenv import load_dotenv

# Load env
load_dotenv(override=True)

# Setup logging
setup_logging()
logger = logging.getLogger("main")

def run_agent():
    """Runs one data‑collection + evaluation cycle."""
    logger.info("Agent cycle triggered.")
    try:
        orchestrator = ProcessOrchestrator()
        orchestrator.run_cycle(days=7)
    except Exception as e:
        logger.error(f"Error in agent cycle: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("Starting Holocene Sourcing Agent...")
    logger.info(f"LLM Model : {Config.LLM_MODEL}")
    logger.info(f"Data Dir  : data/")

    # 1. Initial run on startup
    run_agent()

    # 2. Schedule recurring runs every 30 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_agent, 'interval', minutes=30)
    scheduler.start()
    logger.info("Scheduler started. Next cycle in 30 minutes.")

    # 3. Keep process alive
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Agent stopped.")
