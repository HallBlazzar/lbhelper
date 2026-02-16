import shutil
from enum import StrEnum
from pathlib import Path

from lbhelper import defaults
from lbhelper.run_command import run_command


def remove_build_dir(iso_build_dir: Path, exist_ok: bool = False):
    """
    Remove ``iso_build_dir``. Usually used before start fresh build.

    :param pathlib.Path iso_build_dir: Path to image build directory.
    :param bool exist_ok: If ``True``, remove ``iso_build_dir`` for fresh build.
    """
    if exist_ok:
        defaults.DEFAULT_LOGGER.info(f"Skip build dir {iso_build_dir} removal.")
        return

    defaults.DEFAULT_LOGGER.info(f"Removing build dir {iso_build_dir} ...")
    shutil.rmtree(iso_build_dir, ignore_errors=True)
    defaults.DEFAULT_LOGGER.info(f"Build dir {iso_build_dir} removed.")


class LBOperation(StrEnum):
    BUILD = "build"
    CLEAN = "clean"
    CONFIG = "config"


def run_lb_operation(
    operation: LBOperation,
    iso_build_dir: Path,
    live_build_binary: Path = defaults.DEFAULT_LIVE_BUILD_BINARY,
):
    """
    Run given live build operation in ``iso_build_dir``.

    :param LBOperation operation: A live build operation.
    :param pathlib.Path iso_build_dir: Image build directory.
    :param pathlib.Path,Optional live_build_binary: Live build binary path.
      Default to :const:`defaults.DEFAULT_LIVE_BUILD_BINARY`.
    """
    defaults.DEFAULT_LOGGER.info(f"Running lb {operation.value} in {iso_build_dir} ...")
    run_command(command=[str(live_build_binary), operation.value], cwd=iso_build_dir)
    defaults.DEFAULT_LOGGER.info(f"Finish {operation.value} in {iso_build_dir}.")
