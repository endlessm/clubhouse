conf = configuration_data()
conf.set('bindir', join_paths(prefix, get_option('bindir')))

dbus_dep = dependency ('dbus-1')
session_bus_services_dir = get_option('session-bus-services-dir')

if session_bus_services_dir == ''
   session_bus_services_dir = dbus_dep.get_pkgconfig_variable('session_bus_services_dir')
endif

configure_file(
    input: 'com.endlessm.Clubhouse.service.in',
    output: 'com.endlessm.Clubhouse.service',
    install: true,
    install_dir: session_bus_services_dir,
    configuration: conf
)

gnome.compile_resources(
    'eos-clubhouse',
    files('com.endlessm.Clubhouse.gresource.xml'),
    gresource_bundle: true,
    install: true,
    install_dir: install_dir
)
