# -*- coding: utf-8 -*-
"""This module contains custom widgets (composite panels) to be used in the main application frame."""


import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.agw.ultimatelistctrl as ULC
from math import ceil
import os
import subprocess

import dialog

import config
import fn_path
import fn_gfx


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


# reverse_map = dict(reversed(item) for item in forward_map.items())

# DISCIPLINES = {1:"Mech",
#                2:"Structural",
#                3:"Geotech",
#                4:"Electrical",
#                5:"Seismic"}

# DOCTYPE = {1:"Codes and Specifications",
#            2:"Reference Materials",
#            3:"Catalogues",
#            4:"Calculators"}

# DISCIPLINES2 = {"Mech":1,
#                "Structural":2,
#                "Geotech":3,
#                "Electrical":4,
#                "Seismic":5}

# DOCTYPE2 = {"Codes and Specifications":1,
#            "Reference Materials":2,
#            "Catalogues":3,
#            "Calculators":4}


class CompositeLibrary(wx.Panel):
    """Custom widget that overlays an "add image" button on top of the WidgetGallery custom widget

        Class Variables:
            btn_size (int): Size of the "add image" button in the overlay

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    btn_size = 25

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        # Button overlay and binding
        self.btn_add_image = wx.BitmapButton(self,
                                             bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                             size=(CompositeGallery.btn_size,) * 2)

        # Image gallery subwidget
        self.pnl_gallery = ULC.UltimateListCtrl(self,
                                                wx.ID_ANY,
                                                agwStyle = wx.LC_REPORT |
                                                           wx.LC_VRULES |
                                                           wx.LC_HRULES)
        self.pnl_gallery.Bind(ULC.EVT_LIST_ITEM_ACTIVATED, self.open_document)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_CHECK
        info._image = []
        info._format = 0
        info._kind = 1
        info._text = "File Name"
        self.pnl_gallery.InsertColumnInfo(0, info)

        info = ULC.UltimateListItem()
        info._format = wx.LIST_FORMAT_RIGHT
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT
        info._image = []
        info._text = "Title"
        # info._font = boldfont
        self.pnl_gallery.InsertColumnInfo(1, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info._format = 0
        info._text = "Category"
        # info._font = font
        info._image = []
        self.pnl_gallery.InsertColumnInfo(2, info)

        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info._format = 0
        info._text = "Discipline"
        # info._font = font
        info._image = []
        self.pnl_gallery.InsertColumnInfo(3, info)

        for i, result in enumerate(self.root.search_results):
            self.pnl_gallery.InsertStringItem(i, result[0])
            self.pnl_gallery.SetStringItem(i, 1, result[1])
            self.pnl_gallery.SetStringItem(i, 2, self.parent.parent.pane.map_id_cat[result[2]])
            self.pnl_gallery.SetStringItem(i, 3, self.parent.parent.pane.map_id_disc[result[3]])
            #
            # self.pnl_gallery.InsertStringItem(1, "Puffy")
            # self.pnl_gallery.SetStringItem(1, 1, "Bring It!")
            # self.pnl_gallery.SetStringItem(1, 2, "Pop")
            #
            # self.pnl_gallery.InsertStringItem(2, "Family Force 5")
            # self.pnl_gallery.SetStringItem(2, 1, "III")
            # self.pnl_gallery.SetStringItem(2, 2, "Crunk")

        self.pnl_gallery.SetColumnWidth(0, 120)
        self.pnl_gallery.SetColumnWidth(1, 120)
        self.pnl_gallery.SetColumnWidth(2, 120)
        self.pnl_gallery.SetColumnWidth(3, -3)

        # choice = wx.Choice(self.pnl_gallery, -1, choices=["one", "two"])
        # index = self.pnl_gallery.InsertStringItem(9, "A widget")

        # self.pnl_gallery.SetItemWindow(index, 1, choice, expand=True)

        file_drop_target = DummyFileDrop(self, self.evt_dragged_files)

        # Button overlay binding - Must be after subwidget to bind to
        self.btn_add_image.Bind(wx.EVT_BUTTON, self.event_1)#self.pnl_gallery.evt_add_image)
        self.btn_add_image.Bind(wx.EVT_SET_FOCUS, self.evt_btn_no_focus)
        self.btn_add_image.SetDropTarget(file_drop_target)

        # Main sizer - do not add button so it floats
        szr_main = wx.BoxSizer(wx.VERTICAL)
        szr_main.Add(self.pnl_gallery, proportion=1, flag=wx.EXPAND)
        self.SetSizer(szr_main)

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

    def open_document(self, event):
        """Move the button overlay when resized

            Args:
                event: A resize event object passed from the resize event
        """

        print(event.GetIndex())
        print(event.GetText())
        # subprocess.run(['open', r"C:\Users\JA\Desktop\Contractor Orientation Checklist.pdf"], check=True)
        # os.system(self.cmd_escape(r'C:\Users\JA\Desktop\Contractor Orientation Checklist.pdf'))
        os.startfile(self.cmd_escape(r'C:\Users\JA\Desktop\Contractor Orientation Checklist.pdf'))
        # subprocess.run(self.cmd_escape(r'C:\Users\JA\Desktop\Contractor Orientation Checklist.pdf'), )
        print(5)

    def event_1(self, event):
        """Move the button overlay when resized

            Args:
                event: A resize event object passed from the resize event
        """

        print("test")

    def evt_dragged_files(self, file_paths):
        """Trigger dialog to add new documents

            Args:
                file_paths (list: str): A list of string paths for the file(s) dropped onto this widget
        """

        for document in file_paths:
            _dlg = dialog.AddDocument(self, self.root, document)
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
        self.btn_add_image.SetPosition((_w - CompositeGallery.btn_size, _h - CompositeGallery.btn_size))

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
    """Master pane that contains the normal operational widgets for the application

        Class Variables:
            bar_size (int): Size (height) of the top ribbon with the searchbar

        Args:
            parent (ptr): Reference to the wx.object this panel belongs to

        Attributes:
            parent (ptr): Reference to the wx.object this panel belongs to
    """

    def __init__(self, parent, *args, **kwargs):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        #self.SetDoubleBuffered(True)  # Remove odd effects at main switch to this pane after login

        self.parent = parent
        self.show_restrictions = False

        # Document Category Checkboxes
        self.wgt_chk_category = []
        self.szr_chk_category = wx.BoxSizer(wx.VERTICAL)
        for category in self.parent.map_cat_id:
            _new_checkbox = wx.CheckBox(self, label=category)
            self.wgt_chk_category.append(_new_checkbox)
            self.szr_chk_category.Add(_new_checkbox)
            _new_checkbox.Hide()

        # Discipline Checkboxes
        self.wgt_chk_disciplines = []
        self.szr_chk_disciplines = wx.BoxSizer(wx.VERTICAL)
        for discipline in self.parent.map_disc_id:
            _new_checkbox = wx.CheckBox(self, label=discipline)
            self.wgt_chk_disciplines.append(_new_checkbox)
            self.szr_chk_disciplines.Add(_new_checkbox)
            _new_checkbox.Hide()


        # Restrictions sizer
        _a = wx.StaticBox(self, label="Restrict search to:")
        # _a.Bind(wx.EVT_KEY_DOWN, self.toggle_restrictions)
        szr_restrictions = wx.StaticBoxSizer(_a, orient=wx.HORIZONTAL)
        szr_restrictions.Add(self.szr_chk_category)
        szr_restrictions.AddSpacer(2)
        szr_restrictions.Add(self.szr_chk_disciplines)

        self.SetSizer(szr_restrictions)

    def evt_click_header(self, event):
        if event.GetPosition()[1] < 20:
            self.toggle_restrictions()

    def toggle_restrictions(self):
        self.show_restrictions = not self.show_restrictions
        for each in self.wgt_chk_disciplines + self.wgt_chk_category:
            each.Show() if self.show_restrictions else each.Hide()
        self.parent.Layout()

    def evt_enter_widget(self, event):
        self.toggle_restrictions()

    def evt_leave_widget(self, event):
        if self.HitTest(event.Position) == wx.HT_WINDOW_OUTSIDE:
            self.toggle_restrictions()














class CompositeGallery(wx.Panel):
    """Custom widget that overlays an "add image" button on top of the WidgetGallery custom widget

        Class Variables:
            btn_size (int): Size of the "add image" button in the overlay

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    btn_size = 25

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        # Button overlay and binding
        self.btn_add_image = wx.BitmapButton(self,
                                             bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                             size=(CompositeGallery.btn_size,) * 2)

        # Image gallery subwidget
        self.pnl_gallery = WidgetGallery(self, self.root)

        # Button overlay binding - Must be after subwidget to bind to
        self.btn_add_image.Bind(wx.EVT_BUTTON, self.pnl_gallery.evt_add_image)
        self.btn_add_image.Bind(wx.EVT_SET_FOCUS, self.evt_btn_no_focus)

        # Main sizer - do not add button so it floats
        szr_main = wx.BoxSizer(wx.VERTICAL)
        szr_main.Add(self.pnl_gallery, proportion=1, flag=wx.EXPAND)
        self.SetSizer(szr_main)

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

    def evt_resize(self, event):
        """Move the button overlay when resized

            Args:
                event: A resize event object passed from the resize event
        """

        # Get width and height of the resize and subtract a tuple representing the scrollbar size
        (_w, _h) = event.GetSize() - (16, 0)

        # Move the button that adds more images
        self.btn_add_image.SetPosition((_w - CompositeGallery.btn_size, _h - CompositeGallery.btn_size))

        # Refresh Layout required for unknown reasons - otherwise odd scale behaviour on pnl_gallery
        self.Layout()

    def evt_btn_no_focus(self, event):
        """Prevents focus from being called on the buttons

            Args:
                event: A focus event
        """
        pass


