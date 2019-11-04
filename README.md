# Clubhouse

The Clubhouse is one of the main applications in the Hack image, taking the
user on a guided journey through the world of computing.


## Architecture

The Clubhouse is developed in Python as a GTK application.
It has a main CSD window and a shell component to provide custom system level
dialogs.

### GTK Application

The GTK application contains both the UI and also the Quests code, even
though the latter is decoupled from the main application code (as a
different module for now, but in the future it may become a different
process even).
The main window adapts itself to the screen resolution using 75% of the screen
height and using the background aspect ratio for its width.
The supported resolution range goes from 720p to 1080p and different CSS classes
are used to adapt the rest of the UI other than the artwork to the different
sizes.

### Shell

The Clubhouse has a [Shell component](https://github.com/endlessm/gnome-shell/blob/master/js/ui/components/clubhouse.js) with the main functions:
 1. Provide the Shell Quest View:
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

The `run-lint` script can be used to verify the codebase's coding style. The
lint check is run by the local build script mentioned above, so the build
should fail if there are lint issues. It also means that the lint is run on
any PR on Github.

There's also a convenience script to set up a git commit hook that runs the
mentioned lint script: `setup-git-hooks`. It will use Python's `virtual-env`
to install the lint module locally with `pip` which also ensures that all
developers run the same version of the lint module.

**Pro tip:** If you work frequently in the Clubhouse, it may be time consuming
to have the lint check running on every build, thus, in order to avoid that, the
lint check is actually turned off by the `build-local-flatpak.sh` script if the
git pre-commit hook is set up.

### Building the documentation

The `build-docs` script can be used to build the documentation.

## Quest Dialog Information

For easier authoring of the story, the quests use information that is edited
separately in a spreadsheet, one per row. The minimum information is, one per
column:

- **Message ID**: The quest authors add it to the spreadsheet and use it in
  quests to reference the text below and the rest of the information. The
  message ID doesn't usually change.

- **Text**: The text itself. Quest authors usually add temporary text. Then the
  text is changed and fine-tuned at any time by the story writters. Sometimes
  simple text markup can be used, see below.

This is enough for cases like button labels. Dialogue boxes have more
(optional) information:

- **Speaker**: The character saying the words. Defaults to the main character
  of the quest.

- **Animation**: The animation to play for the character speaking. Defaults to
  a talking animation.

- **SFX**: Code for a sound effect to replace the default dialogue popup
  sound. It will only play if it's a valid code in the sound server.

- **BG**: Code for a background sound. It lasts until the last consecutive
  dialog box that has this same sound listed as BG is closed. It will only play
  if it's a valid code in the sound server.

Message IDs should be prefixed with a quest name, or with the special prefix
`NOQUEST`. Otherwise the information related to this ID won't be imported. For
example if a quest `LostFiles` exist, then good message IDs are:

- `LOSTFILES_ABORT`
- `LOSTFILES_QUESTION`
- `LOSTFILES_HELLO`
- `LOSTFILES_FLIP`
- `LOSTFILES_FLIP_HINT1`
- `LOSTFILES_THE_END`
- `NOQUEST_ADA_NOTHING`

In a quest, message IDs can be used to display different kinds of
dialogues. The prefix can be omitted, in which case the quest's name will be
used as prefix. This means less writing and also less changes if e.g. we decide
to change the quest's name for some reason:

``` python
self.wait_confirm('HELLO')
self.show_hints_message('FLIP')
self.show_message('THE_END', choices=[('End of Episode', self.finish_episode)])
```

The `NOQUEST` prefix is used for all the message IDs that aren't intended for a
specific quest.

#### Quest String Catalog

The general way to get the information related to a message ID is through the
`QuestStringCatalog`class. This is what methods like `show_message()` use
internally. Usually you don't have to use the catalog directly, but if do:

``` python
from eosclubhouse.utils import QuestStringCatalog

# Get some info:
info = QuestStringCatalog.get_info('LOSTFILES_HELLO')

# Get some text:
text = QuestStringCatalog.get_string('NOQUEST_ADA_NOTHING')
```

#### Text Markup

Simple text markup can be used in the text for dialogs (not for text in labels
or other places.)

Example 1: ``We have *bold*, _italics_ and `code`.``

![Example 1](data/docs/markup1.png?raw=true)

Example 2: `*I am _very_ excited* about this quest!`

![Example 2](data/docs/markup2.png?raw=true)

Example 3: `I ~despise~ am not a fan of soup.`

![Example 3](data/docs/markup3.png?raw=true)

Example 4: ``Try setting `gravity = 0` in the code.``

![Example 4](data/docs/markup4.png?raw=true)

### Special Quest Message IDs

There are message IDs treated specially. For example, to override default
messages. Below, `MYQUEST` should be read as the prefix of a valid quest:

#### Messages For Accepting And Aborting Quests

- `MYQUEST_ABORT`: Quests are usually aborted when the external app they are
  using is closed by the user. The information for this ID will be used to
  display a message when that happens. If the information has a SFX, it will
  override the default sound played when quests are aborted. A BG sound will be
  ignored.

- `MYQUEST_QUESTION`: Overrides the default message that appears when a quest
  is proposed (e.g. when a character is clicked and has a quest for the user to
  do). If the information has a SFX, it will override the default sound played
  when quests are proposed. A BG sound will be ignored.

- `MYQUEST_QUEST_ACCEPT`: Overrides the default label used to accept the
  proposed quest. Note this is a label, so only the text information is used.

- `MYQUEST_QUEST_REJECT`: Overrides the default label used to reject the
  proposed quest. Note this is a label, so only the text information is used.

#### Hints Messages

You can use the same message ID with suffixes `_HINT1`, `_HINT2`, etc to
display a message with a number of hints. The message will loop between initial
text and all the hints in sequence. For example if you have message IDs in the
spreadsheet like:

- `MYQUEST_FLIP`
- `MYQUEST_FLIP_HINT1`
- `MYQUEST_FLIP_HINT2`
- `MYQUEST_FLIP_HINT3`

You can display the message with hints in the quest with:

``` python
self.show_hints_message('FLIP')
```

#### Hint Message Used To Launch App

- `MYQUEST_LAUNCH`, `MYQUEST_LAUNCH_HINT1`, ...: If these message IDs are
  defined for the quest, a hint message will be displayed automatically when
  the quest asks the player to launch an app.

The API to ask the player to launch an app is:

``` python
self.ask_for_app_launch(self._app, pause_after_launch=2)
```

#### Characters Idle Messages

When a character has no quest to propose to the player, it will display an idle
message. In this message the character will try to point the player to a
character that does have something to propose. And if none of the characters
have anything to propose, it will fallback to a "NOTHING" message. The special
message IDs to build the idle messages are as follows. Considering two
characters, Ada and Saniel:

- `NOQUEST_ADA_SANIEL`: The text Ada displays to point the player to Saniel,
  when Ada has nothing to offer.

- `NOQUEST_SANIEL_ADA`: The text Saniel displays to point the player to Ada,
  when Saniel has nothing to offer.

- `NOQUEST_ADA_NOTHING`: The text Ada displays when none of the characters have
  a quest to offer.

- `NOQUEST_SANIEL_NOTHING`: The text Saniel displays when none of the
  characters have a quest to offer.

The above messages will be used in any episode, independently from whether they
have been set in a sheet corresponding to a certain episode in the spreadsheet.

It is also possible to specify `NOQUEST` messages that episode dependent. This
is done by using `NOQUEST_EPISODEID` instead of just NOQUEST, where `EPISODEID`
is the ID of the episode, i.e. for `episode3` specific `NOQUEST` messages, they
should have the prefix of `NOQUEST_EPISODE3`. The suffixes work just as
mentioned above for the plain `NOQUEST` messages, e.g.
`NOQUEST_EPISODE2_SANIEL_ADA` will be used when the user clicks on the Saniel
character in episode 2, when this character has no quest to offer but the Ada
character does.

`NOQUEST` messages specific to episodes should be kept in the episode's
respective sheet.

**Note**: This is the default behavior. It can be changed for a
character by overriding the `QuestSet.get_empty_message()` method.

### Importing Quest Dialog Information From The Spreadsheet

To automatically fetch the latest changes in the spreadsheet,
there is the `get-strings-file` script. Usually you want to commit the changes
as well:

    ./tools/get-strings-file --commit

There are more options to fetch specific pages or rows. Call
`./tools/get-strings-file --help` for details.

Internally, the information is stored in CSV files, and exposed through the
`QuestStringCatalog` class.

### Quests/Strings Alternative Location

Sometimes it is convenient to be able to run quests or change dialog strings
without having to build a new Flatpak. Thus, any quests' code, or a modified
strings CSV file can be added to a secondary location and will be loaded
directly by the Clubhouse (overriding any quest/string-id with the same name).
this alternative location is: `~/.var/app/com.hack_computer.Clubhouse/data/quests`

To automatically fetch the spreadsheet into the alternative path:

    ./tools/get-strings-file --use-alternative-path

### ActivityCard Alternate Background Images

When adding new new quest it is covenient to have an alternative directory
to put cards background images in for easy prototyping.

This is why the app will load any jpg image named as the quest id from
`~/.var/app/com.hack_computer.Clubhouse/data/quests/cards/` directory

So if you are adding an quest with an id 'my-new-quest', all you have to do is
add an my-new-quest.jpg file in that directory

### Importing Other Information From The Spreadsheet

Besides the quest strings, there is more information in other pages of the
spreadsheet. Currently: episode names and badges, inventory item names and
descriptions.

Use the `get-info-file` script to import this information, by passing the
spreadsheet page as argument:

`./tools/get-info-file episodes`

### Building the Quests Flow

When you are creating an episode, you start with a diagram like this:

![Example 1](data/docs/quests-flow.png?raw=true)

To build the graph of this diagram, you should:

- Define quest-sets. Each quest-set has an ordered list of quests. Each
  quest-set is mapped to a character in the Clubhouse, and represents the set of
  quests offered by this character.

- Define the availability dependency between quests of different quest-sets. The
  dependency between quests of same quest-sets is automatic: they are made
  available in order, as defined in the previous step.

- Define which quests are automatically offered, if any.

- Define which quest marks the episode as completed.

- Define which quest advance automatically to the next episode. Should be the
  last quest of an episode.

You define the quests in each quest-set like this:

``` python
class QuestSetA(QuestSet):

    __quests__ = ['QuestA1', 'QuestA2', 'QuestA3']
```

**Note**: The order in the names A1, A2, A3 above are just an example. There is
no convention for the class name of quests.

To define the availability dependency between quests of different quest-sets:

``` python
class QuestA3(Quest):

    __available_after_completing_quests__ = ['QuestB1']
```

In the diagram above, quests A2 and A3 are auto-offered once they become
available. The character will offer the next quest immediately after the
previous quest is completed. So the player will get the impression that quests
A1 to A3 are chained together. To make a quest auto-offer:

``` python
class QuestA2(Quest):

    def setup(self):
        self.auto_offer = True
```

One of the quests must mark the episode as completed. This doesn't have to be
the last one. Quests define if they complete the episode with:

``` python
class QuestC2(Quest):

    __complete_episode__ = True

```

The quests coming after the episode is completed are considered bonus. In the
example above, quests B3 and B4 are bonus.

If there are more episodes after this one, the last quest should advance to the
next episode with:

``` python
class QuestB4(Quest):

    __advance_episode__ = True

```

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
is: `~/.var/app/com.hack_computer.Clubhouse/data/characters`

Example:

```
mkdir -p ~/.var/app/com.hack_computer.Clubhouse/data/characters/ada/fullbody
(git clone https://github.com/endlessm/clubhouse)
(cd clubhouse)
cp data/characters/ada/fullbody/hi.* ~/.var/app/com.hack_computer.Clubhouse/data/characters/ada/fullbody

# Change the animation format here and make Ada go crazy. Example: "frames": [0,8,0,8]
gedit ~/.var/app/com.hack_computer.Clubhouse/data/characters/ada/fullbody/hi.json

# Restart the clubhouse:
com.hack_computer.Clubhouse -x && com.hack_computer.Clubhouse -d
```

## Reloading the Clubhouse

The Clubhouse may still be running even when its window is closed, thus, for
forcing it to quit (in order to e.g. re-run it after adding new content to the
alternative quests' location), you can simply press Ctrl+Escape in its window
(you may have to close and re-open it for the focus to be properly set and the
keyboard shortcut to work).

## Running Modes For Development

### Debug Mode

The Clubohouse has a debug mode for developers. It will add debug
lines to the logs.

To set debug mode in the Clubhouse, call:

``` bash
com.hack_computer.Clubhouse --debug
```

Logs are directed to the main instance of the Clubhouse. So if the
Clubhouse was running when you called `--debug`, you won't see any
logs in the Terminal, and the command will exit immediately. If you
want to see debug logs in the Terminal, you will have to first quit
and then start with debug mode again, like this:

``` bash
com.hack_computer.Clubhouse --quit
com.hack_computer.Clubhouse --debug
```

### Measuring Performance

Output the time it takes to run certain setup steps. Useful for finding
performance regressions:

``` bash
CLUBHOUSE_PERF_DEBUG=yes com.hack_computer.Clubhouse
```

### Profiling

Output a file with statistics of the current profile.

``` bash
CLUBHOUSE_PROFILING=yes com.hack_computer.Clubhouse
```

A new file named `clubhouse-runstats` will be created.

You can visualize it with the Python tool `snakeviz` by running

```
pip3 install --user snakeviz
snakeviz clubhouse-runstats
```

To create a Graphviz diagram `dot` file, you can do:

```
pip3 install --user gprof2dot
gprof2dot -f pstats clubhouse-runstats > profile.dot
```

and to visualize it you can run

```
dot -Tsvg -o profile.svg < profile.dot
```

If you do not have the `dot` binary, do not worry. You can also visualize
it in on-line in sites like [dreampuf](https://dreampuf.github.io) or
[GraphvizFiddle](https://stamm-wilbrandt.de/GraphvizFiddle/).


## Future Work ##

### Separating the Quests from the Clubhouse ###

The quests consist of Python code that is run in-process with the
Clubhouse.
The quest code is made simpler than the Clubhouse code due to the use of
libquest to abstract away some of the details, but there is still room
to make it even simpler.

Writing quests with Python code still means the quest writer has to be
at least familiar with this language and paradigm. Moreover, for
stability reasons we still follow a review process for the quests code,
which can extend the time required for a quest to be fully integrated.
This solution limits who we can hire to write the quests and
makes the time for writing them slower than it could be.
Thus, ours plans include changing the quests system so they can be
written by a domain-specific language or a different paradigm like
flow-based programming; this would allow us to even move the quests
out of the Clubhouse so they're completely managed by a third party,
and it lowers the requirements for the quest writer's profile/knowledge.
