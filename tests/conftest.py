import logging
from logging import Logger
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from lbhelper.logger import ConsoleHandler
from shutil import rmtree


@pytest.fixture(scope="function")
def logger():
    test_logger = logging.getLogger("lbhelper-test")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(ConsoleHandler())

    return test_logger

@pytest.fixture(scope="function")
def test_iso_build_dir(logger: Logger):
    try:
        with TemporaryDirectory() as tmpdir:
            tempdir_path = Path(tmpdir)
            logger.debug(f'Created tempdir {tempdir_path} for testing')
            yield tempdir_path
    except Exception as e:
        pytest.fail(f"Caught exception for tempdir {tempdir_path}: {e}")
    finally:
        if tempdir_path.is_dir() and tempdir_path.exists():
            logger.debug(f'Cleaning up dangling tempdir {tempdir_path}')
            rmtree(tempdir_path)
            logger.debug(f'Tempdir {tempdir_path} removed')
