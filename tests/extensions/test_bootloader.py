from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir

from lbhelper.defaults import BOOTLOADER_DIR
from lbhelper.extensions import copy_bootloaders


def test_copy_bootloaders(test_iso_build_dir):
    # Arrange
    default_temp_dir = Path(gettempdir())

    # Act
    copy_bootloaders_target = copy_bootloaders(
        iso_build_dir=test_iso_build_dir,
        source_bootloader_dir=default_temp_dir
    )

    # Assert
    target_file_path = copy_bootloaders_target.target_filepath
    expected_target_file_path = test_iso_build_dir / BOOTLOADER_DIR
    assert target_file_path.resolve() == expected_target_file_path.resolve(), \
        f"target bootloader directory {target_file_path} is not as expected {expected_target_file_path}"

    source_file_path = copy_bootloaders_target.get_source_file()
    assert source_file_path.resolve() == default_temp_dir.resolve(), \
        f"source bootloader directory {source_file_path} is not the same as {default_temp_dir}"
