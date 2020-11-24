# Versioning: We use major.minor.micro version convention with minor odds numbers
# for development releases and even numbers for production/stable releases.
#
# Version bump: pre and post release.

project('eos-clubhouse',
        ['c'],
        version: '1.10.0',
        license: 'GPLv2',
        meson_version: '>= 0.50.0',
)

git_revision = run_command('git', 'rev-parse', '--short', 'HEAD').stdout().strip()

cc = meson.get_compiler('c')
gnome = import('gnome')
i18n = import('i18n')
pymod = import('python')
python = pymod.find_installation('python3')

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
schema_dir = join_paths(data_dir, 'glib-2.0', 'schemas')
pkgdata_dir = join_paths(prefix, meson.project_name())
pythondir = python.get_install_dir()
clubhouse_data_dir = join_paths(data_dir, meson.project_name())

install_dir = join_paths(pythondir, 'eosclubhouse')
sources = []

subdir('data')
subdir('po')

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
