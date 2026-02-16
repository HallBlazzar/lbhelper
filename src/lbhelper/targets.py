from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import List, Callable
from abc import ABCMeta


@dataclass
class Target(metaclass=ABCMeta):
    """
    Abstract class for all Targets.
    """
    pass


class PackagePriority(StrEnum):
    """
    Package priority. Used as value of :attr:`.UpstreamPackages.priority`.
    For more details about each value, see https://www.debian.org/doc/debian-policy/ch-archive.html#priorities .
    Note that `NOTSET` denotes not adding priority to result package set file.
    """
    REQUIRED = "required"
    IMPORTANT = "important"
    STANDARD = "standard"
    OPTIONAL = "optional"
    NOTSET = "NOTSET"


@dataclass
class UpstreamPackages(Target):
    """
    A set of upstream packages.

    :param List[str] packages: List of package names
    :param str package_set_code: A unique identifier for the package set.
    :param bool,Optional live_only: Only install in live image. Default is `False` (install in both live and installed system)
    :param PackagePriority,Optional priority: Package priority. `NOTSET` by default.
    """
    packages: List[str]
    package_set_code: str
    live_only: bool = False
    priority: PackagePriority = PackagePriority.NOTSET


@dataclass
class CustomDeb(Target):
    """
    A custom deb package.

    :param Callable[[], pathlib.Path] get_deb: Callback function to get source deb package.
    """

    get_deb: Callable[[], Path]


@dataclass
class HookScript(Target):
    """
    A hook runs in chroot time.
    See https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-contents.en.html#539 .

    :param Callable[[], pathlib.Path] get_script_file: Callback function to get hook shell script.
    :param bool,Optional live_only: Only run in live image.
       Default is `False` (install in both live and installed system).
    """
    get_script_file: Callable[[], Path]
    hook_name: str
    live_only: bool = False


@dataclass
class StaticFile(Target):
    """
    A static file.

    :param pathlib.Path target_filepath: Expected path on built iso/system.
    :param Callable[[], pathlib.Path] get_source_file: Callback function to get source file.
    :param bool,Optional binary_file: Save file in chroot (`False`) to access via live/installed system.
        or as binary (`True`) to access in iso without booting system. `False` by default.
    """
    target_filepath: Path
    get_source_file: Callable[[], Path]
    binary_file: bool = False


@dataclass
class AptPreferenceType(StrEnum):
    """
    Apt preference type. Used as value of :attr:`AptPreference.preference_type`.
    See https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-package-installation.en.html#514
    """
    BUILD_TIME = "build_time"
    RUN_TIME = "run_time"


@dataclass
class AptPreference(Target):
    """
    An apt preference.
    See https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-package-installation.en.html#514
    and https://linux.die.net/man/5/apt_preferences .

    :param str package: Package selector.
    :param str pin: Pin preference.
    :param int pin_priority: Priority.
    :param AptPreferenceType preference_type: Apt preference type. Refer to :class:`AptPreferenceType`.
    """
    package: str
    pin: str
    pin_priority: int
    preference_type: AptPreferenceType


@dataclass
class DirectConfig(Target):
    """
    Directly copying files/directories to arbitrary destinations under an image build directory.
    Avoid directly using this target unless you have special requirements on customizing build
    process, which should be supported by extensions or new targets(PRs welcomed).

    :param pathlib.Path target_filepath: Expected path under the image build directory.
    :param Callable[[], pathlib.Path] get_source_file: Callback function to get source file.
    """
    target_filepath: Path
    get_source_file: Callable[[], Path]
