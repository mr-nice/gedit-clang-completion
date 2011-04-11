#!/bin/sh

TARGET=""

if [ `whoami` = 'root' ]; then
	TARGET="/usr/lib/gedit-2/plugins"
	echo "Installation as root"
else
	TARGET="$HOME/.gnome2/gedit/plugins"
	mkdir -p "$TARGET"
	echo "Installation as user"
	rm -rf ~/.gnome2/gedit/plugins/clangcompletion*
	cp -Rf clangcompletion* ~/.gnome2/gedit/plugins
fi

echo "Installing clang completion plugin in $TARGET"
