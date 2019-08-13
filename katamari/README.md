# katamari

Deploy infrastructure for the Hack components

## About

This is a tool to build and install a Flatpak containing all the Hack
modules. It can be configured by editing an INI file.

See the [example INI file][1] for information about each setting. To
customize the settings, you can copy the example INI to `config.ini`
in the base folder. Also, a copy will be made automatically for you
the first time you run the build tool.

## Building and Installing Clubhouse katamari

``` shell
./tools/build-clubhouse
```

This script will use the config.ini file for modules and configuration.

By default this script will also build the clippy extension using the config
file clippy.config.ini, if you don't want to build the clippy extension you
can change that in the `config.ini` file, in the Common section the option
`build-extension`.

## Building the clippy extension

``` shell
./tools/build-clippy-extension
```

This script will use the clippy.config.ini file for configuration and will
only build the clippy extension. Keep in mind that you'll need the Clubhouse
installed to be able to build the extension.

## Tool Development

To run the linter:

``` shell
flake8 ./tools/*
```

To run the tests inside the build script:

``` shell
python3 ./tools/_common.py
```

## Authentication
Katamari uses private Endless repos. In order to build them without
the need to provide user name and password please set up your GitHub
account to use SSH authentication.
https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account

[1]: https://github.com/endlessm/katamari/blob/master/data/config.ini.example
