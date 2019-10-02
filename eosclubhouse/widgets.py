from gi.repository import Gtk


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
