import functools
import networkx as nx

from gi.repository import Gio
from gi.repository import GObject
from gi.repository import GLib

from eosclubhouse import logger
from networkx.algorithms.dag import topological_sort


class _AsyncResourceRegistry:
    def __init__(self):
        # self._async_resources = {}
        self._dependency_graph = nx.DiGraph()

    def register_resource(self, async_resource):
        if async_resource.deps and not set(self._dependency_graph.nodes) & set(async_resource.deps):
            logger.warning('Resource \'%s\' cannot be registered because missing dependency.')
            return

        if async_resource.name in self._dependency_graph.nodes:
            logger.warning('Resource \'%s\' cannot be registered because already registered.')
            return

        self._dependency_graph.add_node(async_resource.name, data=async_resource)
        for dep in async_resource.deps:
            self._dependency_graph.add_edges_from([(dep, async_resource.name)])

    def get(self, resource_name):
        nodes = self._dependency_graph.nodes(data=True)
        if resource_name not in nodes:
            return None
        return nodes[resource_name]['data']

    def predecessors(self, resource_name):
        return self._dependency_graph.predecessors(resource_name)

    def __iter__(self):
        for name in topological_sort(self._dependency_graph):
            yield name

    def __len__(self):
        return len(self._dependency_graph.nodes)

    def __getitem__(self, resource_name):
        resource = self.get(resource_name)
        if resource is None:
            raise KeyError('Not found resource with name {}'.format(resource_name))
        return resource


AsyncResourceRegistry = _AsyncResourceRegistry()


class _AsyncResourceLoader(GObject.Object):

    __gsignals__ = {
        'loading-complete': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
        'loading-failed': (
            GObject.SignalFlags.RUN_FIRST, None, (object, )
        ),
        'resource-loaded': (
            GObject.SignalFlags.RUN_FIRST, None, (object, )
        ),
    }

    def __init__(self):
        super().__init__()
        self.connect('resource-loaded', self._async_resource_loaded_cb)
        self.connect('loading-failed', self._async_resource_loading_failed_cb)

        self._pending_async_resources = []
        self._pending_predecessors = {}

    def is_resource_loaded(self, resource_name):
        return resource_name not in self._pending_async_resources

    def load_resources(self):
        self._pending_async_resources = list(AsyncResourceRegistry)
        logger.warning(self._pending_async_resources)
        self._do_load_resources(True)

    def _do_load_resources(self, first_called=False):
        for resource_name in self._pending_async_resources:
            resource = AsyncResourceRegistry.get(resource_name)
            predecessors = AsyncResourceRegistry.predecessors(resource_name)

            if predecessors and not all([self.is_resource_loaded(p) for p in predecessors]):
                continue

            self._pending_predecessors[resource_name] = resource
            resource.load()

    @property
    def is_loading(self):
        return bool(self._pending_async_resources)

    def _async_resource_loaded_cb(self, _self, resource):
        # assert resource.name in self._pending_async_resources
        # del self._pending_async_resources[resource.name]
        # if not self._pending_async_resources:
        #     self.emit('loading-complete')

        del self._pending_predecessors[resource.name]
        self._pending_async_resources.remove(resource.name)

        logger.info('resource %s loaded', resource.name)

        if not self._pending_async_resources:
            logger.info('loading complete!!!')
            self.emit('loading-complete')
        elif not self._pending_predecessors:
            logger.info('predecessors loaded')
            self._do_load_resources()

    def _async_resource_loading_failed_cb(self, _self, resource):
        logger.warning('Faliled to load the resource "{}"'.format(resource))


AsyncResourceLoader = _AsyncResourceLoader()


class AsyncResourceArgument:
    def __init__(self, func, *args, **kwargs):
        self._func = functools.partial(func, *args, **kwargs)

    def get_arg(self):
        return self._func()


class AsyncResource:
    def __init__(self, name, load_func, ready_func, deps=[]):
        self.name = name
        self.loader = AsyncResourceLoader
        self.deps = deps

        self._load_func = load_func
        self._ready_func = ready_func

        self._load_args = {'args': (), 'kwargs': {}}

    def set_load_args(self, *args, **kwargs):
        self._load_args = locals()

    def _get_real_load_args(self):
        new_args = {}

        args = self._load_args['args']
        new_args['args'] = \
            (arg if not isinstance(arg, AsyncResourceArgument) else arg.get_arg() for arg in args)

        kwargs = self._load_args['kwargs']
        new_args['kwargs'] = \
            {key: arg if not isinstance(arg, AsyncResourceArgument) else arg.get_arg()
                for (key, arg) in kwargs.items()}
        return new_args

    def load(self):
        load_args = self._get_real_load_args()
        self._load_func(*load_args['args'], **load_args['kwargs'])

    def ready(self, *args, **kwargs):
        if self._ready_func(*args, **kwargs):
            self.loader.emit('resource-loaded', self)
        else:
            self.loader.emit('loading-failed', self)


