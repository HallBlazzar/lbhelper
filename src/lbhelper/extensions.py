from pathlib import Path
from lbhelper import defaults, DirectConfig


def copy_bootloaders(source_bootloader_dir: Path = defaults.BUILTIN_BOOTLOADER_DIR) -> DirectConfig:
    """
    Copying bootloaders to image build directory. Each subdirectory under the source directory
    represents a bootloader.
    See https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-binary.en.html#641

    :param source_bootloader_dir: Source bootloaders directory. It should contain 1 to multiple bootloaders.
    :return: bootloader copying target
    :rtype: DirectConfig
    """
    if not source_bootloader_dir.exists() or not source_bootloader_dir.is_dir():
        raise Exception(
            f"Bootloader directory {source_bootloader_dir} does not exist or is not a directory"
        )

    return DirectConfig(
        target_filepath=defaults.BOOTLOADER_DIR,
        get_source_file=lambda :source_bootloader_dir
    )
