from gi.repository import Gdk, GdkPixbuf, Gtk


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


# Set widget classes CSS name to be able to select by GType name
widgets_classes = [
    FixedLayerGroup,
    ScalableImage
]

for klass in widgets_classes:
    klass.set_css_name(klass.__gtype_name__)
