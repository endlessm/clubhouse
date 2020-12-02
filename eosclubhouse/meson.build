#@todo: Properly filter the right files to be installed
install_subdir(
    '.',
    install_dir: install_dir
)

conf = configuration_data()
conf.set_quoted('project_name', meson.project_name())
conf.set_quoted('project_version', meson.project_version())
conf.set_quoted('git_revision', git_revision)
conf.set_quoted('characters_dir', characters_dir)
conf.set_quoted('quests_strings_dir', quests_strings_dir)
conf.set_quoted('quests_items_csv', quests_items_csv)
conf.set_quoted('quests_files_dir', quests_files_dir)
conf.set_quoted('item_icons_dir', item_icons_dir)
conf.set_quoted('achievements_dir', achievements_dir)
conf.set_quoted('achievements_csv', achievements_csv)
conf.set_quoted('episodes_dir', episodes_dir)
conf.set_quoted('episodes_csv', episodes_csv)
conf.set_quoted('newsfeed_dir', newsfeed_dir)
conf.set_quoted('newsfeed_csv', newsfeed_csv)
conf.set_quoted('data_dir', clubhouse_data_dir)
conf.set_quoted(
    'reset_script_path',
    join_paths(clubhouse_data_dir, 'tools', 'eos-hack-reset-clubhouse')
)
conf.set_quoted(
    'launch_script_path',
    join_paths(clubhouse_data_dir, 'tools', 'eos-hack-launch')
)
conf.set_quoted(
    'is_installed_script_path',
    join_paths(clubhouse_data_dir, 'tools', 'eos-hack-app-installed')
)
conf.set_quoted(
    'localedir',
    join_paths(get_option('prefix'), get_option('datadir'), 'locale')
)

conf.set_quoted('matomo_host', get_option('matomo-host'))
conf.set_quoted('matomo_site', get_option('matomo-site'))
conf.set_quoted('matomo_base_url', get_option('matomo-base-url'))

configure_file(
    input: 'config.py.in',
    output: 'config.py',
    install: true,
    install_dir: install_dir,
    configuration: conf
)

