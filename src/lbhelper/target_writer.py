import shutil
from abc import abstractmethod, ABCMeta
from pathlib import Path
from typing import Dict, List

import lbhelper.defaults as defaults
from . import AptPreferenceType
from .run_command import run_command
from .targets import Target, UpstreamPackages, PackagePriority, CustomDeb, HookScript, \
    StaticFile, AptPreference, DirectConfig


class TargetHandler(metaclass=ABCMeta):
    """
    Abstract class for target handlers.
    Must implement the execute method which called by the :class:`TargetWriter`.
    """
    @abstractmethod
    def execute(self, targets: List[Target]):
        """
        Called by the :class:`TargetWriter` as the entrypoint for running main target logic.
        See ``target_handlers`` parameter of :class:`TargetWriter`.

        :param List[Target] targets: List of target to process.
        """
        pass


class TargetWriter:
    """
    Process given targets based on corresponding handler.

    :param Dict[type(Target)] target_handlers: Map of target type to target handlers.
    :param List targets: Targets to process. Elements can be :class:`Target` or List[:class:`Target`].
    """
    def __init__(self, target_handlers: Dict[type(Target), TargetHandler.execute], targets: List):
        self.__targets = targets
        self.__target_handlers = target_handlers

        self.__collected_targets = {target_type: [] for target_type in target_handlers.keys()}

    def execute(self):
        """
        Process given targets based on corresponding handler.
        """
        defaults.DEFAULT_LOGGER.info("Write targets ... ")
        self.__collect_targets(self.__targets)
        self.__write_targets()

    def __collect_targets(self, targets: List):
        defaults.DEFAULT_LOGGER.info("Collecting targets ...")

        for target in targets:
            target_type = type(target)
            if target_type in self.__collected_targets.keys():
                self.__collected_targets[target_type].append(target)

            # if target is a list, then call self.__collect_target to collect targets in it
            elif target_type == list:
                self.__collect_targets(target)
            else:
                raise Exception(f"Unknown target type of target {target}: {target_type}")

        defaults.DEFAULT_LOGGER.info("All targets are collected.")

    def __write_targets(self):
        defaults.DEFAULT_LOGGER.info("Writing collected targets ...")
        for target_type, handler in self.__target_handlers.items():
            handler(self.__collected_targets[target_type])
        defaults.DEFAULT_LOGGER.info("All collected targets are saved.")


class UpstreamPackagesWriter(TargetHandler):
    """
    Write upstream packages to :const:`lbhelper.defaults.PACKAGE_LIST_DIR`.
    
    :param pathlib.Path,Optional iso_build_dir: Image build directory.
    """
    def __init__(self, iso_build_dir: Path):
        self.__package_list_dir = iso_build_dir.joinpath(defaults.PACKAGE_LIST_DIR)

    def execute(self, targets: List[UpstreamPackages]):
        defaults.DEFAULT_LOGGER.info("Writing upstream packages ...")

        for target in targets:
            self.__package_list_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{target.package_set_code}.list.chroot" if not target.live_only else f"{target.package_set_code}.list.chroot_live"
            file_path = self.__package_list_dir / filename

            defaults.DEFAULT_LOGGER.info(f"Writing upstream packages {target.package_set_code} to {file_path}...")
            with open(file_path, "a") as f:
                if target.priority != PackagePriority.NOTSET:
                    f.write(f"! Packages Priority {target.priority}\n\n")

                for package in target.packages:
                    f.write(f"{package}\n")
            defaults.DEFAULT_LOGGER.info(f"Upstream packages {file_path} saved.")

        defaults.DEFAULT_LOGGER.info("All upstream packages saved.")