class WidgetGallery(scrolled.ScrolledPanel):
    """Custom scrolled widget to contain a gallery of photos associated with the part of the parent tab

        Class Variables:
            icon_gap (int): Spacing between adjacent icons in sizer
            icon_size (int): Square size intended for the icon for each image

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    icon_gap = 5
    icon_size = 120

    def __init__(self, parent, root):
        """Constructor"""
        super().__init__(parent, style=wx.BORDER_SIMPLE)

        # Variables
        self.parent = parent
        self.root = root

        # Load list of images from database and store the image filenames with extensions
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT image FROM Images WHERE part_num=(?) AND part_rev=(?);",
                     (self.root.part_num, self.root.part_rev))
        self.image_list = [i[0] for i in crsr.fetchall()]
        conn.close()

        # Create list of raw images
        self.images = [fn_path.concat_img(self.root.part_num, img) for img in self.image_list]

        # Create a grid sizer to contain image icons
        self.nrows, self.ncols = 1, len(self.images)
        self.img_object_list = []
        self.sizer_grid = wx.GridSizer(rows=self.nrows + 1,
                                       cols=self.ncols,
                                       hgap=WidgetGallery.icon_gap,
                                       vgap=WidgetGallery.icon_gap)

        # Add cropped and scaled image icons to the grid sizer
        for r in range(self.nrows):
            for c in range(self.ncols):
                _n = self.ncols * r + c
                _tmp = fn_gfx.crop_square(wx.Image(self.images[_n]), WidgetGallery.icon_size)
                _temp = wx.StaticBitmap(self, bitmap=wx.Bitmap(_tmp))
                _temp.Bind(wx.EVT_LEFT_UP, self.evt_image_click)
                self.img_object_list.append(_temp)
                self.sizer_grid.Add(_temp, wx.EXPAND)

        # Main sizer
        szr_main = wx.BoxSizer(wx.VERTICAL)
        szr_main.Add(self.sizer_grid)
        self.SetSizer(szr_main)

        # Setup the scrolling style and function, wanting only vertical scroll to be available
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetWindowStyle(wx.VSCROLL)

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

        # Bind layout recalculation to scrolling
        self.Bind(wx.EVT_SCROLLWIN, self.evt_scroll)

    def evt_image_click(self, event):
        """Call up the dialog for when an image is clicked

            Args:
                event: The triggering click event object
        """

        # Load the "image clicked" dialog
        _dlg = dialog.EditImage(self, self.root, self.img_object_list.index(event.GetEventObject()))
        _dlg.ShowModal()
        if _dlg: _dlg.Destroy()

    def evt_add_image(self, event):
        """Call up dialogs to add an image to the database

            Args:
                event: A button event object passed from the button click
        """

        # Open an explorer dialog to select images to import
        with wx.FileDialog(None, "Open",
                           wildcard="Images (*.png;*.jpg;*.bmp;*.gif)|*.png;*.jpg;*.jpeg;*.bmp;*.gif|"
                                    "PNG (*.png)|*.png|"
                                    "JPEG (*.jpg)|*.jpg;*.jpeg|"
                                    "BMP (*.bmp)|*.bmp|"
                                    "GIF (*.gif)|*.gif",
                           style=wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST) as file_dialog:

            # Check if the user changed their mind about importing
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            # Make a list of chosen images to add to the database
            selected_files = file_dialog.GetPaths()

        # Proceed loading the file(s) chosen by the user to the "add image" dialog
        _dlg = dialog.AddImage(self, self.root, selected_files)
        _dlg.ShowModal()
        if _dlg: _dlg.Destroy()

    def evt_resize(self, event):
        """Resize the image grid

        Retrieves width and height of the grid panel and adds/removes grid columns/rows to fit panel nicely.

            Args:
                event: A resize event object passed from the resize event
        """

        # Get width and height of the resize
        (_w, _h) = event.GetSize()

        # Calculate the number of columns that fit in the scrolled panel, force a minimum of 1 columns
        _c = max((_w - WidgetGallery.icon_gap) // (WidgetGallery.icon_size + WidgetGallery.icon_gap), 1)

        # Redistribute rows and columns for the grid
        self.sizer_grid.SetCols(_c)
        self.sizer_grid.SetRows(ceil(len(self.image_list)/_c))

    def evt_scroll(self, event):
        """Adds forced recalculation of layout on scroll - as default repainting of frames does not work here

            Args:
                event: Scroll event
        """

        wx.CallAfter(self.Layout)
        event.Skip()


class CompositeNotes(wx.Panel):
    """Custom widget that overlays an "add note" button on top of the WidgetNotes custom widget as well as
    governs the column header behavior

        Class Variables:
            btn_size (int): Size of the "add image" button in the overlay
            col_min (list: int): List of minimum column widths for the column headers

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    btn_size = 25
    col_min = [25, 40, -1]

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        # List of text objects in the header
        self.header_list = []

        # Draw button first, as the first object drawn stays on top
        self.btn_add_note = wx.BitmapButton(self,
                                            bitmap=wx.Bitmap(fn_path.concat_gui('plus.png')),
                                            size=(CompositeNotes.btn_size,) * 2)

        # Set up sizer to contain header and scrolled notes
        self.pnl_notes = NotesScrolled(self, self.root)

        # Button overlay binding - Must be after subwidget to bind to
        self.btn_add_note.Bind(wx.EVT_BUTTON, self.pnl_notes.evt_add_note)
        self.btn_add_note.Bind(wx.EVT_SET_FOCUS, self.evt_button_no_focus)

        # Binding for clicking between notes text
        self.pnl_notes.Bind(wx.EVT_LEFT_UP, self.evt_edit_note)

        # Main Sizer
        self.szr_title = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_main = wx.BoxSizer(wx.VERTICAL)
        self.szr_main.Add(self.szr_title, flag=wx.ALL | wx.EXPAND)
        self.szr_main.Add(self.pnl_notes, proportion=1, flag=wx.ALL | wx.EXPAND)

        self.header_list.append(
            wx.StaticText(self,
                          label="Date", style=wx.ALIGN_LEFT))
        self.header_list.append(
            wx.StaticText(self,
                          label="Author", style=wx.ALIGN_LEFT))
        self.header_list.append(wx.StaticText(self, label="Note", style=wx.ALIGN_LEFT))

        self.szr_title.Add(self.header_list[0])
        self.szr_title.Add(self.header_list[1])
        self.szr_title.Add(self.header_list[2], proportion=1)
        #self.szr_title.Add(self.header_list[3])

        # Refresh headers, repopulating self.sizer_title
        self.refresh_headers()

        # Set sizer and resize
        self.SetSizer(self.szr_main)
        self.Layout()

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

    def refresh_headers(self):
        """Refresh the column headers to reflect the column widths in the lower scrolled sizer"""

        # Append three 0s in case the notes list is empty. Only the first 3 entries are observed
        column_widths = [*self.pnl_notes.szr_grid.GetColWidths(), 0, 0, 0][:3]

        # Change the size of the first two column headers
        self.header_list[0].SetMinSize((max(column_widths[0], CompositeNotes.col_min[0]) + NotesScrolled.col_gap, -1))
        self.header_list[1].SetMinSize((max(column_widths[1], CompositeNotes.col_min[1]) + NotesScrolled.col_gap, -1))

        # Ensure headers resize properly
        self.Layout()

    def evt_edit_note(self, event):
        """Determine where in the scrolled panel was clicked and pass that to the method handling the dialog

            Args:
                event: A resize event object passed from the click event
        """

        # Mouse positions within the overall panel, corrected for scroll. The math signage is odd, but works out
        pos_panel = self.pnl_notes.ScreenToClient(wx.GetMousePosition())[1]
        pos_scroll = -self.pnl_notes.CalcScrolledPosition(0, 0)[1]

        # Call method from the panel itself to handle dialog popup
        self.pnl_notes.edit_notes((pos_panel + pos_scroll) // 20)

    def evt_resize(self, event):
        """Move the button overlay when resized

            Args:
                event: A resize event object passed from the resize event
        """

        # Get width and height of the resize and subtract a tuple representing the scrollbar size
        (_w, _h) = event.GetSize() - (16, 0)

        # Move the button that adds more images
        self.btn_add_note.SetPosition((_w - CompositeNotes.btn_size, _h - CompositeNotes.btn_size))

        # Refresh Layout required for unknown reasons - otherwise odd scale behaviour on pnl_gallery
        self.Layout()

    def evt_button_no_focus(self, event):
        """Prevents focus from being called on the buttons

            Args:
                event: A focus event
        """
        pass


class NotesScrolled(scrolled.ScrolledPanel):
    """Custom scrolled widget to contain notes associated with the part of the parent tab

        Class Variables:
            row_gap (int): Vertical spacing between rows in grid
            col_gap (int): Horizontal spacing between columns in grid

        Args:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab

        Attributes:
            parent (ref): Reference to the parent wx.object
            root (ref): Reference to the root parts tab
    """

    row_gap = 5
    col_gap = 15

    def __init__(self, parent, root):
        """Constructor"""
        super().__init__(parent, style=wx.ALL | wx.VSCROLL)

        self.parent = parent
        self.root = root

        # List of current notes items in widget; each entry is a list of three wx.objects
        self.notes_list = []

        # Sizer to hold notes entries - Also set as main sizer
        self.szr_grid = wx.FlexGridSizer(3, NotesScrolled.row_gap, NotesScrolled.col_gap)
        self.szr_grid.AddGrowableCol(2)
        self.szr_grid.SetFlexibleDirection(wx.HORIZONTAL)
        self.szr_grid.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
        self.SetSizer(self.szr_grid)

        # Load notes into the provided grid sizer
        self.load_notes()

        # Setup the scrolling style and function, wanting only vertical scroll to be available
        self.SetupScrolling()
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetWindowStyle(wx.VSCROLL)

        # Not clear as to why this is needed, but without it the scrollbar is missing in some circumstances
        self.SetScrollbars(10, 10, 10, 10)

        # Bind layout recalculation to scrolling
        self.Bind(wx.EVT_SCROLLWIN, self.evt_scroll)

    def load_notes(self):
        """Open SQL database and load notes from table"""

        # Load notes from database
        conn = config.sql_db.connect(config.cfg["db_location"])
        crsr = conn.cursor()
        crsr.execute("SELECT date, author, note FROM Notes WHERE part_num=(?) AND part_rev=(?)",
                     (self.root.part_num, self.root.part_rev))
        _tmp_list = crsr.fetchall()
        conn.close()

        # Sort and remove non-date information from the datetime string
        if _tmp_list:
            _tmp_list = [(a[0][:10],)+a[1:] for a in sorted(_tmp_list, key=lambda x: x[0])]

        # Add the notes to the grid
        for i, note_args in enumerate(_tmp_list):
            self.add_note(*note_args, i)

    def evt_add_note(self, event):
        """Event to trigger the addition of entries to the notes widget

            Args:
                event: A button event object passed from the button click
        """

        _dlg = dialog.AddNote(self, self.root)
        _dlg.ShowModal()
        if _dlg: _dlg.Destroy()

    def add_note(self, timestamp, user, note, id_set=0):
        """Add an entry to the notes widget

            Args:
                self: A reference to the parent wx.object instance
                user: The username that has added the note
                timestamp: The timestamp for when the note was added
                note: The text for the note to be added
        """

        # List of wx.objects to add to the notes widget
        _tmp_item = [wx.StaticText(self, id=id_set, label=timestamp, style=wx.EXPAND),
                     wx.StaticText(self, size=(40, -1), id=id_set, label=user, style=wx.EXPAND),
                     wx.StaticText(self, size=(50, -1), id=id_set, label=note, style=wx.ST_ELLIPSIZE_END)]

        # Binding for the items in the notes widget
        for item in _tmp_item:
            item.Bind(wx.EVT_LEFT_UP, self.evt_edit_notes_trigger)
            self.szr_grid.Add(item, flag=wx.ALL | wx.EXPAND)

        self.notes_list.append(_tmp_item)

        # Refresh both layouts so the scrollbar resets
        self.Layout()
        self.parent.Layout()

    def evt_edit_notes_trigger(self, event):
        """Determine which entry in the scrolled panel was clicked and pass that to the method handling the dialog

            Args:
                event: Click event that triggered this function
        """

        pass
        self.edit_notes(event.GetEventObject().GetId())

    def edit_notes(self, my_index):
        """Method to edit an existing note, based on the provided index in the list

            Args:
                my_index (int): Index for the notes entry you want to edit
        """

        pass
        print(self.notes_list[my_index][0].GetLabel(), self.notes_list[my_index][1].GetLabel(), self.notes_list[my_index][2].GetLabel())
        #dialog = ImageDialog(self.image_list, event.GetEventObject().GetId(), self.parent.part_num, self.parent.part_rev)
        #dialog.ShowModal()
        #dialog.Destroy()

    def evt_scroll(self, event):
        """Adds forced recalculation of layout on scroll - as default repainting of frames does not work here

            Args:
                event: Scroll event
        """

        wx.CallAfter(self.Layout)
        event.Skip()


class CompositeMugshot(wx.Panel):
    """Custom widget that overlays a "show schematic" button on top of the Mugshot widget

            Class Variables:
                mug_size (int): The size of the mugshot photo
                btn_size (int): Size of the "show schematic" button in the overlay

            Args:
                parent (ref): Reference to the parent wx.object
                root (ref): Reference to the root parts tab

            Attributes:
                parent (ref): Reference to the parent wx.object
                root (ref): Reference to the root parts tab
    """

    mug_size = 250
    btn_size = 40

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        # Primary part image
        if self.parent.mugshot:
            image = wx.Image(fn_path.concat_img(self.parent.part_num, self.parent.mugshot), wx.BITMAP_TYPE_ANY)
        else:
            image = wx.Image(fn_path.concat_gui('missing_mugshot.png'), wx.BITMAP_TYPE_ANY)

        # Draw button first as first drawn stays on top
        self.button_dwg = wx.BitmapButton(self,
                                          bitmap=wx.Bitmap(fn_path.concat_gui('schematic.png')),
                                          size=(CompositeMugshot.btn_size,) * 2,
                                          pos=(0, CompositeMugshot.mug_size - CompositeMugshot.btn_size))
        self.button_dwg.Bind(wx.EVT_SET_FOCUS, self.event_button_no_focus)
        self.button_dwg.Bind(wx.EVT_BUTTON, self.evt_blueprint)

        self.imageBitmap = wx.StaticBitmap(self, bitmap=wx.Bitmap(fn_gfx.crop_square(image, CompositeMugshot.mug_size)))

        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_main.Add(self.imageBitmap, flag=wx.ALL)

        self.SetSizer(self.sizer_main)
        self.Layout()
        self.Fit()

    def refresh(self, new_image=None):
        """Updates the mugshot to the image hash provided, directs to the no-image if None is provided

            Args:
                new_image (str): Image filename for mugshot to display
        """
        if new_image:
            temp = fn_path.concat_img(self.parent.part_num, new_image)
        else:
            temp = fn_path.concat_gui('missing_mugshot.png')

        # Update image
        self.imageBitmap.SetBitmap(wx.Bitmap(fn_gfx.crop_square(wx.Image(temp), CompositeMugshot.mug_size)))

    def evt_blueprint(self, event):
        """Loads a dialog or opens a program (unsure) showing the production drawing of said part

            Args:
                event: Button click event
        """

        _dlg = wx.RichMessageDialog(self,
                                   caption="This feature is not yet implemented",
                                   message="This feature will load a production drawing of the current part",
                                   style=wx.OK | wx.ICON_INFORMATION)
        _dlg.ShowModal()
        _dlg.Destroy()

    def event_button_no_focus(self, event):
        """Prevents focus from being called on the buttons

            Args:
                event: A focus event
        """
        pass


class CompositeAssemblies(wx.Panel):
    """Custom scrolled widget to contain sub-assembly and super-assembly data associated with the part of the parent tab

            Class Variables:
                btn_size (int): Size of the "add image" button in the overlay

            Args:
                parent (ref): Reference to the parent wx.object
                root (ref): Reference to the root parts tab

            Attributes:
                parent (ref): Reference to the parent wx.object
                root (ref): Reference to the root parts tab
    """

    btn_size = 25

    def __init__(self, parent, root):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.root = root

        # Draw Sub-Assembly edit button
        self.btn_sub_edit = wx.BitmapButton(self,
                                            bitmap=wx.Bitmap(fn_path.concat_gui('edit.png')),
                                            size=(CompositeAssemblies.btn_size,) * 2)
        self.btn_sub_edit.Bind(wx.EVT_SET_FOCUS, self.evt_button_no_focus)
        self.btn_sub_edit.Bind(wx.EVT_BUTTON, self.evt_sub_edit)

        # Draw Sub-Assembly help button
        self.btn_sub_help = wx.StaticBitmap(self, bitmap=wx.Bitmap(fn_path.concat_gui('help.png')))
        self.btn_sub_help.Bind(wx.EVT_LEFT_UP, self.evt_sub_help)

        # Draw Super-Assembly edit button
        self.btn_super_edit = wx.BitmapButton(self,
                                              bitmap=wx.Bitmap(fn_path.concat_gui('edit.png')),
                                              size=(CompositeAssemblies.btn_size,) * 2)
        self.btn_super_edit.Bind(wx.EVT_SET_FOCUS, self.evt_button_no_focus)
        self.btn_super_edit.Bind(wx.EVT_BUTTON, self.evt_super_edit)

        # Draw Super-Assembly help button
        self.btn_super_help = wx.StaticBitmap(self, bitmap=wx.Bitmap(fn_path.concat_gui('help.png')))
        self.btn_super_help.Bind(wx.EVT_LEFT_UP, self.evt_super_help)

        # Lists containing sub and super assembly info
        self.wgt_sub_assm = wx.ListBox(self,
                                       choices=[i[0] + " r" + i[1] for i in self.root.helper_wgt_sub],
                                       size=(CompositeMugshot.mug_size//2, -1), style=wx.LB_SINGLE | wx.LB_ALWAYS_SB)
        self.wgt_super_assm = wx.ListBox(self,
                                         choices=[i[0] + " r" + i[1] for i in self.root.helper_wgt_super],
                                         size=(CompositeMugshot.mug_size//2, -1), style=wx.LB_SINGLE | wx.LB_ALWAYS_SB)

        # Assembly list binds
        self.wgt_sub_assm.Bind(wx.EVT_LISTBOX, self.evt_click_sub_assm)
        self.wgt_sub_assm.Bind(wx.EVT_MOTION, self.evt_update_tooltip_sub)
        self.wgt_super_assm.Bind(wx.EVT_LISTBOX, self.evt_click_super_assm)
        self.wgt_super_assm.Bind(wx.EVT_MOTION, self.evt_update_tooltip_super)

        # Assembly and Main Sizers
        self.szr_sub_assm = wx.BoxSizer(wx.VERTICAL)
        self.szr_sub_assm.Add(wx.StaticText(self, label="Sub-Assemblies", style=wx.ALIGN_CENTER), border=5,
                              flag=wx.ALL | wx.EXPAND)
        self.szr_sub_assm.Add(self.wgt_sub_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_super_assm = wx.BoxSizer(wx.VERTICAL)
        self.szr_super_assm.Add(wx.StaticText(self, label="Super-Assemblies", style=wx.ALIGN_CENTER), border=5,
                                flag=wx.ALL | wx.EXPAND)
        self.szr_super_assm.Add(self.wgt_super_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_main = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_main.Add(self.szr_sub_assm, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.szr_main.Add(self.szr_super_assm, proportion=1, flag=wx.ALL | wx.EXPAND)

        # Set main sizer and recalculate the layout
        self.SetSizer(self.szr_main)
        self.Layout()

        # Bind button movement to resize
        self.Bind(wx.EVT_SIZE, self.evt_resize)

    def evt_click_sub_assm(self, event):
        """Open a parts tab based on what entry has been clicked

            Args:
                event: A list box click event object passed from the list box when activated
        """

        # Get the index of the clicked item, and open a new parts tab, based on part_num and part_rev
        _index = event.GetSelection()
        self.root.parent.open_parts_tab(*self.root.helper_wgt_sub[_index], wx.GetKeyState(wx.WXK_SHIFT))

        # Deselect the clicked entry of the list box
        event.GetEventObject().SetSelection(wx.NOT_FOUND)

    def evt_click_super_assm(self, event):
        """Open a parts tab based on what entry has been clicked

            Args:
                event: A list box click event object passed from the list box when activated
        """

        # Get the index of the clicked item, and open a new parts tab, based on part_num and part_rev
        _index = event.GetSelection()
        self.root.parent.open_parts_tab(*self.root.helper_wgt_super[_index], wx.GetKeyState(wx.WXK_SHIFT))

        # Deselect the clicked entry of the list box
        event.GetEventObject().SetSelection(wx.NOT_FOUND)

    def evt_update_tooltip_sub(self, event):
        """Update the tooltip with the name of the sub-assembly entry the mouse is over

            Args:
                event: A mouse movement event object passed from the movement event
        """

        # Calculate the index of the item that is under the mouse pointer
        _item_index = self.wgt_sub_assm.HitTest(event.GetPosition())

        # As long as we have a valid index then update the tooltip, otherwise empty it
        if _item_index != -1:
            _num, _rev = self.root.helper_wgt_sub[_item_index]
            _new_msg = self.root.data_wgt_sub[_num][_rev]
            if self.wgt_sub_assm.GetToolTipText() != _new_msg:
                self.wgt_sub_assm.SetToolTip(_new_msg)
        else:
            self.wgt_sub_assm.SetToolTip("")

    def evt_update_tooltip_super(self, event):
        """Update the tooltip with the name of the super-assembly entry the mouse is over

            Args:
                event: A mouse movement event object passed from the movement event
        """

        # Calculate the index of the item that is under the mouse pointer
        _item_index = self.wgt_super_assm.HitTest(event.GetPosition())

        # As long as we have a valid index then update the tooltip, otherwise empty it
        if _item_index != -1:
            _num, _rev = self.root.helper_wgt_super[_item_index]
            _new_msg = self.root.data_wgt_super[_num][_rev]
            if self.wgt_super_assm.GetToolTipText() != _new_msg:
                self.wgt_super_assm.SetToolTip(_new_msg)
        else:
            self.wgt_super_assm.SetToolTip("")

    def evt_sub_edit(self, event):
        """Show the edit dialog for sub-assemblies

            Args:
                event: A button event object passed from the button click
        """

        _dlg = dialog.EditSubAssemblies(self, self.root)
        _dlg.ShowModal()
        if _dlg: _dlg.Destroy()

    def evt_super_edit(self, event):
        """Show the edit dialog for super-assemblies

            Args:
                event: A button event object passed from the button click
        """

        _dlg = dialog.EditSuperAssemblies(self, self.root)
        _dlg.ShowModal()
        if _dlg: _dlg.Destroy()

    def evt_sub_help(self, event):
        """Show the term definition for sub-assembly

            Args:
                event: A click event object passed from the click event
        """

        _dlg = wx.RichMessageDialog(self,
                                    caption="Help: Term Definition",
                                    message="A sub-assembly in this context refers to components or assemblies that, "
                                            "together, assemble into this part.",
                                    style=wx.OK | wx.ICON_INFORMATION)
        _dlg.ShowModal()
        _dlg.Destroy()

    def evt_super_help(self, event):
        """Show the term definition for super-assembly

            Args:
                event: A click event object passed from the click event
        """

        _dlg = wx.RichMessageDialog(self,
                                    caption="Help: Term Definition",
                                    message="A super-assembly in this context refers to assemblies that contain "
                                            "this part.",
                                    style=wx.OK | wx.ICON_INFORMATION)
        _dlg.ShowModal()
        _dlg.Destroy()

    def evt_resize(self, event):
        """Move the button overlays when re-sized

            Args:
                event: A resize event object passed from the resize event
        """

        _help_shift = 6
        _help_size = 10

        # Get width and height of the resize and subtract a correction tuple
        (_w, _h) = event.GetSize() - (1, 1)

        # Move the buttons that edit the assembly lists, and correct to exclude the scrollbar width (17)
        self.btn_super_edit.SetPosition((_w - CompositeAssemblies.btn_size - 17, _h - CompositeAssemblies.btn_size))
        self.btn_sub_edit.SetPosition((_w // 2 - CompositeAssemblies.btn_size - 17, _h - CompositeAssemblies.btn_size))

        # Move the buttons that display help for the assembly lists
        self.btn_super_help.SetPosition((_w - _help_shift - _help_size // 2,
                                         (self.wgt_sub_assm.GetCharHeight() - _help_size) // 2 + 6))
        self.btn_sub_help.SetPosition((_w // 2 - _help_shift - _help_size // 2,
                                       (self.wgt_sub_assm.GetCharHeight() - _help_size) // 2 + 6))

        # Refresh Layout required for unknown reasons - otherwise odd scale behaviour
        self.Layout()

    def evt_button_no_focus(self, event):
        """Prevents focus from being called on the buttons

            Args:
                event: A focus event
        """
        pass