# -*- coding: utf-8 -*-
"""This module defines custom dialog boxes called upon at various instances"""

import wx
import os
import shutil
import datetime
import sqlite3

import config
import fn_path
import autocomplete


class AddDocument(wx.Dialog):
    """Opens a dialog to edit document information prior to adding to the database

        Args:
            parent (ref): Reference to the parent wx.object
            root_pane (ref): Reference to the root parts tab
            old_type (str): The value of the part's "type" before editing

        Attributes:
            parent (ref): Reference to the parent wx.object
            root_pane (ref): Reference to the root parts tab
            old_type (str): The value of the part's "type" before editing
    """

    def __init__(self, parent, root_pane, doc_path):
        """Constructor"""
        super().__init__(parent)

        self.parent = parent
        self.root_pane = root_pane
        self.doc_path = doc_path
        self.doc_name = os.path.basename(doc_path)
        self.ls_tags = list(self.root_pane.tag_to_id.keys())
        self.ls_category = list(self.root_pane.category_to_id.keys())
        self.ls_discipline = list(self.root_pane.discipline_to_id.keys())

        self.ls_add_tags = []

        # Refresh tags list
        self.root_pane.load_tags()

        # Type selection dropdown, with bind and sizer
        self.wgt_filename = wx.StaticText(self, label=self.doc_name, style=wx.ALIGN_CENTER)
        self.wgt_drop_category = wx.ComboBox(self, choices=self.ls_category, style=wx.CB_READONLY)
        self.wgt_drop_discipline = wx.ComboBox(self, choices=self.ls_discipline, style=wx.CB_READONLY)
        self.wgt_drop_level3 = wx.ComboBox(self, choices=[], style=wx.CB_READONLY)

        self.wgt_btn_level3 = wx.Button(self, size=(15, 15))
        self.wgt_btn_level3.Bind(wx.EVT_BUTTON, self.evt_add_level3)

        # When category or discipline are chosen, set the level3 dropdown
        self.wgt_drop_category.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.evt_set_level3)
        self.wgt_drop_discipline.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.evt_set_level3)

        # Category Dropdown
        szr_category = wx.BoxSizer(wx.VERTICAL)
        szr_category.Add(wx.StaticText(self, label="Document Category:"))
        szr_category.Add(self.wgt_drop_category, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Discipline Dropdown
        szr_discipline = wx.BoxSizer(wx.VERTICAL)
        szr_discipline.Add(wx.StaticText(self, label="Engineering Discipline:"))
        szr_discipline.Add(self.wgt_drop_discipline, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Level3 Dropdown
        szr_level3 = wx.BoxSizer(wx.VERTICAL)
        szr_level3_top = wx.BoxSizer(wx.HORIZONTAL)
        szr_level3_top.Add(wx.StaticText(self, label="Subcategory:"))
        szr_level3_top.Add(wx.StaticText(self), proportion=1)
        szr_level3_top.Add(self.wgt_btn_level3, flag=wx.ALIGN_RIGHT)
        szr_level3.Add(szr_level3_top, flag=wx.ALL | wx.EXPAND)
        szr_level3.Add(self.wgt_drop_level3, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Master sizer for the selection dropdowns
        szr_drop = wx.StaticBoxSizer(wx.StaticBox(self, label="Select the type for this part to fall under"), orient=wx.HORIZONTAL)
        szr_drop.Add(szr_category, proportion=1, flag=wx.ALL, border=5)
        szr_drop.Add(szr_discipline, proportion=1, flag=wx.ALL, border=5)
        szr_drop.Add(szr_level3, proportion=1, flag=wx.ALL, border=5)

        # Tag addition box and bind
        self.wgt_title = wx.TextCtrl(self, style=wx.EXPAND)
        szr_title = wx.StaticBoxSizer(wx.StaticBox(self, label="Document Title - Please include the FULL title from the document itself:"), orient=wx.HORIZONTAL)
        szr_title.Add(self.wgt_title, proportion=1, flag=wx.ALL, border=5)

        # Tag addition box and bind
        self.wgt_add_tag = autocomplete.LowercaseTextCtrl(self, completer=self.ls_tags, style=wx.TE_PROCESS_ENTER)
        self.wgt_add_tag.Bind(wx.EVT_TEXT_ENTER, self.evt_add_tag)
        self.wgt_add_tag.Bind(wx.EVT_TEXT_PASTE, self.evt_paste)

        szr_add_tag = wx.StaticBoxSizer(
            wx.StaticBox(self, label="Add Tags - Press [ENTER] to commit tags; mutliple tags can be added:"),
            orient=wx.HORIZONTAL)
        szr_add_tag.Add(self.wgt_add_tag, proportion=1, flag=wx.ALL, border=5)

        # Added PDFs display pane
        self.wgt_tags = wx.TextCtrl(self, size=(500, -1), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.EXPAND)

        # Set initial selection
        # self.wgt_drop_doctype.SetValue(self.old_type)

        # Dialog buttons with binds
        btn_commit = wx.Button(self, label='Commit')
        btn_commit.Bind(wx.EVT_BUTTON, self.evt_commit)
        btn_cancel = wx.Button(self, label='Cancel')
        btn_cancel.Bind(wx.EVT_BUTTON, self.evt_cancel)

        # Dialog button sizer
        szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
        szr_buttons.Add(btn_commit)
        szr_buttons.Add(btn_cancel, flag=wx.LEFT, border=5)

        # Add everything to master sizer and set sizer for pane
        szr_master = wx.BoxSizer(wx.VERTICAL)
        szr_master.Add(self.wgt_filename, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        szr_master.Add(szr_drop, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        szr_master.Add(szr_title, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        szr_master.Add(szr_add_tag
                       , proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        szr_master.Add(szr_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        szr_main = wx.BoxSizer(wx.HORIZONTAL)
        szr_main.Add(szr_master, proportion=1, flag=wx.EXPAND | wx.ALL, border=20)
        szr_main.Add(self.wgt_tags, proportion=3, flag=wx.EXPAND)

        self.SetSizer(szr_main)

        # Set size and title
        self.SetSize((1000, 400))
        self.SetTitle("Change the 'type' for this component")

        self.Bind(wx.EVT_CLOSE, self.evt_close)

    def evt_add_level3(self, event):
        """Execute when adding a tag to the list of tags for this document

            Args:
                event: An enter keystroke event object passed from the wx.TextCtrl
        """

        _dlg = AddLevel3(self, self.root_pane)
        _dlg.ShowModal()

    def evt_set_level3(self, event):
        """Execute when adding a tag to the list of tags for this document

            Args:
                event: An enter keystroke event object passed from the wx.TextCtrl
        """

        if self.wgt_drop_discipline.GetValue() and self.wgt_drop_category.GetValue():

            # Connect to the database
            conn = sqlite3.connect(config.cfg['db_location'])
            crsr = conn.cursor()

            # Retrieve list of all tags from SQL database
            crsr.execute("SELECT id, level3 "
                         "FROM Level3 "
                         "WHERE discipline_id=(?) "
                         "AND category_id=(?);",
                         (self.root_pane.discipline_to_id[self.wgt_drop_discipline.GetValue()],
                          self.root_pane.category_to_id[self.wgt_drop_category.GetValue()]))

            # Set possible options for level 3 dropdown
            _level3_tuples = crsr.fetchall()
            self.level3_to_id = dict((level3, ident) for (ident, level3) in _level3_tuples)
            self.wgt_drop_level3.SetItems([i[1] for i in _level3_tuples])

            # Close connection
            crsr.close()
            conn.close()

    def evt_add_tag(self, event):
        """Execute when adding a tag to the list of tags for this document

            Args:
                event: An enter keystroke event object passed from the wx.TextCtrl
        """

        if self.wgt_add_tag.GetValue().strip() and self.wgt_add_tag.GetValue() not in self.ls_add_tags:
            self.ls_add_tags.append(self.wgt_add_tag.GetValue().strip())
            self.wgt_tags.SetValue("\n".join(self.ls_add_tags))

        self.wgt_add_tag.SetValue("")

    def evt_commit(self, event):
        """Execute when committing a change to the part type

            Args:
                event: A button event object passed from the button click
        """
        # self.evt_add_tag(event)

        _category_name = self.wgt_drop_category.GetValue()
        _discipline_name = self.wgt_drop_discipline.GetValue()

        if _category_name and _discipline_name:

            _discipline_id = self.root_pane.discipline_to_id[self.wgt_drop_discipline.GetValue()]
            _category_id = self.root_pane.category_to_id[self.wgt_drop_category.GetValue()]
            _level3_id = self.level3_to_id[self.wgt_drop_level3.GetValue()] if self.wgt_drop_level3.GetValue() else None
            _level3_name = self.wgt_drop_level3.GetValue()

            # Add any new tags
            self.root_pane.add_tags(self.ls_add_tags)

            # try:
            # Make directory if needed
            _path = fn_path.concat_archive(self.doc_name, _category_name, _discipline_name, _level3_name)
            if not os.path.exists(os.path.dirname(_path)):
                os.makedirs(os.path.dirname(_path))

            # Copy file
            shutil.copy2(self.doc_path, _path)

            # Connect to the database
            conn = sqlite3.connect(config.cfg['db_location'])
            crsr = conn.cursor()

            # Add the new document to the library
            crsr.execute("INSERT INTO Documents (file_name, title, category, discipline, level3, user, time_added) "
                         "VALUES ((?), (?), (?), (?), (?), (?), (?));",
                         (self.doc_name,
                          self.wgt_title.GetValue(),
                          _category_id,
                          _discipline_id,
                          _level3_id,
                          self.root_pane.user,
                          str(datetime.datetime.now().timestamp())))

            # Get ids of the document added and of the tags associated with it
            _doc_id = crsr.lastrowid
            _tag_ids = [self.root_pane.tag_to_id[tag] for tag in self.ls_tags]

            # Add the tags and document to the junction table
            for _tag_id in _tag_ids:
                print((".".join([str(_tag_id), str(_doc_id)]), _tag_id, _doc_id))
                crsr.execute("INSERT INTO JunctionTable (name, tag_id, doc_id) "
                             "VALUES ((?), (?), (?));",
                             (".".join([str(_tag_id), str(_doc_id)]), _tag_id, _doc_id))

            # Commit changes and close connection
            conn.commit()
            crsr.close()
            conn.close()

            self.evt_close()

    def evt_cancel(self, event):
        """Cancel the change and close the dialog

            Args:
                event: A button event object passed from the button click
        """

        self.evt_close()

    def evt_close(self, *args):
        """Close the dialog

            Args:
                args[0]: Null, or an event object passed from the calling event
        """

        self.DestroyLater()

    def evt_paste(self, event):
        """Prevents any text from being pasted into the widget

            Args:
                event: Paste event from parent wx widget
        """

        print("PASTE but nothing happens")


class AddLevel3(wx.Dialog):
    """Opens a dialog to edit document information prior to adding to the database

        Args:
            parent (ref): Reference to the parent wx.object
            root_pane (ref): Reference to the root parts tab
            old_type (str): The value of the part's "type" before editing

        Attributes:
            parent (ref): Reference to the parent wx.object
            root_pane (ref): Reference to the root parts tab
            old_type (str): The value of the part's "type" before editing
    """

    def __init__(self, parent, root_pane):
        """Constructor"""
        super().__init__(parent)

        self.parent = parent
        self.root_pane = root_pane
        self.ls_category = list(self.root_pane.category_to_id.keys())
        self.ls_discipline = list(self.root_pane.discipline_to_id.keys())

        # Type selection dropdown, with bind and sizer
        self.wgt_drop_category = wx.ComboBox(self, choices=self.ls_category, style=wx.CB_READONLY)
        self.wgt_drop_discipline = wx.ComboBox(self, choices=self.ls_discipline, style=wx.CB_READONLY)
        self.wgt_txt_level3 = wx.TextCtrl(self)

        szr_drop = wx.StaticBoxSizer(wx.StaticBox(self, label="Select the type for this part to fall under"),
                                     orient=wx.HORIZONTAL)
        szr_drop.Add(self.wgt_drop_category, proportion=1, flag=wx.ALL, border=5)
        szr_drop.Add(self.wgt_drop_discipline, proportion=1, flag=wx.ALL, border=5)
        szr_drop.Add(self.wgt_txt_level3, proportion=1, flag=wx.ALL, border=5)

        # Dialog buttons with binds
        btn_commit = wx.Button(self, label='Commit')
        btn_commit.Bind(wx.EVT_BUTTON, self.evt_commit)
        btn_cancel = wx.Button(self, label='Cancel')
        btn_cancel.Bind(wx.EVT_BUTTON, self.evt_cancel)

        # Dialog button sizer
        szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
        szr_buttons.Add(btn_commit)
        szr_buttons.Add(btn_cancel, flag=wx.LEFT, border=5)

        # Add everything to master sizer and set sizer for pane
        szr_master = wx.BoxSizer(wx.VERTICAL)
        szr_master.Add(szr_drop, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        szr_master.Add(szr_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        szr_main = wx.BoxSizer(wx.HORIZONTAL)
        szr_main.Add(szr_master, proportion=1, flag=wx.EXPAND | wx.ALL, border=20)

        self.SetSizer(szr_main)

        # Set size and title
        self.SetSize((1000, 360))
        self.SetTitle("Change the 'type' for this component")

        self.Bind(wx.EVT_CLOSE, self.evt_close)

    def evt_commit(self, event):
        """Execute when committing a change to the part type

            Args:
                event: A button event object passed from the button click
        """
        # self.evt_add_tag(event)

        _category_id = self.root_pane.category_to_id[self.wgt_drop_category.GetValue()]
        _category_name = self.wgt_drop_category.GetValue()
        _discipline_id = self.root_pane.discipline_to_id[self.wgt_drop_discipline.GetValue()]
        _discipline_name = self.wgt_drop_discipline.GetValue()
        _level3_name = self.wgt_txt_level3.GetValue()

        if self.wgt_drop_discipline.GetValue() and self.wgt_drop_category.GetValue():

            # Connect to the database
            conn = sqlite3.connect(config.cfg['db_location'])
            crsr = conn.cursor()

            # Add the new document to the library
            crsr.execute("INSERT INTO Level3 (category_id, discipline_id, level3) "
                         "VALUES ((?), (?), (?));",
                         (_category_id,
                          _discipline_id,
                          _level3_name))

            # Commit changes and close connection
            conn.commit()
            crsr.close()
            conn.close()

            self.evt_close()

    def evt_cancel(self, event):
        """Cancel the change and close the dialog

            Args:
                event: A button event object passed from the button click
        """

        self.evt_close()

    def evt_close(self, *args):
        """Close the dialog

            Args:
                args[0]: Null, or an event object passed from the calling event
        """

        self.DestroyLater()