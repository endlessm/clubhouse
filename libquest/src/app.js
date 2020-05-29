/* exported LibQuestApp */
/* global pkg */

const {Gio, GObject} = imports.gi;

const {QuestBus} = imports.questBus;

const DBUS_INTERFACE = `
<node>
  <interface name="com.hack_computer.Libquest">
    <method name="listAvailableQuests">
      <arg type='as' name='quests' direction='out'/>
    </method>
    <method name="loadQuest">
      <arg type='s' name='questID' direction='in'/>
    </method>
  </interface>
</node>`;

const AUTO_CLOSE_MILLISECONDS_TIMEOUT = 300000;  // 5 minutes

var LibQuestApp = GObject.registerClass(class LibQuestApp extends Gio.Application {
    _init() {
        super._init({
            application_id: pkg.name,
            inactivity_timeout: AUTO_CLOSE_MILLISECONDS_TIMEOUT,
            flags: Gio.ApplicationFlags.IS_SERVICE,
        });

        this._questBusList = [];
        this.dbusRegister();
    }

    shutdown() {
        this.dbusUnregister();
        this._questBusList.forEach(q => {
            q.dbusUnregister();
        });
    }

    dbusRegister() {
        const objectPath = '/com/hack_computer/Libquest';
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

    // D-Bus implementation
    loadQuest(questID) {
        const questBus = new QuestBus({quest_id: questID});
        this._questBusList[questID] = questBus;
        log(`Quest ${questBus.quest_id} loaded.`);
    }

    // D-Bus implementation
    // eslint-disable-next-line class-methods-use-this
    listAvailableQuests() {
        // FIXME
        return ['p5-quest'];
    }
});
