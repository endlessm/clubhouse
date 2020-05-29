gnome.compile_resources('com.hack_computer.Libquest.src',
    'com.hack_computer.Libquest.src.gresource.xml',
    gresource_bundle: true, install: true, install_dir: pkgdatadir)

subst = configuration_data()
subst.set('GJS', gjs.path())
subst.set('PACKAGE_VERSION', meson.project_version())
subst.set('prefix', get_option('prefix'))
subst.set('libdir', get_option('libdir'))
subst.set('pkgdatadir', pkgdatadir)
configure_file(input: 'com.hack_computer.Libquest.in',
    output: 'com.hack_computer.Libquest',
    configuration: subst, install_dir: get_option('bindir'))
