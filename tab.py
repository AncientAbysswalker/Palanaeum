# -*- coding: utf-8 -*-
"""This module contains the main Notebook class and all Tab classes that the notebook can display"""

import wx

import widget


class Notebook(wx.Notebook):
    """Notebook class that contains various Tab-type classes within itself

        Args:
            parent (ref): Reference to the parent wx.object pane

        Attributes:
            user (str): The logged-in user. Currently hard-coded to "demo"
            parent (ref): Reference to the parent wx.object pane
            root_pane (ref): Reference to the parent wx.object pane
    """

    def __init__(self, parent):
        """Constructor"""
        wx.Notebook.__init__(self, parent)
        self.SetDoubleBuffered(True)  # Remove slight strobing on tab switch

        # Parental inheritance
        self.parent = parent
        self.root_pane = parent

        # Instance Variables
        self.user = "demo"

        # Set the list of open panels to an empty list. Create a dummy tab.
        self.open_tabs = []
        self.open_search_tab("", [])


    def open_search_tab(self, query, search_results, opt_stay=False):
        """Open a new tab using the provided part number and revision

            Args:
                query (string): The query string to name the new tab
                search_results (list: tuple): List of tuples pertaining to query results
                opt_stay (bool): If true, do not change to newly opened tab - default change tabs
        """

        # If there is not yet a tab for this part number then create one, otherwise redirect to the existing
        if query not in [_tab.query for _tab in self.open_tabs]:
            new_tab = TabSearchQuery(self, self.root_pane, query, search_results)
            self.open_tabs.append(new_tab)
            self.AddPage(new_tab, query)

            # Handles whether to stay on current tab or move to newly opened tab
            if not opt_stay:
                self.SetSelection(self.GetPageCount() - 1)
        elif not opt_stay:
            self.SetSelection([pnl.part_num for pnl in self.open_tabs].index(query))


class TabSearchQuery(wx.Panel):
    """Tab class that displays info relating to the search query.

        Args:
            parent (ref): Reference to the parent wx.object
            root_pane (ref): Reference to the upstream wx.object pane
            query (str): The query string to name the new tab
            search_results (list: tuple): List of tuples pertaining to query results

        Attributes:
            parent (ref): Reference to the parent wx.object
            root_pane (ref): Reference to the upstream wx.object pane
            query (str): The query string to name the new tab
            search_results (list: tuple): List of tuples pertaining to query results
    """

    def __init__(self, parent, root_pane, query, search_results):
        """Constructor"""
        wx.Panel.__init__(self, parent, size=(0, 0))  # Needs size parameter to remove black-square
        self.SetDoubleBuffered(True)  # Remove slight strobing on tab switch
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))  # Ensure that edit cursor does not show by default

        # Parental inheritance
        self.parent = parent
        self.root_pane = root_pane

        # Instance Variables
        self.query = query
        self.search_results = search_results

        # Library widget and sizer
        self.wgt_library = widget.CompositeLibrary(self, root_pane)
        self.szr_library = wx.StaticBoxSizer(wx.StaticBox(self, label='Search Results: ' + query), orient=wx.VERTICAL)
        self.szr_library.Add(self.wgt_library, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Master Sizer
        self.szr_master = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_master.Add(self.szr_library, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Set Sizer
        self.SetSizer(self.szr_master)