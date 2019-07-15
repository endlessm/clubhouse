#!/usr/bin/env python3

import gi
gi.require_version('Flatpak', '1.0')
from gi.repository import Flatpak

def get_installed_flatpak_names():
    user_installation = Flatpak.Installation.new_user()
    system_installation = Flatpak.Installation.new_system()
    installed_flatpak_refs = (user_installation.list_installed_refs() +
                              system_installation.list_installed_refs())

    for ref in installed_flatpak_refs:
        yield ref.get_name()

for app_name in get_installed_flatpak_names():
    print(app_name)
