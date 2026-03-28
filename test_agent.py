import logging
import sys
import os
from dotenv import load_dotenv

# Ensure the root directory is in the path
sys.path.append(os.getcwd())

from src.engine.processor import ProcessOrchestrator
from src.utils.logger import setup_logging
from src.utils.config import Config

# Setup logging
setup_logging()
logger = logging.getLogger("test_run")

def run_test():
    """
    Runs one cycle of the agent to verify API and logic.
    """
    # Load .env to ensure the new key is used
    load_dotenv(override=True)
    
    logger.info("Initializing Sourcing Agent for Demo...")
    logger.info(f"Using LLM Model: {Config.LLM_MODEL}")
    
    try:
        orchestrator = ProcessOrchestrator()
        # Fetch data from the last 7 days for the demo
        orchestrator.run_cycle(days=7)
        logger.info("Demo cycle completed successfully!")
    except Exception as e:
        logger.error(f"Error during demo run: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    run_test()
