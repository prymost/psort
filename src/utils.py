import hashlib
import logging
import datetime
from pathlib import Path


def setup_logging(
    log_dir_name: str = "/tmp/logs", log_file_name_prefix: str = "sync_photos"
) -> Path:
    log_dir = Path(log_dir_name)
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%m-%d-%Y_%H%M%S")
    log_file = log_dir / f"{log_file_name_prefix}_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
    logging.info(f"Logging initialized. Log file: {log_file}")
    return log_file


def calculate_sha256(file_path: Path) -> str:
    """Calculate the SHA256 hash of a file in chunks to save memory"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def generate_target_filename(file_path: Path, date_taken: datetime.datetime) -> str:
    """
    Generates filename: DDMonYYYY_HHMM[SizeLast5].ext
    Example: 02Sep2024_122339737.png
    """
    # Format the date: 02Sep2024_1223
    date_part = date_taken.strftime("%d%b%Y_%H%M")

    # Get last 5 digits of file size
    file_size = file_path.stat().st_size
    size_part = str(file_size)[-5:]

    # Combine with original extension (converted to lowercase)
    return f"{date_part}{size_part}{file_path.suffix.lower()}"
