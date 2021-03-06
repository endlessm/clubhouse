conf = configuration_data()
conf.set('bindir', join_paths(prefix, get_option('bindir')))

dbus_dep = dependency ('dbus-1')
session_bus_services_dir = get_option('session-bus-services-dir')

if session_bus_services_dir == ''
   session_bus_services_dir = dbus_dep.get_pkgconfig_variable('session_bus_services_dir')
endif

configure_file(
    input: 'com.hack_computer.Clubhouse.service.in',
    output: 'com.hack_computer.Clubhouse.service',
    install: true,
    install_dir: session_bus_services_dir,
    configuration: conf
)

gnome.compile_resources(
    'eos-clubhouse',
    files('com.hack_computer.Clubhouse.gresource.xml'),
    source_dir : [
        '.',
        './assets',
        './icons'
    ],
    gresource_bundle: true,
    install: true,
    install_dir: clubhouse_data_dir
)

schemaconf = configuration_data()
schemaconf.set('GETTEXT_PACKAGE', meson.project_name())
schema = configure_file(
  input: 'com.hack_computer.clubhouse.gschema.xml.in',
  output: 'com.hack_computer.clubhouse.gschema.xml',
  configuration: schemaconf,
  install_dir: schema_dir
)
custom_target('compile-schemas',
  input: schema,
  output: 'gschemas.compiled',
  command: [find_program('glib-compile-schemas'), meson.current_build_dir()],
  build_by_default: true,
  install_dir: schema_dir,
  install: true
)

install_data(
    'com.hack_computer.Clubhouse.desktop',
    install_dir: join_paths(data_dir, 'applications')
)

install_data(
    'com.hack_computer.Clubhouse.metainfo.xml',
    install_dir: join_paths(data_dir, 'metainfo')
)

install_data(
    'com.hack_computer.Clubhouse.svg',
    install_dir: 'share/icons/hicolor/scalable/apps'
)

install_data(
    'hack-data.ini',
    install_dir: join_paths(get_option('datadir'), 'hack-components')
)

characters_dir_name = 'characters'
items_dir_name = 'items'
achievements_dir_name = 'achievements'
episodes_dir_name = 'episodes'
newsfeed_dir_name = 'newsfeed'
quests_strings_dir_name = 'quests_strings'
quests_files_dir_name = 'quests_files'
tools_dir_name = 'tools'

data_dir_paths = [characters_dir_name, items_dir_name, achievements_dir_name, episodes_dir_name, newsfeed_dir_name, quests_strings_dir_name, quests_files_dir_name, tools_dir_name]

foreach path : data_dir_paths
    install_subdir(path, install_dir: clubhouse_data_dir)
endforeach

quests_items_csv_name = 'quests_items.csv'
episodes_csv_name = 'episodes.csv'
newsfeed_csv_name = 'newsfeed.csv'
achievements_csv_name = 'achievements.csv'

data_file_paths = [quests_items_csv_name, episodes_csv_name]

foreach path : data_file_paths
    install_data(path, install_dir: clubhouse_data_dir)
endforeach

# For later substitution in the config file
characters_dir = join_paths(clubhouse_data_dir, characters_dir_name)
item_icons_dir = join_paths(clubhouse_data_dir, items_dir_name)
achievements_dir = join_paths(clubhouse_data_dir, achievements_dir_name)
achievements_csv = join_paths(achievements_dir, achievements_csv_name)
episodes_dir = join_paths(clubhouse_data_dir, episodes_dir_name)
episodes_csv = join_paths(clubhouse_data_dir, episodes_csv_name)
quests_strings_dir = join_paths(clubhouse_data_dir, quests_strings_dir_name)
quests_items_csv = join_paths(clubhouse_data_dir, quests_items_csv_name)
quests_files_dir = join_paths(clubhouse_data_dir, quests_files_dir_name)
newsfeed_dir = join_paths(clubhouse_data_dir, newsfeed_dir_name)
newsfeed_csv = join_paths(newsfeed_dir, newsfeed_csv_name)
