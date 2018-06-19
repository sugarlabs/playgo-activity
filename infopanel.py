# -*- coding: UTF-8 -*-
# Copyright 2007-2008 One Laptop Per Child
# Copyright 2007 Gerard J. Cerchio <www.circlesoft.com>
# Copyright 2008 Andrés Ambrois <andresambrois@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gi.repository import Gtk
from gi.repository import Gdk


class InfoPanel(Gtk.EventBox):

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.Box = Gtk.VBox()
        self.status_label = Gtk.Label()
        self.Box.pack_start(self.status_label, True, True, 10)

        self.score_label = Gtk.Label()
        self.Box.pack_start(self.score_label, True, True, 10)
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color.parse("dark grey")[1])
        self.add(self.Box)

        self.show_all()

    def show(self, text):
        self.status_label.set_text(text)

    def show_score(self, text):
        self.score_label.set_text(text)
