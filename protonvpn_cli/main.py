import os
import sys


def main():
    if "SUDO_UID" in os.environ:
        print(
            "\nRunning Proton VPN as root is not supported and "
            "is highly discouraged, as it might introduce "
            "undesirable side-effects."
        )
        if not (choice := input("Are you sure that you want to proceed (y/N): ").lower()) == "y":
            sys.exit(1)

    # Import has to be made here due to dbus delay on ubuntu 18.04,
    # when running with sudo
    from .cli import ProtonVPNCLI
    ProtonVPNCLI()
