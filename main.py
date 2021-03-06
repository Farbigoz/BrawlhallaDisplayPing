import os
import sys
import time
import math
import threading

from package.ping3 import ping
from package.resources import ResourcePath
from package.checkupdate import CheckUpdate
from package.config import ConfigFile, ConfigElement

if sys.platform.lower() not in ['cli','win32']:
    print("only windows is supported for wpf")
    time.sleep(10)
    sys.exit(0)

import clr
clr.AddReference(r"wpf\PresentationFramework")
import System
from System.IO import StreamReader, BinaryWriter, MemoryStream, StringReader
from System.Xml import XmlReader
from System.Windows.Markup import XamlReader, XamlWriter
from System.Threading import Thread, ThreadStart, ApartmentState
from System.Windows import Application, Window, LogicalTreeHelper


System.Reflection.Assembly.LoadFile(ResourcePath('package\Xceed.Wpf.Toolkit.dll'))

SERVERS = {
    "us-e": "pingtest-atl.brawlhalla.com",
    "us-w": "pingtest-cal.brawlhalla.com",
    "eu": "pingtest-ams.brawlhalla.com",
    "sea": "pingtest-sgp.brawlhalla.com",
    "aus": "pingtest-aus.brawlhalla.com",
    "brz": "pingtest-brs.brawlhalla.com",
    "jpn": "pingtest-jpn.brawlhalla.com",
}


# Config path
LOCAL_DATA_FOLDER = "BrawlhallaDisplayPing"
LOCAL_DATA_PATH = os.path.join(os.getenv("APPDATA"), LOCAL_DATA_FOLDER)

if LOCAL_DATA_FOLDER not in os.listdir(os.getenv("APPDATA")):
    os.mkdir(LOCAL_DATA_PATH)


class ConfigMap(ConfigFile):
    text_color = ConfigElement(default="#000000")
    background_color = ConfigElement(default="#eeeeee")
    font_name = ConfigElement(default="System")
    font_size = ConfigElement(default="12")
    server = ConfigElement(default="eu")
    font_weight = ConfigElement(default="Bold")
    posx = ConfigElement(default=0)
    posy = ConfigElement(default=0)


CONFIG = ConfigMap(os.path.join(LOCAL_DATA_PATH, "settings.cfg"))


OverlayXaml = """
<Window 
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" 
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        AllowsTransparency="True" Background="Transparent"
        ResizeMode="NoResize"
        WindowStyle="None"
        Title="Overlay"
        Topmost="True"
        IsHitTestVisible="True"
        Height="200" Width="400"
        ShowInTaskbar="False">

    <Grid Name="Grid" />
</Window> 
"""

OverlayLabelXaml = """
<Label
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    
    Background="Red"
    Foreground="White"
        
    FontFamily="Eras ITC"
    FontWeight="Black"
        
    Content="9999ms"
    
    HorizontalContentAlignment="Center"
    VerticalContentAlignment="Center"
/>
"""

