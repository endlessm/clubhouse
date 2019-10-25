# Scripts to generate the hack cursor theme

To run this you need to have installed:

 * org.inkscape.Inkscape
 * xcursorgen

If you're using EOS you can use toolbox to install xcursorgen:

```
 $ toolbox create --release f30
 $ toolbox enter -c fedora-toolbox-30
 $ toolbox run -c fedora-toolbox-30 sudo dnf install xorg-x11-apps
 $ echo "xcursorgen='toolbox run -c fedora-toolbox-30 xcursorgen'" > .env
```

The `gen.sh` script rebuild all files and place all cursors in the 'output'
folder.

In each folder there are one or more svg files that are the cursor sources and
two scripts:

 * gen-png.sh: Generates the pngs for all sizes using the svg file
 * gen.in.sh: Generates a xcursorgen.in file with the cursor options, each line
              of the output file is of the form:
                <size> <xhot> <yhot> <filename> <ms-delay>

All sizes are in the file `sizes`.
