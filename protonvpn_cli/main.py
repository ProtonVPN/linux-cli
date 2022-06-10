
import os
import sys


def main():
    if "SUDO_UID" in os.environ:
        print(
            "\nRunning Proton VPN as root is not supported and "
            "is highly discouraged, as it might introduce "
            "undesirable side-effects."
        )
        user_input = input("Are you sure that you want to proceed (y/N): ")
        user_input = user_input.lower()
        if not user_input == "y":
            sys.exit(1)

    # Import has to be made here due to dbus delay on ubuntu 18.04,
    # when running with sudo
    from .cli import ProtonVPNCLI
    ProtonVPNCLI()
