from gi.repository import Gdk, GdkPixbuf, Gtk, GObject


def gtk_widget_add_custom_css_provider(widget, for_screen=False,
                                       priority=Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1):
    css_provider = Gtk.CssProvider()
    context = widget.get_style_context()
    if not for_screen:
        context.add_provider(css_provider, priority)
    else:
        context.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, priority)
    return css_provider


class FixedLayerGroup(Gtk.Bin):

    __gtype_name__ = 'FixedLayerGroup'
    __dummy_layer_attr__ = '__{}LayerName'.format(__gtype_name__)

    def __init__(self):
        super().__init__()

        self._layers = {}
        self._overlay = Gtk.Overlay(halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)

        self.add(self._overlay)

    def get_children(self):
        return self._overlay.get_children()

    def add_layer(self, widget, layer_name):
        if layer_name in self._layers:
            return self._layers[layer_name]

        layer = self._new_layer_from_widget(widget)
        self._layers[layer_name] = layer

        self._overlay.add_overlay(layer)
        self._overlay.set_overlay_pass_through(layer, True)

        return layer

    def get_layer(self, layer_name):
        return self._layers.get(layer_name)

    def _new_layer_from_widget(self, widget):
        if isinstance(widget, Gtk.Fixed):
            fixed = widget
        else:
            fixed = Gtk.Fixed()
            fixed.put(widget, 0, 0)

        fixed.props.halign = Gtk.Align.FILL
        fixed.props.valign = Gtk.Align.FILL

        return fixed


