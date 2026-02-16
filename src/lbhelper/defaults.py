import logging
from pathlib import Path

from lbhelper.logger import ConsoleHandler

# ========== Auto Script Related ==========
AUTO_SCRIPT_DIR = Path("auto")
"""
Auto script directory under the image build directory.
"""

BUILD_SCRIPT_PATH = AUTO_SCRIPT_DIR / "build"
"""
``build`` script path under the auto script directory.
"""
CLEAN_SCRIPT_PATH = AUTO_SCRIPT_DIR / "clean"
"""
``clean`` script path under the auto script directory.
"""
CONFIG_SCRIPT_PATH = AUTO_SCRIPT_DIR / "config"
"""
``config`` script path under the auto script directory.
"""

# ========== Config Related ==========
CONFIG_DIR = Path('config')
"""
Configuration directory under the image build directory.
"""

# Static Files related
CHROOT_INCLUDE_DIR = CONFIG_DIR / "includes.chroot"
"""
Files presents in live/installed system
See https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-contents.en.html#live-chroot-local-includes .
"""
BINARY_INCLUDE_DIR = CONFIG_DIR / "includes.binary"
"""
Files presents in iso and system. Similar to :obj:`CHROOT_INCLUDE_DIR`
"""

# Packages related
PACKAGE_LIST_DIR = CONFIG_DIR / "package-lists"
"""
Upstream package lists
See https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-package-installation.en.html
"""
CHROOT_DEB_DIR = CONFIG_DIR / "packages.chroot"
"""
Custom deb directory
See https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-package-installation.en.html#456
"""

# Package Preferences
BUILD_TIME_APT_PREFERENCE_FILE = CONFIG_DIR / "apt" / "preferences"
"""
Build time apt preference file
"""
RUN_TIME_APT_PREFERENCE_FILE = CHROOT_INCLUDE_DIR / "etc" / "apt" / "preferences"
"""
Run time apt preference file
"""

# Hooks
HOOKS_DIR = CONFIG_DIR / "hooks"
"""
Hooks base directory
See https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-contents.en.html#539
"""
LIVE_HOOKS_DIR = HOOKS_DIR / "live"
"""
Live hooks directory
"""
NORMAL_HOOKS_DIR = HOOKS_DIR / "normal"
"""
Normal hooks directory
"""

# Bootloaders
BOOTLOADER_DIR = CONFIG_DIR / "bootloaders"
"""
Live build image bootloader directory
"""
BUILTIN_BOOTLOADER_DIR = Path("/usr/share/live/build/bootloaders")
"""
Default builtin bootloader directory on host. Copied as default bootloaders for live system.
See https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-binary.en.html#640
"""

DEFAULT_LOGGER = logging.getLogger("lbhelper")
"""
Default logger
"""
DEFAULT_LOGGER.setLevel(logging.INFO)
DEFAULT_LOGGER.addHandler(ConsoleHandler())

DEFAULT_ISO_BUILD_DIR = Path("/tmp/iso")
"""
Default image build directory. All configs and files will be copied to here.
"""
DEFAULT_LIVE_BUILD_BINARY = Path("/usr/bin/lb")
"""
Default live build executable path
"""
DEFAULT_DPKG_NAME_BINARY = Path("/usr/bin/dpkg-name")
"""
Default dpkg-name executable path
"""

DEFAULT_IMAGE_NAME = "myos"
"""
Defaul built image name.
"""
DEFAULT_DISTRIBUTION = "trixie"
"""
Default debian distribution.
"""