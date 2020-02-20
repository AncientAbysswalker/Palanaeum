# -*- coding: utf-8 -*-
"""This module contains custom widgets (composite panels) to be used in the main application frame."""


import wx
import wx.lib.agw.ultimatelistctrl as ULC
import os

import dialog

import fn_path


class DummyFileDrop(wx.FileDropTarget):
    """Dummy class to catch files dropped onto the add documents button

        Args:
            parent (ref): Reference to the parent wx.object
            target_function (ref): Reference to the intended function to trigger and pass filepaths to

        Attributes:
            parent (ref): Reference to the parent wx.object
            target_function (ref): Reference to the intended function to trigger and pass filepaths to
    """

    def __init__(self, parent, target_function):
        """Constructor"""
        wx.FileDropTarget.__init__(self)

        self.window = parent
        self.target_function = target_function

    def OnDropFiles(self, x, y, file_paths):
        """Trigger target_function when files are dropped onto this widget

            Args:
                x (int): Integer x position that the file(s) were dropped on
                y (int): Integer y position that the file(s) were dropped on
                file_paths (list: str): A list of string paths for the file(s) dropped onto this widget
        """

        self.target_function(file_paths)

        return True


class CompositeLibrary(wx.Panel):
    """Custom widget that overlays an button on top of a wx list control

        Class Variables:
            btn_size (int): Size of the button in the overlay

        Args:
            parent (ref): Reference to the parent wx.object
            root_pane (ref): Reference to the upstream wx.object pane

        Attributes:
            parent (ref): Reference to the parent wx.object
            root_tab (ref): Reference to the upstream wx.object tab
            root_pane (ref): Reference to the upstream wx.object pane
    """

    btn_size = 25

    def __init__(self, parent, root_pane):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        # Parental inheritance
        self.parent = parent
        self.root_tab = parent
        self.root_pane = root_pane

        # File drop hook
        file_drop_target = DummyFileDrop(self, self.evt_dragged_files)

        # Button overlay and binding
        self.btn_add_image = wx.BitmapButton(self,
                                             bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                             size=(CompositeLibrary.btn_size,) * 2)

        # Library subwidget
        self.pnl_library = ULC.UltimateListCtrl(self,
                                                wx.ID_ANY,
                                                agwStyle = wx.LC_REPORT |
                                                           wx.LC_VRULES |
                                                           wx.LC_HRULES)
        self.pnl_library.Bind(ULC.EVT_LIST_ITEM_ACTIVATED, self.evt_open_document)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_CHECK
        info._image = []
        info._format = 0
        info._kind = 1
        info._text = "File Name"
        self.pnl_library.InsertColumnInfo(0, info)

        info = ULC.UltimateListItem()
        info._format = wx.LIST_FORMAT_RIGHT
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT
        info._image = []
        info._text = "Title"
        # info._font = boldfont
        self.pnl_library.InsertColumnInfo(1, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info._format = 0
        info._text = "Category"
        # info._font = font
        info._image = []
        self.pnl_library.InsertColumnInfo(2, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info._format = 0
        info._text = "Discipline"
        # info._font = font
        info._image = []
        self.pnl_library.InsertColumnInfo(3, info)

        for i, result in enumerate(self.parent.search_results):
            self.pnl_library.InsertStringItem(i, result[0])
            self.pnl_library.SetStringItem(i, 1, result[1])
            self.pnl_library.SetStringItem(i, 2, self.root_pane.id_to_category[result[2]])
            self.pnl_library.SetStringItem(i, 3, self.root_pane.id_to_discipline[result[3]])

        self.pnl_library.SetColumnWidth(0, 120)
        self.pnl_library.SetColumnWidth(1, 120)
        self.pnl_library.SetColumnWidth(2, 120)
        self.pnl_library.SetColumnWidth(3, -3)

        # Button overlay binding - Must be after subwidget to bind to
        self.btn_add_image.Bind(wx.EVT_BUTTON, self.evt_click_button)
        self.btn_add_image.Bind(wx.EVT_SET_FOCUS, self.evt_btn_no_focus)
        self.btn_add_image.SetDropTarget(file_drop_target)

        # Main sizer - do not add button so it floats
        szr_main = wx.BoxSizer(wx.VERTICAL)
        szr_main.Add(self.pnl_library, proportion=1, flag=wx.EXPAND)
        self.SetSizer(szr_main)

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

    def evt_open_document(self, event):
        """Open the desired document after double-clicking on an entry in the library

            Args:
                event: A double-click event object passed from the list control
        """

        _file_name, _title, _id_category, _id_discipline, _id_level3 = (self.root_tab.search_results[event.GetIndex()])
        _category = self.root_pane.id_to_category[_id_category]
        _discipline = self.root_pane.id_to_discipline[_id_discipline]
        _level3 = self.root_pane.id_to_level3[int(_id_level3)] if _id_level3 else None  # Need to int() the key

        os.startfile(self.cmd_escape(fn_path.concat_archive(_file_name, _category, _discipline, _level3)))

    def evt_click_button(self, event):
        """Open a dialog to chose files to add after clicking the add button

            Args:
                event: A button event object passed from the button clicked
        """

        print("test")

    def evt_dragged_files(self, file_paths):
        """Trigger dialog to add new documents

            Args:
                file_paths (list: str): A list of string paths for the file(s) dropped onto this widget
        """

        for document in file_paths:
            _dlg = dialog.AddDocument(self, self.root_pane, document)
            _dlg.ShowModal()
            #if _dlg: _dlg.DestroyLater()

    def evt_resize(self, event):
        """Move the button overlay when resized

            Args:
                event: A resize event object passed from the resize event
        """

        # Get width and height of the resize and subtract a tuple representing the scrollbar size
        (_w, _h) = event.GetSize() - (16, 1)

        # Move the button that adds more images
        self.btn_add_image.SetPosition((_w - CompositeLibrary.btn_size, _h - CompositeLibrary.btn_size))

        # Refresh Layout required for unknown reasons - otherwise odd scale behaviour on pnl_gallery
        self.Layout()

    def evt_btn_no_focus(self, event):
        """Prevents focus from being called on the buttons

            Args:
                event: A focus event
        """
        pass

    @staticmethod
    def cmd_escape(text):
        return '"' + text + '"'


class Restrictions(wx.Panel):
    """Custom widget that contains all restriction checkboxes, and can be collapsed

        Args:
            parent (ptr): Reference to the wx.object this panel belongs to

        Attributes:
            parent (ptr): Reference to the wx.object this panel belongs to
            show_restrictions (bool): State of whether the widget is collapsed or not
    """

    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        # Parental inheritance
        self.parent = parent

        # Instance Variables
        self.show_restrictions = False

        # Subwidget for "Search for text in:" and its sizer
        self.wgt_ls_chk_searchin = []
        wgt_staticbox_searchin = wx.StaticBox(self, label="Search for text in:")
        self.szr_chk_searchin = wx.StaticBoxSizer(wgt_staticbox_searchin, wx.VERTICAL)

        for search_field in ["File Name", "Document Title"]:
            _new_checkbox = wx.CheckBox(self, label=search_field)
            _new_checkbox.SetValue(True)
            self.wgt_ls_chk_searchin.append(_new_checkbox)
            self.szr_chk_searchin.Add(_new_checkbox)

        # Subwidget for "Restrict to categories:" and its sizer
        self.wgt_ls_chk_category = []
        wgt_staticbox_category = wx.StaticBox(self, label="Restrict to categories:")
        self.szr_chk_category = wx.StaticBoxSizer(wgt_staticbox_category, wx.VERTICAL)

        for category in self.parent.category_to_id:
            _new_checkbox = wx.CheckBox(self, label=category)
            self.wgt_ls_chk_category.append(_new_checkbox)
            self.szr_chk_category.Add(_new_checkbox)

        # Subwidget for "Restrict to disciplines:" and its sizer
        self.wgt_ls_chk_disciplines = []
        wgt_staticbox_disciplines = wx.StaticBox(self, label="Restrict to disciplines:")
        self.szr_chk_disciplines = wx.StaticBoxSizer(wgt_staticbox_disciplines, wx.VERTICAL)

        for discipline in self.parent.discipline_to_id:
            _new_checkbox = wx.CheckBox(self, label=discipline)
            self.wgt_ls_chk_disciplines.append(_new_checkbox)
            self.szr_chk_disciplines.Add(_new_checkbox)

        # List of subwidget sizers to collapse
        self.wgt_ls_collapseable = []
        self.wgt_ls_collapseable.append(wgt_staticbox_searchin)
        self.wgt_ls_collapseable.append(wgt_staticbox_category)
        self.wgt_ls_collapseable.append(wgt_staticbox_disciplines)

        # If we do not desire to show the widget initially, hide all involved
        if not self.show_restrictions:
            for to_hide in self.wgt_ls_collapseable + \
                           self.wgt_ls_chk_disciplines + \
                           self.wgt_ls_chk_category + \
                           self.wgt_ls_chk_searchin:
                to_hide.Hide()

        # Main sizer
        szr_main = wx.StaticBoxSizer(wx.StaticBox(self, label="Search Restrictions (Click to Expand):"), 
                                     orient=wx.HORIZONTAL)
        szr_main.Add(self.szr_chk_searchin, proportion=1, flag=wx.EXPAND)
        szr_main.AddSpacer(2)
        szr_main.Add(self.szr_chk_category, proportion=1, flag=wx.EXPAND)
        szr_main.AddSpacer(2)
        szr_main.Add(self.szr_chk_disciplines, proportion=1, flag=wx.EXPAND)

        self.SetSizer(szr_main)

    def evt_click_header(self, event):
        if event.GetPosition()[1] < 20:
            self.toggle_restrictions()

    def toggle_restrictions(self):
        self.show_restrictions = not self.show_restrictions
        for each in self.wgt_ls_chk_searchin + self.wgt_ls_chk_disciplines + self.wgt_ls_chk_category + self.wgt_ls_collapseable:
            each.Show() if self.show_restrictions else each.Hide()
        self.parent.Layout()

    def evt_enter_widget(self, event):
        self.toggle_restrictions()

    def evt_leave_widget(self, event):
        if self.HitTest(event.Position) == wx.HT_WINDOW_OUTSIDE:
            self.toggle_restrictions()