SettingsXaml = """
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" 
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
        xmlns:wpfTool="clr-namespace:Xceed.Wpf.Toolkit;assembly=Xceed.Wpf.Toolkit"
        Title="Settings" Height="500" Width="300">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="25"></RowDefinition>
            <RowDefinition></RowDefinition>
            <RowDefinition Height="2"></RowDefinition>
            <RowDefinition Height="25"></RowDefinition>
            <RowDefinition Height="2"></RowDefinition>
            <RowDefinition Height="25"></RowDefinition>
            <RowDefinition Height="2"></RowDefinition>
            <RowDefinition Height="25"></RowDefinition>
            <RowDefinition Height="2"></RowDefinition>
            <RowDefinition Height="25"></RowDefinition>
            <RowDefinition Height="2"></RowDefinition>
            <RowDefinition Height="25"></RowDefinition>
            <RowDefinition Height="2"></RowDefinition>
            
        </Grid.RowDefinitions>
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="120"></ColumnDefinition>
            <ColumnDefinition></ColumnDefinition>
        </Grid.ColumnDefinitions>
        
        <Label 
            Content="Fonts:"
            VerticalAlignment="Center"
            VerticalContentAlignment="Center"
            Grid.Column="0" Grid.Row="0"/>
        
        <ListBox
            Name="FontsList" 
            SelectionMode="Single"
            Grid.Column="0" Grid.Row="1" Grid.ColumnSpan="2">
        </ListBox>

        <Label 
            Content="Font size:"
            VerticalAlignment="Center"
            VerticalContentAlignment="Center"
            Grid.Column="0" Grid.Row="3"/>

        <wpfTool:ButtonSpinner
            Name="FontSizeSpinner"
            Grid.Column="1" Grid.Row="3">
            <TextBox 
                Name="FontSize"
                VerticalContentAlignment="Center"
            />
        </wpfTool:ButtonSpinner>

        <Label 
            Content="Font weight:"
            VerticalAlignment="Center"
            VerticalContentAlignment="Center"
            Grid.Column="0" Grid.Row="5"/>

        <ComboBox 
            Name="FontWeight"
            Grid.Column="1" Grid.Row="5">
        </ComboBox>

        <Label 
            Content="Text color:"
            VerticalAlignment="Center"
            VerticalContentAlignment="Center"
            Grid.Column="0" Grid.Row="7"/>
        
        <wpfTool:ColorPicker 
            Name="TextColor"
            ShowAvailableColors="False"
            Grid.Column="1" Grid.Row="7"/>
        
        <Label 
            Content="Background clolor:"
            VerticalAlignment="Center"
            VerticalContentAlignment="Center"
            Grid.Column="0" Grid.Row="9"/>

        <wpfTool:ColorPicker 
            Name="BgColor"
            ShowAvailableColors="False"
            Grid.Column="1" Grid.Row="9"/>

        <Label 
            Content="Server:"
            VerticalAlignment="Center"
            VerticalContentAlignment="Center"
            Grid.Column="0" Grid.Row="11"/>

        <ComboBox 
            Name="Servers"
            Grid.Column="1" Grid.Row="11">
        </ComboBox>

    </Grid>
</Window>
"""

ConsoleXaml = """
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" 
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
        Title="Console" Height="300" Width="500">
    <RichTextBox 
            Name="Console"
            VerticalScrollBarVisibility="Auto" 
            Background="Black"
            Foreground="Green"
            IsReadOnly="True">
        <RichTextBox.Resources>
            <Style TargetType="{x:Type Paragraph}">
                <Setter Property="Margin" Value="0"/>
            </Style>
        </RichTextBox.Resources>
    </RichTextBox>
</Window>
"""

MinFontSize = 5
MaxFontSize = 100

FontWeight = {
    "Thin": System.Windows.FontWeights.Thin,
    "ExtraLight": System.Windows.FontWeights.ExtraLight,
    "UltraLight": System.Windows.FontWeights.UltraLight,
    "Light": System.Windows.FontWeights.Light,
    "Normal": System.Windows.FontWeights.Normal,
    "Regular": System.Windows.FontWeights.Regular,
    "Medium": System.Windows.FontWeights.Medium,
    "DemiBold": System.Windows.FontWeights.DemiBold,
    "SemiBold": System.Windows.FontWeights.SemiBold,
    "Bold": System.Windows.FontWeights.Bold,
    "ExtraBold": System.Windows.FontWeights.ExtraBold,
    "UltraBold": System.Windows.FontWeights.UltraBold,
    "Black": System.Windows.FontWeights.Black,
    "ExtraBlack": System.Windows.FontWeights.ExtraBlack
}


def BrushFromHex(hex_color):
    return System.Windows.Media.BrushConverter().ConvertFrom(hex_color)
    

