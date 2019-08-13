#!/usr/bin/env python3
#
# Tool to build and install a Flatpak containing the Clippy Extension.
#
# Copyright (C) 2019 Endless Mobile, Inc.

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


def main(config, only_manifest=False):
    # Create the manifest:
    create_flatpak_manifest(config, MODULES, MANIFEST_FILE)
    if only_manifest:
        return

    repo = config.get('Advanced', 'repo')
    flatpak_branch = config.get_flatpak_branch()

    # Build the flatpak:
    extra_build_options = config.get('Advanced', 'extra_build_options')
    build_flatpak(repo, MANIFEST_FILE, extra_build_options)

    # Install the build in the system:
    if config.get('Common', 'install'):
        extra_install_options = config.get('Advanced', 'extra_install_options')
        install_flatpak(repo, flatpak_branch, APP_ID, extra_install_options)

    # Build a flatpak bundle:
    if config.get('Common', 'bundle'):
        build_bundle(repo, flatpak_branch, APP_ID, options=['--runtime'])
