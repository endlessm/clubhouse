## Coding Style

    eslint .

## Compile Ink file (temp)

    # Needs https://github.com/manuq/inklecate-flatpak
    com.inklestudios.inklecate data/quests/p5-quest.ink

## Build and try (temp)

    ./build-flatpak.sh
    ./run.sh

## Run in persistent mode

Is useful to keep the server alive for debugging purposes. For that,
you can pass the following environment variable:

    flatpak run --env=HACK_LIBQUEST_PERSIST=1 com.hack_computer.Libquest

## Building inkjs

Inkjs ships a standalone build, but is not suitable for importing it
directly from GJS. So we need to rebuild it with custom settings.

- Clone the repository from https://github.com/y-lohse/inkjs
- Setup the project: `yarn install`
- Edit `rollup.config.js` to:
  - Change format: `const format = 'es';`
  - Remove these plugins & settings: `uglify`, `terser`, `sourcemaps`
- Rebuild with: `yarn build`
- Copy `dist/ink.js` to this module.
