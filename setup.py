#!/usr/bin/env python

from setuptools import find_packages, setup
from protonvpn_cli.constants import APP_VERSION

long_description = """
Official Proton VPN CLI for Linux based systems.
"""

setup(
    name="protonvpn-cli",
    version=APP_VERSION,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "protonvpn-cli = protonvpn_cli.main:main"
        ]
    },
    description="Official Proton VPN CLI for Linux",
    author="Proton Technologies AG",
    author_email="contact@protonvpn.com",
    long_description=long_description,
    install_requires=[
        "protonvpn-nm-lib>=3.4.0", "pythondialog"
    ],
    include_package_data=True,
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Security",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
