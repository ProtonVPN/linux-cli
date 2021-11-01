APP_VERSION = "3.10.1"
LOGGER_NAME = "protonvpn-cli"

MAIN_CLI_HELP = """
ProtonVPN CLI v{}

For bugs and errors, please use the form https://protonvpn.com/support-form
or send a report to support@protonvpn.com.

usage:  protonvpn-cli [--version | --help] <command>

commands:
    login               Login with ProtonVPN credentials.
    logout              Disconnect, remove ProtonVPN connection and logout.
    c, connect          Connect to ProtonVPN.
    d, disconnect       Disconnect from ProtonVPN.
    s, status           Show connection status.
    r, reconnect        Reconnect to previously connected server.
    config              Configure user settings.
    ks, killswitch      Configure Kill Switch settings.
    ns, netshield       Configure NetShield settings.

optional arguments:
    -h, --help          Display help message.
    -v, --version       Display versions.
    --get-logs          Get ProtonVPN logs.

examples:
    protonvpn-cli login
    protonvpn-cli login --help
    protonvpn-cli logout
    protonvpn-cli (c | connect)
    protonvpn-cli (c | connect) --help
    protonvpn-cli (d | disconnect)
    protonvpn-cli (s | status)
    protonvpn-cli (r | reconnect)
    protonvpn-cli config
    protonvpn-cli config --help
    protonvpn-cli (-h | --help)
    protonvpn-cli (-v | --version)
    protonvpn-cli --get-logs
""".format(APP_VERSION)

LOGIN_HELP = """
usage:  protonvpn-cli login [-h | --help] <pvpn_username>

positional arguments:
    <pvpn_username> ProtonVPN Username

optional arguments:
    -h, --help      Display help message.

examples:
    protonvpn-cli login pvpn_username
    protonvpn-cli login --help
"""

CONNECT_HELP = """
usage:  protonvpn-cli (c | connect) [-h | --help]
        [[<servername> | [-f | --fastest] | [-r | --random] | --cc | --sc | --p2p | --tor] [-p | --protocol] <protocol>]]

positional arguments:
    <servername>    Directly connecto to
                    specified server (ie: CH#4, CH-US-1, HK5-Tor).

optional arguments:
    -f, --fastest   Connect to the fastest ProtonVPN server.
    -r, --random    Connect to a random ProtonVPN server.
    --cc            Connect to the specified country code (SE, PT, BR, AR).
    --sc            Connect to the fastest Secure-Core server.
    --p2p           Connect to the fastest P2P server.
    --tor           Connect to the fastest Tor server.
    -p , --protocol Connect via specified protocol.
    -h, --help      Display help message.

examples:
    protonvpn-cli connect PT#8 -p tcp
    protonvpn-cli connect --fastest --protocol udp
    protonvpn-cli c --cc PT -p tcp
    protonvpn-cli c --sc
    protonvpn-cli c --p2p -p tcp
    protonvpn-cli connect --tor
    protonvpn-cli c --random --protocol udp
    protonvpn-cli c --help
"""

AUTOSTART_HELP = """
usage:  protonvpn-cli (as | autostart) [-h | --help] [--off | --on]
        [[<servername> | [-f | --fastest] | [-r | --random] | --cc | --sc | --p2p | --tor] [(-p | --protocol) <protocol>] [--gui]]

positional arguments:
    <servername>    Directly connecto to
                    specified server (ie: CH#4, CH-US-1, HK5-Tor).

optional arguments:
    --off, --on     Disable or enable ProtonVPN autostart.
    -f, --fastest   Connect to the fastest ProtonVPN server.
    -r, --random    Connect to a random ProtonVPN server.
    --cc            Connect to the specified country code (SE, PT, BR, AR).
    --sc            Connect to the fastest Secure-Core server.
    --p2p           Connect to the fastest P2P server.
    --tor           Connect to the fastest Tor server.
    -p , --protocol Connect via specified protocol.
    --gui           Autostart ProtonVPN's GUI.
    -h, --help      Display help message.

examples:
    protonvpn-cli autostart --off
    protonvpn-cli autostart --on PT#8 -p tcp
    protonvpn-cli autostart --on --fastest --protocol udp --gui
    protonvpn-cli as --on --cc PT -p tcp
    protonvpn-cli as --on --sc --gui
    protonvpn-cli as --on --p2p -p tcp
    protonvpn-cli autostart --on --tor --gui
    protonvpn-cli as --on --random --protocol udp
    protonvpn-cli as --help
"""

CONFIG_HELP = """
usage:  protonvpn-cli config [-h | --help]
        [[--list | -l] | --dns <command> [--ip <IP>] | [-p | --protocol] <protocol> | [-d | --default] | --vpn-accelerator | --alt-routing]

optional arguments:
    --dns <command>     Change DNS configurations
                        (custom | automatic).
    --ip                Custom DNS IP (max 3 IPs).
    -l, --list          List all configurations.
    -p, --protocol      Change default protocol.
    -d, --default       Reset to default configurations.
    --alt-routing       Change alternative routing preference.
    --vpn-accelerator   VPN Accelerator enables a set of unique performance
                        enhancing technologies which can increase VPN speeds by up to 400%.
    -h, --help          Display help message.

examples:
    protonvpn-cli config --dns automatic
    protonvpn-cli config --dns custom --ip 192.168.0.1
    protonvpn-cli config (-l | --list)
    protonvpn-cli config -p tcp
    protonvpn-cli config --protocol udp
    protonvpn-cli config --vpn-accelerator enable
    protonvpn-cli config --alt-routing enable
    protonvpn-cli config (-d | --default)
    protonvpn-cli config --help
""" # noqa

KS_HELP = """
usage:  protonvpn-cli (ks | killswitch) [-h | --help]
        [--on | --off | --permanent]

optional arguments:
    --on            Start Kill Switch upon connecting to VPN
                    and stop it when disconnecting from VPN.
    --off           Stop and remove Kill Switch.
    --permanent     Start Kill Switch regardless of VPN connection.
                    Warning: This takes effect immediatly and you
                    might end up without internet connection.
                    Either connect to VPN or turn the ks off.
    -h, --help      Display help message.

examples:
    protonvpn-cli (ks | killswitch) --on
    protonvpn-cli (ks | killswitch) --off
    protonvpn-cli (ks | killswitch) --permanent
    protonvpn-cli (ks | killswitch) --help
"""

NETSHIELD_HELP = """
usage:  protonvpn-cli (ns | netshield) [-h | --help]
        [--off | --malware | --ads-malware]

optional arguments:
    --off           Disable NetShield.
    --malware       Block malware.
    --ads-malware   Block malware, ads, & trackers
    -h, --help      Display help message.

examples:
    protonvpn-cli (ns | netshield) --malware
    protonvpn-cli (ns | netshield) --ads-malware
    protonvpn-cli (ns | netshield) --off
    protonvpn-cli (ns | netshield) --help
"""
