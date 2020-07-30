#!/usr/bin/env python3
#
# Copyright © 2020 Endless OS Foundation LLC.
#
# This file is part of clubhouse
# (see https://github.com/endlessm/clubhouse).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# Tool to build and install a Flatpak containing the Clippy Extension.

from _common import (
    create_flatpak_manifest,
    build_flatpak,
    install_flatpak,
    build_bundle,
)

CONFIG_FILE = 'clippy.config.ini'

MANIFEST_FILE = 'katamari/com.hack_computer.Clippy.Extension.json'
APP_ID = 'com.hack_computer.Clippy.Extension'

MODULES = [
    'clippy',
]


def main(config, template=None):
    # Create the manifest:
    create_flatpak_manifest(config, MODULES, MANIFEST_FILE, template)
    if template:
        return

    repo = config.get('Advanced', 'repo')
    flatpak_branch = config.get_flatpak_branch()

    # Build the flatpak:
    build_flatpak(MANIFEST_FILE, config.get_flatpak_build_options())

    # Install the build in the system:
    if config.get('Common', 'install'):
        install_flatpak(repo, flatpak_branch, APP_ID, config.get_flatpak_install_options())

    # Build a flatpak bundle:
    if config.get('Common', 'bundle'):
        build_bundle(repo, flatpak_branch, APP_ID, options=['--runtime'])