class CustomDebWriter(TargetHandler):
    """
    Save custom debs to :const:`lbhelper.defaults.CHROOT_DEB_DIR`.
    
    :param pathlib.Path,Optional iso_build_dir: Image build directory.
    :param pathlib.Path,Optional dpkg_name_binary: dpkg-name binary path. Used to correct ``.deb`` file name.
    """
    def __init__(self, iso_build_dir: Path, dpkg_name_binary: Path = defaults.DEFAULT_DPKG_NAME_BINARY):
        self.__chroot_deb_dir = iso_build_dir.joinpath(defaults.CHROOT_DEB_DIR)
        self.__dpkg_name_binary = dpkg_name_binary

    def execute(self, targets: List[CustomDeb]):
        defaults.DEFAULT_LOGGER.info("Writing custom deb ...")

        for target in targets:
            self.__chroot_deb_dir.mkdir(parents=True, exist_ok=True)
            source_deb = target.get_deb()
            temp_deb_path = self.__chroot_deb_dir / source_deb.name
            defaults.DEFAULT_LOGGER.info(f"Copying custom deb {source_deb} to {temp_deb_path}")
            shutil.copy(source_deb, temp_deb_path)
            run_command([str(self.__dpkg_name_binary), str(temp_deb_path)])

        defaults.DEFAULT_LOGGER.info("All custom deb saved.")


class AptPreferencesWriter(TargetHandler):
    """
    Add time apt preferences to :const:`lbhelper.defaults.BUILD_TIME_APT_PREFERENCE_FILE`
    / :const:`lbhelper.defaults.RUN_TIME_APT_PREFERENCE_FILE` depends on preference type.
    
    :param pathlib.Path,Optional iso_build_dir: Image build directory.
    """
    def __init__(self, iso_build_dir: Path):
        self.__build_time_apt_preference_file = iso_build_dir.joinpath(defaults.BUILD_TIME_APT_PREFERENCE_FILE)
        self.__run_time_apt_preference_file = iso_build_dir.joinpath(defaults.RUN_TIME_APT_PREFERENCE_FILE)

    def execute(self, targets: List[AptPreference]):
        defaults.DEFAULT_LOGGER.info("Writing build time apt preferences ...")
        self._write_apt_preferences(targets)
        defaults.DEFAULT_LOGGER.info("All build time apt preferences saved.")

    def _write_apt_preferences(self, targets: List[AptPreference]):
        for target in targets:
            self.__write_single_target(target)

    def __write_single_target(self, target: AptPreference):
        defaults.DEFAULT_LOGGER.info(f"Preference Type: {target.preference_type}")

        preference_file = self.__build_time_apt_preference_file \
            if target.preference_type is AptPreferenceType.BUILD_TIME \
            else self.__run_time_apt_preference_file

        preference_file.parent.mkdir(parents=True, exist_ok=True)

        defaults.DEFAULT_LOGGER.info(
            f"Writing apt preferences of {target.package} to {preference_file}.")
        with open(preference_file, "a") as f:
            f.writelines(
                [
                    f"Package: {target.package}\n",
                    f"Pin: {target.pin}\n",
                    f"Pin-Priority: {target.pin_priority}\n",
                    "\n",
                ]
            )
        defaults.DEFAULT_LOGGER.info(f"Apt preferences of {target.package} saved.")


class HookScriptWriter(TargetHandler):
    """
    Add hook scripts to :const:`lbhelper.defaults.LIVE_HOOKS_DIR` (for live system)
    and :const:`lbhelper.defaults.NORMAL_HOOKS_DIR` (for live/installed system).

    :param pathlib.Path,Optional iso_build_dir: Image build directory.
    """
    def __init__(self, iso_build_dir: Path):
        self.__live_hooks_dir = iso_build_dir.joinpath(defaults.LIVE_HOOKS_DIR)
        self.__normal_hooks_dir = iso_build_dir.joinpath(defaults.NORMAL_HOOKS_DIR)
        
        # hook priority of pre-defined hooks
        self.__builtin_live_hooks_orders = [10, 50]
        self.__builtin_normal_hooks_orders = [
            1000, 1010, 1020,
            5000, 5010, 5020, 5030, 5040, 5050,
            8000, 8010, 8020, 8030, 8040, 8050, 8060, 8070, 8080, 8090, 8100, 8110,
            9000, 9010, 9020
        ]

        self.__current_live_hook_order = 1
        self.__current_normal_hook_order = 1

    def execute(self, targets: List[HookScript]):
        defaults.DEFAULT_LOGGER.info(f"Writing hook scripts ...")

        for target in targets:
            if target.live_only:
                self.__write_single_target(target=target, hook_dir=self.__live_hooks_dir, current_order=self.__current_live_hook_order)
                self.__current_live_hook_order +=1
                if self.__current_live_hook_order in self.__builtin_live_hooks_orders:
                    self.__current_live_hook_order += 1
            else:
                self.__write_single_target(target=target, hook_dir=self.__normal_hooks_dir, current_order=self.__current_normal_hook_order)
                self.__current_normal_hook_order += 1
                if self.__current_normal_hook_order in self.__builtin_normal_hooks_orders:
                    self.__current_normal_hook_order += 1

        defaults.DEFAULT_LOGGER.info(f"All hook scripts saved.")

    @staticmethod
    def __write_single_target(target: HookScript, hook_dir: Path, current_order: int):
        hook_dir.mkdir(parents=True, exist_ok=True)
        hook_filename = f"{current_order:04}-{target.hook_name}.hook.chroot"
        source_path = target.get_script_file()
        target_path = hook_dir / hook_filename

        defaults.DEFAULT_LOGGER.info(f"Writing {source_path} to {target_path}")
        shutil.copy(source_path, target_path)
        defaults.DEFAULT_LOGGER.info(f"Hook {target_path} saved")


