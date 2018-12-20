#!/bin/bash -e
#
# Reset the demo.

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

add_icon_to_desktop () {
    echo "Adding icon for app ${1}"
    gdbus call --session \
        --dest org.gnome.Shell \
        --object-path /org/gnome/Shell \
        --method org.gnome.Shell.AppStore.AddApplication "${1}.desktop"
}

echo "---DEMO RESET --- Calling factory reset"
eos-hack-reset-clubhouse

echo "---DEMO RESET --- Waiting"
# @todo: Unreliable way to wait for dbus calls to finish.
sleep 5

echo "---DEMO RESET --- Setting custom game state"
mkdir -p ~/.var/app/com.endlessm.GameStateService/data/
cp "${SCRIPTPATH}/data/state.json" ~/.var/app/com.endlessm.GameStateService/data/state.json

echo "---DEMO RESET --- Setting custom state for Fizzics"
mkdir -p ~/.var/app/com.endlessm.Fizzics/data/webkitgtk/localstorage/
cp "${SCRIPTPATH}/data/fizzics_localstorage" \
    ~/.var/app/com.endlessm.Fizzics/data/webkitgtk/localstorage/file__0.localstorage

echo "---DEMO RESET --- Adding icons to Desktop"
add_icon_to_desktop com.endlessm.Fizzics
add_icon_to_desktop com.endlessm.OperatingSystemApp
add_icon_to_desktop com.endlessm.Hackdex_chapter_one

echo "---DEMO RESET --- Restarting Clubhouse"
gdbus call --session \
    --dest com.endlessm.Clubhouse \
    --object-path /com/endlessm/Clubhouse \
    --method org.gtk.Actions.Activate quit [] []

echo "---DEMO RESET --- DONE"
