from eosclubhouse.libquest import Quest
from eosclubhouse import logger


class Sidetrack2(Quest):

    __app_id__ = 'com.hack_computer.Sidetrack'

    __items_on_completion__ = {'item.key.sidetrack.1': {}}
    __available_after_completing_quests__ = ['Sidetrack1']
    __tags__ = ['pathway:games', 'difficulty:medium', 'skillset:LaunchQuests', 'since:1.4']
    __pathway_order__ = 101

    def setup(self):
        self.confirmed_messages = []

    def _reset_confirmed_messages(self):
        self.confirmed_messages = []

    def _get_unconfirmed_message(self, message_id_list):
        for message_id in message_id_list:
            if message_id not in self.confirmed_messages:
                return message_id
        return None

    def step_begin(self):
        self.ask_for_app_launch(message_id='LAUNCH')

        highest_level = self._app.get_js_property('highestAchievedLevel')

        # @fixme: This is a workaround to https://phabricator.endlessm.com/T29180
        # Sometimes Sidetrack app takes lot of time to start and get_js_property times out.
        if highest_level is None:
            logger.debug('Quest %s: Cannot get \'highestAchievedLevel\' for %s. Trying again...',
                         self.get_id(), self.app.dbus_name)
            return self.step_begin

        # This is a workaround to wait until the sidetrack app reads the
        # information from the game state service. In the future we should add
        # a signal or a property to the toyapps and move this wait to a new
        # method in Quest
        current_level = int(self._app.get_js_property('currentLevel'))
        while current_level == 0:
            logger.debug('Current level is 0, waiting for sidetrack to load data')
            self.pause(1)
            current_level = self._app.get_js_property('currentLevel')

        if highest_level < 23 or highest_level > 28:
            self._app.set_js_property('highestAchievedLevel', ('u', 23))
        self._app.set_js_property('availableLevels', ('u', 28))

        # bypass all of the intro to flip to hack and unlock
        if current_level > 23:
            return self.step_play_level, False
        else:
            self._app.set_js_property('startLevel', ('u', 23))

        for message_id in ['INTRO1', 'INTRO2', 'INTRO3', 'INTRO4', 'INTRO5', 'INTRO6']:
            self.wait_confirm(message_id)

        return self.step_wait_and_pulse

    @Quest.with_app_launched()
    def step_wait_and_pulse(self):
        self.app.pulse_flip_to_hack_button(True)

        return self.step_wait_for_flip

    @Quest.with_app_launched()
    def step_wait_for_flip(self):
        self.show_message('FLIP')
        for hint_msg_id in ['FLIP_HINT1', 'FLIP_HINT2']:
            if self._app.get_js_property('flipped') or self.is_cancelled():
                break
            self.wait_for_app_js_props_changed(props=['flipped'], timeout=10)
            if not self._app.get_js_property('flipped'):
                self.show_message(hint_msg_id)

        while not self._app.get_js_property('flipped') and not self.is_cancelled():
            self.wait_for_app_js_props_changed(props=['flipped'])

        self.app.pulse_flip_to_hack_button(False)

        if not self.is_panel_unlocked('lock.sidetrack.1'):
            return self.step_unlock

        return self.step_play_level, False

    @Quest.with_app_launched()
    def step_unlock(self):
        self.pause(1)
        self.wait_confirm('UNLOCK')
        action = self.show_choices_message('UNLOCK_QUESTION',
                                           ('UNLOCK_CHOICE1', None, False),
                                           ('UNLOCK_CHOICE2', None, True)).wait()
        if action.future.result():
            self.wait_confirm('UNLOCK_CORRECT')
        else:
            self.wait_confirm('UNLOCK_PLAUSIBLE')

        self.wait_confirm('UNLOCK3')

        self.wait_confirm('GIVE_KEY')
        self.give_item('item.key.sidetrack.1')

        self.show_message('UNLOCK4')

        while not self.is_panel_unlocked('lock.sidetrack.1') and not self.is_cancelled():
            self.connect_gss_changes().wait()
        self.pause(6)

        return self.step_play_level, False

    @Quest.with_app_launched()
    def step_play_level(self, level_changed, level_success=None):
        current_level = int(self._app.get_js_property('currentLevel'))
        message_id = None
        if current_level == 23:
            self.show_hints_message('LEVEL_23_TOOLBOX')
            self.wait_for_codeview_errors('instructions')
            self.app.pulse_flip_to_hack_button(True)
            self.show_message('LEVEL_23_FLIP_HINT')
            action = self.connect_app_js_props_changes(self._app, ['flipped'])
            self.wait_for_one([action])
            self.app.pulse_flip_to_hack_button(False)
            self.show_message('LEVEL_23_PLAY_HINT')
        elif current_level == 24:
            self.show_hints_message('LEVEL_24')
            self.app.pulse_flip_to_hack_button(True)
            action = self.connect_app_js_props_changes(self._app, ['flipped'])
            self.wait_for_one([action])
            self.app.pulse_flip_to_hack_button(False)
            self.show_hints_message('LEVEL_24_TOOLBOX')
            self.wait_for_codeview_errors('instructions')
            self.app.pulse_flip_to_hack_button(True)
            self.show_message('LEVEL_24_FLIP_HINT')
            action = self.connect_app_js_props_changes(self._app, ['flipped'])
            self.wait_for_one([action])
            self.app.pulse_flip_to_hack_button(False)
            self.show_message('LEVEL_24_PLAY_HINT')
        elif current_level == 25:
            message_id = self._get_unconfirmed_message(['LEVEL_25'])
        elif current_level == 26:
            self.show_hints_message('LEVEL_26')
        elif current_level == 27:
            message_id = self._get_unconfirmed_message(['LEVEL_27'])
        elif current_level == 28:
            for message_id in ['LEVEL_28_FABER', 'LEVEL_28_SANIEL', 'LEVEL_28_FABER_2',
                               'LEVEL_28_RILEY', 'LEVEL_28_SANIEL_2']:
                self.wait_confirm(message_id)
            return self.step_success
        else:
            self.dismiss_message()

        actions = [self.connect_app_js_props_changes(self._app, ['currentLevel', 'success'])]
        if message_id is not None:
            actions.append(self.show_confirm_message(message_id))

        self.wait_for_one(actions)

        level_changed = False
        level_success = None
        if self.confirmed_step():
            self.confirmed_messages.append(message_id)
        elif current_level != self._app.get_js_property('currentLevel'):
            level_changed = True
            self._reset_confirmed_messages()
        else:
            # Current level hasn't changed, so either the player
            # completed the level or died:
            level_success = self._app.get_js_property('success')

        return self.step_play_level, level_changed, level_success

    def step_success(self):
        return self.step_complete_and_stop
