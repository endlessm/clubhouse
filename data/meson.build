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
    source_dir : [
        '.',
        './assets'
    ],
    gresource_bundle: true,
    install: true,
    install_dir: install_dir
)

install_data(
    'eos-clubhouse.desktop',
    install_dir: join_paths(data_dir, 'applications')
)

install_subdir(
    'characters',
    install_dir: join_paths(data_dir, meson.project_name())
)

characters_dir = join_paths(data_dir, meson.project_name(), 'characters')

quests_strings_csv_name = 'quests_strings'

install_subdir(
    quests_strings_csv_name,
    install_dir: join_paths(data_dir, meson.project_name())
)

quests_strings_csv = join_paths(data_dir, meson.project_name(), quests_strings_csv_name)

quests_items_csv_name = 'quests_items.csv'

install_data(
    quests_items_csv_name,
    install_dir: join_paths(data_dir, meson.project_name())
)

quests_items_csv = join_paths(data_dir, meson.project_name(), quests_items_csv_name)

install_subdir(
    'items',
    install_dir: join_paths(data_dir, meson.project_name())
)

item_icons_dir = join_paths(data_dir, meson.project_name(), 'items')
