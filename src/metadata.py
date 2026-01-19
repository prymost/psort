import datetime
import mimetypes
from pathlib import Path
from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import logging


def get_media_date(file_path: Path) -> datetime.datetime:
    """
    Attempts to retrieve the original creation date of a media file.
    Priority:
    1. EXIF 'DateTimeOriginal' (Images)
    2. Metadata 'Creation Date' (Videos)
    3. File System 'st_mtime' (Fallback)
    """

    mime_type, _ = mimetypes.guess_type(file_path)

    date_taken = None

    if mime_type and mime_type.startswith("image"):
        date_taken = _get_image_date(file_path)
    elif mime_type and mime_type.startswith("video"):
        date_taken = _get_video_date(file_path)

    if not date_taken:
        logging.debug(f"Metadata missing for {file_path}, using filesystem date.")
        timestamp = file_path.stat().st_mtime
        date_taken = datetime.datetime.fromtimestamp(timestamp)

    return date_taken


def _get_image_date(file_path: Path):
    """Extracts Date Time Original using the public getexif() API."""
    try:
        with Image.open(file_path) as img:
            # getexif() is the public, Pylance-approved way to access EXIF data
            exif = img.getexif()
            if not exif:
                return None

            # 0x9003 is the Hex code for DateTimeOriginal (equivalent to 36867)
            # This is standard across all EXIF implementations
            date_str = exif.get(0x9003)

            if date_str and isinstance(date_str, str):
                return datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        logging.warning(f"Error reading image metadata for {file_path}: {e}")
        return None


def _get_video_date(file_path: Path):
    """Extracts Creation Date using Hachoir."""
    try:
        parser = createParser(str(file_path))
        if not parser:
            return None

        with parser:
            metadata = extractMetadata(parser)
            if not metadata:
                return None

            return metadata.get("creation_date")
    except Exception as e:
        logging.warning(f"Error reading video metadata for {file_path}: {e}")
        return None
