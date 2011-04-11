#!/bin/sh

LANGSPEC_DIR="/usr/share/gtksourceview-2.0/language-specs"
LANGSPEC_FILE="haxe.lang"

MIME_DIR="/usr/share/mime/packages"
MIME_FILE="haxe.xml"

if [ `whoami` != "root" ]; then
        echo " !! Execute the installation as root or with sudo to install the syntax file"
	exit 1
fi

echo "Installing the syntax file to $LANGSPEC_DIR"
cp "$LANGSPEC_FILE" "$LANGSPEC_DIR/$LANGSPEC_FILE"

if [ ! -f "$MIME_DIR/$MIME_FILE" ]; then
        echo "Installing the mime type file to $MIME_FILE"
	cp "$MIME_FILE" "$MIME_DIR/$MIME_FILE"
        echo "Refreshing mime-types"
	update-mime-database /usr/share/mime
else
	echo "The Mime file is already installed in $MIME_DIR/$MIME_FILE"
fi
