# -*- coding: utf-8 -*-
"""This module defines panes - master panels that act as direct children of the progenitor frame"""

import wx
import sqlite3

import widget
import tab

import config
import fn_path

class PaneMain(wx.Panel):
    """Master pane that contains the normal operational widgets for the application

        Class Variables:
            bar_size (int): Size (height) of the top ribbon with the searchbar

        Args:
            frame (ptr): Reference to the wx.frame this panel belongs to

        Attributes:
            frame (ptr): Reference to the wx.frame this panel belongs to
    """

    bar_size = 25

    def __init__(self, frame):
        """Constructor"""
        wx.Panel.__init__(self, frame)
        self.SetDoubleBuffered(True)  # Remove odd effects at main switch to this pane after login

        # Parental inheritance
        self.frame = frame

        # Load tags and the mapping of tag to id
        self.ls_tags = []
        self.tag_to_id = {}
        self.reload_tags()

        # Mappings between id and discipline and id and category on their respective tables
        self.id_to_discipline, self.discipline_to_id = self.load_disciplines()
        self.id_to_category, self.category_to_id = self.load_categories()
        self.id_to_level3, self.level3_to_id = self.load_level3()

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
        discipline_to_id = dict((discipline, ident) for (ident, discipline) in _discipline_tuples)
        id_to_discipline = dict((ident, discipline) for (ident, discipline) in _discipline_tuples)

        # Close connection
        crsr.close()
        conn.close()

        return id_to_discipline, discipline_to_id

    def load_categories(self):
        """Loads a dictionary and the reverse dictionary for disciplines and their id in the SQL database"""

        # Connect to the database
        conn = sqlite3.connect(config.cfg['db_location'])
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

    def load_level3(self):
        """Loads a dictionary and the reverse dictionary for disciplines and their id in the SQL database"""

        # Connect to the database
        conn = sqlite3.connect(config.cfg['db_location'])
        crsr = conn.cursor()

        # Retrieve list of all tags from SQL database
        crsr.execute("SELECT id, level3 "
                     "FROM Level3;")

        # Write tags to self.tags and define enumeration for cross-reference
        _level3_tuples = crsr.fetchall()
        level3_to_id = dict((level3, ident) for (ident, level3) in _level3_tuples)
        id_to_level3 = dict((ident, level3) for (ident, level3) in _level3_tuples)

        # Close connection
        crsr.close()
        conn.close()

        return id_to_level3, level3_to_id

    def reload_tags(self):
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
        """Loads a list of available tags from the SQL database and populates to self.tags

            Returns:
                (list: str): List of strings that are existing tags
        """

        # Resolve values as single-entry lists containing that value
        if type(add_tags) is not list: add_tags = [add_tags]

        # Only cary on if there is new tags to add
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

        # Empty the searchbar
        self.wgt_searchbar.SetValue("")

    def search_category(self):
        # if any([checkbox.GetValue() for checkbox in self.wgt_ls_chk_category]):
        _truth_cat = any([checkbox.GetValue() for checkbox in self.wgt_restrictions.wgt_ls_chk_category])
        _truth_disc = any([checkbox.GetValue() for checkbox in self.wgt_restrictions.wgt_ls_chk_disciplines])

        _temp_cat = [self.category_to_id[x.GetLabel()] for x in self.wgt_restrictions.wgt_ls_chk_category if x.GetValue()]
        _temp_disc = [self.discipline_to_id[x.GetLabel()] for x in self.wgt_restrictions.wgt_ls_chk_disciplines if x.GetValue()]

        # Connect to the database
        conn = sqlite3.connect(config.cfg['db_location'])
        crsr = conn.cursor()

        crsr.execute(" ".join(["SELECT file_name, title, category, discipline, level3 "
                               "FROM Documents",
                               self.opt_str("WHERE", self.min_truth(1, [_truth_cat, _truth_disc])),
                               self.opt_str("category IN (%s)" % (",".join("?" * len(_temp_cat))), _truth_cat),
                               self.opt_str("AND", self.min_truth(2, [_truth_cat, _truth_disc])),
                               self.opt_str("discipline IN (%s);" % (",".join("?" * len(_temp_disc))), _truth_disc)]),
                     (_temp_cat + _temp_disc))

        # Write tags to self.tags and define enumeration for cross-reference
        search_results = crsr.fetchall()

        search_string = self.wgt_searchbar.GetValue().strip()

        _ot = [x.IsChecked() for x in self.wgt_restrictions.wgt_ls_chk_searchin]

        # Ensure there is something in the search bar before searching
        if search_string:

            new_search = [s for s in search_results if ((search_string in s[0] if _ot[0] else False) or (search_string in s[1] if _ot[1] else False))] #search_string in (s[0] if 0 in _ot else []) or (s[1] if 1 in _ot else [])]

            self.wgt_notebook.open_search_tab(search_string, new_search)

        # Close connection
        crsr.close()
        conn.close()

    @staticmethod
    def opt_str(text, check):
        return text if check else ""

    @staticmethod
    def min_truth(count, truths):
        return sum(truths) >= count