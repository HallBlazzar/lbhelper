Setup And Installation
======================

To build a Debian image with ``lbhelper``, you need:

1. A system with runnable live build binary. In general, if you run with Debian based Linux distribution,
   you can install it via ::

     sudo apt install live-build

   For non-Debian based system, the `live build official documents <https://live-team.pages.debian.net/live-manual/html/live-manual/installation.en.html>`__ might help.

2. Install ``lbhelper`` with any package managers you prefer: ::

     pip install -y lbhelper


Containerized/Virtualized Environment
-------------------------

Generally, ``lbhelper`` can run within any containerized or virtualized environment.
However, installing some packages requires a fully functional environment and shell (e.g., `dictionaries-common <https://bugs.launchpad.net/ubuntu/+source/dictionaries-common/+bug/2062979>`__).
To avoid possible issues, we recommend that running ``lbhelper`` on your system or a VM. If you're trying to run in a container, please consider to use the `Distrobox <https://github.com/89luca89/distrobox/tree/main>`__ with assemble manifest like: ::

    [debian-builder]
    additional_packages="git vim live-build"
    image=debian:trixie
    home=/tmp/lbhelper-build
    additional_flags="--cap-add=CAP_SYSLOG --cap-add=CAP_SYS_ADMIN --privileged"
    start_now=true
    root=true
