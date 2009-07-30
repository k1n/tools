#!/bin/bash

for size in 16 22 24 32 36 48 64 96 128
do
	dir=${size}x${size}
	mkdir $dir
	convert -resize $size orig.png ubuntu-tweak.png
	echo -e "icondir = \$(datadir)/icons/hicolor/${dir}/apps
icon_DATA = ubuntu-tweak.png

EXTRA_DIST = \$(icon_DATA)" > $dir/Makefile.am
	mv ubuntu-tweak.png $dir
	echo $size
done
