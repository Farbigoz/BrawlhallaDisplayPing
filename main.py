import os
import sys
import time
import math
import pkgutil
import tkinter
import threading

import tkinter.ttk
import tkinter.font
import tkinter.colorchooser

from sys import platform

import encodings.idna

from package.ping3 import ping
from package.config import ConfigFile, ConfigElement

FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20

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
LOCAL_DATA_PATH = ""

if platform in ["win32", "win64"]:
    LOCAL_DATA_PATH = os.path.join(os.getenv("APPDATA"), LOCAL_DATA_FOLDER)

    if LOCAL_DATA_FOLDER not in os.listdir(os.getenv("APPDATA")):
        os.mkdir(LOCAL_DATA_PATH)

elif platform == "darwin":
    LOCAL_DATA_PATH = os.path.join(os.getcwd(), "appconfig")

    if "appconfig" not in os.listdir(os.getcwd()):
        os.mkdir(LOCAL_DATA_PATH)


class ConfigMap(ConfigFile):
    text_color = ConfigElement(default="#000000")
    background_color = ConfigElement(default="#eeeeee")
    background_transparent = ConfigElement(default=False)
    font_name = ConfigElement(default="System")
    font_size = ConfigElement(default="12")
    server = ConfigElement(default="eu")
    alpha = ConfigElement(default=0)


