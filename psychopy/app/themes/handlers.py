from copy import deepcopy

from . import colors, icons

# --- Functions to handle specific subclasses of wx.Window ---
import wx
import wx.lib.agw.aui as aui
import wx.stc as stc
from ._themes import ThemeSwitcher


def styleFrame(target):
    # Set background color
    target.SetBackgroundColour(colors.app['frame_bg'])
    # Set foreground color
    target.SetForegroundColour(colors.app['text'])
    # Set aui art provider
    if hasattr(target, 'getAuiManager'):
        target.getAuiManager().SetArtProvider(PsychopyDockArt())
        target.getAuiManager().Update()


def stylePanel(target):
    # Set background color
    target.SetBackgroundColour(colors.app['panel_bg'])
    # Set text color
    target.SetForegroundColour(colors.app['text'])


def styleToolbar(target):
    # Set background color
    target.SetBackgroundColour(colors.app['frame_bg'])
    # Recreate tools
    target.makeTools()


def styleNotebook(target):
    # Set art provider to style tabs
    target.SetArtProvider(PsychopyTabArt())
    # Set dock art provider to get rid of outline
    target.GetAuiManager().SetArtProvider(PsychopyDockArt())
    # Iterate through each page
    for index in range(target.GetPageCount()):
        page = target.GetPage(index)
        # Set page background
        page.SetBackgroundColour(colors.app['panel_bg'])
        # If page points to an icon for the tab, set it
        if hasattr(page, "tabIcon"):
            btn = icons.ButtonIcon(page.tabIcon, size=(16, 16))
            target.SetPageBitmap(index, btn.bitmap)


# Define dict linking object types to style functions
methods = {
    wx.Frame: styleFrame,
    wx.Panel: stylePanel,
    aui.AuiNotebook: styleNotebook,
    # stc.StyledTextCtrl: styleCodeEditor,
    # wx.richtext.RichTextCtrl: styleRichText,
    # wx.py.shell.Shell: styleCodeEditor,
    wx.ToolBar: styleToolbar,
    # wx.StatusBar: styleStatusBar,
    # wx.TextCtrl: styleTextCtrl,
}


class ThemeMixin:
    """
    Mixin class for wx.Window objects, which adds a getter/setter `theme` which will identify children and style them
    according to theme.
    """

    @property
    def theme(self):
        if hasattr(self, "_theme"):
            return self._theme

    @theme.setter
    def theme(self, value):
        # Skip method if theme value is unchanged
        if value == self.theme:
            return
        # Store value
        self._theme = deepcopy(value)

        # Do own styling
        self._applyAppTheme()

        # Get children
        children = []
        if hasattr(self, 'GetChildren'):
            for child in self.GetChildren():
                if child not in children:
                    children.append(child)
        if hasattr(self, 'getAuiManager'):
            for pane in self.getAuiManager().GetAllPanes():
                if pane not in children:
                    children.append(pane.window)
        if hasattr(self, 'GetSizer') and self.GetSizer():
            for child in self.GetSizer().GetChildren():
                if child not in children:
                    children.append(child)
        if hasattr(self, 'MenuItems'):
            for child in self.MenuItems:
                if child not in children:
                    children.append(child)
        if hasattr(self, "GetToolBar"):
            tb = self.GetToolBar()
            if tb not in children:
                children.append(tb)

        # For each child, do styling
        for child in children:
            if isinstance(child, ThemeMixin):
                # If child is a ThemeMixin subclass, we can just set theme
                child.theme = self.theme
            else:
                # Otherwise, look for appropriate method in methods array
                for cls, fcn in methods.items():
                    if isinstance(child, cls):
                        # If child extends this class, call the appropriate method on it
                        fcn(child)

    def _applyAppTheme(self):
        """
        Method for applying app theme to self. By default is the same method as for applying to panels, buttons, etc.
        but can be overloaded when subclassing from ThemeMixin to control behaviour on specific objects.
        """
        for cls, fcn in methods.items():
            if isinstance(self, cls):
                # If child extends this class, call the appropriate method on it
                fcn(self)


class PsychopyDockArt(aui.AuiDefaultDockArt):
    def __init__(self):
        aui.AuiDefaultDockArt.__init__(self)
        # Gradient
        self._gradient_type = aui.AUI_GRADIENT_NONE
        # Background
        self._background_colour = colors.app['frame_bg']
        self._background_gradient_colour = colors.app['frame_bg']
        self._background_brush = wx.Brush(self._background_colour)
        # Border
        self._border_size = 0
        self._border_pen = wx.Pen(colors.app['frame_bg'])
        # Sash
        self._draw_sash = True
        self._sash_size = 5
        self._sash_brush = wx.Brush(colors.app['frame_bg'])
        # Gripper
        self._gripper_brush = wx.Brush(colors.app['frame_bg'])
        self._gripper_pen1 = wx.Pen(colors.app['frame_bg'])
        self._gripper_pen2 = wx.Pen(colors.app['frame_bg'])
        self._gripper_pen3 = wx.Pen(colors.app['frame_bg'])
        self._gripper_size = 0
        # Hint
        self._hint_background_colour = colors.app['frame_bg']
        # Caption bar
        self._inactive_caption_colour = colors.app['docker_bg']
        self._inactive_caption_gradient_colour = colors.app['docker_bg']
        self._inactive_caption_text_colour = colors.app['docker_fg']
        self._active_caption_colour = colors.app['docker_bg']
        self._active_caption_gradient_colour = colors.app['docker_bg']
        self._active_caption_text_colour = colors.app['docker_fg']
        # self._caption_font
        self._caption_size = 25
        self._button_size = 20


class PsychopyTabArt(aui.AuiDefaultTabArt):
    def __init__(self):
        aui.AuiDefaultTabArt.__init__(self)

        self.SetDefaultColours()
        self.SetAGWFlags(aui.AUI_NB_NO_TAB_FOCUS)

        self.SetBaseColour(colors.app['tab_bg'])
        self._background_top_colour = colors.app['panel_bg']
        self._background_bottom_colour = colors.app['panel_bg']

        self._tab_text_colour = lambda page: colors.app['text']
        self._tab_top_colour = colors.app['tab_bg']
        self._tab_bottom_colour = colors.app['tab_bg']
        self._tab_gradient_highlight_colour = colors.app['tab_bg']
        self._border_colour = colors.app['tab_bg']
        self._border_pen = wx.Pen(self._border_colour)

        self._tab_disabled_text_colour = colors.app['text']
        self._tab_inactive_top_colour = colors.app['panel_bg']
        self._tab_inactive_bottom_colour = colors.app['panel_bg']
