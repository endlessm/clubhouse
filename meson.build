project('eos-clubhouse',
        ['c'],
        version: '0.1',
        license: 'GPLv2',
        meson_version: '>= 0.45.0',
)

cc = meson.get_compiler('c')
gnome = import('gnome')
i18n = import('i18n')
python3 = import('python3')

#@todo: CHECK_IF_NEEDED
#
#
prefix = get_option('prefix')
po_dir = join_paths(meson.source_root(), 'po')
data_dir = join_paths(prefix, get_option('datadir'))
locale_dir = join_paths(prefix, get_option('localedir'))
local_state_dir = join_paths(prefix, get_option('localstatedir'))
libexec_dir = join_paths(prefix, get_option('libexecdir'))
source_root = join_paths(meson.source_root(), 'gnome-initial-setup')
pkgdata_dir = join_paths(prefix, meson.project_name())
pythondir = join_paths(prefix, python3.sysconfig_path('purelib'))
clubhouse_data_dir = join_paths(data_dir, meson.project_name())

install_dir = join_paths(pythondir, 'eosclubhouse')
sources = []

subdir('data')

if get_option('run-lint')
    lint_tool = find_program(['./tools/run-lint', 'run-lint'], required: true)

    message('Running Lint...')
    lint_result = run_command(lint_tool, 'tests', 'eosclubhouse')
    if lint_result.returncode() != 0
        error('Lint Failed:\n' + lint_result.stderr().strip())
    endif

    message('Lint Succeeded!')
endif

subdir('eosclubhouse')

install_data(
    'eos-clubhouse',
    install_dir: get_option('bindir')
)

subdir('tests')

meson.add_install_script('meson-postinstall.sh', install_dir)
