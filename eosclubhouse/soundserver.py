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
import functools
import logging
from gi.repository import Gio
from gi.repository import GLib


_logger = logging.getLogger(__name__)


class HackSoundServer:

    _proxy = None
    _pending_calls = []

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
    def _call_dbus_method(class_, method_name, *args, **kwargs):
        method = getattr(class_._proxy, method_name)
        method(*args, **kwargs)

    @classmethod
    def _play(class_, sound_event_id, asynch=True, result_handler=None,
              user_data=None):
        if result_handler is None:
            result_handler = class_._black_hole
        try:
            if asynch:
                class_._call_with_proxy_async(class_._call_dbus_method, 'PlaySound',
                                              "(s)", sound_event_id,
                                              result_handler=result_handler,
                                              user_data=user_data)
            else:
                class_.get_proxy()
                class_._call_play_sound("(s)", sound_event_id)
        except GLib.Error as err:
            _logger.error("Error playing sound '%s': %s", sound_event_id, err.message)

    @classmethod
    def update_properties(class_, sound_event_id, time_ms, props):

        class_._call_with_proxy_async(class_._call_dbus_method, 'UpdateProperties',
                                      "(sia{sv})", sound_event_id, time_ms, props,
                                      result_handler=class_._black_hole, user_data=None)

    @classmethod
    def stop(class_, uuid, result_handler=None, user_data=None):
        """
        Stops a sound asynchronously.

        Args:
            uuid (str): The sound uuid to stop playing.

        Optional keyword arguments:
            result_handler: A function that is invoked when the async call
                finishes. The function's arguments are the following:
                proxy_object, result and user_data.
            data: The user data passed to the result_handler function.
        """
        if result_handler is None:
            result_handler = class_._black_hole
        try:
            class_._call_with_proxy_async(class_._call_dbus_method, 'StopSound',
                                          "(s)", uuid,
                                          result_handler=result_handler,
                                          user_data=user_data)
        except GLib.Error as err:
            _logger.error("Error stopping sound '%s': %s", uuid, err.message)

    @classmethod
    def _black_hole(_class, _proxy, _result, user_data=None):
        pass

    @classmethod
    def get_proxy(class_):
        if not class_._proxy:
            class_._proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION, 0, None, 'com.hack_computer.HackSoundServer',
                '/com/hack_computer/HackSoundServer',
                'com.hack_computer.HackSoundServer', None)
        return class_._proxy

    @classmethod
    def _call_with_proxy_async(class_, callback, *args, **kwargs):
        if class_._proxy:
            if callback:
                callback(*args, **kwargs)
            return class_._proxy

        partial_func = functools.partial(callback, *args, **kwargs)
        class_._pending_calls.append(partial_func)

        Gio.DBusProxy.new_for_bus(
            Gio.BusType.SESSION, 0, None, 'com.hack_computer.HackSoundServer',
            '/com/hack_computer/HackSoundServer',
            'com.hack_computer.HackSoundServer', None,
            class_._on_proxy_ready)
        return None

    @classmethod
    def _on_proxy_ready(class_, proxy, result):
        try:
            class_._proxy = proxy.new_finish(result)
            for partial_func in class_._pending_calls:
                partial_func()
            class_._pending_calls = []
        except GLib.Error as e:
            _logger.warning("Error: Failed to get DBus proxy:", e.message)
            return


class HackSoundItem:
    class Status:
        NONE = 0
        PENDING = 1
        CANCELLING = 3

    def __init__(self, sound_event_id):
        self._id = HackSoundItem.Status.NONE
        self.name = sound_event_id

    def play(self):
        # If we are about to play the sound, do nothing
        if self._id == HackSoundItem.Status.PENDING:
            return

        # If we had to play and to stop before the first UUId was returned,
        # then un-cancel the original sound but do not request another one.
        if self._id == HackSoundItem.Status.CANCELLING:
            self._id = HackSoundItem.Status.PENDING
            return

        # If we are already playing a sound, do nothing (we want to avoid
        # overlapped sounds)
        if self._id != HackSoundItem.Status.NONE:
            return

        self._id = HackSoundItem.Status.PENDING
        HackSoundServer.play(self.name, result_handler=self._play_cb)

    def _play_cb(self, proxy, uuid, user_data):
        if isinstance(uuid, GLib.Error):
            print('Error when attempting to play sound item \'%s\':'
                  ': %s' % (self.name, uuid.message))
            self._id == HackSoundItem.Status.NONE
            return
        if self._id == HackSoundItem.Status.CANCELLING:
            HackSoundServer.stop(uuid)
            self._id = HackSoundItem.Status.NONE
        self._id = uuid

    def stop(self):
        if self._id == HackSoundItem.Status.PENDING:
            self._id = HackSoundItem.Status.CANCELLING
            return
        if self._id in (HackSoundItem.Status.CANCELLING,
                        HackSoundItem.Status.NONE):
            return
        HackSoundServer.stop(self._id)
        self._id = HackSoundItem.Status.NONE
