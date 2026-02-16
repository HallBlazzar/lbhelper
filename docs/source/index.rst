.. lbhelper documentation master file, created by
   sphinx-quickstart on Tue Jan 13 02:16:53 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

lbhelper documentation
======================

**lbhelper** is a library helps you to customized Debian images.

About ``lbhelper``
------------------
Basically, **lbhelper** is a Python wrapper of `Debian Live Build <https://live-team.pages.debian.net/live-manual/html/live-manual/index.en.html>`__.
It provides a set of declarative targets to define customization options supported by the ``Live Build``.
You don't need to have all knowledge about the ``Live Build`` to use this library.
Instead, this document covers necessary information about supported options and build process, which is enough for you to use this library.

What is ``Live Build`` And How it Works
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``Live Build`` is a toolset for building Debian based images.
The project is maintained by Debian and used to build `official Debian Live Images <https://salsa.debian.org/images-team/debian-cd>`__.
This tool is also used by some Debian based distributions like `Kali Linux <https://www.kali.org/docs/development/live-build-a-custom-kali-iso/>`__.

To create a customized image via ``Live Build``, we need to create a directory to store configurations.
Each sub-directory represents different different configuration as below shows:

.. code-block:: text

    ├── auto                        # live-build auto-scripts. Defines config/build/cleanup options for live-build.
    └── config
        ├── archives                # Package mirrors/repositories
        ├── hooks                   # Extra scripts to run during build stages
        │   ├── live                # Hooks to run on live system
        │   └── normal              # Hooks to run on both live and installed system
        ├── includes.binary         # Files to include on the ISO/CD Rom filesystem
        ├── includes.chroot         # Files to include in the live system's filesystem
        ├── package-lists           # Packages to install
        │   ├── *.list.chroot       # Packages to install on both installed and live system
        │   └── *.list.chroot_live  # Packages to install only on live system
        ├── packages.chroot         # Standalone .deb packages to install on both installed and live system
        ├── apt/preferences         # Build time aptitude preference. Takes effect while building imaage
        ├── etc/apt/preferences     # Aptitude preference from installed system.
        └── bootloaders             # Bootloaders for live system

Live and Installed System
"""""""""""""""""""""""""

An image built from ``Live Build`` is a live system which can run directly on Live CD or Live USB.
By contrast, a system installed from a live system is called installed system.
``Live Build`` allows you to customize packages and scripts run on live and installed systems, which gives you more flexibilities while defining and distributing your images.
For instance, you might want to include `calamares <https://calamares.io/>`__ installer in your live system, which is not expected on an installed system.

Build Process
"""""""""""""

``Live Build`` follows the sequence of actions to build an image:

1. [Bootstrap] Setup a Debian chroot directory. All changes will happen there and won't cause impacts to host.
2. [Chroot] Chroot to the directory.
3. [Packages] Installing packages (``/packages-lists``).
4. [Hooks] Run hooks scripts (``/hooks``).
5. [Binary] Includes static files ( ``/includes.*`` ).
6. [Imaging] Create live image ISO.

What ``lbhelper`` Can Do For You
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In ``lbhelper``, configurable options are turned into ``Targets`` classes.
You can pass these targets to an unified function, ``build_image``, to create configurations required by ``Live Build`` and customize build parameters.
Instead of directly managing/tracking multiple files across configuration directory, ``lbhelper`` helps you organize config dependencies as Python modules.
This approach reduces complexity of configuration management.

Additionally, for some common configuration patterns like setting up GRUB or AppImages,
``lbhelper`` provides extensions to simplify setup works.

What ``lbhelper`` Doesn't Solve
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As the orders of actions in build process are immutable, you still need to carefully manage file dependencies by yourself.
For instance, it's not possible to run a script included in ``Binary`` stage in ``Hooks`` stage.

What's Next
^^^^^^^^^^^

Now you should have basic ideas about what ``lbhelper`` can do for you.
You can jump to different sections to learn how to use it.



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   setup
   lbhelper
   modules
   dev
