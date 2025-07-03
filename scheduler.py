from apscheduler.schedulers.background import BackgroundScheduler
from parser import parse_min_score_ai
import logging


logger = logging.getLogger(__name__)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(parse_min_score_ai, 'interval', hours=24)
    scheduler.start()
    logger.info("Scheduler started. Data will refresh every 24 hours.")