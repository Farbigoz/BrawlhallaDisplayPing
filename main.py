import os
import re
import time
import math
import tkinter
import threading

from package.ping3 import ping


SERVERS = {
    "us-e": "pingtest-atl.brawlhalla.com",
    "us-w": "pingtest-cal.brawlhalla.com",
    "eu": "pingtest-ams.brawlhalla.com",
    "sea": "pingtest-sgp.brawlhalla.com",
    "aus": "pingtest-aus.brawlhalla.com",
    "brz": "pingtest-brs.brawlhalla.com",
    "jpn": "pingtest-jpn.brawlhalla.com",
}

CONFIG = {
    "text_color": "#000000",
    "background_color": "#eeeeee",
    "server": "eu"
}

# Loading config file
if os.path.exists("config.cfg"):
    with open("config.cfg", "r", encoding="UTF-8") as cfg:
        cfg_content = cfg.read()
        #[#0-9A-Fa-f]*

        for i in re.findall(r"\n([^ ]*) *= *([^ ]*);\n?", cfg_content):
            if i[0] in CONFIG:

                # Check hex color
                if "color" in i[0]:
                    if not re.findall(r"#[0-9A-Fa-f]{6}", i[1]):
                        continue

                CONFIG[i[0]] = i[1]


class App(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)

        self.label = tkinter.Label(self, text="0ms", font="font.ttf", 
                                   fg=CONFIG["text_color"], bg=CONFIG["background_color"])
        self.label.config(height=1, width=6)
        self.label.pack(side="right", fill="both", expand=True)

        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<ButtonRelease-1>", self.stop_move)
        self.label.bind("<B1-Motion>", self.on_motion)

        threading.Thread(target=self.ping_updater).start()

    def ping_updater(self):
        print("Server:", CONFIG["server"])
        server = SERVERS.get(CONFIG["server"], "eu")

        avg_ping = ping(server, timeout=1, unit="ms")

        while True:
            result_ping = ping(server, timeout=1, unit="ms")
            
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


app=App()
app.mainloop()