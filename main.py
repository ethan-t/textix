#!/usr/bin/env python3

import os
from autopep8 import fix_code
from yapf.yapflib.yapf_api import FormatCode
from subprocess import call
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
gi.require_version('Keybinder', '3.0')
from gi.repository import Gtk, Pango
from gi.repository import GtkSource
from gi.repository import Keybinder
from gi.repository.GtkSource import View as SourceView


class SearchDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Search", parent,
                            Gtk.DialogFlags.MODAL, buttons=(
                                Gtk.STOCK_FIND, Gtk.ResponseType.OK,
                                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        box = self.get_content_area()

        self.entry = Gtk.Entry()
        box.add(self.entry)

        self.show_all()


class Editor(Gtk.Window):
    def __init__(self):
        self.file = "Unnamed"
        Gtk.Window.__init__(self, title="Textix - " + self.file)
        self.set_default_size(200, 400)
        self.grid = Gtk.Grid()
        self.add(self.grid)
        self.create_sourceview()
        self.create_toolbar()

    def create_toolbar(self):
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 0, 0, 3, 1)

        Keybinder.init()
        Keybinder.bind("<Ctrl>S", self.save)

        button_open = Gtk.ToolButton()
        button_open.set_icon_name("document-open-symbolic")
        toolbar.insert(button_open, 0)

        button_save = Gtk.ToolButton()
        button_save.set_icon_name("document-save-symbolic")
        toolbar.insert(button_save, 1)

        button_save_as = Gtk.ToolButton()
        button_save_as.set_icon_name("document-save-as-symbolic")
        toolbar.insert(button_save_as, 2)

        toolbar.insert(Gtk.SeparatorToolItem(), 3)

        button_redo = Gtk.ToolButton()
        button_redo.set_icon_name("edit-redo-symbolic")
        toolbar.insert(button_redo, 4)

        button_undo = Gtk.ToolButton()
        button_undo.set_icon_name("edit-undo-symbolic")
        toolbar.insert(button_undo, 5)

        toolbar.insert(Gtk.SeparatorToolItem(), 6)

        button_search = Gtk.ToolButton()
        button_search.set_icon_name("edit-find-symbolic")
        toolbar.insert(button_search, 7)

        button_clear = Gtk.ToolButton()
        button_clear.set_icon_name("edit-clear-all-symbolic")
        toolbar.insert(button_clear, 8)

        toolbar.insert(Gtk.SeparatorToolItem(), 9)

        button_format = Gtk.ToolButton()
        button_format.set_icon_name("edit-select-all-symbolic")
        toolbar.insert(button_format, 10)

        self.statusbar = Gtk.Statusbar()
        self.context = self.statusbar.get_context_id("lc")
        self.grid.attach(self.statusbar, 0, 2, 1, 1)

        button_open.connect("clicked", self.open)
        button_save.connect("clicked", self.save)
        button_save_as.connect("clicked", self.save_as)
        button_redo.connect("clicked", self.sourcebuffer.redo)
        button_undo.connect("clicked", self.sourcebuffer.undo)
        button_search.connect("clicked", self.search)
        button_clear.connect("clicked", self.clear)
        button_format.connect("clicked", self.format)

    def create_sourceview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 1, 3, 1)
        self.sourceview = SourceView()
        self.sourcebuffer = self.sourceview.get_buffer()
        self.sourceview.set_show_line_numbers(True)
        self.sourceview.set_highlight_current_line(True)
        self.sourceview.set_insert_spaces_instead_of_tabs(True)
        self.sourceview.set_auto_indent(True)
        self.sourceview.modify_font(Pango.FontDescription("Ubuntu Mono 11"))
        self.sourceview.set_indent_width(4)
        self.sourcebuffer.connect("notify::cursor-position", self.cursorStatus)

        lang_manager = GtkSource.LanguageManager()
        self.sourcebuffer.set_language(GtkSource.Language())
        self.sourcebuffer.set_language(lang_manager.get_language("python3"))
        self.sourcebuffer.set_highlight_syntax(True)
        self.tag_found = self.sourcebuffer.create_tag(
            "found", background="yellow")

        scrolledwindow.add(self.sourceview)

    def open(self, widget):
        dialog = Gtk.FileChooserDialog("Choose a file to edit", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filter(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.file = dialog.get_filename()
            self.set_title("Textix - " + self.file)
            with open(self.file) as f:
                self.sourcebuffer.set_text(f.read())
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    def save(self, widget):
        if self.file == "Unnamed":
            self.save_as(self, widget)
        else:
            with open(self.file, "w") as f:
                f.write(self.sourcebuffer.get_text(
                    self.sourcebuffer.get_start_iter(), self.sourcebuffer.get_end_iter(), True))

    def add_filter(self, dialog):
        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        filter_python = Gtk.FileFilter()
        filter_python.set_name("Python")
        filter_python.add_pattern("*.py")
        dialog.add_filter(filter_python)

    def save_as(self, widget):
        dialog = Gtk.FileChooserDialog("Choose a file to save to", self,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filter(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.file = dialog.get_filename()
            self.set_title("Textix - " + self.file)
            with open(self.file, "w") as f:
                f.write(self.sourcebuffer.get_text(
                    self.sourcebuffer.get_start_iter(), self.sourcebuffer.get_end_iter(), True))
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    def cursorStatus(self, widget, huh):
        line = str(self.sourcebuffer.get_iter_at_mark(
            self.sourcebuffer.get_insert()).get_line() + 1)
        index = str(self.sourcebuffer.get_iter_at_mark(
            self.sourcebuffer.get_insert()).get_line_index())
        self.statusbar.push(self.context, "Line Number: " +
                            line + ", Character: " + index)

    def search(self, widget):
        dialog = SearchDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            cursor_mark = self.sourcebuffer.get_insert()
            start = self.sourcebuffer.get_iter_at_mark(cursor_mark)
            if start.get_offset() == self.sourcebuffer.get_char_count():
                start = self.sourcebuffer.get_start_iter()

            self.search_and_mark(dialog.entry.get_text(), start)

        dialog.destroy()

    def clear(self, widget):
        start = self.sourcebuffer.get_start_iter()
        end = self.sourcebuffer.get_end_iter()
        self.sourcebuffer.remove_tag_by_name("found", start, end)

    def search_and_mark(self, text, start):
        end = self.sourcebuffer.get_end_iter()
        match = start.forward_search(text, 0, end)

        if match != None:
            match_start, match_end = match
            self.sourcebuffer.apply_tag(self.tag_found, match_start, match_end)
            self.search_and_mark(text, match_end)

    def format(self, widget):
        old_code = self.sourcebuffer.get_text(
            self.sourcebuffer.get_start_iter(), self.sourcebuffer.get_end_iter(), True)
        new_code = fix_code(old_code)
        newest_code = FormatCode(new_code)[0]
        print(newest_code)
        self.sourcebuffer.set_text(newest_code)


win = Editor()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