def ColorDialog(alpha=255):
        color_dialog = System.Windows.Forms.ColorDialog()
        if color_dialog.ShowDialog() == System.Windows.Forms.DialogResult.OK:
            return BrushFromHex(
                '#%02x%02x%02x%02x' % (alpha, color_dialog.Color.R, color_dialog.Color.G, color_dialog.Color.B)
            )

        return None


class Main(Window):
    def __init__(self):
        self.window = OverlayWindow()
        Application().Run(self.window.window)


class OverlayWindow:
    __slots__ = (
        "window", "console", "settings",
        "server",
        "label", "check_label",
        "menu"
    )

    def __init__(self):
        self.window = XamlReader.Load(XmlReader.Create(StringReader(OverlayXaml)))

        self.console = Console()

        self.InitializeComponent()
        self.LoadConfig()

        self.settings = SettingsWindow(self)

        self.Run()

    def InitializeComponent(self):
        self.server = "eu"

        self.window.MouseLeftButtonDown += self.MoveOverlay
        self.window.MouseLeftButtonUp += self.SaveOverlayPos
        self.window.MouseRightButtonUp += self.OverlayRightClick

        grid = LogicalTreeHelper.FindLogicalNode(self.window, "Grid")
        self.label = XamlReader.Load(XmlReader.Create(StringReader(OverlayLabelXaml)))
        self.check_label = XamlReader.Load(XmlReader.Create(StringReader(OverlayLabelXaml)))

        self.check_label.VerticalAlignment = 0
        self.check_label.HorizontalAlignment = 0

        self.check_label.Background = BrushFromHex("#00000000")
        self.check_label.Foreground = BrushFromHex("#00000000")
        self.check_label.Content = "9999ms"

        grid.Children.Add(self.label)
        grid.Children.Add(self.check_label)
        
        # Overlay menu
        self.menu = System.Windows.Forms.ContextMenuStrip()

        settings_item = System.Windows.Forms.ToolStripMenuItem("Settings")
        settings_item.Click += self.OpenSettings

        console_item = System.Windows.Forms.ToolStripMenuItem("Console")
        console_item.Click += self.OpenConsole

        respos_item = System.Windows.Forms.ToolStripMenuItem("Reset position")
        respos_item.Click += self.ResetPos

        close_item = System.Windows.Forms.ToolStripMenuItem("Close")
        close_item.Click += self.CloseOverlay

        self.menu.Items.Add(settings_item)
        self.menu.Items.Add(console_item)
        self.menu.Items.Add(respos_item)
        self.menu.Items.Add(close_item)

        # Icon menu
        menu_icon = System.Windows.Forms.ContextMenu()

        settings_item_icon = System.Windows.Forms.MenuItem("Settings")
        settings_item_icon.Click += self.OpenSettings

        console_item_icon = System.Windows.Forms.MenuItem("Console")
        console_item_icon.Click += self.OpenConsole

        respos_item_icon = System.Windows.Forms.MenuItem("Reset position")
        respos_item_icon.Click += self.ResetPos

        close_item_icon = System.Windows.Forms.MenuItem("Close")
        close_item_icon.Click += self.CloseOverlay

        menu_icon.MenuItems.Add(settings_item_icon)
        menu_icon.MenuItems.Add(console_item_icon)
        menu_icon.MenuItems.Add(respos_item_icon)
        menu_icon.MenuItems.Add(close_item_icon)

        notify_icon = System.Windows.Forms.NotifyIcon()
        notify_icon.Text = "Brawlhalla Display Ping"
        notify_icon.Icon = System.Drawing.Icon(ResourcePath("icon.ico"))
        notify_icon.ContextMenu = menu_icon
        notify_icon.Click += self.ClickTrayIcon
        notify_icon.Visible = True

    def LoadConfig(self):
        self.SetPos(CONFIG.posx, CONFIG.posy)
        self.SetServer(CONFIG.server)
        self.SetFont(CONFIG.font_name)
        self.SetFontSize(int(CONFIG.font_size))
        self.SetFontWeight(CONFIG.font_weight)
        self.SetTextColor(BrushFromHex(CONFIG.text_color))
        self.SetBackgroundColor(BrushFromHex(CONFIG.background_color))

    def Run(self):
        self.console.Show()

        threading.Thread(target=self.PingUpdater).start()
        threading.Thread(target=self.CheckUpdate).start()

    def SizeUpdater(self, *args):
        if self.check_label.ActualWidth > 0:
            self.window.Width = self.check_label.ActualWidth * 1.1
            self.window.Height = self.check_label.ActualHeight * 1.1
        self.label.Width = self.check_label.ActualWidth
    
    def MoveOverlay(self, sender, e):
        self.window.DragMove()

    def OverlayRightClick(self, sender, e):
        pos = System.Windows.Forms.Control.MousePosition
        self.menu.Show(pos)

    def SaveOverlayPos(self, sender, e):
        CONFIG.posx, CONFIG.posy = self.GetPos()

    def ResetPos(self, sender, e):
        self.SetPos(0, 0)

        CONFIG.posx = 0
        CONFIG.posy = 0

    # Process
    def PingUpdater(self, *args):
        avg_ping = 0
        
        while True:

            result_ping = ping(SERVERS.get(self.server, "eu"), timeout=1, unit="ms", size=1)

            if avg_ping == 0:
                avg_ping = result_ping

            if result_ping is None:
                result_ping = -1
            else:
                result_ping = math.trunc(result_ping)

            if result_ping >= 0:
                avg_ping = (result_ping + avg_ping) / 2
                console_text = f"Ping: {result_ping}ms \t|\tAvg ping: {math.trunc(avg_ping)}ms"
            else:
                console_text = "Lost package"

            self.window.Dispatcher.Invoke(System.Action(lambda: self.console.AddLine(console_text)))
            self.window.Dispatcher.Invoke(System.Action(lambda: self.SetText(f"{result_ping}ms")))

            time.sleep(1)

    # Tray icon
    def ClickTrayIcon(self, sender, e):
        if e.Button == System.Windows.Forms.MouseButtons.Left:
            if self.window.Visibility == 0:
                self.window.Show()

            self.OpenConsole()

    # Set
    def SetText(self, text):
        self.label.Content = text

        self.window.Dispatcher.Invoke(System.Windows.Threading.DispatcherPriority.Render, System.Action(self.SizeUpdater))

    def SetFont(self, font):
        self.label.FontFamily = System.Windows.Media.FontFamily(font)
        self.check_label.FontFamily = self.label.FontFamily

        self.window.Dispatcher.Invoke(System.Windows.Threading.DispatcherPriority.Render, System.Action(self.SizeUpdater))

        CONFIG.font_name = font

    def SetFontSize(self, size):
        self.label.FontSize = size
        self.check_label.FontSize = self.label.FontSize

        self.window.Dispatcher.Invoke(System.Windows.Threading.DispatcherPriority.Render, System.Action(self.SizeUpdater))

        CONFIG.font_size = str(size)
        
    def SetFontWeight(self, font_weight):
        CONFIG.font_weight = font_weight

        font_weight = FontWeight.get(font_weight, System.Windows.FontWeights.Bold)

        self.label.FontWeight = font_weight
        self.check_label.FontWeight = self.label.FontWeight

        self.window.Dispatcher.Invoke(System.Windows.Threading.DispatcherPriority.Render, System.Action(self.SizeUpdater))

    def SetBackgroundColor(self, color):
        self.label.Background = color
        CONFIG.background_color = str(color)

    def SetTextColor(self, color):
        self.label.Foreground = color
        CONFIG.text_color = str(color)

    def SetServer(self, server):
        self.window.Dispatcher.Invoke(System.Action(lambda: self.console.AddLine(f"Server: {server}")))
        self.server = server
        CONFIG.server = server

    def SetPos(self, x, y):
        self.window.Left = x
        self.window.Top =  y

    # Get
    def GetFont(self):
        return self.label.FontFamily

    def GetFontSize(self):
        return self.label.FontSize

    def GetFontWeight(self):
        return self.label.FontWeight

    def GetBackgroundColor(self):
        return self.label.Background

    def GetTextColor(self):
        return self.label.Foreground

    def GetPos(self):
        return int(self.window.Left), int(self.window.Top)

    # Console
    def OpenConsole(self, *args):
        self.console.Show()

    # Settings
    def OpenSettings(self, *args):
        self.settings.Show()

    # Utils
    def CheckUpdate(self):
        update_url = CheckUpdate()

        if update_url is not None:
            msg = System.Windows.Forms.MessageBox.Show(
                "New version is available.\nVisit homepage?",
                "New version available",
                System.Windows.Forms.MessageBoxButtons.YesNo,
                System.Windows.MessageBoxImage.Information
            )
            
            if msg == System.Windows.MessageBoxResult.Yes:
                System.Diagnostics.Process.Start(update_url)

    def Hide(self):
        self.window.Dispatcher.Invoke(System.Windows.Threading.DispatcherPriority.Render, System.Action(self.window.Hide))

    def Show(self):
        self.window.Dispatcher.Invoke(System.Windows.Threading.DispatcherPriority.Render, System.Action(self.window.Show))

    def CloseOverlay(self, *args):
        self.settings.Close()
        self.console.Close()
        self.window.Close()