class AsyncDBusProxyResource(AsyncResource):
    def __init__(self, name, deps=[]):
        super().__init__(name, Gio.DBusProxy.new_for_bus, self._on_proxy_ready, deps)
        self.proxy = None

    def set_load_args(self, *args, **kwargs):
        super().set_load_args(*args, **kwargs)
        self._load_args['args'] = (*self._load_args['args'], self.ready)

    def _on_proxy_ready(self, proxy, result):
        try:
            self.proxy = proxy.new_finish(result)
        except GLib.Error as e:
            logger.warning("Error: Failed to get DBus proxy:", e.message)
            return False
        return True


resource = AsyncDBusProxyResource('proxy:dbus')
resource.set_load_args(Gio.BusType.SESSION, 0, None,
                       'org.freedesktop.DBus',
                       '/org/freedesktop/DBus',
                       'org.freedesktop.DBus',
                       None)
AsyncResourceRegistry.register_resource(resource)

resource = AsyncDBusProxyResource('proxy:shell-app-launcher')
resource.set_load_args(Gio.BusType.SESSION, 0, None,
                       'org.gnome.Shell',
                       '/org/gnome/Shell',
                       'org.gnome.Shell.AppLauncher',
                       None)
AsyncResourceRegistry.register_resource(resource)

resource = AsyncDBusProxyResource('proxy:shell-app-store')
resource.set_load_args(Gio.BusType.SESSION, 0, None,
                       'org.gnome.Shell',
                       '/org/gnome/Shell',
                       'org.gnome.Shell.AppStore',
                       None)
AsyncResourceRegistry.register_resource(resource)

resource = AsyncDBusProxyResource('proxy:shell')
resource.set_load_args(Gio.BusType.SESSION, 0, None,
                       'org.gnome.Shell',
                       '/org/gnome/Shell',
                       'org.gnome.Shell',
                       None)
AsyncResourceRegistry.register_resource(resource)

# Hack resources.
resource = AsyncDBusProxyResource('proxy:sound-server')
resource.set_load_args(Gio.BusType.SESSION, 0, None,
                       'com.hack_computer.HackSoundServer',
                       '/com/hack_computer/HackSoundServer',
                       'com.hack_computer.HackSoundServer',
                       None)
AsyncResourceRegistry.register_resource(resource)

resource = AsyncDBusProxyResource('proxy:game-state-service')
resource.set_load_args(Gio.BusType.SESSION, 0, None,
                       'com.hack_computer.GameStateService',
                       '/com/hack_computer/GameStateService',
                       'com.hack_computer.GameStateService',
                       None)
AsyncResourceRegistry.register_resource(resource)

resource = AsyncDBusProxyResource('proxy:accounts')
resource.set_load_args(Gio.BusType.SYSTEM, 0, None,
                       'org.freedesktop.Accounts',
                       '/org/freedesktop/Accounts',
                       'org.freedesktop.Accounts',
                       None)
AsyncResourceRegistry.register_resource(resource)


def _find_user_name():
    accounts_resource = AsyncResourceRegistry.get('proxy:accounts')
    accounts_proxy = accounts_resource.proxy
    user_path = accounts_proxy.FindUserByName('(s)', GLib.get_user_name())
    return user_path


resource = AsyncDBusProxyResource('proxy:accounts-props', deps=['proxy:accounts'])
resource.set_load_args(Gio.BusType.SYSTEM, 0, None,
                       'org.freedesktop.Accounts',
                       AsyncResourceArgument(_find_user_name),
                       'org.freedesktop.DBus.Properties',
                       None)
AsyncResourceRegistry.register_resource(resource)

resource = AsyncDBusProxyResource('proxy:accounts-user', deps=['proxy:accounts'])
resource.set_load_args(Gio.BusType.SYSTEM, 0, None,
                       'org.freedesktop.Accounts',
                       AsyncResourceArgument(_find_user_name),
                       'org.freedesktop.Accounts.User',
                       None)
AsyncResourceRegistry.register_resource(resource)
