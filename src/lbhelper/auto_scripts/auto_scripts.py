import enum
from importlib.resources import files
from pathlib import Path

from lbhelper import defaults
from lbhelper.defaults import DEFAULT_LOGGER
from lbhelper.file_helpers import render_template_to_file
from dataclasses import dataclass


class AutoScriptType(enum.Enum):
    """
    Auto script type.
    """
    CLEAN = "clean"
    """
    Clean script.
    """
    BUILD = "build"
    """
    Build script.
    """
    CONFIG = "config"
    """
    Config script.
    """


@dataclass
class __AutoScriptInfo:
    """
    Information about an auto script. See :function:`write_auto_script`.

    :param pathlib.Path default_source_script_path: Builtin source script path. See the `auto`
       directory under the module.
    :param pathlib.Path target_script_path: Target script path.
    """
    default_source_script_path: Path
    target_script_path: Path


def write_auto_script(iso_build_dir: Path, script_type: AutoScriptType, source_script_path: Path = None, **kwargs):
    """
    Write specified auto script to :const:`defaults.AUTO_SCRIPT_PATH`. Target script path is predefined in
    this function. If ``source_script_path`` is not given, then builtin template will be used. Note that for the builtin
    config auto script, the ``distribution (str)`` and ``image_name (str)`` are required.

    :param pathlib.Path iso_build_dir: Image build directory.
    :param AutoScriptType script_type: Which type of auto script to write.
    :param pathlib.Path,Optional source_script_path: Source script template. If not given, then builtin
       auto script template mapped to the given ``script_type`` will be used.
    :param kwargs: Additional kwargs to render the template.
    """

    script_info = __get_script_info(iso_build_dir, script_type)

    source_script_path = script_info.default_source_script_path if source_script_path is None else source_script_path

    DEFAULT_LOGGER.info(f"Writing auto script '{script_type}' ...")
    render_template_to_file(template_path=source_script_path, target_path=script_info.target_script_path, **kwargs)
    DEFAULT_LOGGER.info(f"Auto script {script_type} saved.")

    DEFAULT_LOGGER.info(f"Setting auto script {script_type} permission to 755 ...")
    script_info.target_script_path.chmod(0o755)
    DEFAULT_LOGGER.info(f"Auto script {script_type} permission updated")


def __get_script_info(iso_build_dir: Path, script_type: AutoScriptType) -> __AutoScriptInfo:
    """
    Get script info for given auto script type.

    :param pathlib.Path iso_build_dir: Image build directory.
    :param AutoScriptType script_type: Auto script type.
    :return: auto script information
    :rtype: __AutoScriptInfo
    """
    module_path = files(__package__)

    script_info = {
        AutoScriptType.CONFIG: __AutoScriptInfo(
            default_source_script_path=Path(module_path / defaults.CONFIG_SCRIPT_PATH),
            target_script_path=iso_build_dir / defaults.CONFIG_SCRIPT_PATH,
        ),
        AutoScriptType.BUILD: __AutoScriptInfo(
            default_source_script_path=Path(module_path / defaults.BUILD_SCRIPT_PATH),
            target_script_path=iso_build_dir / defaults.BUILD_SCRIPT_PATH,
        ),
        AutoScriptType.CLEAN: __AutoScriptInfo(
            default_source_script_path=Path(module_path / defaults.CLEAN_SCRIPT_PATH),
            target_script_path=iso_build_dir / defaults.CLEAN_SCRIPT_PATH,
        )
    }

    return script_info[script_type]
