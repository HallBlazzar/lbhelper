from pathlib import Path

from .auto_scripts.auto_scripts import AutoScriptType
from .auto_scripts.auto_scripts import write_auto_script
from .defaults import DEFAULT_ISO_BUILD_DIR
from .defaults import DEFAULT_LOGGER
from .defaults import DEFAULT_DISTRIBUTION, DEFAULT_IMAGE_NAME
from .live_build import LBOperation
from .live_build import remove_build_dir
from .live_build import run_lb_operation
from .target_writer import AptPreferencesWriter
from .target_writer import CustomDebWriter
from .target_writer import DirectConfigWriter
from .target_writer import HookScriptWriter
from .target_writer import StaticFileWriter
from .target_writer import TargetWriter
from .target_writer import UpstreamPackagesWriter
from .targets import AptPreference
from .targets import CustomDeb
from .targets import DirectConfig
from .targets import HookScript
from .targets import StaticFile
from .targets import UpstreamPackages
from .extensions import copy_bootloaders


def build_image(
    targets: list,
    iso_build_dir: Path = DEFAULT_ISO_BUILD_DIR, fresh_build: bool = True,
    distribution: str = DEFAULT_DISTRIBUTION,
    image_name: str = DEFAULT_IMAGE_NAME,
    skip_build: bool = False,
):
    """
    Build image from targets.

    :param List targets: Targets to process. Elements can be :class:`Target` or List[:class:`Target`].
    :param pathlib.Path,Optional iso_build_dir: Image build directory.
    :param bool fresh_build: If ``True``, remove build directory before performing any operations for fresh build.
    :param str distribution: Base Debian distribution for image. ``trixie`` by default.
    :param str image_name: Name of image. ``myos`` by default.
    :param bool skip_build: If ``True``, ``lb build`` won't run.
    """
    DEFAULT_LOGGER.info(f"Cleanup build directory {iso_build_dir}")
    remove_build_dir(iso_build_dir=iso_build_dir, exist_ok=fresh_build)

    DEFAULT_LOGGER.info(f"Write auto-scripts")
    write_auto_script(
        iso_build_dir=iso_build_dir,
        script_type=AutoScriptType.CONFIG,
        distribution=distribution, image_name=image_name)
    write_auto_script(iso_build_dir=iso_build_dir, script_type=AutoScriptType.BUILD)
    write_auto_script(iso_build_dir=iso_build_dir, script_type=AutoScriptType.CLEAN)

    DEFAULT_LOGGER.info(f"Run lb config")
    run_lb_operation(operation=LBOperation.CONFIG, iso_build_dir=iso_build_dir)

    DEFAULT_LOGGER.info(f"Attach built-in targets")
    copy_bootloaders_target = copy_bootloaders(iso_build_dir=iso_build_dir)
    targets.append(copy_bootloaders_target)

    DEFAULT_LOGGER.info(f"Write targets")
    TargetWriter(
        target_handlers={
            UpstreamPackages: UpstreamPackagesWriter(iso_build_dir=iso_build_dir),
            CustomDeb: CustomDebWriter(iso_build_dir=iso_build_dir),
            HookScript: HookScriptWriter(iso_build_dir=iso_build_dir),
            StaticFile: StaticFileWriter(iso_build_dir=iso_build_dir),
            AptPreference: AptPreferencesWriter(iso_build_dir=iso_build_dir),
            DirectConfig: DirectConfigWriter(iso_build_dir=iso_build_dir),
        },
        targets=targets,
    ).execute()

    DEFAULT_LOGGER.info(f"Build image")
    if not skip_build:
        run_lb_operation(operation=LBOperation.BUILD, iso_build_dir=iso_build_dir)
    else:
        DEFAULT_LOGGER.info(f"Skip build")
