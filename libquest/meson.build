project('com.hack_computer.Libquest', version: '0.0.0')

gnome = import('gnome')

# Build options

jasmine_report_argument = ''
junit_reports_dir = get_option('jasmine_junit_reports_dir')
if junit_reports_dir != ''
    jasmine_report_argument = '--junit=@0@/${log/.log/.js.xml}'.format(junit_reports_dir)
endif

# Build rules
dbus_dep = dependency ('dbus-1')
gio = dependency('gio-2.0')
gio_unix = dependency('gio-unix-2.0')
glib = dependency('glib-2.0')
gobject = dependency('gobject-2.0')

pkgdatadir = join_paths(get_option('datadir'), meson.project_name())
gjs = find_program('gjs', 'gjs-console')

subdir('src')
subdir('data')

# Summary

message('\n'.join([
    '@0@ @1@'.format(meson.project_name(), meson.project_version()),
    '--------------------------------------',
    'Options:',
    '    Test reports dir: @0@'.format(get_option('jasmine_junit_reports_dir')),
    '',
    'Directories:',
    '    Install prefix: @0@'.format(get_option('prefix')),
    ''
]))
