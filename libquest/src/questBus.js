/* exported QuestBus */
/* global pkg */

const {Gio, GLib, GObject} = imports.gi;
const ByteArray = imports.byteArray;

const {Quest} = imports.quest;

const DBUS_INTERFACE = `
<node>
  <interface name="com.hack_computer.Libquest.Quest">
    <method name="continueStory">
      <arg type='v' name='dialogue' direction='out'/>
      <arg type='v' name='choices' direction='out'/>
    </method>
    <method name="choose">
      <arg type='i' name='choiceIndex' direction='in'/>
    </method>
    <method name="hasEnded">
      <arg type='b' name='hasEnded' direction='out'/>
    </method>
    <method name="restart">
    </method>
    <method name="updateStoryVariable">
      <arg type='s' name='name' direction='in'/>
      <arg type='v' name='newValue' direction='in'/>
    </method>
    <method name="getStoryVariable">
      <arg type='s' name='name' direction='in'/>
      <arg type='v' name='value' direction='out'/>
    </method>
    <property name="mainCharacter" type="s" access="read"/>
    <property name="hasEnded" type="b" access="read"/>
  </interface>
</node>`;

const QUESTS_PATH = GLib.build_filenamev([pkg.pkgdatadir, 'quests']);
// FIXME: Use it, see below.
// const ALTERNATIVE_QUESTS_PATH = GLib.build_filenamev(
//     [GLib.get_user_data_dir(), 'quests']);

function _readQuestContent(questID) {
    // FIXME: Try loading quests from the alternative quests path,
    // like Clubhouse does:
    const storyPath = GLib.build_filenamev([QUESTS_PATH, `${questID}.ink.json`]);

    const storyFile = Gio.File.new_for_path(storyPath);
    const [, storyBytes] = storyFile.load_contents(null);

    // Strip the BOM encoded with the JSON:
    return ByteArray.toString(storyBytes).replace(/^\uFEFF/, '');
}

function logQuest(dialogue, choices) {
    dialogue.forEach(d => {
        log(`${d.character}: ${d.text}`);
    });

    choices.forEach(c => {
        log(`${c.index}: ${c.text}`);
    });
}

var QuestBus = GObject.registerClass({
    Properties: {
        'quest-id': GObject.ParamSpec.string('quest-id', 'Quest ID', 'The quest ID',
            GObject.ParamFlags.READWRITE | GObject.ParamFlags.CONSTRUCT_ONLY, ''),

        'has-ended': GObject.ParamSpec.boolean('has-ended', 'Has ended?',
            'Whether the quest has ended',
            GObject.ParamFlags.READWRITE, false),

        'main-character': GObject.ParamSpec.string('main-character', 'Main Character',
            'The main character telling the story',
            GObject.ParamFlags.READWRITE, ''),
    },
}, class QuestBus extends GObject.Object {
    _init(props = {}) {
        super._init(props);
        this.load();
        this.dbusRegister();
    }

    dbusRegister() {
        const appObjectPath = Gio.Application.get_default().get_dbus_object_path();
        // FIXME add "quest id to dbus path" method
        const objectPath = `${appObjectPath}/quest/${this.quest_id.replace(/-/gi, '_')}`;
        this._dbus = Gio.DBusExportedObject.wrapJSObject(DBUS_INTERFACE, this);

        try {
            this._dbus.export(Gio.DBus.session, objectPath);
        } catch (e) {
            logError(e);
        }
    }

    dbusUnregister() {
        if (this._dbus)
            this._dbus.unexport();
    }

    load() {
        const questContent = _readQuestContent(this.quest_id);
        this._quest = new Quest();
        this._quest.setup(questContent);
    }

    // D-Bus implementation
    continueStory() {
        const {dialogue, choices} = this._quest.continueStory();
        logQuest(dialogue, choices);
        return [dialogue, choices];
    }

    // D-Bus implementation
    choose(choiceIndex) {
        this._quest.choose(choiceIndex);
        log(`${this.quest_id}: Chosen ${choiceIndex}`);
    }

    // D-Bus implementation
    // FIXME use the D-Bus property
    hasEnded() {
        return this._quest.hasEnded;
    }

    restart() {
        this._quest.restart();
        log(`${this.quest_id}: Restarted.`);
    }

    // D-Bus implementation
    updateStoryVariable(name, newValue) {
        this._quest.updateStoryVariable(name, newValue);
        log(`${this.quest_id}: Variable ${name} changed to ${newValue}`);
    }

    // D-Bus implementation
    getStoryVariable(name) {
        const value = this._quest.getStoryVariable(name);
        log(`${this.quest_id}: Variable ${name} is ${value}`);
        return value;
    }
});
