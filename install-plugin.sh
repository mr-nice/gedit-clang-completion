#!/bin/sh

TARGET=""

LANGSPEC_DIR="/usr/share/gtksourceview-2.0/language-specs/"
LANGSPEC_FILE="haxe.lang"

MIME_DIR="/usr/share/mime/packages/"
MIME_FILE="haxe.xml"

if [ `whoami` = 'root' ]; then
	TARGET="/usr/lib/gedit-2/plugins"
	echo "Installation as root"
else
	TARGET="$HOME/.gnome2/gedit/plugins"
	mkdir -p "$TARGET"
	echo "Installation as user"
	rm -rf ~/.gnome2/gedit/plugins/haxecodecompletion*
	cp -Rf haxecodecompletion* ~/.gnome2/gedit/plugins
fi

echo "Installing haxe completion plugin in $TARGET"