class ScalableImage(Gtk.Box):

    __gtype_name__ = 'ScalableImage'

    def __init__(self, path):
        super().__init__()
        image_info = GdkPixbuf.Pixbuf.get_file_info(path)
        if image_info[0] is None or image_info.width == 0 or image_info.height == 0:
            raise IOError('Image file \'{}\' does not exist or unsupported format.'.format(path))

        self.aspect_ratio = image_info.width / image_info.height

        self._css_provider = gtk_widget_add_custom_css_provider(self)

        css = "ScalableImage {{ background-image: url('{}') }}".format(path)
        self._css_provider.load_from_data(css.encode())

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.HEIGHT_FOR_WIDTH

    def do_get_preferred_height_for_width(self, width):
        height = width / self.aspect_ratio
        return height, height


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/breadcrumb-button.ui')
class BreadcrumbButton(Gtk.Box):

    __gtype_name__ = 'BreadcrumbButton'

    _back_box = Gtk.Template.Child()
    _back_button = Gtk.Template.Child()
    _inactive_button = Gtk.Template.Child()
    _main_button = Gtk.Template.Child()
    _popover_button = Gtk.Template.Child()
    _popover_button_image = Gtk.Template.Child()
    _popover_revealer = Gtk.Template.Child()
    _popover_label = Gtk.Template.Child()

    def __init__(self):
        super().__init__(self)
        self._active = True
        self._main_button_label = ''
        self._main_popover_label = ''
        self._popup_handler = None
        self._main_popup_handler = None

    def set_popover_button_visible(self, visible):
        self._popover_button.props.visible = visible

    def _popover_toggled_cb(self, widget, prop):
        if widget.props.visible:
            self._popover_button_image.props.icon_name = 'go-up-symbolic'
            self._popover_revealer.set_reveal_child(True)
        else:
            self._popover_button_image.props.icon_name = 'go-down-symbolic'
            self._popover_revealer.set_reveal_child(False)

    def _get_popover(self):
        return self._popover_button.get_popover()

    def _set_popover(self, value):
        if self._popup_handler:
            self._popover_button.props.popover.disconnect(self._popup_handler)
            self._popup_handler = None

        self._popup_handler = value.connect('notify::visible',
                                            self._popover_toggled_cb)

        self._popover_button.set_popover(value)
        self._popover_button.show_all()

    def _main_popover_toggled_cb(self, widget, prop):
        if widget.props.visible:
            self._main_button.props.label = self._main_popover_label
            self._main_button.props.always_show_image = False
        else:
            self._main_button.props.label = self._main_button_label
            self._main_button.props.always_show_image = True

    def _get_main_popover(self):
        return self._main_button.get_popover()

    def _set_main_popover(self, value):
        if self._main_popup_handler:
            self._main_button.props.popover.disconnect(self._main_popup_handler)
            self._main_popup_handler = None

        if value:
            self._main_popup_handler = value.connect('notify::visible',
                                                     self._main_popover_toggled_cb)

            self._main_button.set_popover(value)
            self._main_button.show_all()

    def _get_action_name(self):
        return self._main_button.get_action_name()

    def _set_action_name(self, value):
        self._main_button.set_action_name(value)
        self._inactive_button.set_action_name(value)

    def _get_action_target(self):
        return self._main_button.get_action_target_value()

    def _set_action_target(self, value):
        self._main_button.set_action_target_value(value)
        self._inactive_button.set_action_target_value(value)

    def _get_label(self):
        return self._main_button_label

    def _set_label(self, value):
        self._main_button_label = value
        self._main_button.set_label(value)

    def _get_icon_name(self):
        return self._main_button.props.image.get_icon_name

    def _set_icon_name(self, value):
        self._main_button.props.image = Gtk.Image(icon_name=value)
        self._main_button.props.image.props.valign = Gtk.Align.CENTER
        self._inactive_button.props.image = Gtk.Image(icon_name=value)
        self._inactive_button.props.image.props.valign = Gtk.Align.CENTER

    def _get_popover_label(self):
        return self._popover_label.get_label()

    def _set_popover_label(self, value):
        self._popover_label.set_label(value)

    def _get_main_popover_label(self):
        return self._main_popover_label

    def _set_main_popover_label(self, value):
        self._main_popover_label = value

    def get_active(self):
        return self._active

    def set_active(self, value):
        self._active = value

        # to make it a circle the width should be the same as the height
        height = self._main_button.get_allocated_height()
        self._inactive_button.set_size_request(height, height)

        if not self.back_label:
            self._back_box.hide()

        if value:
            self._inactive_button.hide()
            self._main_button.show()
            if self._get_popover():
                self._popover_button.show()
            if self.back_label:
                self._back_box.show()
        else:
            self._inactive_button.show()
            self._main_button.hide()
            if self._get_popover():
                self._popover_button.hide()
            if self.back_label:
                self._back_box.hide()

    def _get_back_label(self):
        return self._back_button.get_label()

    def _set_back_label(self, value):
        self._back_button.set_label(value)

    def _get_back_icon_name(self):
        return self._back_button.props.image.get_icon_name

    def _set_back_icon_name(self, value):
        self._back_button.props.image = Gtk.Image(icon_name=value)
        self._back_button.props.image.props.valign = Gtk.Align.CENTER

    def _get_back_action_name(self):
        return self._back_button.get_action_name()

    def _set_back_action_name(self, value):
        self._back_button.set_action_name(value)

    def _get_back_action_target(self):
        return self._back_button.get_action_target_value()

    def _set_back_action_target(self, value):
        self._back_button.set_action_target_value(value)

    main_popover = GObject.Property(_get_main_popover,
                                    _set_main_popover,
                                    type=GObject.TYPE_OBJECT)
    main_popover_label = GObject.Property(_get_main_popover_label,
                                          _set_main_popover_label,
                                          type=str)
    popover = GObject.Property(_get_popover, _set_popover, type=GObject.TYPE_OBJECT)
    popover_label = GObject.Property(_get_popover_label, _set_popover_label, type=str)
    action_name = GObject.Property(_get_action_name, _set_action_name, type=str)
    action_target = GObject.Property(_get_action_target,
                                     _set_action_target,
                                     type=GObject.TYPE_VARIANT)
    label = GObject.Property(_get_label, _set_label, type=str)
    icon_name = GObject.Property(_get_icon_name, _set_icon_name, type=str)
    back_label = GObject.Property(_get_back_label, _set_back_label, type=str)
    back_icon_name = GObject.Property(_get_back_icon_name, _set_back_icon_name, type=str)
    back_action_name = GObject.Property(_get_back_action_name,
                                        _set_back_action_name,
                                        type=str)
    back_action_target = GObject.Property(_get_back_action_target,
                                          _set_back_action_target,
                                          type=GObject.TYPE_VARIANT)
    active = GObject.Property(get_active, set_active, type=bool, default=True)


# Set widget classes CSS name to be able to select by GType name
widgets_classes = [
    BreadcrumbButton,
    FixedLayerGroup,
    ScalableImage
]

for klass in widgets_classes:
    klass.set_css_name(klass.__gtype_name__)
