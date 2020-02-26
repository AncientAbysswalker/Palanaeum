# -*- coding: utf-8 -*-
"""This module defines base widgets that force all typed (ASCII) text to resolve as lowercase or uppercase"""

import wx
import string


class LowercaseTextCtrl(wx.TextCtrl):
    """Custom wrapper for wx.TextCtrl that forces all typed (ASCII) text to resolve as lowercase

        Args:
            *args and **args are directly passed to base wx.TextCtrl
    """

    def __init__(self, *args, **kwargs):
        """Constructor"""
        super(LowercaseTextCtrl, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_CHAR, self.on_char)

    def on_char(self, event):
        """Capture keystrokes and replace uppercase letters with lowercase letters

            Args:
                event: A keystroke event passed to the wx.TextCtrl
        """

        key = event.GetKeyCode()
        text_ctrl = event.GetEventObject()
        if chr(key) in string.ascii_letters:
            text_ctrl.AppendText(chr(key).lower())
            return
        event.Skip()