class StaticFileWriter(TargetHandler):
    """
    Add static file to :const:`lbhelper.defaults.CHROOT_INCLUDE_DIR` (for live/installed system)
    and :const:`lbhelper.defaults.BINARY_INCLUDE_DIR` (as part of iso).
    
    :param pathlib.Path,Optional iso_build_dir: Image build directory.
    """
    def __init__(self, iso_build_dir: Path):
        self.__chroot_include_dir = iso_build_dir.joinpath(defaults.CHROOT_INCLUDE_DIR)
        self.__binary_include_dir = iso_build_dir.joinpath(defaults.BINARY_INCLUDE_DIR)

    def execute(self, targets: List[StaticFile]):
        defaults.DEFAULT_LOGGER.info("Writing static files ...")

        for target in targets:
            include_dir = self.__binary_include_dir if target.binary_file else self.__chroot_include_dir
            target_file_path = include_dir.joinpath(target.target_filepath.relative_to(target.target_filepath.anchor))
            source_file = target.get_source_file()

            defaults.DEFAULT_LOGGER.info(f"Ensuring parent path of {target_file_path} ... ")
            target_file_path.parent.mkdir(parents=True, exist_ok=True)
            defaults.DEFAULT_LOGGER.info(f"Parent path {target_file_path.parent} created.")

            defaults.DEFAULT_LOGGER.info(f"Writing {source_file} to {target_file_path}")
            if source_file.is_file():
                shutil.copy(source_file, target_file_path)
            else:
                shutil.copytree(source_file, target_file_path, dirs_exist_ok=True, symlinks=True)
            defaults.DEFAULT_LOGGER.info(f"Static file {target_file_path} saved.")

        defaults.DEFAULT_LOGGER.info(f"All static files saved.")


class DirectConfigWriter(TargetHandler):
    """
    Add files to image build directory.

    :param pathlib.Path,Optional iso_build_dir: Image build directory.
    """
    def __init__(self, iso_build_dir: Path):
        self.__iso_build_dir = iso_build_dir

    def execute(self, targets: List[DirectConfig]):
        for target in targets:
            source_file = target.get_source_file()
            target_file_path = self.__iso_build_dir.joinpath(target.target_filepath.relative_to(target.target_filepath.anchor))

            defaults.DEFAULT_LOGGER.info(f"Ensuring parent path of {target_file_path} ... ")
            target_file_path.parent.mkdir(parents=True, exist_ok=True)

            defaults.DEFAULT_LOGGER.info(f"Writing {source_file} to {target_file_path}")
            if source_file.is_file():
                shutil.copy(source_file, target_file_path)
            else:
                shutil.copytree(source_file, target_file_path, dirs_exist_ok=True, symlinks=True)
            defaults.DEFAULT_LOGGER.info(f"Direct config {target_file_path} saved.")

        defaults.DEFAULT_LOGGER.info(f"All direct configs saved.")
