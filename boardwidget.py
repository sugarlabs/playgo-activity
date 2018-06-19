# -*- coding: utf-8 -*-
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

from math import pi as PI

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf

import logging

logger = logging.getLogger('PlayGo.GoBoardWidget')


class GoBoardWidget(Gtk.DrawingArea):
    ''' A Go Board Widget '''

    __gsignals__ = {
        'insert-requested': (
            GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
            (GObject.TYPE_INT, GObject.TYPE_INT)),
    }

    # TODO: this should default to DEFAULT_SIZE, not 19,
    # but this is defined in activity.py not here
    def __init__(self, status, size=19):
        Gtk.DrawingArea.__init__(self)

        self.status = status
        self.size = size
        self.lastX = -1
        self.lastY = -1
        self.territories = None
        self.BoardPixbuf = GdkPixbuf.Pixbuf.new_from_file("./images/board.gif")
        self.WhitePixbuf = GdkPixbuf.Pixbuf.new_from_file("./images/white.gif")
        self.BlackPixbuf = GdkPixbuf.Pixbuf.new_from_file("./images/black.gif")

        self.set_size_request(500, 500)

        self.add_events(Gdk.EventMask.BUTTON1_MOTION_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.POINTER_MOTION_HINT_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK)

        self.connect('button-release-event', self.button_release_cb)
        self.connect("draw", self.draw_cb)

    def button_release_cb(self, widget, event):
        x, y = self.get_mouse_event_xy(event)
        self.emit('insert-requested', x, y)

    def draw_cb(self, widget, context):
        """This is where the widget must draw itself."""

        self.context = context
        alloc = self.get_allocation()

        # Scale everything
        self.unit = (min(alloc.height, alloc.width) + 10) / (self.size + 1)
        self.ScaledBlackPixbuf = self.BlackPixbuf.scale_simple(
            int(self.unit), int(self.unit), GdkPixbuf.InterpType.BILINEAR)
        self.ScaledWhitePixbuf = self.WhitePixbuf.scale_simple(
            int(self.unit), int(self.unit), GdkPixbuf.InterpType.BILINEAR)
        # Draw the board
        Gdk.cairo_set_source_pixbuf(context, self.BoardPixbuf, 0, 0)
        context.paint()

        # Draw the lines
        self.draw_lines(context)
        # Draw the stones
        self.draw_stones(context, self.status)
        # Draw scored terriotires if they exist (end of game)
        if self.territories:
            self.draw_scored_territories(context, self.territories)

    def draw_lines(self, ctx):
        # Single width black lines
        ctx.set_line_width(1)
        ctx.set_source_rgba(0, 0, 0, 1)

        # Horizontal lines
        for i in xrange(1, self.size + 1):
            ctx.move_to(self.unit, i * self.unit)
            ctx.line_to(self.size * self.unit, i * self.unit)

        # Vertical lines
        for i in xrange(1, self.size + 1):
            ctx.move_to(i * self.unit, self.unit)
            ctx.line_to(i * self.unit, self.size * self.unit)

        ctx.stroke()

        # star point coords per board size
        if self.size == 19:
            seq = [4, 10, 16]

        elif self.size == 13:
            seq = [4, 7, 10]

        elif self.size == 9:
            seq = [3, 7]
            # set the middle singleton
            ctx.arc(self.unit * 5, self.unit * 5, 3, 0, PI * 2)
            ctx.fill_preserve()
            ctx.stroke()

        else:
            seq = []

        # stroke in the star points
        # TODO: adjust size for teeny boards
        for x in seq:
            for y in seq:
                ctx.arc(self.unit * x, self.unit * y, 3, 0, PI * 2)
                ctx.fill_preserve()
                ctx.stroke()

    def draw_stone(self, ctx, x, y, color, widget):
        """
        paint a single stone on a point
        """

        x = x + 1
        y = y + 1

        Gdk.cairo_set_source_pixbuf(
            ctx,
            self.ScaledBlackPixbuf if color == 'B' else self.ScaledWhitePixbuf,
            self.unit * x - self.unit / 2, self.unit * y - self.unit / 2)

        ctx.paint()

    def draw_stones(self, ctx, status):
        for x in status.keys():
            self.draw_stone(ctx, x[0], x[1], status[x], self)

    def draw_scored_territory(self, ctx, x, y, color, widget):
        x = x + 1
        y = y + 1

        if color == 'B':
            ctx.set_source_rgba(0, 0, 0, 1)
        else:
            ctx.set_source_rgba(1, 1, 1, 1)

        ctx.set_line_width(4)

        # Horizontal mark
        ctx.move_to(self.unit * x - self.unit / 4, self.unit * y)
        ctx.line_to(self.unit * x + self.unit / 4, self.unit * y)

        # Vertical mark
        ctx.move_to(self.unit * x, self.unit * y - self.unit / 4)
        ctx.line_to(self.unit * x, self.unit * y + self.unit / 4)

        ctx.stroke()

    def draw_scored_territories(self, ctx, territories):
        for color in territories.keys():
            for n in territories[color]:
                self.draw_scored_territory(ctx, n[0], n[1], color, self)

    def get_mouse_event_xy(self, event):
        """
        calculate the x and y position on the board given pixel address
        """

        x0 = 0  # self.get_allocation().x
        y0 = 0  # self.get_allocation().y
        x = int(((event.x - x0) / (self.unit if self.unit > 0 else 1)) - 0.5)
        y = int(((event.y - y0) / (self.unit if self.unit > 0 else 1)) - 0.5)
        if x > self.size - 1:
            x = self.size - 1

        if y > self.size - 1:
            y = self.size - 1

        return x, y

    def redraw_area(self, x, y):
        x, y = self.get_pixel_from_coordinates(x, y)
        rect = Gdk.Rectangle()
        rect.x = int(x - self.unit / 2)
        rect.y = int(y - self.unit / 2)
        rect.width = int(self.unit)
        rect.height = int(self.unit)
        self.get_window().invalidate_rect(rect, False)

    def draw_ghost_stone(self, x, y, color):
        x, y = self.get_pixel_from_coordinates(x, y)
        if x == self.lastX and y == self.lastY:
            return

        if self.lastX is not -1:
            rect = Gdk.Rectangle()
            rect.x = int(self.lastX - self.unit / 2)
            rect.y = int(self.lastY - self.unit / 2)
            rect.width = int(self.unit)
            rect.height = int(self.unit)
            self.get_window().invalidate_rect(rect, False)

        self.lastX = x
        self.lastY = y

        ctx = self.context
        if color is 'B':
            ctx.set_source_rgba(0, 0, 0, .5)
        else:
            ctx.set_source_rgba(1, 1, 1, .5)

        ctx.arc(self.lastX, self.lastY, self.unit / 2 - 4, 0, 2 * PI)
        ctx.fill_preserve()
        ctx.stroke()
        del ctx

    def get_pixel_from_coordinates(self, x, y):
        if x > self.size - 1:
            x = self.size - 1

        if y > self.size - 1:
            y = self.size - 1

        x = (x + 1) * self.unit
        y = (y + 1) * self.unit

        return x, y

    def clear(self):
        self.lastX = -1
        self.lastY = -1
        self.queue_draw()