class SettingsWindow:
    __slots__ = (
        "window", "overlay",
        "num_regex",
        "fonts_list", "fonts_size", "font_size_spinner", "font_weight",
        "text_color", "bg_color", "bg_tranparent", "servers"
    )

    def __init__(self, overlay: OverlayWindow):
        self.overlay = overlay

        self.window = XamlReader.Load(XmlReader.Create(StringReader(SettingsXaml)))
        self.InitializeComponent()
        self.LoadConfig()

    def InitializeComponent(self):
        self.window.Closing += self.FormClosing

        self.num_regex = System.Text.RegularExpressions.Regex("[^0-9]+")

        self.fonts_list = LogicalTreeHelper.FindLogicalNode(self.window, "FontsList")
        self.fonts_list.SelectionChanged += self.FontSelected

        self.font_size_spinner = LogicalTreeHelper.FindLogicalNode(self.window, "FontSizeSpinner")
        self.font_size_spinner.Spin += self.SpinFontSize

        self.fonts_size = self.font_size_spinner.Content
        self.fonts_size.PreviewKeyDown += self.KeyDownFontSize
        self.fonts_size.KeyDown += self.KeyDownFontSize
        System.Windows.DataObject.AddPastingHandler(
            self.fonts_size, System.Windows.DataObjectPastingEventHandler(self.PasteFontSize)
        )

        self.font_weight = LogicalTreeHelper.FindLogicalNode(self.window, "FontWeight")
        self.font_weight.SelectionChanged += self.FontWeightelected

        self.text_color = LogicalTreeHelper.FindLogicalNode(self.window, "TextColor")
        self.text_color.SelectedColorChanged += self.SetTextColor
        self.text_color.Opened += self.OpenTextColor

        self.bg_color = LogicalTreeHelper.FindLogicalNode(self.window, "BgColor")
        self.bg_color.SelectedColorChanged += self.SetBackgroundColor
        self.bg_color.Opened += self.OpenBackgroundColor

        self.servers = LogicalTreeHelper.FindLogicalNode(self.window, "Servers")
        self.servers.SelectionChanged += self.ServerSelected

    def LoadConfig(self):
        for font in sorted([f.Source for f in System.Windows.Media.Fonts.SystemFontFamilies]):
            font_item = System.Windows.Controls.ListBoxItem()
            font_item.Content = font
            index = self.fonts_list.Items.Add(font_item)

            if font == str(self.overlay.GetFont()):
                self.fonts_list.SelectedIndex = index

        self.fonts_size.Text = str(int(self.overlay.GetFontSize()))
        
        for weight, weight_cls in FontWeight.items():
            index = self.font_weight.Items.Add(weight)

            if self.overlay.GetFontWeight() == weight_cls:
                self.font_weight.SelectedIndex = index

        self.text_color.SelectedColor = System.Windows.Media.ColorConverter.ConvertFromString(
                                                            str(self.overlay.GetTextColor())
                                                        )
        self.bg_color.SelectedColor = System.Windows.Media.ColorConverter.ConvertFromString(
                                                            str(self.overlay.GetBackgroundColor())
                                                        )

        for server in SERVERS.keys():
            index = self.servers.Items.Add(server)

            if self.overlay.server == server:
                self.servers.SelectedIndex = index

    # Fonts
    def FontSelected(self, sender, e):
        self.overlay.SetFont(self.fonts_list.SelectedItem.Content)

    # Font size
    def PasteFontSize(self, sender, e):
        e.CancelCommand()

    def KeyDownFontSize(self, sender, e):
        e.Handled = True

    def SpinFontSize(self, sender, e):
        font_size = int(self.fonts_size.Text)

        if e.Direction == 0 and font_size < MaxFontSize:
            font_size += 1
        elif e.Direction == 1 and font_size > MinFontSize:
            font_size -= 1

        self.fonts_size.Text = str(font_size)
        self.overlay.SetFontSize(font_size)

    # Font style
    def FontWeightelected(self, sender, e):
        self.overlay.SetFontWeight(self.font_weight.SelectedItem)

    # Colors
    def SetTextColor(self, sender, e):
        self.overlay.SetTextColor(BrushFromHex(str(e.NewValue)))

    def OpenTextColor(self, sender, e):
        self.text_color.SelectedColor = System.Windows.Media.ColorConverter.ConvertFromString(
                                                            str(self.overlay.GetTextColor())
                                                        )

    def SetBackgroundColor(self, sender, e):
        self.overlay.SetBackgroundColor(BrushFromHex(str(e.NewValue)))

    def OpenBackgroundColor(self, sender, e):
        self.bg_color.SelectedColor = System.Windows.Media.ColorConverter.ConvertFromString(
                                                            str(self.overlay.GetBackgroundColor())
                                                        )

    # Server
    def ServerSelected(self, sender, e):
        if self.servers.SelectedItem != self.overlay.server:
            self.overlay.SetServer(self.servers.SelectedItem)

    # Utils
    def Show(self):
        self.window.Show()

    def FormClosing(self, sender, e):
        e.Cancel = True
        self.window.Hide()

    def Close(self):
        self.window.Close()


