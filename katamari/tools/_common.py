#!/usr/bin/env python3
#
# Tool to build and install a Flatpak containing all the Hack modules.
#
# Copyright (C) 2019 Endless Mobile, Inc.

import argparse
import configparser
import json
import os
import re
import shutil
import string
import subprocess
import sys

# Not all our modules are private, but since some are and we build all
# of them, we use the private GitHub URL:
GIT_URL_TEMPLATE = 'ssh://git@github.com/endlessm/{}.git'

DEFAULTS = {
    'Common': {
        'install': True,
        'bundle': False,
        'stable': False,
    },
    'Advanced': {
        'repo': 'repo',
        'branch': '',
        'extra_build_options': '',
        'extra_install_options': '',
    },
}


class BuildError(Exception):
    pass


class Config:
    def __init__(self, config_file, example_file=None, defaults=None, flatpak_branch=None):
        dst_config = os.path.join('katamari', config_file)
        if example_file is None:
            example_file = os.path.join('katamari', 'data', config_file + '.example')

        # If a config file doesn't exist, create it:
        if not os.path.exists(dst_config):
            shutil.copyfile(example_file, dst_config)

        self._config = configparser.ConfigParser()
        self._config.read(dst_config)

        if defaults is None:
            self._defs = DEFAULTS
        else:
            self._defs = defaults

        # flatpak_branch overrides the default and file configuration and
        # forces to use this value
        if flatpak_branch:
            self._config['Advanced']['branch'] = flatpak_branch

    def get(self, section, key):
        if section not in self._config:
            return self._defs[section][key]

        if isinstance(self._defs[section][key], bool):
            method_name = 'getboolean'
        else:
            method_name = 'get'

        method = getattr(self._config[section], method_name)
        return method(key, self._defs[section][key])

    def get_default_branch(self):
        return 'stable' if self.get('Common', 'stable') else 'master'

    def get_flatpak_branch(self):
        # First, check if there is an override in the advanced
        # settings:
        advanced_branch = self.get('Advanced', 'branch')
        if advanced_branch:
            return advanced_branch

        if 'Modules' in self._config and len(self._config['Modules']):
            return 'custom'

        return self.get_default_branch()

    def get_template_values(self, modules):
        template_values = {
            'BRANCH': self.get_flatpak_branch(),
        }

        default_git_branch = self.get_default_branch()

        for module in modules:
            source_key = _get_source_key(module)
            if 'Modules' in self._config and module in self._config['Modules']:
                module_value = self._config['Modules'][module]
                value = _get_source(module, module_value, default_git_branch)
            else:
                default_git_url = _get_default_git_url(module)
                value = _get_git_source(default_git_url, default_git_branch)

            template_values[source_key] = json.dumps(value)

            # Per-module options:
            if module in self._defs:
                for option in self._defs[module]:
                    option_key = _get_option_key(module, option)
                    value = self.get(module, option)
                    template_values[option_key] = json.dumps(value)

        return template_values

    def print_parsed_config(self):
        self._config.write(sys.stdout)


def _get_default_git_url(module):
    return GIT_URL_TEMPLATE.format(module)


def _get_source_key(module):
    return module.upper().replace('-', '_') + '_SOURCE'


def _get_option_key(module, option):
    return module.upper().replace('-', '_') + '_' + option.upper()


def _get_git_source(git_url, git_branch):
    return {
        'type': 'git',
        'url': git_url,
        'branch': git_branch,
    }


def _get_dir_source(directory):
    return {
        'type': 'dir',
        'path': directory,
        'skip': ['.flatpak-builder'],
    }


