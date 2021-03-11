import os
import sys
import time
import math
import threading

from package.ping3 import ping
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
from System.Drawing import Font


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
    background_transparent = ConfigElement(default=False)
    font_name = ConfigElement(default="System")
    font_size = ConfigElement(default="12")
    server = ConfigElement(default="eu")
    font_weight = ConfigElement(default="Bold")


CONFIG = ConfigMap(os.path.join(LOCAL_DATA_PATH, "settings.cfg"))


OverlayXaml = """
<Window 
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" 
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        AllowsTransparency="True" Background="Transparent"
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

    VerticalAlignment="Center"
    HorizontalAlignment="Center"
    
    HorizontalContentAlignment="Center"
    VerticalContentAlignment="Center"
/>
"""

"""
    VerticalAlignment="Center"
    HorizontalAlignment="Center"
"""

SettingsXaml = """
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" 
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
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

        <Grid
            Grid.Column="1" Grid.Row="3">
            <Grid.RowDefinitions>
                <RowDefinition></RowDefinition>
                <RowDefinition></RowDefinition>
            </Grid.RowDefinitions>
            <Grid.ColumnDefinitions>
                <ColumnDefinition></ColumnDefinition>
                <ColumnDefinition Width="15"></ColumnDefinition>
            </Grid.ColumnDefinitions>
            
            <TextBox
                Name="FontSize"
                VerticalContentAlignment="Center"
                Grid.Column="0" Grid.Row="0" Grid.RowSpan="2"/>

            <Button 
                Name="FontSizeUp"
                Grid.Column="1" Grid.Row="0"/>
            <Button
                Name="FontSizeDown"
                Grid.Column="1" Grid.Row="1"/>
        </Grid>

        <Label 
            Content="Font style:"
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
        
        <Button 
            Name="TextColor"
            Background="White"
            Grid.Column="1" Grid.Row="7"/>
        
        <Label 
            Content="Background clolor:"
            VerticalAlignment="Center"
            VerticalContentAlignment="Center"
            Grid.Column="0" Grid.Row="9"/>

        <Grid
            Grid.Column="1" Grid.Row="9">
            <Grid.RowDefinitions>
                <RowDefinition></RowDefinition>
            </Grid.RowDefinitions>
            <Grid.ColumnDefinitions>
                <ColumnDefinition></ColumnDefinition>
                <ColumnDefinition Width="75"></ColumnDefinition>
                <ColumnDefinition Width="20"></ColumnDefinition>
            </Grid.ColumnDefinitions>

            <Button 
                Name="BackgroundColor"
                Background="Black"
                Grid.Column="0"/>

            <Label 
                Content="Transparent:"
                VerticalAlignment="Center"
                VerticalContentAlignment="Center"
                Grid.Column="1"/>

            <CheckBox 
                Name="BackgroundTranparent"
                VerticalContentAlignment="Center"
                Grid.Column="2" Margin="0,1,0,-1"/>

        </Grid>

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


class OverlayWindow(Window):
    def __init__(self):
        self.window = XamlReader.Load(XmlReader.Create(StringReader(OverlayXaml)))
        self.InitializeComponent()
        self.Loading()
        
        self.settings = SettingsWindow(self)

        threading.Thread(target=self.PingUpdater).start()
        threading.Thread(target=self.CheckUpdate).start()
        Application().Run(self.window)

    def InitializeComponent(self):
        self.server = "eu"

        self.window.MouseLeftButtonDown += self.MoveOverlay
        self.window.MouseRightButtonUp += self.OverlayRightClick

        self.grid = LogicalTreeHelper.FindLogicalNode(self.window, "Grid")
        self.label = XamlReader.Load(XmlReader.Create(StringReader(OverlayLabelXaml)))
        self.check_label = XamlReader.Load(XmlReader.Create(StringReader(OverlayLabelXaml)))
        
        self.grid.Children.Add(self.label)

        #self.label.VerticalAlignment = 0
        #self.label.HorizontalAlignment = 0

        self.check_label.Background = BrushFromHex("#00000000")
        self.check_label.Foreground = BrushFromHex("#00000000")
        self.check_label.Content = "9999ms"
        self.grid.Children.Add(self.check_label)
        
        # make menu
        self.menu = System.Windows.Forms.ContextMenuStrip()

        settings_item = System.Windows.Forms.ToolStripMenuItem("Settings")
        settings_item.Click += self.OpenSettings

        close_item = System.Windows.Forms.ToolStripMenuItem("Close")
        close_item.Click += self.CloseOverlay

        self.menu.Items.Add(settings_item)
        self.menu.Items.Add(close_item)

    def Loading(self):
        self.SetServer(CONFIG.server)
        self.SetFont(CONFIG.font_name)
        self.SetFontSize(int(CONFIG.font_size))
        self.SetFontWeight(CONFIG.font_weight)
        self.SetTextColor(BrushFromHex(CONFIG.text_color))

        bg_color = CONFIG.background_color

        if CONFIG.background_transparent:
            if len(bg_color) == 7:
                bg_color = f"#00{bg_color[1:]}"
            else:
                bg_color = f"#00{bg_color[3:]}"

        self.SetBackgroundColor(BrushFromHex(bg_color))

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

    def PingUpdater(self, *args):
        avg_ping = 0
        
        while True:

            result_ping = ping(SERVERS.get(self.server, "eu"), timeout=1, unit="ms")

            if result_ping is None:
                result_ping = -1
            else:
                result_ping = math.trunc(result_ping)

            if result_ping >= 0:
                avg_ping = (result_ping + avg_ping) / 2
                print(f"Ping: {result_ping}ms \t|\tAvg ping: {math.trunc(avg_ping)}ms")
            else:
                print("Lost package")


            self.window.Dispatcher.Invoke(System.Action(lambda: self.SetText(f"{result_ping}ms")))

            time.sleep(1)

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
        CONFIG.background_transparent = str(color).startswith("#00")

    def SetTextColor(self, color):
        self.label.Foreground = color

    def SetServer(self, server):
        print("Server:", server)
        self.server = server
        CONFIG.server = server

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


    def CloseOverlay(self, *args):
        self.settings.Close()
        self.window.Close()

    # Settings
    def OpenSettings(self, *args):
        self.settings.Show()

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


class SettingsWindow(Window):
    MinFontSize = 5
    MaxFontSize = 100

    def __init__(self, overlay: OverlayWindow):
        self.overlay = overlay

        self.window = XamlReader.Load(XmlReader.Create(StringReader(SettingsXaml)))
        self.InitializeComponent()
        self.Loading()

    def InitializeComponent(self):
        self.window.Closing += self.FormClosing

        self.num_regex = System.Text.RegularExpressions.Regex("[^0-9]+")

        self.fonts_list = LogicalTreeHelper.FindLogicalNode(self.window, "FontsList")
        self.fonts_list.SelectionChanged += self.FontSelected

        self.fonts_size = LogicalTreeHelper.FindLogicalNode(self.window, "FontSize")
        self.fonts_size.PreviewKeyDown += self.KeyDownFontSize
        self.fonts_size.KeyDown += self.KeyDownFontSize
        System.Windows.DataObject.AddPastingHandler(
            self.fonts_size, System.Windows.DataObjectPastingEventHandler(self.PasteFontSize)
        )

        self.font_size_up = LogicalTreeHelper.FindLogicalNode(self.window, "FontSizeUp")
        self.font_size_up.Click += lambda sender, e: self.FontSizeUp()

        self.font_size_down = LogicalTreeHelper.FindLogicalNode(self.window, "FontSizeDown")
        self.font_size_down.Click += lambda sender, e: self.FontSizeDown()

        self.font_weight = LogicalTreeHelper.FindLogicalNode(self.window, "FontWeight")
        self.font_weight.SelectionChanged += self.FontWeightelected

        self.text_color = LogicalTreeHelper.FindLogicalNode(self.window, "TextColor")
        self.text_color.Click += self.SetTextColor

        self.bg_color = LogicalTreeHelper.FindLogicalNode(self.window, "BackgroundColor")
        self.bg_color.Click += self.SetBackgroundColor

        self.bg_tranparent = LogicalTreeHelper.FindLogicalNode(self.window, "BackgroundTranparent")
        self.bg_tranparent.Click += self.SetBackgroundTransparent

        self.servers = LogicalTreeHelper.FindLogicalNode(self.window, "Servers")
        self.servers.SelectionChanged += self.ServerSelected

    def Loading(self):
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

        self.text_color.Background = self.overlay.GetTextColor()
        self.bg_color.Background = BrushFromHex("#FF" + str(self.overlay.GetBackgroundColor())[3:])
        self.bg_tranparent.IsChecked = str(self.overlay.GetBackgroundColor()).startswith("#00")

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
        if e.Key == 24:
            self.FontSizeUp()

        elif e.Key == 26:
            self.FontSizeDown()
        
        e.Handled = True

    def FontSizeUp(self):
        if self.fonts_size.Text.strip() == "":
            self.fonts_size.Text = f"{self.MinFontSize}"

        text_size = int(self.fonts_size.Text)
        if text_size < self.MaxFontSize:
            self.fonts_size.Text = str(text_size+1)
            self.CommitFontSize()

    def FontSizeDown(self):
        if self.fonts_size.Text.strip() == "":
            self.fonts_size.Text = f"{self.MinFontSize}"

        text_size = int(self.fonts_size.Text)
        if text_size > self.MinFontSize:
            self.fonts_size.Text = str(text_size-1)
            self.CommitFontSize()

    def CommitFontSize(self, size=None):
        if size is None:
            self.overlay.SetFontSize(int(self.fonts_size.Text))
        else:
            self.overlay.SetFontSize(size)

    # Font style
    def FontWeightelected(self, sender, e):
        self.overlay.SetFontWeight(self.font_weight.SelectedItem)

    # Colors
    def SetTextColor(self, sender, e):
        color = ColorDialog()
        if color is not None:
            self.text_color.Background = color
            self.overlay.SetTextColor(color)

    def SetBackgroundColor(self, sender, e):
        color = ColorDialog(0 if self.bg_tranparent.IsChecked else 255)
        if color is not None:
            self.bg_color.Background = BrushFromHex("#FF" + str(color)[3:])
            self.overlay.SetBackgroundColor(color)

    def SetBackgroundTransparent(self, sender, e):
        color_hex = str(self.overlay.GetBackgroundColor())

        if self.bg_tranparent.IsChecked:
            color_hex = f"#00{color_hex[3:]}"
        else:
            color_hex = f"#FF{color_hex[3:]}"

        self.overlay.SetBackgroundColor(BrushFromHex(color_hex))

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


if __name__ == '__main__':
    thread = Thread(ThreadStart(OverlayWindow))
    thread.SetApartmentState(ApartmentState.STA)
    thread.Start()
    thread.Join()
