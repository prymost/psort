import logging
import datetime
from pathlib import Path

def setup_logging(log_dir_name: str = '/tmp/logs', log_file_name_prefix: str = 'sync_photos') -> Path:
    log_dir = Path(log_dir_name)
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%m-%d-%Y_%H%M%S')
    log_file = log_dir / f"{log_file_name_prefix}_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Logging initialized. Log file: {log_file}")
    return log_file