def _get_source(module, module_value, default_git_branch):
    """Get source for module to embed it in the flatpak manifest.

    It guesses what module_value means. Examples:

    - Passing a git branch:

    >>> _get_source('clubhouse', 'mybranch', default_git_branch='master')
    {'type': 'git', 'url': 'ssh://git@github.com/endlessm/clubhouse.git', 'branch': 'mybranch'}

    - Passing a git url:

    >>> _get_source('clubhouse', 'https://my-repo.git', default_git_branch='master')
    {'type': 'git', 'url': 'https://my-repo.git', 'branch': 'master'}

    - Passing a git url plus a git branch:

    >>> _get_source('clubhouse', 'https://my-repo.git:mybranch', default_git_branch='master')
    {'type': 'git', 'url': 'https://my-repo.git', 'branch': 'mybranch'}

    - Passing a local directory (Note: don't pass your home dir! This
      is just for testing):

    >>> s = _get_source('clubhouse', '~/', default_git_branch='master')
    >>> s['type']
    'dir'

    >>> from os.path import expanduser
    >>> expanduser("~") == s['path']
    True

    """
    if module_value.endswith('.git'):
        # We assume the format is a git url:
        return _get_git_source(module_value, default_git_branch)

    full_path = os.path.abspath(os.path.expanduser(module_value))
    if os.path.isdir(full_path):
        # We assume the format is a local directory:
        return _get_dir_source(full_path)

    if ':' in module_value:
        # We assume the format is a git url:branch
        git_url, git_branch = module_value.rsplit(':', 1)
        return _get_git_source(git_url, git_branch)

    # At last we assume the format is a git branch for the default git
    # url.
    git_url = _get_default_git_url(module)
    return _get_git_source(git_url, module_value)


def create_flatpak_manifest(config, modules, manifest, template=None):
    template_values = config.get_template_values(modules)

    manifest_file = manifest
    if template:
        template_values['BRANCH'] = '@BRANCH@'
        manifest_file = template

    manifest_out = ''
    with open(manifest + '.in') as fd:
        template = string.Template(fd.read())
        manifest_out = template.substitute(template_values)
        # Removing comments to avoid problems with strict json
        manifest_out = re.sub(r'\s*\/\*\*.*\*\*\/', '', manifest_out)

    with open(manifest_file, 'w') as fd:
        fd.write(manifest_out)


def run_command(*args, **kwargs):
    p = subprocess.run(*args, **kwargs)
    if p.returncode != 0:
        raise BuildError('Error running: {}'.format(' '.join(p.args)))


def build_flatpak(repo, manifest, extra_build_options=None):
    flatpak_builder_options = ['--force-clean', '--repo=' + repo]
    if extra_build_options:
        flatpak_builder_options.extend(extra_build_options.split())

    run_command(['flatpak-builder', 'build', manifest] + flatpak_builder_options)


def install_flatpak(repo, flatpak_branch, app_id, extra_install_options=None):
    flatpak_install_options = ['--reinstall']
    if extra_install_options:
        flatpak_install_options.extend(extra_install_options.split())
    run_command(['flatpak', 'install'] +
                flatpak_install_options +
                ['./' + repo, app_id + '//' + flatpak_branch])


def build_bundle(repo, flatpak_branch, app_id, options=[]):
    run_command(['flatpak', 'build-bundle', repo, app_id + '.flatpak',
                 app_id, flatpak_branch, *options])


def run(main, *args, **kwargs):
    parser = argparse.ArgumentParser(description='Tool to build and install a Flatpak.')
    parser.add_argument('mode', nargs='?', choices=('print-config',),
                        metavar='MODE',
                        help='print-config: Print the parsed configuration.')
    parser.add_argument('--manifest-template',
                        help=('Only generates the flatpak template manifest'
                              ' in the desired location.'))
    cli_args = parser.parse_args()

    # Run this script in the base directory:
    source_dir = subprocess.check_output(
        ['/usr/bin/git', 'rev-parse', '--show-toplevel'],
        universal_newlines=True).strip()
    os.chdir(source_dir)

    config = Config(*args, **kwargs)

    if cli_args.mode == 'print-config':
        config.print_parsed_config()
        sys.exit()

    try:
        main(config, cli_args.manifest_template)
    except BuildError as error:
        sys.exit(error)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
