# -*- coding: utf-8 -*-
"""This module defines panes - master panels that act as direct children of the progenitor frame"""

import wx

import login
import tab
import fn_path
import sqlite3
import os

DISCIPLINES = {"Mech":1,
               "Structural":2,
               "Geotech":3,
               "Electrical":4,
               "Seismic":5}

DOCTYPE = {"Codes and Specifications":1,
           "Reference Materials":2,
           "Catalogues":3,
           "Calculators":4}


class PaneMain(wx.Panel):
    """Master pane that contains the normal operational widgets for the application

        Class Variables:
            bar_size (int): Size (height) of the top ribbon with the searchbar

        Args:
            parent (ptr): Reference to the wx.object this panel belongs to

        Attributes:
            parent (ptr): Reference to the wx.object this panel belongs to
    """

    bar_size = 25

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.SetDoubleBuffered(True)  # Remove odd effects at main switch to this pane after login

        self.parent = parent

        # Search bar and bind
        self.tags = []
        self.tag_enum = {}
        self.reload_tags()

        # Search bar and bind
        self.wgt_searchbar = wx.TextCtrl(self,
                                         size=(PaneMain.bar_size*10, PaneMain.bar_size),
                                         style=wx.TE_PROCESS_ENTER)
        self.wgt_searchbar.Bind(wx.EVT_TEXT_ENTER, self.evt_search)

        # Document Category Checkboxes
        self.wgt_chk_category = []
        self.szr_chk_category = wx.BoxSizer(wx.VERTICAL)
        for category in DOCTYPE:
            _new_checkbox = wx.CheckBox(self, label=category)
            self.wgt_chk_category.append(_new_checkbox)
            self.szr_chk_category.Add(_new_checkbox)

        # Discipline Checkboxes
        self.wgt_chk_disciplines = []
        self.szr_chk_disciplines = wx.BoxSizer(wx.VERTICAL)
        for discipline in DISCIPLINES:
            _new_checkbox = wx.CheckBox(self, label=discipline)
            self.wgt_chk_disciplines.append(_new_checkbox)
            self.szr_chk_disciplines.Add(_new_checkbox)

        # Search bar button and bind
        btn_search = wx.BitmapButton(self,
                                     bitmap=wx.Bitmap(fn_path.concat_gui('search.png')),
                                     size=(PaneMain.bar_size, ) * 2)
        btn_search.Bind(wx.EVT_BUTTON, self.evt_search)
        btn_search.Bind(wx.EVT_SET_FOCUS, self.evt_button_no_focus)

        # Notebook widget
        self.wgt_notebook = tab.Notebook(self)

        # Restrictions sizer
        szr_restrictions = wx.StaticBoxSizer(wx.StaticBox(self, label="Restrict Search To:"), orient=wx.HORIZONTAL)
        szr_restrictions.Add(self.szr_chk_category)
        szr_restrictions.AddSpacer(2)
        szr_restrictions.Add(self.szr_chk_disciplines)

        # Top bar sizer
        szr_bar = wx.BoxSizer(wx.HORIZONTAL)
        szr_bar.AddSpacer(3)
        szr_bar.Add(self.wgt_searchbar)
        szr_bar.AddSpacer(2)
        szr_bar.Add(btn_search)
        szr_bar.Add(wx.StaticText(self), proportion=1)
        szr_bar.Add(szr_restrictions, flag=wx.RIGHT)
        szr_bar.AddSpacer(2)

        # Main Sizer
        self.szr_main = wx.BoxSizer(wx.VERTICAL)
        self.szr_main.Add(szr_bar, flag=wx.EXPAND)
        self.szr_main.AddSpacer(1)
        self.szr_main.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.szr_main.Add(self.wgt_notebook, proportion=1, flag=wx.EXPAND)

        self.SetSizer(self.szr_main)

    def reload_tags(self):
        """Loads a list of available tags from the SQL database and populates to self.tags"""

        # Connect to the database
        conn = sqlite3.connect(os.path.expandvars("%UserProfile%") + r"\PycharmProjects\Palanaeum\test.sqlite")
        crsr = conn.cursor()

        # Retrieve list of all tags from SQL database
        crsr.execute("SELECT id, tag "
                     "FROM Tags;")

        # Write tags to self.tags and define enumeration for cross-reference
        _tag_tuples = crsr.fetchall()
        self.tag_enum = dict((tag, ident) for (ident, tag) in _tag_tuples)
        self.tags = [i[1] for i in _tag_tuples]

        # Close connection
        crsr.close()
        conn.close()

    def add_tags(self, add_tags):
        """Loads a list of available tags from the SQL database and populates to self.tags

            Returns:
                (list: str): List of strings that are existing tags
        """

        # Resolve values as single-entry lists containing that value
        if type(add_tags) is not list: add_tags = [add_tags]

        # Only cary on if there is new tags to add
        _new_tags = [(str(x),) for x in add_tags if str(x) not in self.tags]
        if _new_tags:
            # Connect to the database
            conn = sqlite3.connect(os.path.expandvars("%UserProfile%") + r"\PycharmProjects\Palanaeum\test.sqlite")
            crsr = conn.cursor()

            # Modify the existing cell in the database for existing part number and desired column
            crsr.executemany("INSERT INTO Tags (tag) "
                             "VALUES (?);",
                             _new_tags)

            # Commit changes and close connection
            conn.commit()
            crsr.close()
            conn.close()

            self.reload_tags()

    def evt_button_no_focus(self, event):
        """Prevents focus from being called on the buttons

            Args:
                event: A focus event
        """
        pass

    def evt_search(self, *args):
        """Search for a part number and call open_parts_tab before emptying the searchbar

            Args:
                args[0]: Either None or a button click event
        """

        self.search_category()
        # self.search_discipline()

        # if any([checkbox.GetValue() for checkbox in self.wgt_chk_category]):
        #
        #     _temp = [DOCTYPE[x.GetLabel()] for x in self.wgt_chk_category if x.GetValue()]
        #
        #     # Connect to the database
        #     conn = sqlite3.connect(os.path.expandvars("%UserProfile%") + r"\PycharmProjects\Palanaeum\test.sqlite")
        #     crsr = conn.cursor()
        #
        #     # Retrieve list of all tags from SQL database
        #     crsr.execute("SELECT file_name "
        #                  "FROM Documents "
        #                  "WHERE category "
        #                  "IN (%s);" % (",".join("?" * len(_temp))),
        #                  _temp)
        #
        #     # Write tags to self.tags and define enumeration for cross-reference
        #     print([i[0] for i in crsr.fetchall()])
        #
        #     # Close connection
        #     crsr.close()
        #     conn.close()
        #
        # else:
        #     print("no boxex")

        # Ensure there is something in the search bar before searching
        # if self.wgt_searchbar.GetValue().strip():
        #     self.wgt_notebook.open_parts_tab(self.wgt_searchbar.GetValue(), search_results)

        # Empty the searchbar
        self.wgt_searchbar.SetValue("")

    def search_category(self):
        # if any([checkbox.GetValue() for checkbox in self.wgt_chk_category]):
        _truth_cat = any([checkbox.GetValue() for checkbox in self.wgt_chk_category])
        _truth_disc = any([checkbox.GetValue() for checkbox in self.wgt_chk_disciplines])

        _temp_cat = [DOCTYPE[x.GetLabel()] for x in self.wgt_chk_category if x.GetValue()]
        _temp_disc = [DISCIPLINES[x.GetLabel()] for x in self.wgt_chk_disciplines if x.GetValue()]

        # Connect to the database
        conn = sqlite3.connect(os.path.expandvars("%UserProfile%") + r"\PycharmProjects\Palanaeum\test.sqlite")
        crsr = conn.cursor()

        crsr.execute(" ".join(["SELECT file_name, title, category, discipline "
                               "FROM Documents",
                               self.opt_str("WHERE", self.min_truth(1, [_truth_cat, _truth_disc])),
                               self.opt_str("category IN (%s)" % (",".join("?" * len(_temp_cat))), _truth_cat),
                               self.opt_str("AND", self.min_truth(2, [_truth_cat, _truth_disc])),
                               self.opt_str("discipline IN (%s);" % (",".join("?" * len(_temp_disc))), _truth_disc)]),
                     (_temp_cat + _temp_disc))

        # Write tags to self.tags and define enumeration for cross-reference
        search_results = crsr.fetchall()
        # print(_a)

        # Ensure there is something in the search bar before searching
        if self.wgt_searchbar.GetValue().strip():
            self.wgt_notebook.open_parts_tab(self.wgt_searchbar.GetValue(), search_results)

        # Close connection
        crsr.close()
        conn.close()



    @staticmethod
    def opt_str(text, check):
        return text if check else ""

    @staticmethod
    def min_truth(count, truths):
        return sum(truths) >= count

    #
    # def search_discipline(self):
    #     if any([checkbox.GetValue() for checkbox in self.wgt_chk_disciplines]):
    #
    #         _temp = [DISCIPLINES[x.GetLabel()] for x in self.wgt_chk_disciplines if x.GetValue()]
    #
    #         # Connect to the database
    #         conn = sqlite3.connect(os.path.expandvars("%UserProfile%") + r"\PycharmProjects\Palanaeum\test.sqlite")
    #         crsr = conn.cursor()
    #
    #         # Retrieve list of all tags from SQL database
    #         crsr.execute("SELECT file_name "
    #                      "FROM Documents "
    #                      "WHERE discipline "
    #                      "IN (%s);" % (",".join("?" * len(_temp))),
    #                      _temp)
    #
    #         # Write tags to self.tags and define enumeration for cross-reference
    #         print([i[0] for i in crsr.fetchall()])
    #
    #         # Close connection
    #         crsr.close()
    #         conn.close()
    #
    #     else:
    #         return


# class PaneLogin(wx.Panel):
#     """Master pane that deals with login behaviour for the application.
#
#         Args:
#             parent (ptr): Reference to the wx.object this panel belongs to
#             sizer_landing (ptr): Reference to the sizer (of the parent) the landing pane belongs to
#             pane_landing (ptr): Reference to the landing pane
#
#         Attributes:
#             parent (ptr): Reference to the wx.object this panel belongs to
#     """
#
#     def __init__(self, parent, sizer_landing, pane_landing):
#         """Constructor"""
#         wx.Panel.__init__(self, parent)
#         self.SetDoubleBuffered(True)  # Remove slight strobing on failed login
#
#         self.parent = parent
#
#         # Widget that controls user login auth - currently set to debug (no auth) for testing and dev
#         login_panel = login.LoginDebug(self, sizer_landing, pane_landing)
#
#         # Main Sizer
#         sizer_main = wx.BoxSizer(wx.VERTICAL)
#         sizer_main.AddStretchSpacer()
#         sizer_main.Add(login_panel, flag=wx.CENTER)
#         sizer_main.AddStretchSpacer()
#
#         # Set main sizer
#         self.SetSizer(sizer_main)
