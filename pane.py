# -*- coding: utf-8 -*-
"""This module defines panes - master panels that act as direct children of the progenitor frame"""

import wx
import sqlite3
import os

import widget
import tab

import config
import fn_path


class PaneMain(wx.Panel):
    """Master pane that contains the normal operational widgets for the application

        Class Variables:
            bar_size (int): Size (height) of the top ribbon with the searchbar

        Args:
            parent (ptr): Reference to the wx.frame this panel belongs to

        Attributes:
            parent (ptr): Reference to the wx.frame this panel belongs to
    """

    bar_size = 25

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.SetDoubleBuffered(True)  # Remove odd effects at main switch to this pane after login

        # Parental inheritance
        self.parent = parent

        # Set user for application
        self.user = os.getlogin()

        # Load tags and the mapping of tag to id
        self.ls_tags = []
        self.tag_to_id = {}
        self.load_tags()

        # Define and load mappings between id and discipline
        self.id_to_discipline = {}
        self.discipline_to_id = {}
        self.load_disciplines()

        # Define and load mappings between id and category
        self.id_to_category = {}
        self.category_to_id = {}
        self.load_categories()

        # Define and load mappings between id and level3
        self.id_to_level3 = {}
        self.level3_to_id = {}
        self.load_level3()

        # Search bar and bind
        self.wgt_searchbar = wx.TextCtrl(self,
                                         size=(PaneMain.bar_size*10, PaneMain.bar_size),
                                         style=wx.TE_PROCESS_ENTER)
        self.wgt_searchbar.Bind(wx.EVT_TEXT_ENTER, self.evt_search)

        # Search bar button and bind
        btn_search = wx.BitmapButton(self,
                                     bitmap=wx.Bitmap(fn_path.concat_gui('search.png')),
                                     size=(PaneMain.bar_size, ) * 2)
        btn_search.Bind(wx.EVT_BUTTON, self.evt_search)
        btn_search.Bind(wx.EVT_SET_FOCUS, self.evt_button_no_focus)

        # Notebook widget
        self.wgt_notebook = tab.Notebook(self)

        # Restrictions sizer
        self.wgt_restrictions = widget.Restrictions(self)
        self.wgt_restrictions.Bind(wx.EVT_LEFT_DOWN, self.wgt_restrictions.evt_click_header)
        self.wgt_restrictions.SetMinSize((500, -1))

        # Top bar sizer
        szr_top_bar = wx.BoxSizer(wx.HORIZONTAL)
        szr_top_bar.AddSpacer(3)
        szr_top_bar.Add(self.wgt_searchbar)
        szr_top_bar.AddSpacer(2)
        szr_top_bar.Add(btn_search)
        szr_top_bar.Add(wx.StaticText(self), proportion=1)
        szr_top_bar.Add(self.wgt_restrictions, flag=wx.RIGHT)
        szr_top_bar.AddSpacer(2)

        # Main Sizer
        self.szr_main = wx.BoxSizer(wx.VERTICAL)
        self.szr_main.Add(szr_top_bar, flag=wx.EXPAND)
        self.szr_main.AddSpacer(1)
        self.szr_main.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND)
        self.szr_main.Add(self.wgt_notebook, proportion=1, flag=wx.EXPAND)

        # Set sizer and refresh layout
        self.SetSizer(self.szr_main)
        self.Layout()

    def load_disciplines(self):
        """Loads a dictionary and the reverse dictionary for disciplines and their id in the SQL database"""

        # Connect to the database
        conn = sqlite3.connect(config.cfg['db_location'])
        crsr = conn.cursor()

        # Retrieve list of all tags from SQL database
        crsr.execute("SELECT id, discipline "
                     "FROM Disciplines;")

        # Write tags to self.tags and define enumeration for cross-reference
        _discipline_tuples = crsr.fetchall()
        self.discipline_to_id = dict((discipline, ident) for (ident, discipline) in _discipline_tuples)
        self.id_to_discipline = dict((ident, discipline) for (ident, discipline) in _discipline_tuples)

        # Close connection
        crsr.close()
        conn.close()

    def load_categories(self):
        """Loads a dictionary and the reverse dictionary for categories and their id in the SQL database"""

        # Connect to the database
        conn = sqlite3.connect(config.cfg['db_location'])
        crsr = conn.cursor()

        # Retrieve list of all tags from SQL database
        crsr.execute("SELECT id, category "
                     "FROM Categories;")

        # Write tags to self.tags and define enumeration for cross-reference
        _category_tuples = crsr.fetchall()
        self.category_to_id = dict((category, ident) for (ident, category) in _category_tuples)
        self.id_to_category = dict((ident, category) for (ident, category) in _category_tuples)

        # Close connection
        crsr.close()
        conn.close()

    def load_level3(self):
        """Loads a dictionary and the reverse dictionary for level3's and their id in the SQL database"""

        # Connect to the database
        conn = sqlite3.connect(config.cfg['db_location'])
        crsr = conn.cursor()

        # Retrieve list of all tags from SQL database
        crsr.execute("SELECT id, level3 "
                     "FROM Level3;")

        # Write tags to self.tags and define enumeration for cross-reference
        _level3_tuples = crsr.fetchall()
        self.level3_to_id = dict((level3, ident) for (ident, level3) in _level3_tuples)
        self.id_to_level3 = dict((ident, level3) for (ident, level3) in _level3_tuples)

        # Close connection
        crsr.close()
        conn.close()

    def load_tags(self):
        """Loads a list of available tags from the SQL database and populates to self.tags"""

        # Connect to the database
        conn = sqlite3.connect(config.cfg['db_location'])
        crsr = conn.cursor()

        # Retrieve list of all tags from SQL database
        crsr.execute("SELECT id, tag "
                     "FROM Tags;")

        # Write tags to self.tags and define enumeration for cross-reference
        _tag_tuples = crsr.fetchall()
        self.tag_to_id = dict((tag, ident) for (ident, tag) in _tag_tuples)
        self.ls_tags = [i[1] for i in _tag_tuples]

        # Close connection
        crsr.close()
        conn.close()

    def add_tags(self, add_tags):
        """Adds a list of new tags to the SQL database

            Returns:
                (list: str): List of strings that are existing tags
        """

        # Ensure tags list is updated prior to adding potentially new tags
        self.load_tags()

        # Resolve values as single-entry lists containing that value
        if type(add_tags) is not list: add_tags = [add_tags]

        # Only carry on if there is new tags to add
        _new_tags = [(str(x),) for x in add_tags if str(x) not in self.ls_tags]
        if _new_tags:
            # Connect to the database
            conn = sqlite3.connect(config.cfg['db_location'])
            crsr = conn.cursor()

            # Modify the existing cell in the database for existing part number and desired column
            crsr.executemany("INSERT INTO Tags (tag) "
                             "VALUES (?);",
                             _new_tags)

            # Commit changes and close connection
            conn.commit()
            crsr.close()
            conn.close()

            # Load new tags after adding tags
            self.load_tags()

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

        # Is there restrictions (limitations) on category and discipline?
        is_lim_cat = any([checkbox.GetValue() for checkbox in self.wgt_restrictions.wgt_ls_chk_category])
        is_lim_disc = any([checkbox.GetValue() for checkbox in self.wgt_restrictions.wgt_ls_chk_disciplines])
        ls_is_lim = [is_lim_cat, is_lim_disc]

        # List of restrictions (limitations) on category and discipline
        ls_lim_cat = [self.category_to_id[x.GetLabel()] for x in self.wgt_restrictions.wgt_ls_chk_category
                      if x.GetValue()]
        ls_lim_disc = [self.discipline_to_id[x.GetLabel()] for x in self.wgt_restrictions.wgt_ls_chk_disciplines
                       if x.GetValue()]

        # Connect to the database
        conn = sqlite3.connect(config.cfg['db_location'])
        crsr = conn.cursor()

        # Complex SQL execution depending on what restrictions are chosen, if any
        crsr.execute(" ".join(["SELECT file_name, title, category, discipline, level3 "
                               "FROM Documents",
                               self.opt_str("WHERE", self.min_truth(1, ls_is_lim)),
                               self.opt_str("category IN (%s)" % (",".join("?" * len(ls_lim_cat))), is_lim_cat),
                               self.opt_str("AND", self.min_truth(2, ls_is_lim)),
                               self.opt_str("discipline IN (%s);" % (",".join("?" * len(ls_lim_disc))), is_lim_disc)]),
                     (ls_lim_cat + ls_lim_disc))

        # Grab search results and search string
        search_results = crsr.fetchall()
        search_string = self.wgt_searchbar.GetValue().strip()

        # Determine what fields to search for text in
        ls_searchin = [x.IsChecked() for x in self.wgt_restrictions.wgt_ls_chk_searchin]

        # Ensure there is something in the search bar before searching
        if search_string:
            search_results_refined = [s for s in search_results
                                      if ((search_string in s[0] if ls_searchin[0] else False) or
                                          (search_string in s[1] if ls_searchin[1] else False))]

            # Open new tab of results
            self.wgt_notebook.open_search_tab(search_string, search_results_refined)

        # Close connection
        crsr.close()
        conn.close()

        # Empty the searchbar
        self.wgt_searchbar.SetValue("")

    @staticmethod
    def opt_str(text, check):
        return text if check else ""

    @staticmethod
    def min_truth(count, truths):
        return sum(truths) >= count