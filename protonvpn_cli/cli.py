import argparse
import sys

from proton.constants import VERSION as proton_version
from protonvpn_nm_lib.constants import APP_VERSION as lib_version
from protonvpn_nm_lib.enums import ProtocolEnum

from .cli_wrapper import CLIWrapper
from .constants import (APP_VERSION, CONFIG_HELP,
                        CONNECT_HELP, AUTOSTART_HELP, KS_HELP, LOGIN_HELP, MAIN_CLI_HELP,
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
            "ProtonVPN CLI v{} "
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
                "\nProtonVPN CLI v{} "
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
        """Shortcut to connect to ProtonVPN."""
        return self.connect()

    def connect(self):
        """Connect to ProtonVPN."""
        parser = argparse.ArgumentParser(
            description="Connect to ProtonVPN", prog="protonvpn-cli c",
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
            help="Connect to the fastest ProtonVPN server.",
            action="store_true"
        )
        group.add_argument(
            "-r", "--random",
            help="Connect to a random ProtonVPN server.",
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

    def as(self):
        """Shortcut to autostart ProtonVPN."""

        return self.autostart()

    def autostart(self):
        """Autostart ProtonVPN."""

        parser = argparse.ArgumentParser(description= "Autostart ProtonVPN", prog= "protonvpn-cli as", add_help= False)
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--off", help= "Disable ProtonVPN autostart.", dest= "enabled", action= "store_false")
        group.add_argument("--on", help= "Enable and set up ProtonVPN autostart.", dest= "enabled", action= "store_true")
        parser.set_defaults(enabled= True)
        group = parser.add_mutually_exclusive_group()
        group.add_argument("servername", nargs= "?", help= "Servername (CH#4, CH-US-1, HK5-Tor).", metavar= "")
        group.add_argument("-f", "--fastest", help= "Connect to the fastest ProtonVPN server.", action= "store_true")
        group.add_argument("-r", "--random", help= "Connect to a random ProtonVPN server.", action= "store_true")
        group.add_argument("--cc", help= "Connect to the specified country code (SE, PT, BR, AR).", metavar= "")
        group.add_argument("--sc", help= "Connect to the fastest Secure-Core server.", action= "store_true")
        group.add_argument("--p2p", help= "Connect to the fastest torrent server.", action= "store_true")
        group.add_argument("--tor", help= "Connect to the fastest Tor server.", action= "store_true")
        parser.add_argument("-p", "--protocol", help= "Connect via specified protocol.", choices= [ProtocolEnum.TCP.value, ProtocolEnum.UDP.value], metavar= "", type= str.lower)
        parser.add_argument("--gui", help= "Autostart ProtonVPN's GUI.", action= "store_true")
        parser.add_argument("-h", "--help", required= False, action= "store_true")
        args = parser.parse_args(sys.argv[2:])
        logger.info("Options: {}".format(args))

        if args.help:
            print(AUTOSTART_HELP)
            return 0

        return self.cli_wrapper.autostart(args)

    def d(self):
        """Shortcut to disconnect from ProtonVPN."""
        return self.disconnect()

    def disconnect(self):
        """Disconnect from ProtonVPN."""
        return self.cli_wrapper.disconnect()

    def login(self):
        """Login ProtonVPN."""
        parser = argparse.ArgumentParser(
            description="Connect to ProtonVPN", prog="protonvpn-cli login",
            add_help=False
        )
        parser.add_argument(
            "username",
            help="ProtonVPN username.",
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
        """Logout ProtonVPN."""
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
            description="Connect to ProtonVPN",
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
            description="Connect to ProtonVPN",
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
                description="Set ProtonVPN DNS setting",
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
            description="Connect to ProtonVPN", prog="protonvpn-cli config",
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
            )
        ):
            print(CONFIG_HELP)
            return 0
        elif (
            (
                not args.protocol
                and not args.default
                and not args.alt_routing
                and not args.vpn_accelerator
                and not args.help
            ) or (
                not args.protocol
                and not args.vpn_accelerator
                and not args.alt_routing
                and not args.default
                and args.help
            )
        ) and args.dns and args.dns.pop() == "custom":
            return custom_dns()

        return self.cli_wrapper.configurations_menu(args2)
