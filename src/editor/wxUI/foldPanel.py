import wx
import editor.edPreferences as edPreferences
from editor.constants import ICONS_PATH

Panel_Fold_size = 23.0

Bitmap_offset_right = 5
Label_offset_right_0 = 20  # label offset without toggle btn
Label_offset_right_1 = 40  # label offset with toggle btn
Toggle_btn_offset_right = 7
Controls_offset_right = 18

FOLD_OPEN_ICON = ICONS_PATH + "\\" + "foldOpen_16.png"
FOLD_CLOSE_ICON = ICONS_PATH + "\\" + "foldClose_16.png"

Debug_Mode = True  # debug mode add a small separation of 0.2 between two vertical adjacent controls


class FoldPanel(wx.Panel):
    def __init__(self, fold_manager, label, is_sub_panel=False):
        wx.Panel.__init__(self, fold_manager)

        self.SetWindowStyleFlag(wx.BORDER_NONE)
        self.SetBackgroundColour(wx.Colour(edPreferences.Colors.Panel_Dark))

        self.fold_manager = fold_manager

        self.__label = label
        self.__controls_in_sizer = False
        self.__is_sub_panel = is_sub_panel

        # load text resources
        self.font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.text_colour = edPreferences.Colors.Bold_Label

        self.fd_control = None
        self.label_control = None

        self.wx_properties = []
        self.expanded = False

        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # self.static_line = wx.StaticLine(self, style=wx.SL_HORIZONTAL)
        # self.static_line.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
        # self.v_sizer.Add(self.static_line, 0, wx.EXPAND | wx.BOTTOM, border=0)
        self.v_sizer.Add(self.h_sizer, 0, wx.EXPAND)

        self.SetSizer(self.v_sizer)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_evt_left_down)
        self.Bind(wx.EVT_SIZE, self.on_evt_size)

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, value):
        self.label_control.SetLabel(value)
        self.__label = value

    def add_control(self, _property):
        self.wx_properties.append(_property)

    def set_controls(self, controls: list):
        for prop in self.wx_properties:
            prop.Destroy()
        self.wx_properties.extend(controls)

    def create_buttons(self, toggle_btn=None, control_group=None):
        """Draws panel open and close buttons, a toggle property, set via call to fold_panel.set_toggle_property
        and an optional wx_custom.control_group"""

        # set panel open and close icons
        self.fd_open_icon = wx.Image(FOLD_OPEN_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.fd_close_icon = wx.Image(FOLD_CLOSE_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.fd_control = wx.StaticBitmap(self, -1, self.fd_close_icon, (0, 0), size=wx.Size(9, 9))

        #
        # self.options_panel = control_group

        self.label_control = wx.StaticText(self, label=self.__label)
        self.label_control.SetFont(self.font)
        self.label_control.SetForegroundColour(self.text_colour)

        self.h_sizer.AddSpacer(2)
        self.h_sizer.Add(self.fd_control, 0, wx.EXPAND | wx.TOP, border=1)
        self.h_sizer.AddSpacer(2)

        if toggle_btn:
            self.h_sizer.Add(toggle_btn, 0, wx.EXPAND | wx.RIGHT, border=3)
        else:
            self.h_sizer.AddSpacer(2)

        self.h_sizer.Add(self.label_control, 0, wx.EXPAND | wx.TOP, border=2)

        if control_group:
            self.h_sizer.AddStretchSpacer()
            self.h_sizer.Add(control_group, 0, wx.EXPAND | wx.RIGHT, border=5)

        self.v_sizer.Layout()

    def on_pin(self, idx):
        pass

    def on_clear_pinned(self, idx):
        pass

    def update_controls(self, shown=True):
        layout = False
        for i in range(len(self.wx_properties)):
            control = self.wx_properties[i]
            if shown:
                if not self.__controls_in_sizer:
                    self.v_sizer.Add(control, 0, wx.EXPAND | wx.LEFT, border=8)
                control.Show()
                layout = True
            else:
                self.v_sizer.Detach(control)
                control.Hide()
                layout = False

        self.__controls_in_sizer = layout
        self.v_sizer.Layout()

    def switch_expanded_state(self, state=None):
        if state:
            self.expanded = state

        if not self.expanded:  # if closed, open
            self.update_controls(True)
            self.expanded = True
            self.fold_manager.on_panel_foldout(self)

            # change graphics to fold open
            self.fd_control.SetBitmap(self.fd_open_icon)
            self.fd_control.SetSize(wx.Size(9, 9))
            self.fd_control.SetPosition((-1, 6))

        else:  # if open, close
            self.update_controls(False)
            self.expanded = False
            self.fold_manager.on_panel_foldout(self)

            # change graphics to fold close
            self.fd_control.SetBitmap(self.fd_close_icon)
            self.fd_control.SetSize(wx.Size(9, 9))
            self.fd_control.SetPosition((-1, 5))

    def clear(self):
        for control in self.wx_properties:
            control.Hide()
        self.wx_properties.clear()

    def on_evt_left_down(self, evt):
        self.switch_expanded_state()
        evt.Skip()

    def on_evt_size(self, evt):
        self.update_controls(self.expanded)
        evt.Skip()


class FoldPanelManager(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.SetWindowStyleFlag(wx.BORDER_NONE)
        # self.SetBackgroundColour(wx.Colour(100, 100, 100, 255))

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.panels = []
        self.parent = args[0]

    def add_panel(self, name="", is_sub_panel=False):
        panel = FoldPanel(self, name, is_sub_panel)

        if is_sub_panel:
            self.sizer.Add(panel, 0, wx.EXPAND | wx.LEFT, border=8)
        else:
            self.sizer.Add(panel, 0, wx.EXPAND)

        self.panels.append(panel)
        return panel

    def on_panel_foldout(self, panel):
        self.PostSizeEventToParent()

    @property
    def panel_count(self):
        return len(self.panels)
