# Clubhouse

The Clubhouse is one of the main applications in the Hack image, taking the
user on a guided journey through the world of computing.


## Architecture

The Clubhouse is developed in Python as a GTK application.
It has a main window that is treated in a special way by the Shell, and a
a Shell part too.

### GTK Application

The GTK application contains both the UI and also the Quests code, even
though the latter is decoupled from the main application code (as a
different module for now, but in the future it may become a different
process even).

### Shell

The Clubhouse has a [Shell component](https://github.com/endlessm/gnome-shell/blob/master/js/ui/components/clubhouse.js) with two main functions:
 1. Provide the Clubhouse's open and close buttons:
   The open button needs to be available in the desktop/windows views of the
   Shell; the close button is implemented in the Shell because it sits on top
   of the Clubhouse window's left border.
 2. Provide the Shell Quest View:
   There are two quest views (the dialogs that represent a quest) associated
   with the Clubhouse, one in the GTK application itself, and one in the
   Shell so it's displayed on top of every area in the Shell, even when the
   application's window is closed.


## Development

A few helper scripts can be found in the `tools` folder.

### Building a Flatpak

The Clubhouse is distributed as a Flatpak, and it's advisable that it's
developed and debugged as a Flatpak too. To help building the Flatpak, we have
the `build-local-flatpak.sh` script.
This script changes the Flatpak's manifest module for the Clubhouse from a
`git` type, to a `dir` type (meaning it will build files even when not
committed to git yet, which is normally the case when developing), and creates
a local Flatpak repo for the app.
The script also takes any extra arguments for `flatpak-builder`, thus, if you
want to quickly build a Clubhouse Flatpak with any changes you may have done,
and install it in the user installation base, you can do:

`./tools/build-local-flatpak.sh --install`

### Coding Style

The `run_lint` script can be used to verify the codebase's coding style.
Before sending a PR on Github, please verify the coding style with this tool.
In the future we will be running it as part of the Continuous Integration for
PRs.

Since it's easy to forget to run it, there's also a convenience script to set
up a git commit hook that runs the mentioned lint script: `setup-git-hooks`.
If `flake8` (the lint tool that `run_lint` uses) is not in installed, it will
use Python's `virtual-env` to install it locally.

### Quest Dialog Strings

The quests use strings that are edited in a spreadsheet and used as a CSV
file. For quickly fetching the latest spreadsheet and save it directly into
CSV, we have the `get-strings-file` script.

### Quests/Strings Alternative Location

Sometimes it is convenient to be able to run quests or change dialog strings
without having to build a new Flatpak. Thus, any quests' code, or a modified
strings CSV file can be added to a secondary location and will be loaded
directly by the Clubhouse (overriding any quest/string-id with the same name).
this alternative location is: `~/.var/app/com.endlessm.Clubhouse/data/quests`

### Sprite Animations Format

Character animations in the Clubhouse are implemented with
sprites. Each sprite is composed of two files:

- A PNG file that contains all the animation frames, in sequence.

- A JSON file with the metadata required to load and play the frames
  in the PNG as an animation.

This is the format of the JSON file:

```json
{
  "default-delay": 100,
  "frames": [
    "0 750",
    1,
    2,
    3,
    "4 2000-3000",
    3,
    2,
    1,
    "0 2250-6250"
  ],
  "height": 306,
  "width": 147
}
```

All frames are the same size, and is defined by "width" and "height"
in the metadata.

The sequence of frames and timings are defined by "frames" in the
metadata. The frame numbers are zero-based. The sequence has the frame
number, optionally accompanied by a delay. If a delay is not provided,
"default-delay" in the metadata will be used. The delay can be a
number in milliseconds, or it can be a range like `2000-3000`
above. If a range is provided, a random delay will be picked from the
range each time the animation is played. Thus, the same frame can be
reused with different timing in the sequence. The example above
defines an animation using 5 frames. It will:

- Display frame 0 for 750 milliseconds.
- Display frames 1 to 3 in sequence, for the default delay of 100 milliseconds.
- Display frame 4 for a random delay between 2 and 3 seconds.
- Display frames 3 to 1 in reverse sequence, with default delay as before.
- Display frame 0 for a random delay between 2250 and 6250 milliseconds.

The Clubhouse plays the animations in loop.

### Character Animations Alternative Location

There is an alternative path where a designer/developer can place a
character animation that is used instead of the default one. Animators
can use this to test new character animations and edit the current
ones without re-installing the clubhouse. This alternative location
is: `~/.var/app/com.endlessm.Clubhouse/data/characters`

Example:

```
mkdir -p ~/.var/app/com.endlessm.Clubhouse/data/characters/ada/fullbody
(git clone https://github.com/endlessm/clubhouse)
(cd clubhouse)
cp data/characters/ada/fullbody/hi.* ~/.var/app/com.endlessm.Clubhouse/data/characters/ada/fullbody

# Change the animation format here and make Ada go crazy. Example: "frames": [0,8,0,8]
gedit ~/.var/app/com.endlessm.Clubhouse/data/characters/ada/fullbody/hi.json

# Restart the clubhouse:
com.endlessm.Clubhouse -x && com.endlessm.Clubhouse -d
```

## Reloading the Clubhouse

The Clubhouse may still be running even when its window is closed, thus, for
forcing it to quit (in order to e.g. re-run it after adding new content to the
alternative quests' location), you can simply press Ctrl+Escape in its window
(you may have to close and re-open it for the focus to be properly set and the
keyboard shortcut to work).