CONFIG = ConfigMap(os.path.join(LOCAL_DATA_PATH, "settings.cfg"))


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class App(tkinter.Tk):
    transp_color = '#010203'

    def __init__(self):
        self.app_run = True

        tkinter.Tk.__init__(self)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)

        self.wm_attributes('-transparentcolor', self.transp_color)
        self.wm_attributes('-alpha', 1 - (CONFIG.alpha / 100))

        self.font_name = CONFIG.font_name
        self.font_size = CONFIG.font_size
        self.text_color = CONFIG.text_color
        self.background_color = CONFIG.background_color
        self.background_transparent = CONFIG.background_transparent

        if self.background_transparent:
            bg_color = self.transp_color
        else:
            bg_color = self.background_color

        self.label = tkinter.Label(self, text="160ms", font=(self.font_name, self.font_size),
                                   fg=self.text_color, bg=bg_color)
        self.label.config(height=1, width=6)
        self.label.pack(side="right", fill="both", expand=True)

        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<ButtonRelease-1>", self.stop_move)
        self.label.bind("<B1-Motion>", self.on_motion)

        self.label.bind("<Button-3>", self.do_popup)

        self.transparent_bg_val = tkinter.BooleanVar(value=self.background_transparent)

        self.menu = tkinter.Menu(self, tearoff=0)
        self.menu_servers = tkinter.Menu(self, tearoff=1)
        self.menu.add_command(label="Select font", command=self.select_font_window)
        self.menu.add_command(label="Set text color", command=self.select_text_color)
        self.menu.add_command(label="Set background color", command=self.select_bg_color)
        self.menu.add_command(label="Set widget transparent", command=self.select_alpha_window)
        self.menu.add_checkbutton(label="Transparent background", command=self.select_transparent_bg,
                                  onvalue=1, offvalue=0, variable=self.transparent_bg_val)
        self.menu.add_separator()
        self.menu.add_cascade(label="Set server", menu=self.menu_servers)
        self.menu.add_separator()
        self.menu.add_command(label="Close", command=self.stop_app)

        self._server = tkinter.StringVar(self, CONFIG.server)

        for server in SERVERS.keys():
            self.menu_servers.add_radiobutton(label=server, value=server, command=self.server_selected,
                                              variable=self._server)

        threading.Thread(target=self.ping_updater).start()

    def server_selected(self):
        CONFIG.server = self._server.get()
        print(f"Server: {CONFIG.server}")

    # Select colors
    def select_text_color(self):
        color_code = tkinter.colorchooser.askcolor(title="Choose text color")
        hex_color = color_code[1]

        if hex_color is not None:
            self.text_color = hex_color
            CONFIG.text_color = self.text_color
            self.label.config(fg=self.text_color)

    def select_bg_color(self):
        color_code = tkinter.colorchooser.askcolor(title="Choose background color")
        hex_color = color_code[1]

        if hex_color is not None:
            self.background_color = hex_color
            CONFIG.background_color = self.background_color
            self.label.config(bg=self.background_color)

            self.select_transparent_bg()

    def select_transparent_bg(self):
        if self.transparent_bg_val.get():
            self.background_transparent = True
            CONFIG.background_transparent = True
            # self.label.config(bg=self.transp_color)
            self.wm_attributes('-transparentcolor', self.background_color)
        else:
            self.background_transparent = False
            CONFIG.background_transparent = False
            # self.label.config(bg=self.background_color)
            self.wm_attributes('-transparentcolor', self.transp_color)

    # Select alpha window
    def select_alpha_window(self):
        window = tkinter.Tk()
        window.iconbitmap(resource_path("icon.ico"))
        window.wm_title("Set alpha")
        window.geometry("250x30")
        # window.resizable(0, 0)

        # Font size
        var = tkinter.StringVar(window)
        var.set(str(CONFIG.alpha))

        validate_num = (window.register(lambda s, S: self.num_validate(window, s, S)), '%s', '%S')

        alpha_size = tkinter.Spinbox(window, from_=0, to=50, width=300, validate="all",
                                     validatecommand=validate_num, command=lambda: self.alpha_selected(alpha_size),
                                     textvariable=var)
        alpha_size.pack(side=tkinter.BOTTOM, fill=tkinter.X)

    def alpha_selected(self, alpha_size: tkinter.Spinbox):
        alpha_size_: str = alpha_size.get()
        if alpha_size_ != "" and alpha_size_.isdigit() and (50 >= int(alpha_size_) >= 0):
            CONFIG.alpha = int(alpha_size_)
            self.wm_attributes('-alpha', 1 - (CONFIG.alpha / 100))

    # Select font window
    def select_font_window(self):
        window = tkinter.Tk()
        window.iconbitmap(resource_path("icon.ico"))
        window.wm_title("Set font")
        window.geometry("300x500")
        # window.resizable(0, 0)

        # Font size
        var = tkinter.StringVar(window)
        var.set(str(self.font_size))

        validate_num = (window.register(lambda s, S: self.num_validate(window, s, S)), '%s', '%S')

        font_size = tkinter.Spinbox(window, from_=5, to=40, width=300, validate="all", validatecommand=validate_num,
                                    command=lambda: self.font_size_selected(font_size), textvariable=var, )
        font_size.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        # Fonts list
        scrollbar = tkinter.Scrollbar(window)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        font_list = tkinter.Listbox(window, yscrollcommand=scrollbar.set, width=300 - 17)
        for font in tkinter.font.families(window):
            font_list.insert(tkinter.END, font)

        font_list.pack(side=tkinter.LEFT, fill=tkinter.Y)
        scrollbar.config(command=font_list.yview)

        font_list.bind('<<ListboxSelect>>', lambda _: self.font_selected(font_list))

    def font_selected(self, font_list: tkinter.Listbox):
        self.font_name = str(font_list.get(font_list.curselection()))
        CONFIG.font_name = self.font_name
        self.label.config(font=(self.font_name, self.font_size))

    def font_size_selected(self, font_size: tkinter.Spinbox):
        font_size_: str = font_size.get()
        if font_size_ != "" and font_size_.isdigit() and (40 >= int(font_size_) >= 5):
            self.font_size = font_size_
            CONFIG.font_size = self.font_size
            self.label.config(font=(self.font_name, self.font_size))

    # Popup actions
    def do_popup(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    # Ping updater
    def ping_updater(self):
        print("Server:", CONFIG["server"])

        avg_ping = 0

        while self.app_run:
            result_ping = ping(SERVERS.get(self._server.get(), "eu"), timeout=1, unit="ms")

            if result_ping is None:
                result_ping = -1
            else:
                result_ping = math.trunc(result_ping)

            self.label.config(text=f"{result_ping}ms")

            if result_ping >= 0:
                avg_ping = (result_ping + avg_ping) / 2
                print(f"Ping: {result_ping}ms \t|\tAvg ping: {math.trunc(avg_ping)}ms")
            else:
                print("Lost package")

            time.sleep(1)

        sys.exit(0)

    # Move widget
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    # Validator
    def num_validate(self, root, s, S):
        # disallow anything but numbers
        valid = S == '' or S.isdigit()
        if not valid:
            root.bell()
        return valid

    # Stop app
    def stop_app(self):
        self.destroy()
        self.app_run = False


app = App()
app.mainloop()
