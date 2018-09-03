#@todo: Properly filter the right files to be installed
install_subdir(
    '.',
    install_dir: install_dir
)

conf = configuration_data()
conf.set_quoted('characters_dir', characters_dir)

configure_file(
    input: 'config.py.in',
    output: 'config.py',
    install: true,
    install_dir: install_dir,
    configuration: conf
)
