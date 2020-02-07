# -*- coding: utf-8 -*-
"""Main Interface Window and Application Launch"""

import sys
import wx

import pane
import mode

import config
import fn_path


class WindowFrame(wx.Frame):
    """Base class defining the application window (frame)"""

    def __init__(self, *args, **kwargs):
        """Constructor"""
        wx.Frame.__init__(self, *args, **kwargs)

        # Define the primary sizer for the primary pane
        self.szr_main = wx.BoxSizer(wx.VERTICAL)

        # Define the main pane, hide until after login, add to sizer
        self.pane_main = pane.PaneMain(self)
        self.szr_main.Add(self.pane_main, proportion=1, flag=wx.EXPAND)

        # Define lower status bar
        self.status = self.CreateStatusBar(1)
        self.status.SetStatusText("Written by Ancient Abysswalker")

        # Disable menu bar for the moment as I don't have a need for it
        # self.menubar = wx.MenuBar()
        # menu_file = wx.Menu()
        # menu_edit = wx.Menu()
        # menu_help = wx.Menu()
        # menu_file.Append(wx.NewId(), "New", "Creates A new file")
        # append_item = menu_file.Append(wx.NewId(), "Add ID", "Add an ID")
        # self.Bind(wx.EVT_MENU, self.evt_on_add, append_item)
        # self.menubar.Append(menu_file, "File")
        # self.menubar.Append(menu_edit, "Edit")
        # self.menubar.Append(menu_help, "Help")
        # self.SetMenuBar(self.menubar)

        # Set icon
        self.SetIcon(wx.Icon(fn_path.concat_gui('icon.png')))

        # Set window minimum size, set starting sizer and show window
        self.SetMinSize((700, 500))
        self.SetSizer(self.szr_main)
        self.Show()

    # def evt_on_add(self, event):
    #     pass


if __name__ == '__main__':
    """Launch the application."""

    # Set build number to display
    build = "1.0.0"

    # First set build/dev mode
    mode.set_mode(getattr(sys, 'frozen', False))

    # Define appliction and call config
    app = wx.App(False)
    config.load_config(app)

    # if getattr(sys, 'frozen', False):
    #     config.cfg["db_location"] = os.path.join(os.getcwd(), 'LoCaS.sqlite')
    #     config.cfg["img_archive"] = os.getcwd()

    # Define window size and frame, and start the main application loop
    win = WindowFrame(None, size=(1200, 600))
    win.SetTitle("Palanaeum - Build " + build)
    app.MainLoop()
