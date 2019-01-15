import logging
from gi.repository import Gio
from gi.repository import GLib


_logger = logging.getLogger(__name__)


class HackSoundServer:

    _proxy = None

    @classmethod
    def play(class_, sound_event_id, result_handler=None, user_data=None):
        """
        Plays a sound asynchronously.
        By default, it "fires and forgets": no return value.

        Args:
            sound_event_id (str): The sound event id to play.

        Optional keyword arguments:
            result_handler: A function that is invoked when the async call
                finishes. The function's arguments are the following:
                proxy_object, result and user_data.
            data: The user data passed to the result_handler function.
        """
        class_._play(sound_event_id, result_handler=result_handler,
                     user_data=user_data)

    @classmethod
    def play_sync(class_, sound_event_id):
        """
        Plays a sound synchronously.

        Args:
            sound_event_id (str): The sound event id to play.

        Returns:
            str: The uuid of the new played sound.
        """
        return class_._play(sound_event_id, asynch=False)

    @classmethod
    def _play(class_, sound_event_id, asynch=True, result_handler=None,
              user_data=None):
        if result_handler is None:
            result_handler = class_._black_hole
        try:
            if asynch:
                class_.get_proxy().PlaySound("(s)", sound_event_id,
                                             result_handler=result_handler,
                                             user_data=user_data)
            else:
                return class_.get_proxy().PlaySound("(s)", sound_event_id)
        except GLib.Error as err:
            _logger.error("Error playing sound '%s': %s", sound_event_id, err.message)

    @classmethod
    def update_properties(class_, sound_event_id, time_ms, props):
        class_.get_proxy().UpdateProperties(
            "(sia{sv})", sound_event_id, time_ms, props,
            result_handler=class_._black_hole, user_data=None)

    @classmethod
    def stop(class_, uuid, result_handler=None, user_data=None):
        """
        Decreases the refcount of a sound by one asynchronously.

        A call for this method only means that one of the calls for playing no
        longer wants it to keep playing, i.e. for the sound to effectively be
        stopped, this method needs to be called as many times as the `play`
        one. Alternatively, use the `terminate` method to promptly stop the
        sound regardless of how many references there are.

        Args:
            uuid (str): The sound uuid to stop playing.

        Optional keyword arguments:
            result_handler: A function that is invoked when the async call
                finishes. The function's arguments are the following:
                proxy_object, result and user_data.
            data: The user data passed to the result_handler function.
        """
        class_._stop(uuid, "StopSound", result_handler, user_data)

    @classmethod
    def terminate(class_, uuid, result_handler=None, user_data=None):
        """
        Sets the refcount of a sound to zero asynchronously.

        A single call to this method will stop the sound regardless of how many
        references (calls for play) there are for it. Use this method if you
        need to make sure that the sound is really stopped.

        Args:
            uuid (str): The sound uuid to stop playing.

        Optional keyword arguments:
            result_handler: A function that is invoked when the async call
                finishes. The function's arguments are the following:
                proxy_object, result and user_data.
            data: The user data passed to the result_handler function.
        """
        class_._stop(uuid, "TerminateSound", result_handler, user_data)

    @classmethod
    def _stop(class_, uuid, method_name, result_handler=None, user_data=None):
        if result_handler is None:
            result_handler = class_._black_hole
        try:
            method = getattr(class_.get_proxy(), method_name)
            method("(s)", uuid, result_handler=result_handler, user_data=user_data)
        except GLib.Error as err:
            _logger.error("%s: Error stopping sound '%s': %s", method_name,
                          uuid, err.message)

    @classmethod
    def _black_hole(_class, _proxy, _result, user_data=None):
        pass

    @classmethod
    def get_proxy(class_):
        if not class_._proxy:
            class_._proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION, 0, None, 'com.endlessm.HackSoundServer',
                '/com/endlessm/HackSoundServer',
                'com.endlessm.HackSoundServer', None)
        return class_._proxy