class Console:
    __slots__ = (
        "window", "console"
    )

    def __init__(self):
        self.window = XamlReader.Load(XmlReader.Create(StringReader(ConsoleXaml)))
        self.InitializeComponent()

    def InitializeComponent(self):
        self.window.Closing += self.FormClosing

        self.console = LogicalTreeHelper.FindLogicalNode(self.window, "Console")
        self.console.Document = System.Windows.Documents.FlowDocument()

        self.console.TextChanged += self.LineAdded

    def LineAdded(self, sender, e):
        self.console.ScrollToEnd()

    def AddLine(self, text):
        #if self.window.Visibility == 0 and self.window.WindowState == 0:
        self.console.Document.Blocks.Add(System.Windows.Documents.Paragraph(System.Windows.Documents.Run(text)))
        if self.console.Document.Blocks.Count > 100:
            self.console.Document.Blocks.Remove(
                self.console.Document.Blocks.get_FirstBlock()
            )

    def Show(self):
        self.window.Show()

    def FormClosing(self, sender, e):
        e.Cancel = True
        self.window.Hide()

    def Close(self):
        self.window.Close()


if __name__ == '__main__':
    thread = Thread(ThreadStart(Main))
    thread.SetApartmentState(ApartmentState.STA)
    thread.Start()
    thread.Join()
