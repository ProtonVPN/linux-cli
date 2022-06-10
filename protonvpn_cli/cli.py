import argparse
import sys

from proton.constants import VERSION as proton_version
from protonvpn_nm_lib.constants import APP_VERSION as lib_version
from protonvpn_nm_lib.enums import ProtocolEnum

from .cli_wrapper import CLIWrapper
from .constants import (APP_VERSION, CONFIG_HELP,
                        CONNECT_HELP, KS_HELP, LOGIN_HELP, MAIN_CLI_HELP,
                        NETSHIELD_HELP)
from .logger import logger


class ProtonVPNCLI:
    def __init__(self):
        logger.info(
            "\n"
            + "---------------------"
            + "----------------"
            + "------------\n\n"
            + "-----------\t"
            + "Initialized protonvpn-cli"
            + "\t-----------\n\n"
            + "---------------------"
            + "----------------"
            + "------------"
        )
        logger.info(
            "Proton VPN CLI v{} "
            "(protonvpn-nm-lib v{}; proton-client v{})".format(
                APP_VERSION, lib_version, proton_version
            )
        )

        self.cli_wrapper = CLIWrapper()
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("command", nargs="?")
        parser.add_argument(
            "-v", "--version", required=False, action="store_true"
        )
        parser.add_argument(
            "-h", "--help", required=False, action="store_true"
        )
        parser.add_argument(
            "--get-logs", required=False, action="store_true"
        )
        args = parser.parse_args(sys.argv[1:2])

        if args.version:
            print(
                "\nProton VPN CLI v{} "
                "(protonvpn-nm-lib v{}; proton-client v{})".format(
                    APP_VERSION, lib_version, proton_version
                )
            )
            res = 0
        elif args.get_logs:
            res = self.cli_wrapper.get_logs()
        elif not args.command or not hasattr(self, args.command) or args.help:
            print(MAIN_CLI_HELP)
            res = 0
        else:
            logger.info("CLI command: {}".format(args))
            res = getattr(self, args.command)()

        parser.exit(res)

    def c(self):
        """Shortcut to connect to Proton VPN."""
        return self.connect()

    def connect(self):
        """Connect to Proton VPN."""
        parser = argparse.ArgumentParser(
            description="Connect to Proton VPN", prog="protonvpn-cli c",
            add_help=False
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "servername",
            nargs="?",
            help="Servername (CH#4, CH-US-1, HK5-Tor).",
            metavar=""
        )
        group.add_argument(
            "-f", "--fastest",
            help="Connect to the fastest Proton VPN server.",
            action="store_true"
        )
        group.add_argument(
            "-r", "--random",
            help="Connect to a random Proton VPN server.",
            action="store_true"
        )
        group.add_argument(
            "--cc",
            help="Connect to the specified country code (SE, PT, BR, AR).",
            metavar=""
        )
        group.add_argument(
            "--sc",
            help="Connect to the fastest Secure-Core server.",
            action="store_true"
        )
        group.add_argument(
            "--p2p",
            help="Connect to the fastest torrent server.",
            action="store_true"
        )
        group.add_argument(
            "--tor",
            help="Connect to the fastest Tor server.",
            action="store_true"
        )
        parser.add_argument(
            "-p", "--protocol", help="Connect via specified protocol.",
            choices=[
                ProtocolEnum.TCP.value,
                ProtocolEnum.UDP.value,
            ], metavar="", type=str.lower
        )
        parser.add_argument(
            "-h", "--help", required=False, action="store_true"
        )

        args = parser.parse_args(sys.argv[2:])
        logger.info("Options: {}".format(args))
        if args.help:
            print(CONNECT_HELP)
            return 0

        return self.cli_wrapper.connect(args)

    def d(self):
        """Shortcut to disconnect from Proton VPN."""
        return self.disconnect()

    def disconnect(self):
        """Disconnect from Proton VPN."""
        return self.cli_wrapper.disconnect()

    def login(self):
        """Login Proton VPN."""
        parser = argparse.ArgumentParser(
            description="Connect to Proton VPN", prog="protonvpn-cli login",
            add_help=False
        )
        parser.add_argument(
            "username",
            help="Proton VPN username.",
            nargs="?",
        )
        parser.add_argument(
            "-h", "--help", required=False, action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])
        if args.help or args.username is None:
            print(LOGIN_HELP)
            return 0

        return self.cli_wrapper.login(args.username)

    def logout(self):
        """Logout Proton VPN."""
        return self.cli_wrapper.logout()

    def s(self):
        """Shortcut to display connection status"""
        return self.status()

    def status(self):
        """Display connection status."""
        return self.cli_wrapper.status()

    def ks(self):
        """Shortcut to manage killswitch settings."""
        return self.killswitch()

    def killswitch(self):
        """Manage killswitch settings."""
        parser = argparse.ArgumentParser(
            description="Connect to Proton VPN",
            prog="protonvpn-cli killswitch",
            add_help=False
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--on",
            help="Enable killswitch.",
            action="store_true"
        )
        group.add_argument(
            "--off",
            help="Disable killswitch.",
            action="store_true"
        )
        group.add_argument(
            "--permanent",
            help="Permanent killswitch.",
            action="store_true"
        )
        parser.add_argument(
            "-h", "--help", required=False, action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])
        if args.help or (
            not args.help
            and not args.on
            and not args.off
            and not args.permanent
        ):
            print(KS_HELP)
            return 0

        logger.info("Kill Switch command: {}".format(args))
        return self.cli_wrapper.set_killswitch(args)

    def r(self):
        """Shortcut to reconnect."""
        return self.reconnect()

    def reconnect(self):
        """Reconnect to previously connected server."""
        return self.cli_wrapper.reconnect()

    def ns(self):
        """Shortcut to manage NetShield settings."""
        return self.netshield()

    def netshield(self):
        """Manage NetShield settings."""
        parser = argparse.ArgumentParser(
            description="Connect to Proton VPN",
            prog="protonvpn-cli netshield",
            add_help=False
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--off",
            help="Disable NetShield.",
            action="store_true"
        )
        group.add_argument(
            "--malware",
            help="Block malware.",
            action="store_true"
        )
        group.add_argument(
            "--ads-malware",
            help="Block malware, ads, & trackers.",
            action="store_true",
        )
        parser.add_argument(
            "-h", "--help", required=False, action="store_true"
        )
        args = parser.parse_args(sys.argv[2:])
        if args.help or (
            not args.help
            and not args.malware
            and not args.ads_malware
            and not args.off
        ):
            print(NETSHIELD_HELP)
            return 0

        logger.info("NetShield command: {}".format(args))
        return self.cli_wrapper.set_netshield(args)

    def config(self):
        """Manage user settings."""
        def custom_dns():
            parser = argparse.ArgumentParser(
                description="Set Proton VPN DNS setting",
                prog="protonvpn-cli config --dns custom",
                add_help=False
            )
            group = parser.add_mutually_exclusive_group()
            group.add_argument(
                "--ip",
                help="Custom DNS IPs.",
                nargs="+",
            )
            args = parser.parse_args(sys.argv[4:])
            logger.info("Config DNS command: {}".format(args))

            if not args.ip:
                print(CONFIG_HELP)
                return 0

            return self.cli_wrapper.configurations_menu(args)

        parser = argparse.ArgumentParser(
            description="Connect to Proton VPN", prog="protonvpn-cli config",
            add_help=False
        )
        group = parser.add_mutually_exclusive_group()
        parser.add_argument(
            "-h", "--help", required=False, action="store_true"
        )
        group.add_argument(
            "--dns",
            help="DNS settings.",
            nargs=1,
            choices=[
                "automatic",
                "custom",
            ]
        )
        group.add_argument(
            "--vpn-accelerator",
            help="VPN Accelerator enables a set of unique performance "
            "enhancing technologies which can increase VPN speeds "
            "by up to 400%",
            nargs=1,
            choices=[
                "enable",
                "disable",
            ]
        )
        group.add_argument(
            "-p", "--protocol",
            help="Protocol settings.",
            nargs=1,
            choices=[
                ProtocolEnum.TCP.value,
                ProtocolEnum.UDP.value,
            ]
        )
        group.add_argument(
            "--alt-routing",
            help="Alternative routing.",
            nargs=1,
            choices=[
                "enable",
                "disable",
            ]
        )
        group.add_argument(
            "--moderate-nat",
            help="Moderate NAT.",
            nargs=1,
            choices=[
                "enable",
                "disable",
            ]
        )
        group.add_argument(
            "--non-standard-ports",
            help="Non Standard Ports.",
            nargs=1,
            choices=[
                "enable",
                "disable",
            ]
        )
        group.add_argument(
            "-d", "--default",
            help="Reset do default configurations.",
            action="store_true"
        )
        group.add_argument(
            "-l", "--list",
            help="List user settings.",
            action="store_true"
        )

        args = parser.parse_args(sys.argv[2:4])
        args2 = parser.parse_args(sys.argv[2:4])

        logger.info("Config command: {}".format(args2))
        if (
            args.help
            or (
                not args.dns
                and not args.protocol
                and not args.help
                and not args.default
                and not args.list
                and not args.vpn_accelerator
                and not args.alt_routing
                and not args.moderate_nat
                and not args.non_standard_ports
            )
        ):
            print(CONFIG_HELP)
            return 0
        elif (
            not args.protocol
            and not args.default
            and not args.alt_routing
            and not args.vpn_accelerator
            and not args.moderate_nat
            and not args.non_standard_ports
            and not args.help

        ) and args.dns and args.dns.pop() == "custom":
            return custom_dns()

        return self.cli_wrapper.configurations_menu(args2)
