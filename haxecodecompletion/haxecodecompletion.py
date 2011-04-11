# Copyright (C) 2006-2007 Osmo Salomaa
# Copyright (C) 2008 Rodrigo Pinheiro Marques de Araujo
# Copyright (C) 2008 Michael Mc Donnell                      
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


"""Complete python code with Ctrl+Alt+Space key combination."""


import gedit
import gobject
import gtk
import re
from complete import haxe_complete
import configurationdialog
import configuration

from completionwindow import CompletionWindow

class CompletionPlugin(gedit.Plugin):

    """Complete python code with the tab key."""

    re_alpha = re.compile(r"\w+", re.UNICODE | re.MULTILINE)
    re_non_alpha = re.compile(r"\W+", re.UNICODE | re.MULTILINE)

    def __init__(self):

        gedit.Plugin.__init__(self)
        self.completions = None
        self.name = "HaxeCompletionPlugin"
        self.window = None

    def activate(self, window):
        """Activate plugin."""

        self.window = window
        handler_ids = []
        callback = self.on_window_tab_added
        handler_id = window.connect("tab-added", callback)
        handler_ids.append(handler_id)
        window.set_data(self.name, handler_ids)
        for view in window.get_views():
            self.connect_view(view)

    def cancel(self):
        """Hide the completion window and return False."""
        return False

    def connect_view(self, view):
        """Connect to view's signals."""
        handler_ids = []
        callback = self.on_view_key_press_event
        handler_id = view.connect("key-press-event", callback)
        handler_ids.append(handler_id)
        view.set_data(self.name, handler_ids)

    def create_configure_dialog(self):
        """Creates and displays a ConfigurationDialog."""
        dlg = configurationdialog.ConfigurationDialog()
        return dlg

    def deactivate(self, window):
        """Deactivate plugin."""
        widgets = [window]
        widgets.append(window.get_views())
        widgets.append(window.get_documents())
        for widget in widgets:
            handler_ids = widget.get_data(self.name)
            for handler_id in handler_ids:
                widget.disconnect(handler_id)
            widget.set_data(self.name, None)
        self.window = None
        cleanup ()

    def display_completions(self, view, event):
        """Find completions and display them."""
        doc = view.get_buffer()
        insert = doc.get_iter_at_mark(doc.get_insert())

        offset = 0
        incomplete = u''
        text = unicode (doc.get_text (*doc.get_bounds ()), 'utf-8')

        # We first get the line we're in and verify we're not in a line comment
        linestart = insert.copy ()
        linestart.set_offset (insert.get_offset () - insert.get_line_offset ())
        current_line = unicode (doc.get_text (linestart, insert))
        comment_index = current_line.find ('//')       
        if comment_index != -1 and insert.get_line_offset () > comment_index:
            return self.cancel ()

        # Now we look if we're potentially inside a multi line comment, in which
        # case, we cancel the completion as well
        closing_multi_comment_index = text.rfind ('*/', 0, insert.get_offset ())
        opening_multi_comment_index = text.rfind ('/*', 0, insert.get_offset ())
        if opening_multi_comment_index > closing_multi_comment_index:
            return self.cancel ()
 
        # We get the incomplete word.
        start = insert.copy()
        while start.backward_char():
            char = unicode(start.get_char())
            if not self.re_alpha.match(char) or char == ".":
                start.forward_char()
                break
        incomplete = unicode(doc.get_text(start, insert))

        # If the number we're trying to complete is a digit, we stop the completion
        if incomplete.isdigit ():
            return self.cancel ()

        if event.keyval == gtk.keysyms.period:
            # If we complete with the dot key, gedit won't have inserted it prior to calling
            # this function, which is why we add the dot manually
            offset = insert.get_offset ()
            text = text[:offset] + '.' + text[offset:]
            if text[offset - 1] == '.': # We don't want to complete something we KNOW is incorrect.
                # This is just to avoid waiting when doing the ... operator.
                return self.cancel ()
            offset += 1
            incomplete = "" # When pressing . the incomplete word is the one right before the dot.
        else:
            offset = start.get_offset ()

        # We call the haxe engine to get the list of completion.
        completes = haxe_complete (doc.get_uri (), text, offset)

        # Nothing in the completion list, so no need to do anything
        if not completes:
            return self.cancel()

        self.show_popup (view, completes, incomplete)

    def is_configurable(self):
        """Show the plugin as configurable in gedits plugin list."""
        return True

    def on_view_key_press_event(self, view, event):
        """Display the completion window or complete the current word."""
        active_doc = self.window.get_active_document()
        # If the current tab is not a Haxe sourcefile, do not attempt to complete
        # TODO It would be best to never get called in the first place.

        try:
            if not active_doc.get_uri ().endswith ('hx'):
                return self.cancel ()
        except:
            return self.cancel ()

        #  The "Alt"-key might be mapped to something else
        # TODO Find out which keybinding are already in use.
        keybinding = configuration.getKeybindingCompleteTuple()
        ctrl_pressed = (event.state & gtk.gdk.CONTROL_MASK) == gtk.gdk.CONTROL_MASK
        #alt_pressed = (event.state & gtk.gdk.MOD1_MASK) == gtk.gdk.MOD1_MASK
        #shift_pressed = (event.state & gtk.gdk.SHIFT_MASK) == gtk.gdk.SHIFT_MASK
        keyval = gtk.gdk.keyval_from_name(keybinding[configuration.KEY])
        key_pressed = (event.keyval == keyval)

        # It's ok if a key is pressed and it's needed or
        # if a key is not pressed if it isn't needed.
        ctrl_ok = not (keybinding[configuration.MODIFIER_CTRL] ^ ctrl_pressed )
        #alt_ok =  not (keybinding[configuration.MODIFIER_ALT] ^ alt_pressed )
        #shift_ok = not (keybinding[configuration.MODIFIER_SHIFT] ^ shift_pressed )

        if ctrl_ok and key_pressed or event.keyval == gtk.keysyms.period:
            return self.display_completions(view, event)
        
        return self.cancel()

    def on_window_tab_added(self, window, tab):
        """Connect the document and view in tab."""
        self.connect_view(tab.get_view())


    def show_popup(self, view, completions, tempstr=""):
        """Show the completion window."""
        # Determine the position in x, y of the insert mark to later place the window
        wd = gtk.TEXT_WINDOW_TEXT
        doc = view.get_buffer ()
        rect = view.get_iter_location(doc.get_iter_at_mark (doc.get_insert()))
        x, y = view.buffer_to_window_coords(wd, rect.x, rect.y)
        x, y = view.translate_coordinates(self.window, x, y)
        
        # Get the original position of the Window
        root_x, root_y = self.window.get_position()
        # Create the popup
        popup = CompletionWindow(self.window, self)
        # Set its font accordingly
        context = view.get_pango_context()
        font_desc = context.get_font_description()
        popup.set_font_description(font_desc)
        # Position it
        # FIXME : Position should depend on the font.
        popup.move(root_x + x + 24, root_y + y + 44)
        # Set the completion list
        popup.set_completions(completions, tempstr)
        popup.show_all()
        
