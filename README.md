# Proton VPN Linux CLI

Copyright (c) 2023 Proton Technologies AG

This repository holds the Proton VPN Linux CLI.
For licensing information see [COPYING](COPYING.md).
For contribution policy see [CONTRIBUTING](CONTRIBUTING.md).

## Description
The [Proton VPN](https://protonvpn.com) Linux CLI is intended for every Proton VPN service user.

You can download the latest stable release, either from our official repositories or directly on the [official GitHub repository](https://github.com/ProtonVPN/linux-cli/releases/latest).

### Dependencies:
| **Distro**                              | **Command**                                                                                                     |
|:----------------------------------------|:----------------------------------------------------------------------------------------------------------------|
|Fedora/RHEL                              | `python3-dialog` |
|Ubuntu/Linux Mint/Debian and derivatives | `python3-dialog` |
|Arch Linux/Manjaro                       | `python-pythondialog` |

### Additional dependency:
[Proton VPN NM Library](https://github.com/ProtonVPN/protonvpn-nm-lib)

## Installation
Follow our [knowledge base article](https://protonvpn.com/support/linux-vpn-tool/) on how to install the CLI on your system.

## How to use

| **Command**                           | **Description**                                       |
|:--------------------------------------|:------------------------------------------------------|
|`protonvpn-cli login <pvpn_username>`  | Login with Proton VPN credentials.                    |
|`protonvpn-cli logout`                 | Logout from Proton VPN.                               |
|`protonvpn-cli connect, c`             | Display connect dialog in terminal.                   |
|`protonvpn-cli c [servername]`         | Connect to specified server.                          |
|`protonvpn-cli c -r`                   | Connect to random server.                             |
|`protonvpn-cli c -f`                   | Connect to fastest server.                            |
|`protonvpn-cli c --p2p`                | Connect to fastest P2P server.                        |
|`protonvpn-cli c --cc [countrycode]`   | Connect to fastest server in a specified country.     |
|`protonvpn-cli c --sc`                 | Connect to fastest Secure Core server.                |
|`protonvpn-cli disconnect, d`          | Disconnect from VPN session.                          |
|`protonvpn-cli s, status`              | Display VPN session status.                           |
|`protonvpn-cli config`                 | Change user settings.                                 |
|`protonvpn-cli ks, killswitch`         | Change kill switch settings.                          |
|`protonvpn-cli --version`              | Display version.                                      |
|`protonvpn-cli --help`                 | Show help message.                                    |
