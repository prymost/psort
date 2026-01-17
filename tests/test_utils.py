import pytest
import logging
import datetime
from unittest.mock import patch
from src.utils import setup_logging


@pytest.fixture(autouse=True)
def reset_logging():
    """
    Reset logging configuration before and after each test.
    """
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()
    yield
    # Cleanup
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()


def test_setup_logging_defaults(tmp_path):
    """
    Test setup_logging with default arguments.
    """
    fixed_date = datetime.datetime(2023, 10, 27, 10, 30, 0)

    with (
        patch("src.utils.datetime") as mock_datetime,
        patch("src.utils.Path.mkdir") as mock_mkdir,
        patch("logging.FileHandler") as mock_file_handler,
    ):

        mock_datetime.datetime.now.return_value = fixed_date
        mock_instance = mock_file_handler.return_value
        mock_instance.level = logging.NOTSET

        # Execute
        log_file = setup_logging()

        # Assertions
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        expected_name = "sync_photos_10-27-2023_103000.log"
        assert log_file.name == expected_name
        assert str(log_file.parent) == "/tmp/logs"

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) == 2
        assert any(h == mock_instance for h in root_logger.handlers)


def test_setup_logging_custom_paths(tmp_path):
    """
    Test setup_logging with custom arguments using a temporary directory.
    """
    custom_dir = tmp_path / "custom_logs"
    custom_prefix = "test_run"
    fixed_date = datetime.datetime(2025, 1, 1, 12, 0, 0)

    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = fixed_date

        # Execute
        log_file = setup_logging(
            log_dir_name=str(custom_dir), log_file_name_prefix=custom_prefix
        )

        # Assertions
        assert custom_dir.exists()
        assert log_file.exists()

        # Check content
        content = log_file.read_text()
        assert "Logging initialized" in content


def test_logging_formatter_config(tmp_path):
    """
    Verify that the formatter is correctly configured on the handlers.
    """
    log_dir = tmp_path / "logs"

    # Execute
    setup_logging(log_dir_name=str(log_dir))

    # Get the handlers attached to the root logger
    root_logger = logging.getLogger()
    handlers = root_logger.handlers

    # Verify we have handlers
    assert len(handlers) > 0

    # Check the formatter on the first handler (FileHandler or StreamHandler)
    formatter = handlers[0].formatter

    assert "%(asctime)s" in formatter._fmt
    assert "%(levelname)s" in formatter._fmt
    assert "%(message)s" in formatter._fmt
