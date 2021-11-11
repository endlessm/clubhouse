import os
import json
import shutil
from gettext import gettext as _
from gi.repository import Gtk, Gio, GLib

from eosclubhouse import utils, libquest


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/custom-modal.ui')
class CustomQuestModal(Gtk.Dialog):

    __gtype_name__ = 'CustomQuestModal'

    title = Gtk.Template.Child()
    subtitle = Gtk.Template.Child()
    description = Gtk.Template.Child()
    image = Gtk.Template.Child()
    difficulty = Gtk.Template.Child()
    character = Gtk.Template.Child()
    code_list_box = Gtk.Template.Child()
    add_code_row = Gtk.Template.Child()

    def __init__(self, quest=None, **kwargs):
        self._app = Gio.Application.get_default()
        self._files = []

        super().__init__(use_header_bar=True)
        self.set_deletable(False)
        self.set_transient_for(self._app.get_active_window())
        self.set_destroy_with_parent(True)
        self.set_modal(True)
        self.get_style_context().add_class('custom-modal')

        self._description_buffer = self.description.get_buffer()

        self.quest = quest
        if quest is None:
            self.load_template()

        header = self.get_header_bar()
        cancel = Gtk.Button(label=_("Cancel"))
        cancel.connect("clicked", lambda x: self.on_response(0))
        header.pack_start(cancel)

        ok = Gtk.Button(label=_("Ok"))
        ok.connect("clicked", lambda x: self.on_response(Gtk.ResponseType.OK))
        ok.get_style_context().add_class('suggested-action')

        header.pack_end(ok)
        header.show_all()

    def on_response(self, response_id, user_data=None):
        if response_id == Gtk.ResponseType.OK:
            self.save()
        else:
            self.destroy()

    def save(self):
        title = self.title.get_text()
        subtitle = self.subtitle.get_text()
        description = self._description_buffer.props.text
        difficulty = self.difficulty.get_active_id().lower()
        image = self.image.get_filename()
        character = self.character.get_active_id()

        metadata = {
            '_LABELS': {
                'QUEST_NAME': title,
                'QUEST_SUBTITLE': subtitle,
                'QUEST_DESCRIPTION': description,
            },
            '_DEFAULT_CHARACTER': character,
            '__tags__': [f'difficulty:{difficulty}'],
        }

        quest_id = utils.quest_name_to_id(title)
        dest_dir = os.path.join(utils.CUSTOM_QUEST_PATH, quest_id)

        # Check if the quest_id exists
        if os.path.exists(dest_dir):
            self.show_error('A quest with that name already exists, use a different one')
            return

        quest_file = None
        files = []
        for index in range(len(self.code_list_box) - 1):
            row = self.code_list_box.get_row_at_index(index)
            if row.main:
                quest_file = row.path
                continue
            files.append(row.path)

        if not files and not quest_file:
            self.show_error('You should include at least one Quest Code ink file')
            return

        # Create the quest folder
        os.mkdir(dest_dir)

        story_file = os.path.join(dest_dir, 'quest.ink')
        metadata_file = os.path.join(dest_dir, 'metadata.json')
        image_file = os.path.join(dest_dir, 'quest.jpg')

        # Create metadata.json file
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        # Copy the image to the new folder quest.jpg
        if image:
            shutil.copy(image, image_file)

        # Copy ink files
        shutil.copy(quest_file, story_file)
        for f in files:
            shutil.copy(f, dest_dir)

        # Reload the custom quests on libregistry
        libquest.Registry.load_custom()

        # TODO:
        # * reload the listview!
        self.destroy()

    def show_error(self, msg):
        dialog = Gtk.MessageDialog(self,
                                   0,
                                   Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.CLOSE,
                                   msg)

        dialog.set_transient_for(self)
        dialog.set_destroy_with_parent(True)
        dialog.set_modal(True)
        dialog.run()
        dialog.destroy()

    def load_template(self):
        template = utils.CUSTOM_QUEST_TEMPLATE
        code_path = os.path.join(template, 'quest.ink')
        metadata_path = os.path.join(template, 'metadata.json')
        image_path = os.path.join(template, 'quest.jpg')
        with open(metadata_path) as f:
            metadata = json.load(f)

        labels = metadata['_LABELS']
        tags = metadata['__tags__']

        self.title.set_text(labels['QUEST_NAME'])
        self.subtitle.set_text(labels['QUEST_SUBTITLE'])
        self._description_buffer.set_text(labels['QUEST_DESCRIPTION'])
        self.character.set_active_id(metadata['_DEFAULT_CHARACTER'])

        image = Gio.File.new_for_path(image_path)
        self.image.set_file(image)

        for tag in tags:
            if tag.split(':')[0] == 'difficulty':
                difficulty = tag.split(':')[1]
                if difficulty == 'easy':
                    self.difficulty.set_active(0)
                elif difficulty == 'medium':
                    self.difficulty.set_active(1)
                else:
                    self.difficulty.set_active(2)

    @Gtk.Template.Callback()
    def _on_code_row_activated(self, widget, row):
        if row == self.add_code_row:
            dialog = Gtk.FileChooserNative.new('Select ink files to add',
                                               self,
                                               Gtk.FileChooserAction.OPEN,
                                               '_Add',
                                               '_Cancel')
            dialog.set_select_multiple(True)
            file_filter = Gtk.FileFilter()
            file_filter.set_name('Ink')
            file_filter.add_pattern('*.ink')
            dialog.add_filter(file_filter)

            response = dialog.run()
            if response == Gtk.ResponseType.ACCEPT:
                filenames = dialog.get_filenames()
                for f in filenames:
                    self._add_ink_row(f)

    def _add_ink_row(self, path):
        is_first = len(self.code_list_box) == 1
        self.code_list_box.prepend(InkFileRow(self, path, is_first))

    def set_main_story(self, path):
        for index in range(len(self.code_list_box) - 1):
            row = self.code_list_box.get_row_at_index(index)
            row.set_main(path == row.path)


class InkFileRow(Gtk.ListBoxRow):
    def __init__(self, modal, path, main=False):
        super().__init__()
        self.path = path
        self.modal = modal
        self._text = Gtk.Label(label=os.path.basename(self.path))
        self._text.set_hexpand(True)
        self._text.set_xalign(0.0)

        self._delete = Gtk.Button.new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.BUTTON)
        context = self._delete.get_style_context()
        context.add_class('flat')

        self._main = Gtk.Button.new_from_icon_name('emblem-favorite-symbolic', Gtk.IconSize.BUTTON)
        context = self._main.get_style_context()
        context.add_class('main-button')
        context.add_class('flat')
        self.set_main(main)

        self._box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._box.add(self._main)
        self._box.add(self._text)
        self._box.add(self._delete)

        self._box.props.height_request = 50
        self._box.props.margin_start = 12
        self._box.props.margin_end = 6
        self._box.props.spacing = 12

        self.add(self._box)
        self.show_all()

        self._delete.connect('clicked', self._on_delete)
        self._main.connect('clicked', self._on_main)

    @property
    def text(self):
        return self._text.get_text()

    def _on_delete(self, *args, **kwargs):
        self.destroy()

    def _on_main(self, *args, **kwargs):
        self.modal.set_main_story(None)
        self.set_main(not self.main)

    def set_main(self, value):
        self.main = value
        if value:
            self._main.get_style_context().remove_class('main-unselected')
        else:
            self._main.get_style_context().add_class('main-unselected')
