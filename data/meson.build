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
    install_dir: clubhouse_data_dir
)

install_data(
    'eos-clubhouse.desktop',
    install_dir: join_paths(data_dir, 'applications')
)

characters_dir_name = 'characters'
items_dir_name = 'items'
quests_strings_csv_name = 'quests_strings'
quests_items_csv_name = 'quests_items.csv'

data_paths = [characters_dir_name, items_dir_name, quests_strings_csv_name, quests_items_csv_name]

foreach path : data_paths
    install_subdir(path, install_dir: clubhouse_data_dir)
endforeach

# For later substitution in the config file
characters_dir = join_paths(clubhouse_data_dir, characters_dir_name)
item_icons_dir = join_paths(clubhouse_data_dir, items_dir_name)
quests_strings_csv = join_paths(clubhouse_data_dir, quests_strings_csv_name)
quests_items_csv = join_paths(clubhouse_data_dir, quests_items_csv_name)
