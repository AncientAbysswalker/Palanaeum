# -*- coding: utf-8 -*-
"""This module contains as class of widgets that support auto-completion dropdowns and forced lowercase text. \n

    Forked from the original source code by Toni Ruža at http://bitbucket.org/raz/wxautocompletectrl."""

import wx
import wx.html

import case_control


# noinspection PyPep8Naming
class SuggestionsPopup(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self, parent,
            style=(wx.FRAME_NO_TASKBAR |
                   wx.FRAME_FLOAT_ON_PARENT |
                   wx.STAY_ON_TOP)
        )
        self.suggestions = self._ListBox(self)
        self.suggestions.SetItemCount(0)
        self.unformated_suggestions = None

        self.Sizer = wx.BoxSizer()
        self.Sizer.Add(self.suggestions, 1, wx.EXPAND)

    class _ListBox(wx.html.HtmlListBox):
        items = None

        def OnGetItem(self, n):
            return self.items[n]

    def SetSuggestions(self, suggestions, unformated_suggestions):
        self.suggestions.items = suggestions
        self.suggestions.SetItemCount(len(suggestions))
        self.suggestions.SetSelection(0)
        self.suggestions.Refresh()
        self.unformated_suggestions = unformated_suggestions

    def CursorUp(self):
        selection = self.suggestions.GetSelection()
        if selection > 0:
            self.suggestions.SetSelection(selection - 1)

    def CursorDown(self):
        selection = self.suggestions.GetSelection()
        last = self.suggestions.GetItemCount() - 1
        if selection < last:
            self.suggestions.SetSelection(selection + 1)

    def CursorHome(self):
        if self.IsShown():
            self.suggestions.SetSelection(0)

    def CursorEnd(self):
        if self.IsShown():
            self.suggestions.SetSelection(self.suggestions.GetItemCount() - 1)

    def GetSelectedSuggestion(self):
        return self.unformated_suggestions[self.suggestions.GetSelection()]

    def GetSuggestion(self, n):
        return self.unformated_suggestions[n]


# noinspection PyPep8Naming
class LowercaseTextCtrl(case_control.LowercaseTextCtrl):

    completer = None
    popup = None

    def __init__(self, parent, id_=wx.ID_ANY, value=wx.EmptyString,
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
                 validator=wx.DefaultValidator, name=wx.TextCtrlNameStr,
                 height=300, completer=None, multiline=False, frequency=250,
                 append_mode=False):
        style = style | wx.TE_PROCESS_ENTER
        if multiline:
            style = style | wx.TE_MULTILINE

        # This line has changed to make the original wx.TextCtrl have forced lowercase text
        case_control.LowercaseTextCtrl.__init__(
            self, parent, id_, value, pos, size, style, validator, name
        )
        self.height = height
        self.frequency = frequency
        self.append_mode = append_mode

        # Handling for different data-types of completer
        if completer:
            if type(completer) == list:
                self.SetCompleter(self.list_completer(completer))
            else:
                self.SetCompleter(completer)

        self.queued_popup = False
        self.skip_event = False

    def SetAppendMode(self, append_mode):
        self.append_mode = append_mode

    def GetAppendMode(self):
        return self.append_mode

    def SetCompleter(self, completer):
        """Initializes the autocompletion.

        The 'completer' has to be a function with one argument
        (the current value of the control, ie. the query)
        and it has to return two lists: formated (html) and unformated
        suggestions.
        """
        self.completer = completer

        frame = self.TopLevelParent

        self.popup = SuggestionsPopup(self.TopLevelParent)

        frame.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_TEXT, self.OnTextUpdate)
        self.Bind(wx.EVT_SIZE, self.OnSizeChange)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.popup.suggestions.Bind(wx.EVT_LEFT_DOWN, self.OnSuggestionClicked)
        self.popup.suggestions.Bind(wx.EVT_KEY_DOWN, self.OnSuggestionKeyDown)

    def AdjustPopupPosition(self):
        self.popup.Move(self.ClientToScreen((0, self.Size.height)).Get())
        self.popup.Layout()
        self.popup.Refresh()

    def OnMove(self, event):
        self.AdjustPopupPosition()
        event.Skip()

    def OnTextUpdate(self, event):
        if self.skip_event:
            self.skip_event = False
        elif not self.queued_popup:
            wx.CallLater(self.frequency, self.AutoComplete)
            self.queued_popup = True
        event.Skip()

    def AutoComplete(self):
        self.queued_popup = False
        if self.Value != "":
            formated, unformated = self.completer(self.Value)
            if len(formated) > 0:
                self.popup.SetSuggestions(formated, unformated)
                self.AdjustPopupPosition()
                self.Unbind(wx.EVT_KILL_FOCUS)
                self.popup.ShowWithoutActivating()
                self.SetFocus()
                self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
            else:
                self.popup.Hide()
        else:
            self.popup.Hide()

    def OnSizeChange(self, event):
        self.popup.Size = (self.Size[0], self.height)
        event.Skip()

    def OnKeyDown(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_UP:
            self.popup.CursorUp()
            return

        elif key == wx.WXK_DOWN:
            self.popup.CursorDown()
            return

        elif key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and self.popup.Shown:
            self.skip_event = True
            if self.append_mode:
                self.AppendValue(self.popup.GetSelectedSuggestion())
            else:
                self.SetValue(self.popup.GetSelectedSuggestion())
            self.SetInsertionPointEnd()
            self.popup.Hide()
            return

        elif key == wx.WXK_HOME:
            self.popup.CursorHome()

        elif key == wx.WXK_END:
            self.popup.CursorEnd()

        elif event.ControlDown() and chr(key).lower() == "a":
            self.SelectAll()

        elif key == wx.WXK_ESCAPE:
            self.popup.Hide()
            return

        event.Skip()

    def OnSuggestionClicked(self, event):
        self.skip_event = True
        n = self.popup.suggestions.HitTest(event.Position)
        self.Value = self.popup.GetSuggestion(n)
        self.SetInsertionPointEnd()
        wx.CallAfter(self.SetFocus)
        event.Skip()

    def OnSuggestionKeyDown(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.skip_event = True
            if self.append_mode:
                self.AppendValue(self.popup.GetSelectedSuggestion())
            else:
                self.SetValue(self.popup.GetSelectedSuggestion())
            self.SetInsertionPointEnd()
            self.popup.Hide()
        event.Skip()

    def OnKillFocus(self, event):
        if not self.popup.IsActive():
            self.popup.Hide()
        event.Skip()

    def AppendValue(self, selection_suggestion):
        value = self.GetValue().lower()
        selection = selection_suggestion.lower()
        maxpos = 0
        for i in range(1, len(value) + 1):
            send = value[-i:]
            if selection.startswith(send):
                maxpos = i
        self.SetValue(
            self.GetValue()[:len(value) - maxpos] + selection_suggestion
        )

    @staticmethod
    def list_completer(a_list):
        def completer(query):
            formatted, unformatted = list(), list()
            if query:
                unformatted = [item for item in a_list if query in item]
                for item in unformatted:
                    s = item.find(query)
                    formatted.append(
                        "%s<b><u>%s</b></u>%s" % (item[:s], query, item[s + len(query):])
                    )

            return formatted, unformatted

        return completer
