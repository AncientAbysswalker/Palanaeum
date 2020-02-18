# -*- coding: utf-8 -*-
"""This module defines panes - master panels that act as direct children of the progenitor frame"""

import wx

import login
import tab
import fn_path
import sqlite3
import os

import widget

# DISCIPLINES = {"Mech":1,
#                "Structural":2,
#                "Geotech":3,
#                "Electrical":4,
#                "Seismic":5}

# DOCTYPE = {"Codes and Specifications":1,
#            "Reference Materials":2,
#            "Catalogues":3,
#            "Calculators":4}


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
        self.show_restrictions = False

        self.map_id_disc, self.map_disc_id = self.load_disciplines()
        self.map_id_cat, self.map_cat_id = self.load_categories()

        # Search bar and bind
        self.wgt_searchbar = wx.TextCtrl(self,
                                         size=(PaneMain.bar_size*10, PaneMain.bar_size),
                                         style=wx.TE_PROCESS_ENTER)
        self.wgt_searchbar.Bind(wx.EVT_TEXT_ENTER, self.evt_search)

        # # Document Category Checkboxes
        # self.wgt_chk_category = []
        # self.szr_chk_category = wx.BoxSizer(wx.VERTICAL)
        # for category in DOCTYPE:
        #     _new_checkbox = wx.CheckBox(self, label=category)
        #     self.wgt_chk_category.append(_new_checkbox)
        #     self.szr_chk_category.Add(_new_checkbox)
        #
        # # Discipline Checkboxes
        # self.wgt_chk_disciplines = []
        # self.szr_chk_disciplines = wx.BoxSizer(wx.VERTICAL)
        # for discipline in DISCIPLINES:
        #     _new_checkbox = wx.CheckBox(self, label=discipline)
        #     self.wgt_chk_disciplines.append(_new_checkbox)
        #     self.szr_chk_disciplines.Add(_new_checkbox)

        # Search bar button and bind
        btn_search = wx.BitmapButton(self,
                                     bitmap=wx.Bitmap(fn_path.concat_gui('search.png')),
                                     size=(PaneMain.bar_size, ) * 2)
        btn_search.Bind(wx.EVT_BUTTON, self.evt_search)
        btn_search.Bind(wx.EVT_SET_FOCUS, self.evt_button_no_focus)

        # Notebook widget
        self.wgt_notebook = tab.Notebook(self)

        # Search-in sizer
        _b = wx.StaticBox(self, label="Search for text in:")
        # _a.Bind(wx.EVT_KEY_DOWN, self.toggle_restrictions)
        szr_search = wx.StaticBoxSizer(_b, orient=wx.HORIZONTAL)
        # szr_search.Add(self.szr_chk_category)
        # szr_search.AddSpacer(2)
        # szr_search.Add(self.szr_chk_disciplines)

        # Restrictions sizer
        # _a = wx.StaticBox(self, label="Restrict search to:")
        # # _a.Bind(wx.EVT_KEY_DOWN, self.toggle_restrictions)
        # szr_restrictions = wx.StaticBoxSizer(_a, orient=wx.HORIZONTAL)
        # szr_restrictions.Add(self.szr_chk_category)
        # szr_restrictions.AddSpacer(2)
        # szr_restrictions.Add(self.szr_chk_disciplines)
        self._a = widget.Restrictions(self)
        self._a.Bind(wx.EVT_LEFT_DOWN, self._a.evt_click_header)
        # self._a.Bind(wx.EVT_ENTER_WINDOW, self._a.evt_enter_widget)
        # self._a.Bind(wx.EVT_LEAVE_WINDOW, self._a.evt_leave_widget)

        # self._a.Bind(wx.EVT_LEAVE_WINDOW, self._a.toggle_restrictions)
        self._a.SetMinSize((500, -1))

        # Top bar sizer
        szr_bar = wx.BoxSizer(wx.HORIZONTAL)
        szr_bar.AddSpacer(3)
        szr_bar.Add(self.wgt_searchbar)
        szr_bar.AddSpacer(2)
        szr_bar.Add(btn_search)
        szr_bar.Add(wx.StaticText(self), proportion=1)
        szr_bar.Add(szr_search, flag=wx.RIGHT)
        szr_bar.Add(wx.StaticText(self), proportion=1)
        szr_bar.Add(self._a, flag=wx.RIGHT)
        szr_bar.AddSpacer(2)

        # Main Sizer
        self.szr_main = wx.BoxSizer(wx.VERTICAL)
        self.szr_main.Add(szr_bar, flag=wx.EXPAND)
        self.szr_main.AddSpacer(1)
        self.szr_main.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.szr_main.Add(self.wgt_notebook, proportion=1, flag=wx.EXPAND)

        self.SetSizer(self.szr_main)

        self.Layout()

    def load_disciplines(self):
        """Loads a dictionary and the reverse dictionary for disciplines and their id in the SQL database"""

        # Connect to the database
        conn = sqlite3.connect(os.path.expandvars("%UserProfile%") + r"\PycharmProjects\Palanaeum\test.sqlite")
        crsr = conn.cursor()

        # Retrieve list of all tags from SQL database
        crsr.execute("SELECT id, discipline "
                     "FROM Disciplines;")

        # Write tags to self.tags and define enumeration for cross-reference
        _discipline_tuples = crsr.fetchall()
        discipline_to_id = dict((discipline, ident) for (ident, discipline) in _discipline_tuples)
        id_to_discipline = dict((ident, discipline) for (ident, discipline) in _discipline_tuples)

        # Close connection
        crsr.close()
        conn.close()

        return id_to_discipline, discipline_to_id

    def load_categories(self):
        """Loads a dictionary and the reverse dictionary for disciplines and their id in the SQL database"""

        # Connect to the database
        conn = sqlite3.connect(os.path.expandvars("%UserProfile%") + r"\PycharmProjects\Palanaeum\test.sqlite")
        crsr = conn.cursor()

        # Retrieve list of all tags from SQL database
        crsr.execute("SELECT id, category "
                     "FROM Categories;")

        # Write tags to self.tags and define enumeration for cross-reference
        _category_tuples = crsr.fetchall()
        category_to_id = dict((category, ident) for (ident, category) in _category_tuples)
        id_to_category = dict((ident, category) for (ident, category) in _category_tuples)

        # Close connection
        crsr.close()
        conn.close()

        return id_to_category, category_to_id

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

        # self.toggle_restrictions()
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
        _truth_cat = any([checkbox.GetValue() for checkbox in self._a.wgt_chk_category])
        _truth_disc = any([checkbox.GetValue() for checkbox in self._a.wgt_chk_disciplines])

        _temp_cat = [self.map_cat_id[x.GetLabel()] for x in self._a.wgt_chk_category if x.GetValue()]
        _temp_disc = [self.map_disc_id[x.GetLabel()] for x in self._a.wgt_chk_disciplines if x.GetValue()]

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

        search_string = self.wgt_searchbar.GetValue().strip()

        print(search_results)

        # Ensure there is something in the search bar before searching
        if search_string:

            new_search = [s for s in search_results if search_string in s[0]]

            self.wgt_notebook.open_parts_tab(search_string, new_search)

        # Close connection
        crsr.close()
        conn.close()

    def toggle_restrictions(self, *args):
        for each in self.wgt_chk_disciplines + self.wgt_chk_category:
            each.Show() if self.show_restrictions else each.Hide()
        self.Layout()
        self.show_restrictions = not self.show_restrictions

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
