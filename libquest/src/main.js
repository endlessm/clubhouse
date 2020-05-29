/* exported main */

const {GLib} = imports.gi;

const {LibQuestApp} = imports.app;

function main(argv) {
    const libQuestApp = new LibQuestApp();

    if (GLib.getenv('HACK_LIBQUEST_PERSIST'))
        libQuestApp.hold();

    return libQuestApp.run(argv);
}

