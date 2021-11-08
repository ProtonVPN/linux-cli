import copy
import datetime
import getpass
import inspect
import time
from textwrap import dedent
from pathlib import Path
import subprocess

from protonvpn_nm_lib import exceptions
from protonvpn_nm_lib.api import protonvpn
from protonvpn_nm_lib.constants import SUPPORTED_PROTOCOLS
from protonvpn_nm_lib.enums import (ConnectionMetadataEnum,
                                    ConnectionStartStatusEnum,
                                    ConnectionStatusEnum, ConnectionTypeEnum,
                                    DisplayUserSettingsEnum, FeatureEnum,
                                    KillswitchStatusEnum,
                                    NetshieldTranslationEnum, ProtocolEnum,
                                    ProtocolImplementationEnum, ServerTierEnum,
                                    UserSettingStatusEnum,
                                    VPNConnectionStateEnum)

from .cli_dialog import ProtonVPNDialog
from .logger import logger


class CLIWrapper:
    def __init__(self):
        self.SUPPORTED_FEATURES = {
            FeatureEnum.NORMAL: "",
            FeatureEnum.SECURE_CORE: "Secure-Core",
            FeatureEnum.TOR: "Tor",
            FeatureEnum.P2P: "P2P",
            FeatureEnum.STREAMING: "Streaming",
            FeatureEnum.IPv6: "IPv6"
        }
        self.SERVER_TIERS = {
            ServerTierEnum.FREE: "Free",
            ServerTierEnum.BASIC: "Basic",
            ServerTierEnum.PLUS_VISIONARY: "Plus/Visionary",
            ServerTierEnum.PM: "PMTEAM"
        }
        self.KILLSWITCH_STATUS_TEXT = {
            KillswitchStatusEnum.HARD: "Permanent",
            KillswitchStatusEnum.SOFT: "On",
            KillswitchStatusEnum.DISABLED: "Off",
        }
        self.DNS_REMINDER_MESSAGE = "These changes will apply " \
            "the next time you connect to VPN."
        self.CLI_CONNECT_DICT = dict(
            servername=ConnectionTypeEnum.SERVERNAME,
            fastest=ConnectionTypeEnum.FASTEST,
            random=ConnectionTypeEnum.RANDOM,
            cc=ConnectionTypeEnum.COUNTRY,
            sc=ConnectionTypeEnum.SECURE_CORE,
            p2p=ConnectionTypeEnum.PEER2PEER,
            tor=ConnectionTypeEnum.TOR,
        )
        self.protonvpn = protonvpn
        self.user_settings = self.protonvpn.get_settings()
        self.dialog = ProtonVPNDialog(self.protonvpn)

    def login(self, username=None):
        """Proxymethod to login user with ProtonVPN credentials."""
        if self.protonvpn.check_session_exists():
            print("\nYou are already logged in.")
            return 1

        password = getpass.getpass("Enter your ProtonVPN password: ")
        logger.info("Credentials provided, attempting to login")

        retry_or_contact_support = "Please retry or contact support."

        try:
            self.protonvpn.login(username, password)
        except exceptions.API9001Error as e:
            logger.exception(e)
            print(
                "\nHuman Verification is required. "
                "Please use the application to pass the human verification step."
            )
            return 1
        except exceptions.InsecureConnection as e:
            logger.exception(e)
            print(
                "\nYour connection is not secure. "
                "Try changing networks and/or enable alternative routing."
            )
            return 1
        except exceptions.APITimeoutError as e:
            logger.exception(e)
            print("Connection to API timed out.  {}".format(retry_or_contact_support))
            return 1
        except exceptions.UnreacheableAPIError as e:
            logger.exception(e)
            print("Unable to reach API. {}".format(retry_or_contact_support))
            return 1
        except exceptions.APIError as e:
            logger.exception(e)
            print("Error in reaching API. {}".format(retry_or_contact_support))
            return 1
        except exceptions.NetworkConnectionError as e:
            logger.exception(e)
            print("Network Error. {}".format(retry_or_contact_support))
            return 1
        except exceptions.UnknownAPIError as e:
            logger.exception(e)
            print("Unknown API error. {}".format(retry_or_contact_support))
            return 1
        except (
            exceptions.API8002Error, exceptions.API5002Error,
            exceptions.API5003Error, exceptions.API85031Error,
            exceptions.API12087Error
        ) as e:
            logger.exception(e)
            print("\n{}".format(e))
            return 1
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            print(
                "Unknown error occured. If the issue persists, "
                "please contact support."
            )
            return 1

        print("\nSuccessful login.")
        return 0

    def set_alternative_routing(self, status):
        _status = {
            "enable": UserSettingStatusEnum.ENABLED,
            "disable": UserSettingStatusEnum.DISABLED
        }

        try:
            self.user_settings.alternative_routing = _status[status]
        except KeyError as e:
            logger.exception(e)
            print("\nInvalid option was provided")
            return 1
        except Exception as e:
            logger.exception(e)
            print(
                "\nUnable to set alternative routing. "
                "If the issue persists, please contact support."
            )
            return 1

        print("\nAlternative Routing has been {}d. ".format(status))
        return 0

    def logout(self):
        """Proxymethod to logout user."""
        if not self.protonvpn.check_session_exists():
            print("\nNo ProtonVPN session was found, please login first.")
            return 1

        if self.protonvpn.get_active_protonvpn_connection():
            user_choice = input(
                "\nLogging out will disconnect the active VPN connection.\n"
                "Do you want to continue ? [y/N]: "
            ).lower().strip()

            if not user_choice == "y":
                return 0

        print("Attempting to logout.")
        try:
            self.protonvpn.logout()
        except exceptions.KeyringDataNotFound as e:
            logger.exception(e)
            print("\n{}".format(e))
            return 1
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            print("\n{}".format(e))
            return 1

        print(
            "\nSession was ended and "
            "you were successfully logged out."
        )

        return 0

    def connect(self, args):
        """Proxymethod to connect to ProtonVPN."""
        if not self.protonvpn.check_session_exists():
            print("\nNo session was found. Please login first.")
            return 1

        connect_type = False
        connect_type_extra_arg = False
        for cls_attr in inspect.getmembers(args):
            if cls_attr[0] in self.CLI_CONNECT_DICT and cls_attr[1]:
                connect_type = self.CLI_CONNECT_DICT[cls_attr[0]]
                if isinstance(cls_attr[1], bool):
                    connect_type_extra_arg = cls_attr[0]
                    break

                connect_type_extra_arg = cls_attr[1]

        protocol = args.protocol

        if not connect_type and not connect_type_extra_arg:
            try:
                servername, protocol = self.dialog.start()
            except Exception as e:
                logger.exception(e)
                print("\n{}".format(e))
                return 1

            connect_type = ConnectionTypeEnum.SERVERNAME
            connect_type_extra_arg = servername
            protocol = protocol

        print("Setting up ProtonVPN.")
        killswitch_msg = "If Kill Switch is enabled, please disabled " \
            "it temporarily to store necessary configurations."
        relogin_msg = "If you've recently upgraded your plan, please re-login."

        try:
            self.protonvpn.setup_connection(
                connection_type=connect_type,
                connection_type_extra_arg=connect_type_extra_arg,
                protocol=protocol
            )
        except exceptions.ServerCacheNotFound as e:
            logger.exception(e)
            print(
                "\nServer cache is missing. "
                "Please ensure that you have internet connection to "
                "cache servers."
            )
            print(killswitch_msg)
            return 1
        except exceptions.ServernameServerNotFound as e:
            logger.exception(e)
            print(
                "\nNo server could be found with the provided servername.\n"
                "Either the server is under maintenance or\nyou "
                "don't have access to it with your plan."
            )
            print(relogin_msg)
            return 1
        except exceptions.FeatureServerNotFound as e:
            logger.exception(e)
            print(
                "\nNo servers were found with the provided feature.\n"
                "Either the servers with the provided feature are "
                "under maintenance or\nyou don't have access to the "
                "specified feature with your plan."
            )
            print(relogin_msg)
            return 1
        except exceptions.FastestServerInCountryNotFound as e:
            logger.exception(e)
            print(
                "\nNo server could be found with the provided country.\n"
                "Either the provided country is not available or\n"
                "you don't have access to the specified country "
                "with your plan."
            )
            print(relogin_msg)
            return 1
        except (
            exceptions.RandomServerNotFound, exceptions.FastestServerNotFound
        ) as e:
            logger.exception(e)
            print(
                "\nNo server could be found.\n"
                "Please ensure that you have an active internet connection.\n"
                "If the issue persists, please contact support."
            )
            return 1
        except exceptions.DefaultOVPNPortsNotFoundError as e:
            logger.exception(e)
            print(
                "\nThere are missing configurations. "
                "Please ensure that you have internet connection."
            )
            print(killswitch_msg)
            return 1
        except exceptions.IllegalServername as e:
            logger.exception(e)
            print(
                "\nProvided servername is invalid. Please ensure that you've "
                "correctly typed the servername."
            )
            return 1
        except exceptions.DisableConnectivityCheckError as e:
            logger.exception(e)
            print(
                "\nIt was not possible to automatically disable connectivity check. "
                "This step is necessary for the Kill Switch to function properly, "
                "please disable connectivity check copying and pasting the following"
                "command into terminal:\nbusctl set-property org.freedesktop.NetworkManager "
                "/org/freedesktop/NetworkManager org.freedesktop.NetworkManager "
                "ConnectivityCheckEnabled 'b' 0"
            )
            return 1
        except (
            exceptions.API8002Error, exceptions.API5002Error,
            exceptions.API5003Error, exceptions.API85031Error,
            exceptions.API12087Error
        ) as e:
            logger.exception(e)
            print("\n{}".format(e))
            return 1
        except exceptions.API9001Error as e:
            logger.exception(e)
            print(
                "\nHuman Verification is required. "
                "Please use the application to pass the human verification step."
            )
            return 1
        except exceptions.InsecureConnection as e:
            logger.exception(e)
            print(
                "\nYour connection is not secure. "
                "Try changing networks and/or enable alternative routing."
            )
            return 1
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            print(
                "\nAn unknown error has occured. Please ensure that you have "
                "internet connectivity."
                "\nIf the issue persists, please contact support."
            )
            return 1

        return self._connect()

    def autostart(self, args):
        """Proxymethod to autostart ProtonVPN."""

        print("Setting up ProtonVPN autostart.")
        has_service = Path("~/.config/systemd/user/protonvpn-autostart.service").is_file()

        if not args.enabled and has_service:
            try:
                subprocess.run(["systemctl", "--user", "disable", "protonvpn-autostart.service"], check= True)
                print("\nProtonVPN autostart disabled successfully.")
            except subprocess.CalledProcessError as e:
                logger.exception(e)
                print("\nCould not disable ProtonVPN autostart.")
                return 1
        elif args.enabled:
            connect_type = False
            connect_type_extra_arg = False

            for cls_attr in inspect.getmembers(args):
                if cls_attr[0] in self.CLI_CONNECT_DICT and cls_attr[1]:
                    connect_type = self.CLI_CONNECT_DICT[cls_attr[0]]

                    if isinstance(cls_attr[1], bool):
                        connect_type_extra_arg = cls_attr[0]
                        break

                    connect_type_extra_arg = cls_attr[1]

            protocol = args.protocol

            if has_service:
                if connect_type or connect_type_extra_arg or args.gui:
                    active = False

                    try:
                        subprocess.run(["systemctl", "--user", "is-active", "protonvpn.service"], check= True)
                        subprocess.run(["systemctl", "--user", "stop", "protonvpn.service"], check= True)
                        active = True
                    except subprocess.CalledProcessError:
                        pass

                    try:
                        self._generate_service(connect_type, connect_type_extra_arg, protocol, args.gui)
                    except Exception as e:
                        logger.exception(e)
                        print("\nCould not generate service file.")
                        return 1

                    try:
                        subprocess.run(["systemctl", "--user", "daemon-reload"], check= True)
                    except subprocess.CalledProcessError as e:
                        logger.exception(e)
                        print("\nCould not reload Systemd daemon.")
                        return 1

                    if active:
                        try:
                            subprocess.run(["systemctl", "--user", "start", "protonvpn.service"], check= True)
                        except subprocess.CalledProcessError as e:
                            logger.exception(e)
                            print("\nCould not restart service.")
                            return 1
            else:
                if not connect_type and not connect_type_extra_arg:
                    try:
                        servername, protocol = self.dialog.start()
                    except Exception as e:
                        logger.exception(e)
                        print("\n{}".format(e))
                        return 1

                    connect_type = ConnectionTypeEnum.SERVERNAME
                    connect_type_extra_arg = servername
                    protocol = protocol

                try:
                    self._generate_service(connect_type, connect_type_extra_arg, protocol, args.gui)
                except Exception as e:
                    logger.exception(e)
                    print("\nCould not generate service file.")
                    return 1

                try:
                    subprocess.run(["systemctl", "--user", "daemon-reload"], check= True)
                except subprocess.CalledProcessError as e:
                    logger.exception(e)
                    print("\nCould not reload Systemd daemon.")
                    return 1

            try:
                subprocess.run(["systemctl", "--user", "enable", "protonvpn.service"], check= True)
                print("\nProtonVPN autostart enabled successfully.")
            except subprocess.CalledProcessError as e:
                logger.exception(e)
                print("\nCould not enable ProtonVPN autostart.")
                return 1

        return 0

    def _generate_service(self, connect_type, connect_type_extra_arg, protocol, gui):
        unit = "[Unit]"
        unit += "\nDescription=ProtonVPN autostart service"
        unit += "\n\n[Service]"
        unit += "\nType=oneshot"
        unit += "\nRemainAfterExit=yes"

        if self.user_settings.killswitch != KillswitchStatusEnum.DISABLED:
            unit += "\nExecStartPre=-protonvpn-cli ks --off"
            unit += "\nExecStartPre=-protonvpn-cli ks --"

            if self.user_settings.killswitch == KillswitchStatusEnum.HARD:
                unit += "permanent"
            else:
                unit += "on"

        unit += "\nExecStartPre=sh -c \"until systemctl is-active network-online.target; do sleep 1; done\""
        unit += "\nExecStart=protonvpn-cli c "

        if connect_type == ConnectionTypeEnum.FASTEST:
            unit += "-f"
        elif connect_type == ConnectionTypeEnum.RANDOM:
            unit += "-r"
        elif connect_type == ConnectionTypeEnum.SECURE_CORE:
            unit += "--sc"
        elif connect_type == ConnectionTypeEnum.PEER2PEER:
            unit += "--p2p"
        elif connect_type == ConnectionTypeEnum.TOR:
            unit += "--tor"
        elif connect_type == ConnectionTypeEnum.COUNTRY:
            unit += "--cc " + connect_type_extra_arg
        else:
            unit += connect_type_extra_arg

        if protocol != None:
            unit += " -p " + protocol

        if gui:
            unit += "\nExecStartPost=-sh -c \"protonvpn &\""

        unit += "\nTimeoutStartSec=30"
        unit += "\nExecStop=protonvpn-cli d"
        unit += "\nRestart=on-failure"
        unit += "\n\n[Install]"
        unit += "\nWantedBy=default.target"

        with open("~/.config/systemd/user/protonvpn-autostart.service", "w") as file:
            file.write(unit)

    def disconnect(self):
        """Proxymethod to disconnect from ProtonVPN."""
        print("Attempting to disconnect from ProtonVPN.")

        try:
            self.protonvpn.disconnect()
        except exceptions.ConnectionNotFound:
            print(
                "\nNo ProtonVPN connection was found. "
                "Please connect first to a ProtonVPN server."
            )
            return 1
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            print("\n{}".format(e))
            return 1

        print("\nSuccessfully disconnected from ProtonVPN.")
        return 0

    def reconnect(self):
        """Reconnect to previously connected server."""
        print("Gathering previous ProtonVPN connection data.")
        try:
            self.protonvpn.setup_reconnect()
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            print(
                "\nUnable to setup reconnect. "
                "Please make sure that you have access to internet or "
                "that you've previously connected to another server."
            )
            return 1

        return self._connect(True)

    def _connect(self, is_reconnecting=False):
        connection_metadata = self.protonvpn.get_connection_metadata()
        print(
            "{} to ProtonVPN on {} with {}.".format(
                "Reconnecting" if is_reconnecting else "Connecting",
                connection_metadata[
                    ConnectionMetadataEnum.SERVER.value
                ],
                connection_metadata[
                    ConnectionMetadataEnum.PROTOCOL.value
                ].upper(),
            )
        )
        try:
            connect_response = self.protonvpn.connect()
        except Exception as e:
            logger.exception(e)
            print("\n{}".format(e))
            return 1

        logger.info("Dbus response: {}".format(connect_response))

        state = connect_response.get(ConnectionStartStatusEnum.STATE, None)

        if state == VPNConnectionStateEnum.IS_ACTIVE:
            print("\nSuccessfully connected to ProtonVPN.")
            return 0
        else:
            print("\nUnable to connect to ProtonVPN: {}".format(
                connect_response[ConnectionStartStatusEnum.MESSAGE]
            ))
            return 1

    def set_killswitch(self, args):
        """Set kill switch setting.

        Args:
            Namespace (object): list objects with cli args
        """
        logger.info("Setting kill switch to: {}".format(args))
        options_dict = dict(
            permanent=KillswitchStatusEnum.HARD,
            on=KillswitchStatusEnum.SOFT,
            off=KillswitchStatusEnum.DISABLED
        )
        contextual_conf_msg = {
            KillswitchStatusEnum.HARD: "Permanent kill switch has been enabled.", # noqa
            KillswitchStatusEnum.SOFT:"Kill switch has been enabled. Please reconnect to VPN to activate it.", # noqa
            KillswitchStatusEnum.DISABLED: "Kill switch has been disabled."
        }
        for cls_attr in inspect.getmembers(args):
            if cls_attr[0] in options_dict and cls_attr[1]:
                kill_switch_option = options_dict[cls_attr[0]]

        try:
            self.user_settings.killswitch = kill_switch_option
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            print(e)
            return 1

        print("\n{}".format(contextual_conf_msg[kill_switch_option]))
        return 0

    def set_netshield(self, args):
        """Set netshield setting.

        Args:
            Namespace (object): list objects with cli args
        """
        logger.info("Setting netshield to: {}".format(args))
        if not self.protonvpn.check_session_exists():
            print("\nPlease login to to be able to set NetShield.")
            return 1

        # To-do: Once infra is updated, implement this check
        # if not self.protonvpn.get_session().clientconfig.features.netshield:
        #     print("\nThis feature is currently not supported.")
        #     return

        session = self.protonvpn.get_session()
        if not args.off and session.vpn_tier == ServerTierEnum.FREE.value:
            print(
                "\nBrowse the Internet free of malware, ads, "
                "and trackers with NetShield.\n"
                "To use NetShield, upgrade your subscription at: "
                "https://account.protonvpn.com/dashboard"
            )
            return 1

        restart_vpn_message = ""
        if self.protonvpn.get_active_protonvpn_connection():
            restart_vpn_message = " Please restart your VPN connection "\
                "to enable NetShield."

        contextual_confirmation_msg = {
            NetshieldTranslationEnum.MALWARE: "Netshield set to protect against malware.", # noqa
            NetshieldTranslationEnum.ADS_MALWARE: "Netshield set to protect against ads and malware.", # noqa
            NetshieldTranslationEnum.DISABLED: "Netshield has been disabled."
        }

        options_dict = dict(
            malware=NetshieldTranslationEnum.MALWARE,
            ads_malware=NetshieldTranslationEnum.ADS_MALWARE,
            off=NetshieldTranslationEnum.DISABLED
        )

        for cls_attr in inspect.getmembers(args):
            if cls_attr[0] in options_dict and cls_attr[1]:
                user_choice = options_dict[cls_attr[0]]

        try:
            self.user_settings.netshield = user_choice
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            print("\n{}".format(e))
            return 1

        print(
            "\n" + contextual_confirmation_msg[user_choice]
            + restart_vpn_message
        )
        return 0

    def configurations_menu(self, args):
        """Configure user settings."""
        logger.info("Starting to configure")
        cli_config_commands = dict(
            protocol=self.set_protocol,
            dns=self.set_automatic_dns,
            ip=self.set_custom_dns,
            list=self.list_configurations,
            vpn_accelerator=self.set_vpn_accelerator,
            alt_routing=self.set_alternative_routing,
            default=self.restore_default_configurations,
        )

        for cls_attr in inspect.getmembers(args):
            if cls_attr[0] in cli_config_commands and cls_attr[1]:
                command = list(cls_attr)

        if "ip" in command:
            option_value = command[1]
        else:
            try:
                option_value = command[1].pop()
            except (KeyError, AttributeError):
                option_value = None

        return cli_config_commands[command[0]](option_value)

    def set_protocol(self, protocol):
        try:
            self.user_settings.protocol = ProtocolEnum(protocol)
        except (exceptions.ProtonVPNException, Exception) as e:
            logger.exception(e)
            print(e)
            return 1

        if protocol in SUPPORTED_PROTOCOLS[ProtocolImplementationEnum.OPENVPN]:
            protocol = "OpenVPN (" + protocol.value.upper() + ")"

        print(
            "\nDefault connection protocol "
            "has been updated to OpenVPN ({}).".format(
                protocol.upper()
            )
        )
        return 0

    def set_automatic_dns(self, _):
        """Set DNS setting."""
        logger.info("Setting dns to automatic")

        try:
            self.user_settings.dns = UserSettingStatusEnum.ENABLED
        except Exception as e:
            logger.exception(e)
            print(e)
            return 1

        confirmation_message = "\nDNS automatic configuration enabled.\n" \
            + self.DNS_REMINDER_MESSAGE

        print(confirmation_message)
        return 0

    def set_custom_dns(self, dns_ip_list):
        if len(dns_ip_list) > 3:
            logger.error("More then 3 custom DNS IPs were provided")
            print(
                "\nYou provided more then 3 DNS servers. "
                "Please enter up to 3 DNS server IPs."
            )
            return 1

        try:
            self.user_settings.dns_custom_ips = dns_ip_list
        except Exception as e:
            logger.exception(e)
            print(e)
            return 1

        self.user_settings.dns = UserSettingStatusEnum.CUSTOM

        print_custom_dns_list = ", ".join(dns for dns in dns_ip_list)
        confirmation_message = "\nDNS will be managed by "\
            "the provided custom IPs: \n{}\n\n{}".format(
                print_custom_dns_list,
                self.DNS_REMINDER_MESSAGE
            )
        print(confirmation_message)
        return 0

    def set_vpn_accelerator(self, status):
        if not self.protonvpn.check_session_exists():
            print("\nPlease login to be able to set VPN Accelerator.")
            return 1
        if not self.protonvpn.get_session().clientconfig.features.vpn_accelerator:
            print("\nThis feature is currently not supported.")
            return 1

        status = (
            UserSettingStatusEnum.ENABLED
            if status == "enable"
            else UserSettingStatusEnum.DISABLED
        )

        try:
            self.user_settings.vpn_accelerator = status
        except Exception as e:
            logger.exception(e)
            print(e)
            return 1

        reconnect_message = "If connected to VPN, please reconnect for " \
            "changes to take effect."
        contextual_message = "VPN accelerator has been disabled."
        if status == UserSettingStatusEnum.ENABLED:
            contextual_message = "VPN accelerator has been enabled."

        print("\n{} {}".format(contextual_message, reconnect_message))
        return 0

    def list_configurations(self, _):
        try:
            user_settings_dict = self.__transform_user_setting_to_readable_format(
                self.user_settings.get_user_settings()
            )
        except: # noqa
            print("\nUnable to display configurations")
            return 1

        status_to_print = dedent("""
            ProtonVPN User Settings
            ---------------------------
            Default Protocol:\t{protocol}
            Kill Switch:\t\t{killswitch}
            Netshield:\t\t{netshield}
            DNS:\t\t\t{dns}
            Alternative Routing:\t{alt_routing}
            VPN Accelerator:\t{vpn_accel}
        """).format(
            protocol=user_settings_dict[DisplayUserSettingsEnum.PROTOCOL],
            alt_routing=user_settings_dict[DisplayUserSettingsEnum.ALT_ROUTING],
            killswitch=user_settings_dict[DisplayUserSettingsEnum.KILLSWITCH],
            netshield=user_settings_dict[DisplayUserSettingsEnum.NETSHIELD],
            vpn_accel=user_settings_dict[DisplayUserSettingsEnum.VPN_ACCELERATOR],
            dns=user_settings_dict[DisplayUserSettingsEnum.DNS],
        )
        print(status_to_print)
        return 0

    def __transform_user_setting_to_readable_format(self, raw_format):
        """Transform the dict in raw_format to human readeable format.

        Args:
            raw_format (dict)

        Returns:
            dict
        """
        raw_protocol = raw_format[DisplayUserSettingsEnum.PROTOCOL]
        raw_ks = raw_format[DisplayUserSettingsEnum.KILLSWITCH]
        raw_dns = raw_format[DisplayUserSettingsEnum.DNS]
        raw_custom_dns = raw_format[DisplayUserSettingsEnum.CUSTOM_DNS]
        raw_ns = raw_format[DisplayUserSettingsEnum.NETSHIELD]
        raw_alt_routing = raw_format[DisplayUserSettingsEnum.ALT_ROUTING]
        raw_vpn_accel = raw_format[DisplayUserSettingsEnum.VPN_ACCELERATOR]

        # protocol
        if raw_protocol in SUPPORTED_PROTOCOLS[ProtocolImplementationEnum.OPENVPN]: # noqa
            transformed_protocol = "OpenVPN ({})".format(
                raw_protocol.value.upper()
            )
        else:
            transformed_protocol = raw_protocol.value.upper()

        # killswitch
        transformed_ks = self.KILLSWITCH_STATUS_TEXT[raw_ks]

        # dns
        dns_status = {
            UserSettingStatusEnum.ENABLED: "Automatic",
            UserSettingStatusEnum.CUSTOM: "Custom: {}".format(
                ", ".join(raw_custom_dns)
            ),
        }
        transformed_dns = dns_status[raw_dns]

        # netshield
        netshield_status = {
            NetshieldTranslationEnum.MALWARE: "Malware", # noqa
            NetshieldTranslationEnum.ADS_MALWARE: "Ads and malware", # noqa
            NetshieldTranslationEnum.DISABLED: "Disabled" # noqa
        }
        transformed_ns = netshield_status[raw_ns]

        # vpn accelerator
        transformed_vpn_accel = "Enabled" if raw_vpn_accel == UserSettingStatusEnum.ENABLED else "Disabled" # noqa

        # alternative_routing
        transformed_alt_routing = "Enabled" if raw_alt_routing == UserSettingStatusEnum.ENABLED else "Disabled" # noqa

        return {
            DisplayUserSettingsEnum.PROTOCOL: transformed_protocol,
            DisplayUserSettingsEnum.KILLSWITCH: transformed_ks,
            DisplayUserSettingsEnum.DNS: transformed_dns,
            DisplayUserSettingsEnum.NETSHIELD: transformed_ns,
            DisplayUserSettingsEnum.ALT_ROUTING: transformed_alt_routing,
            DisplayUserSettingsEnum.VPN_ACCELERATOR: transformed_vpn_accel,
        }

    def restore_default_configurations(self, _):
        """Restore default configurations."""
        user_choice = input(
            "\nAre you sure you want to restore to "
            "default configurations? [y/N]: "
        ).lower().strip()

        if not user_choice == "y":
            return 0

        logger.info("Restoring default configurations")

        print("Restoring default ProtonVPN configurations...")
        time.sleep(0.5)

        try:
            self.user_settings.reset_to_default_configs()
        except Exception as e:
            print("\n{}".format(e))
            return 1

        print("\nConfigurations were successfully reset to default values.")
        return 0

    def get_logs(self):
        bug_report = self.protonvpn.get_bug_report()
        print("\nGenerating logs...")
        try:
            bug_report.generate_logs()
        except Exception as e:
            logger.exception(e)
            print("\nUnable to generate logs:", format(e))
            return 1

        print("Opening file explorer...")
        try:
            bug_report.open_folder_with_logs()
        except Exception as e:
            logger.exception(e)
            print(
                "\nUnable to open file explorer with logs."
                "You can find logs at ~/.cache/protonvpn/logs"
            )
            return 1

        return 0

    def status(self):
        """Proxymethod to diplay connection status."""
        if not self.protonvpn.get_active_protonvpn_connection():
            print("\nNo active ProtonVPN connection.")
            return 0

        # cache servers if needed
        try:
            self.protonvpn.get_session().servers
        except: # noqa
            pass

        logger.info("Gathering connection information")
        conn_status_dict = self.__transform_status_to_readable_format(
            self.protonvpn.get_connection_status()
        )
        server = conn_status_dict.pop(
            ConnectionStatusEnum.SERVER_INFORMATION
        )

        tier_enum = ServerTierEnum(server.tier)
        _features = copy.copy(server.features)
        try:
            _features.pop(FeatureEnum.NORMAL)
        except IndexError:
            pass

        if len(_features) > 1:
            features = ", ".join(
                [self.SUPPORTED_FEATURES[feature] for feature in _features]
            )
        elif len(_features) == 1:
            features = self.SUPPORTED_FEATURES[_features[0]]
        else:
            features = "None"
        features = "Server Features: " + features
        entry_country = self.protonvpn.get_country().get_country_name(
            server.entry_country
        )
        exit_country = self.protonvpn.get_country().get_country_name(
            server.exit_country
        )

        status_to_print = dedent("""
            ProtonVPN Connection Status
            ---------------------------
            IP: \t\t {server_ip}
            Server: \t {server}
            Country: \t {secure_core}{country}
            Protocol: \t {proto}
            Server Load: \t {load}%
            Server Plan: \t {server_tier}
            {features}Kill switch: \t {killswitch_status}
            Connection time: {time}
        """).format(
            server_ip="(Missing)"
            if not ConnectionStatusEnum.SERVER_IP
            else conn_status_dict[ConnectionStatusEnum.SERVER_IP],
            country=exit_country,
            city=server.city,
            server=server.name,
            load=int(server.load),
            server_tier=self.SERVER_TIERS[tier_enum],
            features=""
            if len(_features) == 0
            else features + "\n",
            secure_core=(
                "{} >> ".format(entry_country)
                if FeatureEnum.SECURE_CORE in _features
                else ""
            ),
            killswitch_status=conn_status_dict[
                ConnectionStatusEnum.KILLSWITCH
            ],
            proto=conn_status_dict[ConnectionStatusEnum.PROTOCOL],
            time=conn_status_dict[ConnectionStatusEnum.TIME],
        )
        print(status_to_print)

        return 0

    def __transform_status_to_readable_format(self, raw_dict):
        """Transform raw dict to human redeable vales:

        Args:
            raw_dict (dict)

        Returns:
            dict
        """
        server_information_dict = raw_dict[
            ConnectionStatusEnum.SERVER_INFORMATION
        ]
        raw_protocol = raw_dict[ConnectionStatusEnum.PROTOCOL]
        raw_ks = raw_dict[ConnectionStatusEnum.KILLSWITCH]
        raw_ns = raw_dict[ConnectionStatusEnum.NETSHIELD]
        raw_time = raw_dict[ConnectionStatusEnum.TIME]
        server_ip = raw_dict[ConnectionStatusEnum.SERVER_IP]

        # protocol
        if raw_protocol in SUPPORTED_PROTOCOLS[ProtocolImplementationEnum.OPENVPN]: # noqa
            transformed_protocol = "OpenVPN ({})".format(
                raw_protocol.value.upper()
            )
        else:
            transformed_protocol = raw_protocol.value.upper()

        ks_add_extra = ""
        logger.info("KS status: {} - User setting: {}".format(
            raw_ks, self.user_settings.killswitch
        ))

        if (
            raw_ks == KillswitchStatusEnum.DISABLED
            and self.user_settings.killswitch != KillswitchStatusEnum.DISABLED
        ):
            ks_add_extra = "(Inactive, restart connection to activate KS)"

        transformed_ks = self.KILLSWITCH_STATUS_TEXT[
            self.user_settings.killswitch
        ] + " " + ks_add_extra

        # netshield
        netshield_status = {
            NetshieldTranslationEnum.MALWARE: "Malware", # noqa
            NetshieldTranslationEnum.ADS_MALWARE: "Ads and malware", # noqa
            NetshieldTranslationEnum.DISABLED: "Disabled" # noqa
        }
        transformed_ns = netshield_status[raw_ns]

        transformed_time = self.__convert_time_from_epoch(
            raw_time
        )

        return {
            ConnectionStatusEnum.SERVER_INFORMATION: server_information_dict, # noqa
            ConnectionStatusEnum.PROTOCOL: transformed_protocol,
            ConnectionStatusEnum.KILLSWITCH: transformed_ks,
            ConnectionStatusEnum.TIME: transformed_time,
            ConnectionStatusEnum.NETSHIELD: transformed_ns,
            ConnectionStatusEnum.SERVER_IP: server_ip,
        }

    def __convert_time_from_epoch(self, seconds_since_epoch):
        """Convert time from epoch to 24h.

        Args:
           time_in_epoch (string): time in seconds since epoch

        Returns:
            string: time in 24h format, since last connection was made
        """
        connection_time = (
            time.time()
            - int(seconds_since_epoch)
        )
        return str(
            datetime.timedelta(
                seconds=connection_time
            )
        ).split(".")[0]
