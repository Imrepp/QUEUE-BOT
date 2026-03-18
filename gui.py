"""
gui.py — QUEUE BOT
Live log panel built into the main window.
Bot reads Discord embeds for queue detection.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import asyncio
import os
import sys
import bot as bot_module
from bot import QueueBot, play_sound
from logger import setup_logger

logger = setup_logger()
# Base directory — works both as .py script and PyInstaller .exe
import pathlib, sys
if getattr(sys, "frozen", False):
    BASE_DIR = pathlib.Path(sys.executable).parent.resolve()
else:
    BASE_DIR = pathlib.Path(__file__).parent.resolve()

CONFIG_PATH = str(BASE_DIR / "config.json")
PREFS_PATH  = str(BASE_DIR / "prefs.json")
LOGO_PATH   = str(BASE_DIR / "logo.png")
ICO_PATH    = str(BASE_DIR / "queue_bot.ico")

BG      = "#050d1a"
SURFACE = "#0a1628"
CARD    = "#0d1f35"
BORDER  = "#1a3a5c"
GREEN   = "#00e676"
GREEN_DK= "#00b359"
YELLOW  = "#ffd740"
RED     = "#ff5252"
BLUE    = "#448aff"
PINK    = "#ff80ab"
PURPLE  = "#b388ff"
TEXT    = "#eaeaf0"
MUTED   = "#6b6b8a"
FONT_H  = ("Segoe UI", 13, "bold")
FONT_B  = ("Segoe UI", 9,  "bold")
FONT_N  = ("Segoe UI", 9)
FONT_S  = ("Segoe UI", 8)
MONO    = ("Consolas", 8)
MONO_S  = ("Consolas", 9)

def apply_styles():
    """Apply custom ttk styles for scrollbars and other widgets."""
    style = ttk.Style()
    style.theme_use("clam")
    # Custom dark scrollbar
    style.configure("Dark.Vertical.TScrollbar",
                    background=BORDER, troughcolor=SURFACE,
                    bordercolor=SURFACE, arrowcolor=MUTED,
                    relief="flat", borderwidth=0)
    style.map("Dark.Vertical.TScrollbar",
              background=[("active", BLUE), ("pressed", BLUE)])
    style.configure("Dark.Horizontal.TScrollbar",
                    background=BORDER, troughcolor=SURFACE,
                    bordercolor=SURFACE, arrowcolor=MUTED,
                    relief="flat", borderwidth=0)
    style.map("Dark.Horizontal.TScrollbar",
              background=[("active", BLUE), ("pressed", BLUE)])
    # Custom separator
    style.configure("TSeparator", background=BORDER)


DEFAULT_CONFIG = '{\n    "token": "YOUR_TOKEN_HERE",\n    "leave_threshold": 10,\n    "click_delay": 0.5,\n    "servers": [\n        {\n            "name": "Sword",\n            "group": "pvptiers",\n            "queue_bot_id": 1328378417145446440,\n            "guild_id": 513709294844117013,\n            "queue_channel_id": 984399122775814154,\n            "commands_channel_id": 721746883608969216,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Axe",\n            "group": "pvptiers",\n            "queue_bot_id": 1328378417145446440,\n            "guild_id": 896903597709754398,\n            "queue_channel_id": 1060545718936404068,\n            "commands_channel_id": 940156911523856394,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "UHC",\n            "group": "pvptiers",\n            "queue_bot_id": 1328378417145446440,\n            "guild_id": 860880412975824898,\n            "queue_channel_id": 1012662259966808104,\n            "commands_channel_id": 860881608391655424,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Netherite Pot",\n            "group": "pvptiers",\n            "queue_bot_id": 1328378417145446440,\n            "guild_id": 875309328607899658,\n            "queue_channel_id": 1005941369862377502,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Diamond Pot",\n            "group": "pvptiers",\n            "queue_bot_id": 1328378417145446440,\n            "guild_id": 1007038689412665404,\n            "queue_channel_id": 1129786993962930256,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "SMP",\n            "group": "pvptiers",\n            "queue_bot_id": 1328378417145446440,\n            "guild_id": 981948043903533176,\n            "queue_channel_id": 1059958041186947072,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Crystal",\n            "group": "pvptiers",\n            "queue_bot_id": 1328378417145446440,\n            "guild_id": 1333178700883034269,\n            "queue_channel_id": 1333182357674655774,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Mace",\n            "group": "pvptiers",\n            "queue_bot_id": 1328378417145446440,\n            "guild_id": 1345939343448997908,\n            "queue_channel_id": 1395704403230720060,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Diamond Pot",\n            "group": "mctiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1317971630886227998,\n            "queue_channel_id": 1317974027922309131,\n            "commands_channel_id": 1317974024936100070,\n            "auto_join": true,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Netherite Pot",\n            "group": "mctiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 987654321098765432,\n            "queue_channel_id": 1317971632484126789,\n            "commands_channel_id": 1317971631490076748,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Sword",\n            "group": "mctiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1317975081976332338,\n            "queue_channel_id": 1317975085470187621,\n            "commands_channel_id": 1317975082890428530,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Axe",\n            "group": "mctiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1317974470132240424,\n            "queue_channel_id": 1317974473617707091,\n            "commands_channel_id": 1317974471793184798,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "UHC",\n            "group": "mctiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1316948661384646767,\n            "queue_channel_id": 1316948663095791621,\n            "commands_channel_id": 1316948662043021314,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "SMP",\n            "group": "mctiers",\n            "queue_bot_id": 1124128173609713734,\n            "guild_id": 1224245679749206050,\n            "queue_channel_id": 1224245683129815060,\n            "commands_channel_id": 1224245680646787147,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Mace",\n            "group": "mctiers",\n            "queue_bot_id": 1124128173609713734,\n            "guild_id": 1187058381849112606,\n            "queue_channel_id": 1306852692152422491,\n            "commands_channel_id": 1224397572639293480,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Crystal",\n            "group": "mctiers",\n            "queue_bot_id": 1124128173609713734,\n            "guild_id": 898743810207653919,\n            "queue_channel_id": 965410638530744381,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Speed",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1158750236689305670,\n            "queue_channel_id": 1306882989904494663,\n            "commands_channel_id": 1251279352436621354,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "OGV",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1217042808607608872,\n            "queue_channel_id": 1217898287491715193,\n            "commands_channel_id": 1217754816000950292,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Diamond SMP",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1257127206790889552,\n            "queue_channel_id": 1306861081079058502,\n            "commands_channel_id": 1257280576063410196,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Cart",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1052301884028883005,\n            "queue_channel_id": 1313223001701093417,\n            "commands_channel_id": 1316123120532455477,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Bow",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1046087157447671960,\n            "queue_channel_id": 1313209691253374996,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Diamond Crystal",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1130550476379803718,\n            "queue_channel_id": 1329892733678129172,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Elytra",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1033857757578801182,\n            "queue_channel_id": 1215727875605663836,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Trident",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1157140514420826134,\n            "queue_channel_id": 1346586243185643590,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Manhunt",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1166030453011128341,\n            "queue_channel_id": 1306888453895753738,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Bed",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1244860811843862639,\n            "queue_channel_id": 1313216656683827221,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Creeper",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1232098988925386823,\n            "queue_channel_id": 1306913286503010314,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Debuff",\n            "group": "subtiers",\n            "queue_bot_id": 1308417680361000970,\n            "guild_id": 1149904523398225921,\n            "queue_channel_id": 1306874524855435306,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "queue_open_keywords": [\n                "Tester(s) Available",\n                "Available!"\n            ],\n            "queue_closed_keywords": [\n                "Not Available",\n                "Closed",\n                "Unavailable"\n            ]\n        },\n        {\n            "name": "Stray",\n            "group": "hungergames",\n            "queue_bot_id": 1472734607756759090,\n            "guild_id": 874911656721907763,\n            "queue_channel_id": 1448387796707442791,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "stray_mode": true,\n            "queue_open_keywords": [],\n            "queue_closed_keywords": []\n        },\n        {\n            "name": "Wheel Survival",\n            "group": "hungergames",\n            "queue_bot_id": 0,\n            "guild_id": 1347308374412365997,\n            "queue_channel_id": 1364706882312212490,\n            "commands_channel_id": 0,\n            "auto_join": false,\n            "stray_mode": true,\n            "any_bot": true,\n            "queue_open_keywords": [],\n            "queue_closed_keywords": []\n        }\n    ]\n}'

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        # Auto-create default config so the .exe works standalone
        with open(CONFIG_PATH, "w") as f:
            f.write(DEFAULT_CONFIG)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def load_prefs() -> dict:
    if os.path.exists(PREFS_PATH):
        with open(PREFS_PATH, "r") as f:
            return json.load(f)
    return {}

def save_prefs(prefs: dict):
    with open(PREFS_PATH, "w") as f:
        json.dump(prefs, f, indent=2)


# ── Warning popup ──────────────────────────────────────────────────────────

class WarningPopup(tk.Toplevel):
    def __init__(self, parent, server_name, position, on_leave):
        super().__init__(parent)
        self.title("Queue Warning")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.attributes("-topmost", True)
        try:
            self.iconbitmap(ICO_PATH)
        except Exception:
            pass
        self._on_leave = on_leave
        self._build(server_name, position)
        self.update_idletasks()
        pw, ph = 400, 210
        px = parent.winfo_x() + parent.winfo_width()  // 2 - pw // 2
        py = parent.winfo_y() + parent.winfo_height() // 2 - ph // 2
        self.geometry(f"{pw}x{ph}+{px}+{py}")
        self.after(30000, self._stay)

    def _build(self, server_name, position):
        tk.Frame(self, bg=YELLOW, height=3).pack(fill="x")
        tk.Label(self, text="⚠  QUEUE WARNING",
                 font=("Segoe UI", 12, "bold"), fg=YELLOW, bg=BG).pack(pady=(16, 3))
        tk.Label(self, text=f"#{position} in queue  —  {server_name}",
                 font=FONT_N, fg=TEXT, bg=BG).pack()
        tk.Label(self, text="Are you sure you want to stay in queue this quickly?",
                 font=FONT_S, fg=MUTED, bg=BG, wraplength=340).pack(pady=(4, 16))
        row = tk.Frame(self, bg=BG)
        row.pack()
        tk.Button(row, text="✓  STAY", font=FONT_B, fg="#000", bg=GREEN,
                  activebackground=GREEN_DK, relief="flat", padx=16, pady=7,
                  cursor="hand2", command=self._stay).pack(side="left", padx=6)
        tk.Button(row, text="✕  LEAVE", font=FONT_B, fg=TEXT, bg=RED,
                  activebackground="#cc3344", relief="flat", padx=16, pady=7,
                  cursor="hand2", command=self._leave).pack(side="left", padx=6)
        tk.Label(self, text="Auto-stays in 30s if no action",
                 font=("Segoe UI", 7), fg="#333355", bg=BG).pack(pady=(10, 0))

    def _stay(self):
        try: self.destroy()
        except: pass

    def _leave(self):
        self._on_leave()
        try: self.destroy()
        except: pass


# ── Main window ────────────────────────────────────────────────────────────

class App(tk.Tk):

    PAUSE_DURATION = 60

    def __init__(self):
        super().__init__()
        self.title("QUEUE BOT")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(620, 560)
        apply_styles()

        self.config_data  = load_config()

        # If token is missing or placeholder, show setup screen first
        if not self.config_data.get("token") or self.config_data["token"] in ("", "YOUR_TOKEN_HERE"):
            self._show_token_setup()
        else:
            self._finish_init()

    # ── Token setup screen ────────────────────────────────────────────

    def _show_token_setup(self):
        """Full-screen token entry shown when no token is set."""
        self.title("QUEUE BOT — Setup")
        try:
            self.iconbitmap(ICO_PATH)
        except Exception:
            pass
        self.configure(bg=BG)
        self.resizable(False, False)
        self._center(500, 420)

        tk.Frame(self, bg=GREEN, height=3).pack(fill="x")

        # Show logo
        try:
            from PIL import Image, ImageTk
            img = Image.open(LOGO_PATH).convert("RGBA").resize((64, 64), Image.LANCZOS)
            self._setup_logo = ImageTk.PhotoImage(img)
            tk.Label(self, image=self._setup_logo, bg=BG).pack(pady=(20, 0))
        except Exception:
            tk.Label(self, text="🎮", font=("Segoe UI", 40), bg=BG).pack(pady=(20, 0))

        tk.Label(self, text="QUEUE BOT", font=("Segoe UI", 20, "bold"),
                 fg=TEXT, bg=BG).pack(pady=(8, 4))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=40, pady=(0, 12))

        # Region selector
        tk.Label(self, text="Select Your Region",
                 font=FONT_B, fg=TEXT, bg=BG).pack()
        tk.Label(self, text="This sets which queue channels the bot watches.",
                 font=("Segoe UI", 8), fg=MUTED, bg=BG).pack(pady=(2, 10))

        region_frame = tk.Frame(self, bg=BG)
        region_frame.pack()

        self._setup_region      = tk.StringVar(value="EU")
        self._setup_region_btns = {}

        for region, color in [("🌍  EU", "EU"), ("🌎  NA", "NA")]:
            is_selected = (color == "EU")
            rb = tk.Button(region_frame, text=region,
                           font=("Segoe UI", 10, "bold"),
                           fg="#000" if is_selected else TEXT,
                           bg=GREEN if is_selected else BORDER,
                           activebackground=GREEN_DK, relief="flat",
                           padx=24, pady=8, cursor="hand2",
                           command=lambda r=color: self._select_setup_region(r))
            rb.pack(side="left", padx=8)
            self._setup_region_btns[color] = rb

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=40, pady=(12, 0))

        tk.Label(self, text="Enter your Discord Token",
                 font=FONT_B, fg=TEXT, bg=BG).pack(pady=(12, 0))
        tk.Label(self,
                 text="Open Discord in browser -> F12 -> Network tab -> send a message\n-> click the request -> Headers -> copy Authorization value",
                 font=("Segoe UI", 8), fg=MUTED, bg=BG, justify="center").pack(pady=(4, 12))

        token_frame = tk.Frame(self, bg=BG)
        token_frame.pack(padx=40, fill="x")

        self._token_var = tk.StringVar()
        token_entry = tk.Entry(token_frame, textvariable=self._token_var,
                               font=("Consolas", 9), bg=CARD, fg=TEXT,
                               insertbackground=TEXT, relief="flat",
                               highlightthickness=1, highlightbackground=BORDER,
                               highlightcolor=GREEN, show="*", width=50)
        token_entry.pack(fill="x", ipady=8, padx=2)

        def on_token_change(*args):
            has_token = bool(self._token_var.get().strip())
            btns = getattr(self, "_setup_region_btns", {})
            for rgn, rb in btns.items():
                if has_token:
                    rb.config(cursor="arrow", command=lambda: None)
                else:
                    rb.config(cursor="hand2",
                              command=lambda r=rgn: self._select_setup_region(r))
        self._token_var.trace_add("write", on_token_change)

        # Show/hide toggle
        show_var = tk.BooleanVar(value=False)
        def toggle_show():
            token_entry.config(show="" if show_var.get() else "*")
        tk.Checkbutton(token_frame, text="Show token", variable=show_var,
                       font=FONT_S, fg=MUTED, bg=BG, activebackground=BG,
                       selectcolor=SURFACE, cursor="hand2",
                       command=toggle_show).pack(anchor="w", pady=(4, 0))

        self._setup_error = tk.Label(self, text="", font=FONT_S, fg=RED, bg=BG)
        self._setup_error.pack(pady=(8, 0))

        tk.Button(self, text="✓  Save & Start",
                  font=FONT_B, fg="#000", bg=GREEN,
                  activebackground=GREEN_DK, relief="flat",
                  padx=24, pady=9, cursor="hand2",
                  command=self._save_token).pack(pady=16)

        tk.Label(self, text="Your token is stored locally in config.json only.",
                 font=("Segoe UI", 7), fg="#222238", bg=BG).pack()

        token_entry.focus_set()
        # Allow pressing Enter to submit
        token_entry.bind("<Return>", lambda e: self._save_token())

    def _select_setup_region(self, region: str):
        self._setup_region.set(region)
        for r, btn in self._setup_region_btns.items():
            btn.config(bg=GREEN if r == region else BORDER,
                       fg="#000" if r == region else TEXT)

    def _save_token(self):
        token = self._token_var.get().strip()
        if not token:
            self._setup_error.config(text="Please enter your token!")
            return
        if len(token) < 50:
            self._setup_error.config(text="That doesn't look like a valid token.")
            return

        # Save to config.json
        self.config_data["token"] = token
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config_data, f, indent=4)

        # Save selected region
        region = getattr(self, "_setup_region", tk.StringVar(value="EU")).get()
        prefs = load_prefs()
        prefs["region"] = region
        # Apply region channel IDs
        for s in self.config_data["servers"]:
            eu = s.get("queue_channel_id_eu")
            na = s.get("queue_channel_id_na")
            if eu and na:
                s["queue_channel_id"] = eu if region == "EU" else na
        save_prefs(prefs)

        # Destroy setup screen and rebuild as main app
        for widget in self.winfo_children():
            widget.destroy()
        self.resizable(True, True)
        self.title("QUEUE BOT")
        self._finish_init()

    def _load_icon(self):
        """Load the app icon."""
        try:
            self.iconbitmap(ICO_PATH)
        except Exception:
            pass

    def _finish_init(self):
        """Called after token is confirmed — completes initialization."""
        self._load_icon()
        self.prefs        = load_prefs()
        self.check_vars   = {}
        self.label_refs   = {}
        self.label_vars   = {}
        self.ls_vars:     dict[int, tk.StringVar] = {}  # last seen per guild_id
        self.status_dots: dict[int, tk.Label]     = {}  # queue open/closed dot per guild_id
        self._active_bot  = None
        self._bot_thread  = None
        self._paused      = False
        self._pause_timer = None
        self._countdown   = 0

        bot_module.warn_callback      = self._show_warning
        bot_module.gui_log_callback   = self._append_log
        bot_module.notify_callback    = self._notify
        bot_module.last_seen_callback    = self._update_last_seen
        bot_module.status_dot_callback  = self._set_status_dot
        bot_module.joined_callback       = self._on_queue_joined
        bot_module.accept_callback       = self._show_accept_timer

        # Load saved custom sound
        prefs = load_prefs()
        if "custom_sound" in prefs and os.path.exists(prefs["custom_sound"]):
            bot_module.custom_sound_path = prefs["custom_sound"]

        # Load saved volume
        if "volume" in prefs:
            bot_module.sound_volume = prefs["volume"] / 100.0

        # Load saved region and apply channel IDs
        saved_region = prefs.get("region", "EU")
        self._region = tk.StringVar(value=saved_region)
        for s in self.config_data["servers"]:
            eu = s.get("queue_channel_id_eu")
            na = s.get("queue_channel_id_na")
            if eu and na:
                s["queue_channel_id"] = eu if saved_region == "EU" else na

        # Set window icon
        try:
            self.iconbitmap(ICO_PATH)
        except Exception:
            pass

        self._build_ui()
        self._center(820, 680)
        # System tray: install pystray and uncomment to enable
        # self.bind("<Unmap>", self._on_minimize)
        self.after(300, self._launch_bot)

    # ── UI ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        topbar = tk.Frame(self, bg=SURFACE, pady=10)
        topbar.pack(fill="x")
        tk.Frame(topbar, bg=GREEN, width=4).pack(side="left", fill="y", padx=(0, 12))

        # Logo in top bar
        try:
            from PIL import Image, ImageTk
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
            if os.path.exists(icon_path):
                img = Image.open(icon_path).resize((36, 36), Image.LANCZOS)
                self._topbar_logo = ImageTk.PhotoImage(img)
                tk.Label(topbar, image=self._topbar_logo, bg=SURFACE).pack(side="left", padx=(0, 8))
        except Exception:
            pass

        left = tk.Frame(topbar, bg=SURFACE)
        left.pack(side="left", fill="y")
        # Logo + title row
        title_row = tk.Frame(left, bg=SURFACE)
        title_row.pack(anchor="w")
        try:
            from PIL import Image, ImageTk
            img = Image.open(LOGO_PATH).convert("RGBA").resize((28, 28))
            self._logo_img = ImageTk.PhotoImage(img)
            tk.Label(title_row, image=self._logo_img, bg=SURFACE).pack(side="left", padx=(0, 8))
        except Exception:
            pass
        tk.Label(title_row, text="QUEUE BOT", font=("Segoe UI", 14, "bold"),
                 fg=TEXT, bg=SURFACE).pack(side="left")
        tk.Label(left, text="Pings Minecraft ranked server's across Discord",
                 font=FONT_S, fg=MUTED, bg=SURFACE).pack(anchor="w")
        right = tk.Frame(topbar, bg=SURFACE)
        right.pack(side="right", padx=16)
        self.status_dot = tk.Label(right, text="●", font=("Segoe UI", 18), fg=MUTED, bg=SURFACE)
        self.status_dot.pack(side="left")
        self.status_lbl = tk.Label(right, text="Starting...", font=FONT_S, fg=MUTED, bg=SURFACE)
        self.status_lbl.pack(side="left", padx=(4, 0))

        # Toolbar row 1: Select + Filter buttons
        toolbar1 = tk.Frame(self, bg=BG, pady=4)
        toolbar1.pack(fill="x", padx=14)

        self._pill(toolbar1, "All",  self._select_all).pack(side="left", padx=(0, 4))
        self._pill(toolbar1, "None", self._select_none).pack(side="left", padx=(0, 10))

        tk.Frame(toolbar1, bg=BORDER, width=1).pack(side="left", fill="y", pady=2, padx=(0, 8))

        self._active_filter = tk.StringVar(value="all")
        self._filter_btns = {}
        groups = [("PVPTIERS", "pvptiers"), ("MCTIERS", "mctiers"),
                  ("SUBTIERS", "subtiers"), ("HUNGER GAMES", "hungergames")]
        for label, key in groups:
            btn = tk.Button(toolbar1, text=label, font=("Segoe UI", 8, "bold"),
                            fg=MUTED, bg=BG,
                            activebackground=BORDER, activeforeground=TEXT,
                            relief="flat", padx=9, pady=4, cursor="hand2",
                            command=lambda k=key: self._filter_group(k))
            btn.pack(side="left", padx=2)
            self._filter_btns[key] = btn

        self.after(100, lambda: self._filter_group("pvptiers"))
        self.after(150, lambda: self._set_region(self._region.get()))

        # Show current region as a static label (no clicking)
        tk.Frame(toolbar1, bg=BORDER, width=1).pack(side="left", fill="y", pady=2, padx=(8, 6))
        self._region_lbl_var = tk.StringVar(value="EU")
        tk.Label(toolbar1, textvariable=self._region_lbl_var,
                 font=("Segoe UI", 8, "bold"), fg=GREEN, bg=BG).pack(side="left")
        self.after(150, self._apply_region_label)

        # Toolbar row 2: Action buttons
        toolbar2 = tk.Frame(self, bg=BG, pady=2)
        toolbar2.pack(fill="x", padx=14)

        self._pill(toolbar2, "🔑  Token", self._show_token_change, fg=YELLOW).pack(side="left", padx=(0, 6))
        self._pill(toolbar2, "⚠  Disclaimer", self._show_disclaimer, fg=RED).pack(side="left", padx=(0, 6))
        self._pill(toolbar2, "🔊  Volume", self._show_volume, fg=PINK).pack(side="left", padx=(0, 6))
        self._pill(toolbar2, "⏱  Delay", self._show_startup_delay, fg=PURPLE).pack(side="left", padx=(0, 6))
        self._pill(toolbar2, "🌐  Website", self._open_group_website, fg=GREEN).pack(side="left", padx=(0, 6))
        self._pill(toolbar2, "?  How It Works", self._show_how_it_works, fg=BLUE).pack(side="left", padx=(0, 6))
        self.pause_btn = tk.Button(toolbar2, text="⏸  Pause 60s",
                                   font=FONT_B, fg=TEXT, bg=BORDER,
                                   activebackground="#3a3a55", activeforeground=TEXT,
                                   relief="flat", padx=12, pady=5, cursor="hand2",
                                   command=self._toggle_pause)
        self.pause_btn.pack(side="left")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(0, 4))

        self.count_lbl = tk.Label(self, text="", font=FONT_S, fg=MUTED, bg=BG)
        self.count_lbl.pack(anchor="w", padx=16, pady=(0, 4))
        self._refresh_count()

        # Main area: left = servers, right = live logs
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=14, pady=(0, 6))
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        # ── Left: server grid ───────────────────────────────────────────
        left_frame = tk.Frame(main, bg=BG)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        tk.Label(left_frame, text="SERVERS", font=("Segoe UI", 8, "bold"),
                 fg=MUTED, bg=BG).pack(anchor="w", pady=(0, 4))

        wrapper = tk.Frame(left_frame, bg=BG)
        wrapper.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(wrapper, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(wrapper, orient="vertical", style="Dark.Vertical.TScrollbar", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self.grid_frame = tk.Frame(self._canvas, bg=BG)
        self._cwin = self._canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cwin, width=e.width))
        def _on_grid_scroll(e):
            # Only scroll if canvas is scrollable (content taller than view)
            if self._canvas.yview() != (0.0, 1.0):
                self._canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        self._canvas.bind_all("<MouseWheel>", _on_grid_scroll)

        servers = self.config_data["servers"]
        for i, s in enumerate(servers):
            gid   = s["guild_id"]
            saved = self.prefs.get(str(gid), s.get("auto_join", False))
            var   = tk.BooleanVar(value=saved)
            self.check_vars[gid] = var
            self._make_card(s, var, i // 2, i % 2)

        self.grid_frame.columnconfigure(0, weight=1, uniform="c")
        self.grid_frame.columnconfigure(1, weight=1, uniform="c")

        # ── Right: live log panel ───────────────────────────────────────
        right_frame = tk.Frame(main, bg=BG)
        right_frame.grid(row=0, column=1, sticky="nsew")

        log_header = tk.Frame(right_frame, bg=BG)
        log_header.pack(fill="x", pady=(0, 4))
        tk.Label(log_header, text="LIVE LOGS", font=("Segoe UI", 8, "bold"),
                 fg=MUTED, bg=BG).pack(side="left")
        tk.Button(log_header, text="Clear", font=("Segoe UI", 7), fg=MUTED, bg=BORDER,
                  activebackground="#2a2a40", relief="flat", padx=6, pady=2,
                  cursor="hand2", command=self._clear_logs).pack(side="right")

        log_wrap = tk.Frame(right_frame, bg=CARD,
                            highlightthickness=1, highlightbackground=BORDER)
        log_wrap.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_wrap, bg=CARD, fg=TEXT,
                                font=MONO_S, relief="flat", wrap="word",
                                padx=8, pady=8, highlightthickness=0,
                                bd=0, cursor="arrow", state="disabled")
        log_sb = ttk.Scrollbar(log_wrap, orient="vertical", style="Dark.Vertical.TScrollbar", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_sb.set)
        log_sb.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        # When mouse is over log panel, redirect scroll to log only
        self.log_text.bind("<Enter>", lambda e: self.log_text.bind_all("<MouseWheel>",
            lambda ev: self.log_text.yview_scroll(int(-1*(ev.delta/120)), "units")))
        self.log_text.bind("<Leave>", lambda e: self._rebind_canvas_scroll())

        # Clear log file on startup
        self._clear_log_file()

        # Colour tags for log lines
        self.log_text.tag_config("green",  foreground=GREEN)
        self.log_text.tag_config("red",    foreground=RED)
        self.log_text.tag_config("yellow", foreground=YELLOW)
        self.log_text.tag_config("blue",   foreground=BLUE)
        self.log_text.tag_config("muted",  foreground=MUTED)
        self.log_text.tag_config("normal", foreground="#8888aa")

        # Footer
        tk.Label(self, text="Made by AI - CLAUDE  •  Credits to repp - Imreppofficial",
                 font=("Segoe UI", 7), fg="#222238", bg=BG).pack(pady=4)

    def _pill(self, parent, text, cmd, fg=MUTED):
        return tk.Button(parent, text=text, font=FONT_S, fg=fg, bg=BORDER,
                         activebackground="#2e2e48", activeforeground=fg,
                         relief="flat", padx=10, pady=5, cursor="hand2", command=cmd)

    def _make_card(self, server, var, row, col):
        gid  = server["guild_id"]
        name = server["name"]
        disp = name if len(name) <= 22 else name[:19] + "..."

        outer = tk.Frame(self.grid_frame, bg=BG, padx=3, pady=3)
        outer.grid(row=row, column=col, sticky="nsew")

        card = tk.Frame(outer, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="both", expand=True)

        bar = tk.Frame(card, width=3, bg=GREEN if var.get() else BORDER)
        bar.pack(side="left", fill="y")
        self.label_refs[gid] = bar

        inner = tk.Frame(card, bg=CARD, padx=8, pady=7)
        inner.pack(fill="both", expand=True)

        # Title row with status dot
        title_row = tk.Frame(inner, bg=CARD)
        title_row.pack(fill="x")
        dot = tk.Label(title_row, text="●", font=("Segoe UI", 8),
                       fg=MUTED, bg=CARD)
        dot.pack(side="left", padx=(0, 4))
        self.status_dots[gid] = dot
        tk.Label(title_row, text=disp, font=("Segoe UI", 8, "bold"),
                 fg=TEXT, bg=CARD, anchor="w").pack(side="left", fill="x", expand=True)



        btm = tk.Frame(inner, bg=CARD)
        btm.pack(fill="x", pady=(5, 0))

        is_stray = server.get("group", "") == "hungergames"
        on_label  = "AUTO-PING" if is_stray else "AUTO-JOIN"
        lv = tk.StringVar(value=on_label if var.get() else "LOG ONLY")
        self.label_vars[gid] = lv

        sl = tk.Label(btm, textvariable=lv, font=("Segoe UI", 7, "bold"),
                      fg=GREEN if var.get() else MUTED, bg=CARD)
        sl.pack(side="left")
        bar._sl  = sl
        bar._lv  = lv
        bar._var = var

        # Last seen label — only for queue servers, not hunger games
        if server.get("group", "") != "hungergames":
            ls_var = self.ls_vars.get(gid)
            if ls_var is None:
                ls_var = tk.StringVar(value="Last seen: Never")
                self.ls_vars[gid] = ls_var
            ls_lbl = tk.Label(inner, textvariable=ls_var, font=("Segoe UI", 7),
                              fg="#3a5a7a", bg=CARD, anchor="w")
            ls_lbl.pack(fill="x")
            bar._ls_var = ls_var

        def make_toggle(b=bar, s=sl, l=lv, v=var, ol=on_label):
            def toggle():
                on = v.get()
                l.set(ol if on else "LOG ONLY")
                s.config(fg=GREEN if on else MUTED)
                b.config(bg=GREEN if on else BORDER)
                self._refresh_count()
                self._save_and_update_bot()
            return toggle

        tk.Checkbutton(btm, variable=var, bg=CARD, activebackground=CARD,
                       selectcolor=GREEN, cursor="hand2",
                       command=make_toggle()).pack(side="right")

    # ── Live log panel ─────────────────────────────────────────────────

    def _rebind_canvas_scroll(self):
        """Restore mousewheel to scroll the server grid canvas."""
        def _on_grid_scroll(e):
            # Only scroll if canvas is scrollable (content taller than view)
            if self._canvas.yview() != (0.0, 1.0):
                self._canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        self._canvas.bind_all("<MouseWheel>", _on_grid_scroll)


    def _append_log(self, msg: str):
        """Called from bot thread — safely appends a line to the log panel."""
        def _do():
            import datetime
            ts  = datetime.datetime.now().strftime("%H:%M:%S")
            line = f"[{ts}] {msg}\n"

            tag = "normal"
            mu  = msg.upper()
            if "✅" in msg or "JOINED" in mu or "QUEUE OPEN" in mu:
                tag = "green"
            elif "🔴" in msg or "LEFT QUEUE" in mu or "AUTO-LEAV" in mu:
                tag = "red"
            elif "⚠" in msg or "WARNING" in mu:
                tag = "yellow"
            elif "❌" in msg or "ERROR" in mu or "CRASHED" in mu:
                tag = "red"
            elif "LOGGED IN" in mu or "WATCHING" in mu:
                tag = "blue"
            elif "LOG ONLY" in mu or "SKIPPING" in mu or "NO QUEUE" in mu:
                tag = "muted"

            self.log_text.config(state="normal")
            self.log_text.insert("end", line, tag)
            self.log_text.see("end")
            self.log_text.config(state="disabled")

            # Keep max 500 lines
            lines = int(self.log_text.index("end-1c").split(".")[0])
            if lines > 500:
                self.log_text.config(state="normal")
                self.log_text.delete("1.0", "50.0")
                self.log_text.config(state="disabled")

        self.after(0, _do)

    def _clear_logs(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def _clear_log_file(self):
        """Delete ALL log files on startup so logs are fresh each session."""
        import glob
        log_dir = str(BASE_DIR / "logs")
        if os.path.exists(log_dir):
            for f in glob.glob(os.path.join(log_dir, "*.log")):
                try:
                    os.remove(f)
                except Exception:
                    pass

    # ── Group filter ───────────────────────────────────────────────────

    def _filter_group(self, group: str):
        self._active_filter.set(group)

        # Update button highlight
        for key, btn in self._filter_btns.items():
            if key == group:
                btn.config(bg=BORDER, fg=GREEN if key == "hungergames" else TEXT)
            else:
                btn.config(bg=BG, fg=MUTED)
        self._active_filter.set(group)

        # Destroy and rebuild the grid with only matching servers
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        servers = self.config_data["servers"]
        visible = [s for s in servers if s.get("group", "") == group]

        col_idx = 0
        row_idx = 0
        for server in visible:
            gid = server["guild_id"]
            var = self.check_vars.get(gid)
            if var is None:
                continue
            self._make_card(server, var, row_idx, col_idx)
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

        self.grid_frame.columnconfigure(0, weight=1, uniform="c")
        self.grid_frame.columnconfigure(1, weight=1, uniform="c")
        self._canvas.yview_moveto(0)  # scroll back to top

    # ── Notifications ───────────────────────────────────────────────────

    def _notify(self, title: str, message: str):
        """Show Windows toast + play sound."""
        import threading
        def _do():
            try:
                from win10toast import ToastNotifier
                ToastNotifier().show_toast(title, message, duration=6, threaded=True)
            except Exception:
                try:
                    from winotify import Notification
                    Notification(app_id="QUEUE BOT", title=title, msg=message).show()
                except Exception:
                    pass
        threading.Thread(target=_do, daemon=True).start()

    # ── Select all / none ──────────────────────────────────────────────────

    def _select_all(self):
        # Only select servers visible in current filter
        current_group = self._active_filter.get()
        for s in self.config_data["servers"]:
            if current_group == "all" or s.get("group", "") == current_group:
                gid = s["guild_id"]
                if gid in self.check_vars:
                    self.check_vars[gid].set(True)
        self._filter_group(current_group)
        self._refresh_count()
        self._save_and_update_bot()

    def _select_none(self):
        # Only deselect servers visible in current filter
        current_group = self._active_filter.get()
        for s in self.config_data["servers"]:
            if current_group == "all" or s.get("group", "") == current_group:
                gid = s["guild_id"]
                if gid in self.check_vars:
                    self.check_vars[gid].set(False)
        self._filter_group(current_group)
        self._refresh_count()
        self._save_and_update_bot()

    def _refresh_card(self, gid, enabled):
        bar = self.label_refs.get(gid)
        if not bar: return
        bar._lv.set("AUTO-JOIN" if enabled else "LOG ONLY")
        bar._sl.config(fg=GREEN if enabled else MUTED)
        bar.config(bg=GREEN if enabled else BORDER)

    def _refresh_count(self):
        total   = len(self.check_vars)
        enabled = sum(1 for v in self.check_vars.values() if v.get())
        self.count_lbl.config(
            text=f"{total} servers  •  {enabled} auto-join  •  {total-enabled} log only")

    # ── Bot lifecycle ──────────────────────────────────────────────────

    def _get_enabled(self):
        return {gid for gid, var in self.check_vars.items() if var.get()}

    def _is_discord_running(self) -> bool:
        """Check if Discord is running as a process."""
        try:
            import subprocess
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Discord.exe"],
                capture_output=True, text=True, creationflags=0x08000000
            )
            return "Discord.exe" in result.stdout
        except Exception:
            return True  # If check fails, assume it's running

    def _launch_bot(self):
        if self._bot_thread and self._bot_thread.is_alive():
            return

        # Check if Discord is running
        if not self._is_discord_running():
            self._set_status("paused")
            self._append_log("⚠ Discord is not running! Please open Discord first.")
            self.after(5000, self._launch_bot)  # retry in 5s
            return

        enabled = self._get_enabled()
        self._set_status("running")

        prefs = load_prefs()
        delay = prefs.get("startup_delay", 0)

        def run():
            if delay > 0:
                self._append_log(f"⏱ Waiting {delay}s before connecting...")
                import time
                time.sleep(delay)
            b = QueueBot(self.config_data, enabled)
            self._active_bot = b
            try:
                b.run(self.config_data["token"])
            except Exception as e:
                logger.error(f"Bot crashed: {e}")
                self._append_log(f"❌ Bot crashed: {e}")
                self.after(0, lambda: self._set_status("error"))

        self._bot_thread = threading.Thread(target=run, daemon=True)
        self._bot_thread.start()

    def _save_and_update_bot(self):
        prefs = {str(gid): var.get() for gid, var in self.check_vars.items()}
        save_prefs(prefs)
        if self._active_bot:
            self._active_bot.enabled_server_ids = self._get_enabled()

    def _toggle_pause(self):
        if self._paused: self._resume_bot()
        else:            self._pause_bot()

    def _pause_bot(self):
        self._paused    = True
        self._countdown = self.PAUSE_DURATION
        self.pause_btn.config(text=f"▶  Resume ({self._countdown}s)", bg="#3a1a1a", fg=YELLOW)
        self._set_status("paused")
        self._append_log(f"⏸ Bot paused for {self.PAUSE_DURATION}s")
        if self._active_bot:
            asyncio.run_coroutine_threadsafe(self._active_bot.close(), self._active_bot.loop)
        self._tick_countdown()

    def _tick_countdown(self):
        if not self._paused: return
        self._countdown -= 1
        if self._countdown <= 0:
            self._resume_bot()
        else:
            self.pause_btn.config(text=f"▶  Resume ({self._countdown}s)")
            self._pause_timer = self.after(1000, self._tick_countdown)

    def _resume_bot(self):
        self._paused = False
        if self._pause_timer:
            self.after_cancel(self._pause_timer)
            self._pause_timer = None
        self.pause_btn.config(text="⏸  Pause 60s", bg=BORDER, fg=TEXT)
        self._append_log("▶ Bot resuming...")
        self._launch_bot()

    def _set_status(self, state):
        states = {"running": (GREEN, "Running"),
                  "paused":  (YELLOW, "Paused"),
                  "error":   (RED,   "Error — check logs")}
        color, label = states.get(state, (MUTED, state))
        self.status_dot.config(fg=color)
        self.status_lbl.config(text=label)

    # ── EU/NA region switch ────────────────────────────────────────────

    def _apply_region_label(self):
        region = load_prefs().get("region", "EU")
        self._region.set(region)
        if hasattr(self, "_region_lbl_var"):
            self._region_lbl_var.set(region)
        self._set_region(region)

    def _toggle_region(self):
        current = self._region.get()
        self._set_region("NA" if current == "EU" else "EU")

    def _set_region(self, region: str):
        self._region.set(region)
        if hasattr(self, "_region_lbl_var"):
            self._region_lbl_var.set(region)
        if hasattr(self, "_region_lbl"):
            self._region_lbl.config(fg=GREEN if region == "EU" else YELLOW)

        # Update active queue_channel_id in config for each server
        for s in self.config_data["servers"]:
            eu = s.get("queue_channel_id_eu")
            na = s.get("queue_channel_id_na")
            if eu and na:
                s["queue_channel_id"] = eu if region == "EU" else na

        # Save
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config_data, f, indent=4)
        prefs = load_prefs()
        prefs["region"] = region
        save_prefs(prefs)

        # Update bot's watched channels live
        if self._active_bot:
            self._active_bot.watched_channels.clear()
            for s in self.config_data["servers"]:
                self._active_bot.watched_channels[s["queue_channel_id"]] = s

        self._append_log(f"🌍 Switched to {region} region")

    # ── Website opener ─────────────────────────────────────────────────

    def _open_group_website(self):
        urls = {
            "pvptiers":    "https://pvptiers.com/ranking/overall",
            "mctiers":     "https://mctiers.com/rankings/overall",
            "subtiers":    "https://subtiers.net/ranking/overall",
            "hungergames": "https://store.stray.gg/",
        }
        group = self._active_filter.get()
        url   = urls.get(group)
        if url:
            import webbrowser
            webbrowser.open(url)
        else:
            # Show all links
            self._show_all_websites()

    def _show_all_websites(self):
        win = tk.Toplevel(self)
        win.title("Websites")
        win.configure(bg=BG)
        win.resizable(False, False)
        self._set_win_icon(win)
        win.grab_set()
        pw, ph = 320, 240
        px = self.winfo_x() + self.winfo_width()  // 2 - pw // 2
        py = self.winfo_y() + self.winfo_height() // 2 - ph // 2
        win.geometry(f"{pw}x{ph}+{px}+{py}")
        tk.Frame(win, bg=BLUE, height=3).pack(fill="x")
        tk.Label(win, text="🌐  Websites", font=("Segoe UI", 12, "bold"),
                 fg=TEXT, bg=BG).pack(pady=(14, 10))
        links = [
            ("MCTiers",     "https://mctiers.com/rankings/overall"),
            ("PvPTiers",    "https://pvptiers.com/ranking/overall"),
            ("SubTiers",    "https://subtiers.net/ranking/overall"),
            ("Stray",       "https://store.stray.gg/"),
            ("Wheel Surv.", "http://sg.wheelmc.org/"),
        ]
        import webbrowser
        for name, url in links:
            row = tk.Frame(win, bg=BG)
            row.pack(fill="x", padx=30, pady=2)
            tk.Label(row, text=name, font=FONT_B, fg=TEXT, bg=BG, width=10,
                     anchor="w").pack(side="left")
            lbl = tk.Label(row, text=url[:35]+"…" if len(url)>35 else url,
                           font=FONT_S, fg=BLUE, bg=BG, cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
            lbl.bind("<Enter>",    lambda e, l=lbl: l.config(fg=GREEN))
            lbl.bind("<Leave>",    lambda e, l=lbl: l.config(fg=BLUE))
        tk.Button(win, text="Close", font=FONT_B, fg=TEXT, bg=BORDER,
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  command=win.destroy).pack(pady=12)

    # ── Accept timer popup ─────────────────────────────────────────────

    def _show_accept_timer(self, server_name: str, server_cfg: dict):
        """Show a 2 minute countdown — user must click Accept or gets /leave'd."""
        def open_popup():
            win = tk.Toplevel(self)
            win.title("Queue Ready!")
            win.configure(bg=BG)
            win.resizable(False, False)
            win.attributes("-topmost", True)
            self._set_win_icon(win)
            pw, ph = 380, 240
            px = self.winfo_x() + self.winfo_width()  // 2 - pw // 2
            py = self.winfo_y() + self.winfo_height() // 2 - ph // 2
            win.geometry(f"{pw}x{ph}+{px}+{py}")

            tk.Frame(win, bg=GREEN, height=3).pack(fill="x")
            tk.Label(win, text="✅  QUEUE READY!",
                     font=("Segoe UI", 13, "bold"), fg=GREEN, bg=BG).pack(pady=(16, 4))
            tk.Label(win, text=f"You are in the {server_name} queue!",
                     font=FONT_N, fg=TEXT, bg=BG).pack()
            tk.Label(win, text="Click ACCEPT or you will be removed in:",
                     font=FONT_S, fg=MUTED, bg=BG).pack(pady=(4, 0))

            countdown_var = tk.StringVar(value="2:00")
            tk.Label(win, textvariable=countdown_var,
                     font=("Segoe UI", 28, "bold"), fg=YELLOW, bg=BG).pack(pady=(4, 12))

            accepted = [False]
            remaining = [120]  # 2 minutes in seconds

            def tick():
                if accepted[0]:
                    return
                remaining[0] -= 1
                mins = remaining[0] // 60
                secs = remaining[0] % 60
                countdown_var.set(f"{mins}:{secs:02d}")

                # Turn red in last 30 seconds
                if remaining[0] <= 30:
                    for w in win.winfo_children():
                        if isinstance(w, tk.Label) and w.cget("textvariable") == str(countdown_var):
                            w.config(fg=RED)

                if remaining[0] <= 0:
                    # Time's up — send /leave
                    self._append_log(f"⏰ Accept timer expired for {server_name} — sending /leave")
                    if self._active_bot:
                        import asyncio
                        asyncio.run_coroutine_threadsafe(
                            self._active_bot.send_leave_command(server_cfg),
                            self._active_bot.loop
                        )
                    try: win.destroy()
                    except: pass
                    return

                win.after(1000, tick)

            def accept():
                accepted[0] = True
                self._append_log(f"✅ Accepted queue for {server_name}!")
                play_sound()
                try: win.destroy()
                except: pass

            def leave():
                accepted[0] = True
                self._append_log(f"🔴 Declined queue for {server_name} — sending /leave")
                if self._active_bot:
                    import asyncio
                    asyncio.run_coroutine_threadsafe(
                        self._active_bot.send_leave_command(server_cfg),
                        self._active_bot.loop
                    )
                try: win.destroy()
                except: pass

            btn_row = tk.Frame(win, bg=BG)
            btn_row.pack()
            tk.Button(btn_row, text="✓  ACCEPT",
                      font=FONT_B, fg="#000", bg=GREEN,
                      activebackground=GREEN_DK, relief="flat",
                      padx=20, pady=8, cursor="hand2",
                      command=accept).pack(side="left", padx=8)
            tk.Button(btn_row, text="✕  LEAVE",
                      font=FONT_B, fg=TEXT, bg=RED,
                      activebackground="#cc3344", relief="flat",
                      padx=20, pady=8, cursor="hand2",
                      command=leave).pack(side="left", padx=8)

            # Play sound and start countdown
            play_sound()
            win.after(1000, tick)

        self.after(0, open_popup)

    # ── Auto-uncheck on join ───────────────────────────────────────────

    def _on_queue_joined(self, joined_server_name: str):
        """When a queue is joined, uncheck all other non-hungergames servers."""
        def _do():
            for s in self.config_data["servers"]:
                if s.get("group", "") == "hungergames":
                    continue  # never touch stray/wheel survival
                gid = s["guild_id"]
                var = self.check_vars.get(gid)
                if var is None:
                    continue
                if s["name"] == joined_server_name:
                    continue  # keep the joined one checked
                if var.get():
                    var.set(False)
                    self._refresh_card(gid, False)
            self._refresh_count()
            self._save_and_update_bot()
            self._append_log(f"🔒 Joined {joined_server_name} — unchecked all other queues")
        self.after(0, _do)

    # ── Queue status dot ───────────────────────────────────────────────

    def _set_status_dot(self, server_name: str, is_open: bool):
        """Update the green/grey dot on a server card."""
        def _do():
            for s in self.config_data["servers"]:
                if s["name"] == server_name:
                    dot = self.status_dots.get(s["guild_id"])
                    if dot:
                        dot.config(fg=GREEN if is_open else MUTED)
                    break
        self.after(0, _do)

    # ── Startup delay ──────────────────────────────────────────────────

    def _show_startup_delay(self):
        win = tk.Toplevel(self)
        self._set_win_icon(win)
        win.title("Startup Delay")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        win.attributes("-topmost", True)
        pw, ph = 360, 220
        px = self.winfo_x() + self.winfo_width()  // 2 - pw // 2
        py = self.winfo_y() + self.winfo_height() // 2 - ph // 2
        win.geometry(f"{pw}x{ph}+{px}+{py}")

        tk.Frame(win, bg=BLUE, height=3).pack(fill="x")
        tk.Label(win, text="⏱  Startup Delay",
                 font=("Segoe UI", 12, "bold"), fg=TEXT, bg=BG).pack(pady=(16, 4))
        tk.Label(win, text="Wait this many seconds after launch\nbefore connecting to Discord.",
                 font=FONT_S, fg=MUTED, bg=BG, justify="center").pack(pady=(0, 12))

        prefs = load_prefs()
        delay_var = tk.IntVar(value=prefs.get("startup_delay", 0))
        delay_lbl = tk.Label(win, text=f"{delay_var.get()}s",
                             font=("Segoe UI", 11, "bold"), fg=BLUE, bg=BG)
        delay_lbl.pack()

        def on_change(val):
            v = int(float(val))
            delay_lbl.config(text=f"{v}s")

        tk.Scale(win, from_=0, to=60, orient="horizontal",
                 variable=delay_var, command=on_change,
                 bg=CARD, fg=TEXT, troughcolor=BORDER,
                 highlightthickness=0, sliderrelief="flat",
                 activebackground=BLUE, length=280,
                 showvalue=False).pack(pady=(6, 0))

        def save_close():
            prefs["startup_delay"] = delay_var.get()
            save_prefs(prefs)
            win.destroy()
            self._append_log(f"⏱ Startup delay set to {delay_var.get()}s")

        tk.Button(win, text="✓  Save", font=FONT_B, fg="#000", bg=GREEN,
                  activebackground=GREEN_DK, relief="flat",
                  padx=18, pady=7, cursor="hand2",
                  command=save_close).pack(pady=14)

    # ── Volume control ─────────────────────────────────────────────────

    def _show_volume(self):
        win = tk.Toplevel(self)
        self._set_win_icon(win)
        win.title("Notification Volume")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        win.attributes("-topmost", True)
        pw, ph = 360, 220
        px = self.winfo_x() + self.winfo_width()  // 2 - pw // 2
        py = self.winfo_y() + self.winfo_height() // 2 - ph // 2
        win.geometry(f"{pw}x{ph}+{px}+{py}")

        tk.Frame(win, bg=GREEN, height=3).pack(fill="x")
        tk.Label(win, text="🔊  Notification Volume",
                 font=("Segoe UI", 12, "bold"), fg=TEXT, bg=BG).pack(pady=(16, 4))
        tk.Label(win, text="Drag to adjust the notification sound volume.",
                 font=FONT_S, fg=MUTED, bg=BG).pack(pady=(0, 12))

        # Load saved volume
        prefs = load_prefs()
        saved_vol = int(prefs.get("volume", 100))

        vol_var = tk.IntVar(value=saved_vol)
        vol_lbl = tk.Label(win, text=f"{saved_vol}%",
                           font=("Segoe UI", 11, "bold"), fg=GREEN, bg=BG)
        vol_lbl.pack()

        def on_change(val):
            v = int(float(val))
            vol_lbl.config(text=f"{v}%")
            import bot as bm
            bm.sound_volume = v / 100.0

        slider = ttk.Scale(win, from_=0, to=100, orient="horizontal",
                           variable=vol_var, command=on_change, length=280)
        slider.pack(pady=(6, 0))

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(pady=14)

        def test_sound():
            import bot as bm
            bm.play_sound()

        def save_close():
            prefs["volume"] = vol_var.get()
            save_prefs(prefs)
            win.destroy()

        tk.Button(btn_row, text="▶  Test", font=FONT_B, fg=TEXT, bg=BORDER,
                  activebackground="#2e2e48", relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  command=test_sound).pack(side="left", padx=6)
        tk.Button(btn_row, text="✓  Save", font=FONT_B, fg="#000", bg=GREEN,
                  activebackground=GREEN_DK, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  command=save_close).pack(side="left", padx=6)

    # ── Disclaimer popup ───────────────────────────────────────────────

    def _show_disclaimer(self):
        win = tk.Toplevel(self)
        self._set_win_icon(win)
        win.title("Disclaimer")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        win.attributes("-topmost", True)
        pw, ph = 480, 380
        px = self.winfo_x() + self.winfo_width()  // 2 - pw // 2
        py = self.winfo_y() + self.winfo_height() // 2 - ph // 2
        win.geometry(f"{pw}x{ph}+{px}+{py}")

        tk.Frame(win, bg=RED, height=3).pack(fill="x")
        tk.Label(win, text="⚠  Disclaimer",
                 font=("Segoe UI", 13, "bold"), fg=RED, bg=BG).pack(pady=(16, 10))

        lines = [
            ("⚠  You must JOIN each Discord server manually",
             "    The bot can only detect queues in servers you have already joined on Discord."),
            ("",  ""),
            ("⚠  Use at your own risk.",
             "    This tool automates Discord actions which may violate Discord's Terms of Service. "
             "By using it, you accept full responsibility for any consequences, "
             "including account suspension or bans."),
            ("",  ""),
            ("🔑  Your token is stored locally in config.json only.",
             "    It is never sent to any server or shared with anyone."),
        ]

        for title, desc in lines:
            if title == "":
                continue
            tk.Label(win, text=title, font=("Segoe UI", 9, "bold"),
                     fg=RED, bg=BG, anchor="w", justify="left").pack(
                     fill="x", padx=30, pady=(6, 0))
            if desc:
                tk.Label(win, text=desc, font=("Segoe UI", 8),
                         fg="#aa3333", bg=BG, anchor="w", justify="left",
                         wraplength=380).pack(fill="x", padx=42, pady=(0, 2))

        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)
        tk.Button(win, text="Got it", font=FONT_B, fg="#000", bg=GREEN,
                  activebackground=GREEN_DK, relief="flat",
                  padx=20, pady=7, cursor="hand2",
                  command=win.destroy).pack(pady=(0, 14))

    # ── Last seen ──────────────────────────────────────────────────────

    def _update_last_seen(self, server_name: str, time_str: str):
        """Update the last seen label on the server card."""
        def _do():
            for s in self.config_data["servers"]:
                if s["name"] == server_name:
                    gid = s["guild_id"]
                    lv = self.ls_vars.get(gid)
                    if lv:
                        lv.set(f"Last seen: {time_str}")
                    break
        self.after(0, _do)

    # ── System tray ────────────────────────────────────────────────────

    def _setup_tray(self):
        """Set up system tray icon so minimizing hides to tray."""
        try:
            import pystray
            from PIL import Image as PILImage

            try:
                tray_img = PILImage.open(LOGO_PATH).convert("RGBA").resize((64, 64))
            except Exception:
                tray_img = PILImage.new("RGBA", (64, 64), (5, 13, 26, 255))

            def on_show(icon, item):
                icon.stop()
                self._tray_icon = None
                self.after(0, self.deiconify)

            def on_quit(icon, item):
                icon.stop()
                self.after(0, self.destroy)

            menu = pystray.Menu(
                pystray.MenuItem("Show", on_show, default=True),
                pystray.MenuItem("Quit", on_quit)
            )
            self._tray_icon = pystray.Icon("QUEUE BOT", tray_img, "QUEUE BOT", menu)

            import threading
            threading.Thread(target=self._tray_icon.run, daemon=True).start()

        except ImportError:
            pass  # pystray not installed — skip tray

    def _on_minimize(self, event):
        """Hide to tray when minimized — only if pystray is available."""
        if self.state() != "iconic":
            return
        try:
            import pystray
            self.withdraw()
            if not hasattr(self, "_tray_icon") or self._tray_icon is None:
                self._setup_tray()
        except ImportError:
            pass  # pystray not installed — just minimize normally

    # ── Token change popup ─────────────────────────────────────────────

    def _show_token_change(self):
        win = tk.Toplevel(self)
        self._set_win_icon(win)
        win.title("Change Token")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        win.attributes("-topmost", True)
        pw, ph = 460, 260
        px = self.winfo_x() + self.winfo_width()  // 2 - pw // 2
        py = self.winfo_y() + self.winfo_height() // 2 - ph // 2
        win.geometry(f"{pw}x{ph}+{px}+{py}")

        tk.Frame(win, bg=YELLOW, height=3).pack(fill="x")
        tk.Label(win, text="🔑  Change Discord Token",
                 font=("Segoe UI", 12, "bold"), fg=TEXT, bg=BG).pack(pady=(16, 4))
        tk.Label(win, text="Paste your new token below. The app will restart the bot.",
                 font=FONT_S, fg=MUTED, bg=BG).pack(pady=(0, 12))

        frame = tk.Frame(win, bg=BG, padx=24)
        frame.pack(fill="x")

        token_var = tk.StringVar(value=self.config_data.get("token", ""))
        entry = tk.Entry(frame, textvariable=token_var,
                         font=("Consolas", 9), bg=CARD, fg=TEXT,
                         insertbackground=TEXT, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER,
                         highlightcolor=GREEN, show="*", width=50)
        entry.pack(fill="x", ipady=8)

        show_var = tk.BooleanVar(value=False)
        def toggle_show():
            entry.config(show="" if show_var.get() else "*")
        tk.Checkbutton(frame, text="Show token", variable=show_var,
                       font=FONT_S, fg=MUTED, bg=BG, activebackground=BG,
                       selectcolor=SURFACE, cursor="hand2",
                       command=toggle_show).pack(anchor="w", pady=(4, 0))

        err_lbl = tk.Label(win, text="", font=FONT_S, fg=RED, bg=BG)
        err_lbl.pack(pady=(6, 0))

        def save():
            token = token_var.get().strip()
            if not token:
                err_lbl.config(text="Please enter a token!")
                return
            if len(token) < 50:
                err_lbl.config(text="That doesn't look like a valid token.")
                return
            self.config_data["token"] = token
            with open(CONFIG_PATH, "w") as f:
                json.dump(self.config_data, f, indent=4)
            # Restart the bot with the new token
            if self._active_bot:
                asyncio.run_coroutine_threadsafe(
                    self._active_bot.close(), self._active_bot.loop)
            self.after(1000, self._launch_bot)
            self._append_log("🔑 Token updated — restarting bot...")
            win.destroy()

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(pady=12)
        tk.Button(btn_row, text="✓  Save & Restart",
                  font=FONT_B, fg="#000", bg=GREEN,
                  activebackground=GREEN_DK, relief="flat",
                  padx=16, pady=7, cursor="hand2",
                  command=save).pack(side="left", padx=6)
        tk.Button(btn_row, text="Cancel",
                  font=FONT_B, fg=TEXT, bg=BORDER,
                  activebackground="#2e2e48", relief="flat",
                  padx=16, pady=7, cursor="hand2",
                  command=win.destroy).pack(side="left", padx=6)

        entry.bind("<Return>", lambda e: save())

    # ── Warning popup ──────────────────────────────────────────────────

    def _show_warning(self, server_name, position):
        def open_popup():
            cfg = next((s for s in self.config_data["servers"]
                        if s["name"] == server_name), None)
            def on_leave():
                if self._active_bot and cfg:
                    asyncio.run_coroutine_threadsafe(
                        self._active_bot.send_leave_command(cfg),
                        self._active_bot.loop)
            WarningPopup(self, server_name, position, on_leave)
        self.after(0, open_popup)

    # ── Token change popup ────────────────────────────────────────────

    def _show_token_change(self):
        win = tk.Toplevel(self)
        self._set_win_icon(win)
        win.title("Change Token")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        win.attributes("-topmost", True)
        pw, ph = 420, 200
        px = self.winfo_x() + self.winfo_width()  // 2 - pw // 2
        py = self.winfo_y() + self.winfo_height() // 2 - ph // 2
        win.geometry(f"{pw}x{ph}+{px}+{py}")

        tk.Frame(win, bg=YELLOW, height=3).pack(fill="x")
        tk.Label(win, text="Change Discord Token",
                 font=("Segoe UI", 12, "bold"), fg=TEXT, bg=BG).pack(pady=(20, 4))
        tk.Label(win, text="Your token is saved locally in config.json only.",
                 font=FONT_S, fg=MUTED, bg=BG).pack()

        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=20, pady=12)

        frame = tk.Frame(win, bg=BG)
        frame.pack(padx=24, fill="x")

        tk.Label(frame, text="New Token:", font=FONT_S, fg=MUTED, bg=BG).pack(anchor="w")

        token_var = tk.StringVar()
        entry = tk.Entry(frame, textvariable=token_var,
                         font=("Consolas", 9), bg=CARD, fg=TEXT,
                         insertbackground=TEXT, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER,
                         highlightcolor=GREEN, show="*")
        entry.pack(fill="x", ipady=8, pady=(4, 0))

        show_var = tk.BooleanVar(value=False)
        def toggle_show():
            entry.config(show="" if show_var.get() else "*")
        tk.Checkbutton(frame, text="Show token", variable=show_var,
                       font=FONT_S, fg=MUTED, bg=BG, activebackground=BG,
                       selectcolor=SURFACE, cursor="hand2",
                       command=toggle_show).pack(anchor="w", pady=(4, 0))

        error_lbl = tk.Label(win, text="", font=FONT_S, fg=RED, bg=BG)
        error_lbl.pack(pady=(6, 0))

        def save():
            token = token_var.get().strip()
            if not token:
                error_lbl.config(text="Please enter a token!")
                return
            if len(token) < 50:
                error_lbl.config(text="That doesn't look like a valid token.")
                return
            self.config_data["token"] = token
            with open(CONFIG_PATH, "w") as f:
                json.dump(self.config_data, f, indent=4)
            # Restart bot with new token
            if self._active_bot:
                import asyncio
                asyncio.run_coroutine_threadsafe(self._active_bot.close(), self._active_bot.loop)
            self.after(1500, self._launch_bot)
            win.destroy()
            self._append_log("🔑 Token updated — restarting bot...")

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(pady=12)
        tk.Button(btn_row, text="✓  Save & Restart",
                  font=FONT_B, fg="#000", bg=GREEN,
                  activebackground=GREEN_DK, relief="flat",
                  padx=16, pady=7, cursor="hand2",
                  command=save).pack(side="left", padx=6)
        tk.Button(btn_row, text="Cancel",
                  font=FONT_B, fg=TEXT, bg=BORDER,
                  activebackground="#2e2e48", relief="flat",
                  padx=16, pady=7, cursor="hand2",
                  command=win.destroy).pack(side="left", padx=6)

        entry.bind("<Return>", lambda e: save())
        entry.focus_set()

    # ── How it works ───────────────────────────────────────────────────

    def _show_how_it_works(self):
        win = tk.Toplevel(self)
        self._set_win_icon(win)
        win.title("How It Works")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        win.attributes("-topmost", True)
        pw, ph = 480, 520
        px = self.winfo_x() + self.winfo_width()  // 2 - pw // 2
        py = self.winfo_y() + self.winfo_height() // 2 - ph // 2
        win.geometry(f"{pw}x{ph}+{px}+{py}")

        tk.Frame(win, bg=GREEN, height=3).pack(fill="x")
        tk.Label(win, text="How The Bot Works",
                 font=("Segoe UI", 13, "bold"), fg=TEXT, bg=BG).pack(pady=(16, 2))
        tk.Label(win, text="A complete breakdown of every feature",
                 font=FONT_S, fg=MUTED, bg=BG).pack(pady=(0, 8))
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 8))

        frame = tk.Frame(win, bg=BG)
        frame.pack(fill="both", expand=True, padx=20)
        text = tk.Text(frame, bg=CARD, fg=TEXT, font=("Segoe UI", 9),
                       relief="flat", wrap="word", padx=14, pady=12,
                       highlightthickness=1, highlightbackground=BORDER,
                       bd=0, cursor="arrow", spacing2=3, spacing3=5)
        text.pack(fill="both", expand=True)
        text.tag_config("h",  foreground=GREEN,  font=("Segoe UI", 9, "bold"))
        text.tag_config("b",  foreground=TEXT,   font=("Segoe UI", 9))
        text.tag_config("hi", foreground=YELLOW, font=("Segoe UI", 9, "bold"))
        text.tag_config("d",  foreground=MUTED,  font=("Segoe UI", 8))
        text.tag_config("cr", foreground="#444466", font=("Segoe UI", 8, "italic"))

        content = [
            ("h", "OVERVIEW\n"),
            ("b", "Watches MCTiers Discord servers for queue messages. When a queue opens, it instantly clicks the Join button for you.\n\n"),
            ("h", "QUEUE JOINING\n"),
            ("d", "▸ "), ("b", "Monitors the queue channel for messages from the SubTiers bot.\n"),
            ("d", "▸ "), ("b", "Reads both message text AND embeds to detect 'Tester(s) Available!'.\n"),
            ("d", "▸ "), ("b", "On startup, scans recent messages in case a queue is already open.\n\n"),
            ("h", "POSITION TRACKING\n"),
            ("hi", "▸ Position 11+:  "), ("b", "Bot sends /leave automatically — queue is too full.\n"),
            ("hi", "▸ Position 1–4:  "), ("b", "Warning popup asks if you want to stay or leave.\n\n"),
            ("h", "LIVE LOGS\n"),
            ("d", "▸ "), ("b", "Every event is shown in the log panel on the right in real time.\n"),
            ("d", "▸ "), ("b", "Green = queue open/joined, Red = left queue, Yellow = warning.\n\n"),
            ("h", "QUEUE SIZE FILTER\n"),
            ("d", "▸ "), ("b", "If a queue already has 11 or more players in it, the bot will NOT join.\n"),
            ("d", "▸ "), ("b", "This prevents joining a full queue where you'd just get auto-kicked anyway.\n\n"),
            ("h", "LAST SEEN\n"),
            ("d", "▸ "), ("b", "Each server card shows the last time its queue was open.\n"),
            ("d", "▸ "), ("b", "Updates live every time a queue is detected.\n\n"),
            ("h", "SYSTEM TRAY\n"),
            ("d", "▸ "), ("b", "Minimizing the window hides it to the system tray.\n"),
            ("d", "▸ "), ("b", "The bot keeps running in the background. Right-click the tray icon to show or quit.\n"),
            ("d", "▸ "), ("b", "Requires: pip install pystray\n\n"),
            ("d", "▸ "), ("b", "Stops the bot for 60 seconds then auto-resumes. Click again to resume early.\n\n"),
            ("h", "AUTO-START ON BOOT\n"),
            ("d", "▸ "), ("b", "Put a shortcut to start_bot.bat in Win+R → shell:startup.\n\n"),
            ("d", "─" * 55 + "\n"),
            ("cr", "🤖 Made by AI - CLAUDE\n"),
            ("cr", "🇵🇱 Credits to repp - Imreppofficial\n"),
        ]
        text.config(state="normal")
        for tag, c in content:
            text.insert("end", c, tag)
        text.config(state="disabled")

        # Scroll isolation for the how-it-works text box
        text.bind("<Enter>", lambda e: text.bind_all("<MouseWheel>",
            lambda ev: text.yview_scroll(int(-1*(ev.delta/120)), "units")))
        text.bind("<Leave>", lambda e: self._rebind_canvas_scroll())

        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=20, pady=8)
        tk.Button(win, text="Got it", font=FONT_B, fg="#000", bg=GREEN,
                  activebackground=GREEN_DK, relief="flat",
                  padx=22, pady=7, cursor="hand2",
                  command=win.destroy).pack(pady=(0, 14))

    # ── Helpers ────────────────────────────────────────────────────────

    def _open_url(self, url: str):
        """Open a URL in the default browser."""
        import webbrowser
        webbrowser.open(url)

    def _center(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _set_win_icon(self, win):
        """Apply the app icon to any popup window."""
        try:
            win.iconbitmap(ICO_PATH)
        except Exception:
            pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
