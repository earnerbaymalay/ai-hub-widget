#!/usr/bin/env python3
"""
AI Hub Desktop Widget v5.0
===========================
Clean, solid, VS-Code-sidebar aesthetic.
No transparency. Instant theme switching.
Active session detection. Real network stats via psutil.

Requirements: Python 3.8+, Windows 10/11, WMI, psutil
Install deps:  pip install psutil WMI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import json
import os
import sys
import socket
import time
from datetime import datetime

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import wmi
    HAS_WMI = True
except ImportError:
    HAS_WMI = False

try:
    from ctypes import windll
    windll.user32.SetProcessDPIAware()
except Exception:
    pass

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_FILE = os.path.expanduser("~/.ai-hub-v5-config.json")

DEFAULT_CONFIG = {
    "position":     {"x": 50, "y": 50},
    "size":         {"width": 380, "height": 720},
    "always_on_top": True,
    "theme":        "dark",
    "selected_ai":  "Claude",
}

# ============================================================================
# AI TOOLS  ─  7 tools, rendered in a 3-column grid
# ============================================================================

AI_TOOLS = {
    "Claude":  {"cmd": "claude",                        "color": "#E57035", "icon": "◉", "key": "c",  "desc": "Anthropic",  "proc": "claude.exe"},
    "Kimi":    {"cmd": "kimi",                          "color": "#00D4AA", "icon": "◈", "key": "k",  "desc": "Moonshot",   "proc": "kimi.exe"},
    "Gemini":  {"cmd": "gemini",                        "color": "#4285F4", "icon": "◆", "key": "g",  "desc": "Google",     "proc": "gemini.exe"},
    "Qwen":    {"cmd": "qwen",                          "color": "#7B68EE", "icon": "◇", "key": "q",  "desc": "Alibaba",    "proc": "qwen.exe"},
    "Codex":   {"cmd": "codex",                         "color": "#10A37F", "icon": "▣", "key": "cx", "desc": "OpenAI",     "proc": "codex.exe"},
    "Kilo":    {"cmd": "kilo",                          "color": "#F472B6", "icon": "▲", "key": "kc", "desc": "Kilo Code",  "proc": "kilo.exe"},
    "Ollama":  {"cmd": "ollama run dolphin-uncensored", "color": "#FF6B6B", "icon": "◎", "key": "o",  "desc": "Local LLMs", "proc": "ollama.exe"},
}

# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

PROMPT_TEMPLATES = {
    "💻 Dev": [
        ("Create Function",  "Create a Python function that [describe functionality]. Include type hints, docstring, and error handling."),
        ("Refactor Code",    "Refactor the following code to improve readability and performance:\n\n[paste code here]"),
        ("Debug Issue",      "Debug this code. The error is: [describe error]. Here's the code:\n\n[paste code here]"),
        ("Code Review",      "Review this code for best practices, security issues, and potential bugs:\n\n[paste code here]"),
        ("Write Unit Tests", "Write comprehensive unit tests using pytest for:\n\n[paste code here]"),
    ],
    "📊 Analysis": [
        ("Explain Code",    "Explain what this code does step by step:\n\n[paste code here]"),
        ("Compare Options", "Compare and contrast [option A] vs [option B]. List pros and cons of each."),
        ("Security Audit",  "Perform a security audit on this code. Identify vulnerabilities:\n\n[paste code here]"),
        ("Architecture",    "Analyze this system architecture. Identify bottlenecks:\n\n[describe system]"),
    ],
    "✨ Creative": [
        ("Generate Ideas",   "Generate 10 creative ideas for [topic/problem]. Be specific and actionable."),
        ("Write Content",    "Write a [blog post/email/doc] about [topic]. Target audience: [audience]."),
        ("Brainstorm Names", "Brainstorm 15 unique names for [project/product]."),
    ],
    "⚙️ System": [
        ("PowerShell Script", "Create a PowerShell script to [task]. Include error handling and comments."),
        ("Batch Automation",  "Write a batch script that [describe task]. Add logging and error checking."),
        ("System Diagnostic", "Generate a Windows diagnostic report for disk, memory, and services."),
    ],
}

# ============================================================================
# THEMES
# ============================================================================

THEMES = {
    "dark": {
        "bg":       "#1E1E1E",
        "bg2":      "#252526",
        "bg3":      "#2D2D30",
        "border":   "#3C3C3C",
        "sep":      "#3C3C3C",
        "text":     "#D4D4D4",
        "text2":    "#858585",
        "accent":   "#0078D4",
        "success":  "#4EC9B0",
        "warning":  "#CE9178",
        "error":    "#F44747",
        "term_bg":  "#0C0C0C",
        "term_fg":  "#CCCCCC",
        "dot_on":   "#4EC9B0",
        "dot_off":  "#444444",
    },
    "light": {
        "bg":       "#F5F5F5",
        "bg2":      "#EBEBEB",
        "bg3":      "#DCDCDC",
        "border":   "#C8C8C8",
        "sep":      "#C8C8C8",
        "text":     "#1E1E1E",
        "text2":    "#6E6E6E",
        "accent":   "#005FB8",
        "success":  "#107C10",
        "warning":  "#CA5010",
        "error":    "#C72E2E",
        "term_bg":  "#FAFAFA",
        "term_fg":  "#1E1E1E",
        "dot_on":   "#107C10",
        "dot_off":  "#CCCCCC",
    },
    "midnight": {
        "bg":       "#0D0D12",
        "bg2":      "#13131A",
        "bg3":      "#1A1A24",
        "border":   "#2A2A3A",
        "sep":      "#2A2A3A",
        "text":     "#C8C8D4",
        "text2":    "#606080",
        "accent":   "#7B68EE",
        "success":  "#4ECCA3",
        "warning":  "#F0A500",
        "error":    "#FF5F5F",
        "term_bg":  "#070710",
        "term_fg":  "#C8C8D4",
        "dot_on":   "#4ECCA3",
        "dot_off":  "#2A2A3A",
    },
}

# ============================================================================
# MAIN APP
# ============================================================================

class AIHub:
    def __init__(self):
        self.config        = self._load_config()
        self.t             = THEMES[self.config.get("theme", "dark")]
        self._net_prev     = None
        self._net_time     = None
        self._ai_dots      = {}
        self._ai_cards     = {}

        self._setup_window()
        self.selected_ai = tk.StringVar(value=self.config.get("selected_ai", "Claude"))
        self._build_ui()
        self._start_monitors()

    # ──────────────────────────────────────────────
    # Config
    # ──────────────────────────────────────────────

    def _load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE) as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
        return DEFAULT_CONFIG.copy()

    def _save_config(self):
        try:
            cfg = {
                "position":     {"x": self.root.winfo_x(), "y": self.root.winfo_y()},
                "size":         {"width": self.root.winfo_width(), "height": self.root.winfo_height()},
                "always_on_top": bool(self.root.attributes("-topmost")),
                "theme":        self.config.get("theme", "dark"),
                "selected_ai":  self.selected_ai.get(),
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    # ──────────────────────────────────────────────
    # Window setup
    # ──────────────────────────────────────────────

    def _setup_window(self):
        self.root = tk.Tk()
        self.root.title("AI Hub")
        sz  = self.config.get("size", DEFAULT_CONFIG["size"])
        pos = self.config.get("position", DEFAULT_CONFIG["position"])
        self.root.geometry(f"{sz['width']}x{sz['height']}+{pos['x']}+{pos['y']}")
        self.root.minsize(340, 480)
        self.root.configure(bg=self.t["bg"])
        self.root.attributes("-topmost", self.config.get("always_on_top", True))
        self.root.attributes("-alpha", 1.0)          # SOLID — never transparent
        self.root.overrideredirect(True)             # Custom title bar
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._drag_x = self._drag_y = 0

    # ──────────────────────────────────────────────
    # UI root build
    # ──────────────────────────────────────────────

    def _build_ui(self):
        t = self.t
        self.main = tk.Frame(self.root, bg=t["bg"])
        self.main.pack(fill=tk.BOTH, expand=True)

        self._build_header()

        # ── Scrollable body ──────────────────────
        outer = tk.Frame(self.main, bg=t["bg"])
        outer.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(outer, bg=t["bg"], highlightthickness=0, bd=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)

        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.body = tk.Frame(self.canvas, bg=t["bg"])
        self._win_id = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        self.body.bind("<Configure>",
                       lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self._win_id, width=e.width))

        # Mousewheel only while hovering the scroll canvas (won't fight terminal)
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_scroll))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self._build_system(self.body)
        self._build_ai_tools(self.body)
        self._build_command(self.body)
        self._build_templates(self.body)
        self._build_output(self.body)

        self._build_statusbar()

    def _on_scroll(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ──────────────────────────────────────────────
    # Header
    # ──────────────────────────────────────────────

    def _build_header(self):
        t = self.t
        hdr = tk.Frame(self.main, bg=t["bg2"], height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        for w in [hdr]:
            w.bind("<Button-1>",  self._drag_start)
            w.bind("<B1-Motion>", self._drag_move)

        # Left: logo + title
        left = tk.Frame(hdr, bg=t["bg2"])
        left.pack(side=tk.LEFT, padx=12)
        left.bind("<Button-1>",  self._drag_start)
        left.bind("<B1-Motion>", self._drag_move)

        logo = tk.Label(left, text="⬡", font=("Segoe UI", 16),
                        fg=t["accent"], bg=t["bg2"])
        logo.pack(side=tk.LEFT)
        logo.bind("<Button-1>",  self._drag_start)
        logo.bind("<B1-Motion>", self._drag_move)

        tk.Label(left, text=" AI Hub", font=("Segoe UI", 11, "bold"),
                 fg=t["text"], bg=t["bg2"]).pack(side=tk.LEFT)
        tk.Label(left, text=" v5", font=("Segoe UI", 8),
                 fg=t["text2"], bg=t["bg2"]).pack(side=tk.LEFT, pady=(4, 0))

        # Right: theme picker + window controls
        right = tk.Frame(hdr, bg=t["bg2"])
        right.pack(side=tk.RIGHT, padx=6)

        self._theme_var = tk.StringVar(value=self.config.get("theme", "dark"))
        combo = ttk.Combobox(right, textvariable=self._theme_var,
                             values=list(THEMES.keys()),
                             width=9, state="readonly",
                             font=("Segoe UI", 8))
        combo.pack(side=tk.LEFT, padx=(0, 10), pady=10)
        combo.bind("<<ComboboxSelected>>", self._switch_theme)

        self._hdr_btn(right, "─", self.root.iconify)
        self._hdr_btn(right, "×", self._on_close, hover=t["error"])

    def _hdr_btn(self, parent, text, cmd, hover=None):
        t = self.t
        lbl = tk.Label(parent, text=text, font=("Segoe UI", 13),
                       fg=t["text2"], bg=t["bg2"], cursor="hand2", width=3)
        lbl.pack(side=tk.LEFT)
        lbl.bind("<Button-1>", lambda e: cmd())
        lbl.bind("<Enter>",    lambda e: lbl.config(fg=hover or t["text"]))
        lbl.bind("<Leave>",    lambda e: lbl.config(fg=t["text2"]))

    # ──────────────────────────────────────────────
    # Section header helper
    # ──────────────────────────────────────────────

    def _section(self, parent, title):
        """Returns a padded content frame, preceded by a labelled divider."""
        t = self.t
        row = tk.Frame(parent, bg=t["bg"])
        row.pack(fill=tk.X, padx=14, pady=(14, 4))
        tk.Label(row, text=title, font=("Segoe UI", 8, "bold"),
                 fg=t["text2"], bg=t["bg"]).pack(side=tk.LEFT)
        tk.Frame(row, bg=t["sep"], height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0), pady=1)

        frame = tk.Frame(parent, bg=t["bg"])
        frame.pack(fill=tk.X, padx=14, pady=(0, 4))
        return frame

    # ──────────────────────────────────────────────
    # System Monitor
    # ──────────────────────────────────────────────

    def _build_system(self, parent):
        t = self.t
        f = self._section(parent, "SYSTEM")

        # CPU
        cpu_row = tk.Frame(f, bg=t["bg"])
        cpu_row.pack(fill=tk.X, pady=2)
        tk.Label(cpu_row, text="CPU", font=("Segoe UI", 9),
                 fg=t["text2"], bg=t["bg"], width=5, anchor="w").pack(side=tk.LEFT)
        self.cpu_bar = self._bar(cpu_row)
        self.cpu_lbl = tk.Label(cpu_row, text="─ %", font=("Segoe UI", 9, "bold"),
                                fg=t["success"], bg=t["bg"], width=6)
        self.cpu_lbl.pack(side=tk.LEFT, padx=(6, 0))

        # RAM
        ram_row = tk.Frame(f, bg=t["bg"])
        ram_row.pack(fill=tk.X, pady=2)
        tk.Label(ram_row, text="RAM", font=("Segoe UI", 9),
                 fg=t["text2"], bg=t["bg"], width=5, anchor="w").pack(side=tk.LEFT)
        self.ram_bar = self._bar(ram_row)
        self.ram_lbl = tk.Label(ram_row, text="─ %", font=("Segoe UI", 9, "bold"),
                                fg=t["success"], bg=t["bg"], width=6)
        self.ram_lbl.pack(side=tk.LEFT, padx=(6, 0))

        # Drives (rebuilt on each update)
        self.drive_frame = tk.Frame(f, bg=t["bg"])
        self.drive_frame.pack(fill=tk.X, pady=(6, 2))

        # Network
        net_row = tk.Frame(f, bg=t["bg"])
        net_row.pack(fill=tk.X, pady=2)
        tk.Label(net_row, text="▼", font=("Segoe UI", 9),
                 fg=t["success"], bg=t["bg"]).pack(side=tk.LEFT)
        self.net_dn = tk.Label(net_row, text="─ KB/s", font=("Segoe UI", 8),
                               fg=t["text"], bg=t["bg"], width=11, anchor="w")
        self.net_dn.pack(side=tk.LEFT, padx=(2, 10))
        tk.Label(net_row, text="▲", font=("Segoe UI", 9),
                 fg=t["warning"], bg=t["bg"]).pack(side=tk.LEFT)
        self.net_up = tk.Label(net_row, text="─ KB/s", font=("Segoe UI", 8),
                               fg=t["text"], bg=t["bg"], width=11, anchor="w")
        self.net_up.pack(side=tk.LEFT, padx=2)

        # Uptime
        self.uptime_lbl = tk.Label(f, text="⏱ ─", font=("Segoe UI", 8),
                                   fg=t["text2"], bg=t["bg"], anchor="w")
        self.uptime_lbl.pack(fill=tk.X, pady=(2, 0))

    def _bar(self, parent, width=160):
        t = self.t
        c = tk.Canvas(parent, width=width, height=6, bg=t["bg3"],
                      highlightthickness=0, bd=0)
        c.pack(side=tk.LEFT, padx=(6, 0))
        return c

    def _draw_bar(self, canvas, pct, color, width=160):
        canvas.delete("all")
        canvas.create_rectangle(0, 0, width, 6, fill=self.t["bg3"], outline="")
        fill = max(2, int(width * pct / 100))
        canvas.create_rectangle(0, 0, fill, 6, fill=color, outline="")

    def _usage_color(self, pct):
        t = self.t
        if pct < 60:  return t["success"]
        if pct < 85:  return t["warning"]
        return t["error"]

    # ──────────────────────────────────────────────
    # AI Tool Cards
    # ──────────────────────────────────────────────

    def _build_ai_tools(self, parent):
        f = self._section(parent, "AI TOOLS")
        grid = tk.Frame(f, bg=self.t["bg"])
        grid.pack(fill=tk.X)
        for i in range(3):
            grid.columnconfigure(i, weight=1)
        for idx, (name, cfg) in enumerate(AI_TOOLS.items()):
            row, col = divmod(idx, 3)
            self._ai_card(grid, name, cfg, row, col)

    def _ai_card(self, grid, name, cfg, row, col):
        t = self.t
        selected = (name == self.selected_ai.get())

        card = tk.Frame(grid, bg=t["bg2"], cursor="hand2",
                        highlightbackground=cfg["color"] if selected else t["border"],
                        highlightthickness=1)
        card.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
        self._ai_cards[name] = card

        # Left accent stripe
        tk.Frame(card, bg=cfg["color"], width=3).pack(side=tk.LEFT, fill=tk.Y)

        # Card body
        body = tk.Frame(card, bg=t["bg2"])
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        top = tk.Frame(body, bg=t["bg2"])
        top.pack(fill=tk.X)

        tk.Label(top, text=cfg["icon"], font=("Segoe UI", 13),
                 fg=cfg["color"], bg=t["bg2"]).pack(side=tk.LEFT)

        dot = tk.Label(top, text="●", font=("Segoe UI", 7),
                       fg=t["dot_off"], bg=t["bg2"])
        dot.pack(side=tk.RIGHT)
        self._ai_dots[name] = dot

        tk.Label(body, text=name, font=("Segoe UI", 8, "bold"),
                 fg=t["text"], bg=t["bg2"], anchor="w").pack(fill=tk.X)
        tk.Label(body, text=cfg["desc"], font=("Segoe UI", 7),
                 fg=t["text2"], bg=t["bg2"], anchor="w").pack(fill=tk.X)

        # Click anywhere on card
        for w in [card, body, top, *top.winfo_children(), *body.winfo_children()]:
            try:
                w.bind("<Button-1>", lambda e, n=name: self._select_ai(n))
                w.bind("<Enter>",    lambda e, c=card, clr=cfg["color"]: c.config(
                    highlightbackground=clr))
                w.bind("<Leave>",    lambda e, n=name, c=card, clr=cfg["color"]: c.config(
                    highlightbackground=clr if n == self.selected_ai.get() else self.t["border"]))
            except Exception:
                pass

    def _select_ai(self, name):
        self.selected_ai.set(name)
        for n, card in self._ai_cards.items():
            card.config(highlightbackground=AI_TOOLS[n]["color"]
                        if n == name else self.t["border"])
        self._ai_label.config(text=f"▶  {name}", fg=AI_TOOLS[name]["color"])
        self._log(f"Switched to {name}\n", "info")
        self._save_config()

    # ──────────────────────────────────────────────
    # Command Center
    # ──────────────────────────────────────────────

    def _build_command(self, parent):
        t = self.t
        f = self._section(parent, "COMMAND")

        cur = self.selected_ai.get()
        self._ai_label = tk.Label(f,
            text=f"▶  {cur}",
            font=("Segoe UI", 10, "bold"),
            fg=AI_TOOLS[cur]["color"], bg=t["bg"], anchor="w")
        self._ai_label.pack(fill=tk.X, pady=(0, 6))

        # Input row
        row = tk.Frame(f, bg=t["bg"])
        row.pack(fill=tk.X)

        self.cmd_entry = tk.Entry(row, font=("Segoe UI", 10),
                                  bg=t["bg2"], fg=t["text"],
                                  insertbackground=t["accent"],
                                  relief=tk.FLAT,
                                  highlightbackground=t["border"],
                                  highlightthickness=1)
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.cmd_entry.bind("<Return>", lambda e: self._send())

        tk.Button(row, text="▶", font=("Segoe UI", 10),
                  fg=t["accent"], bg=t["bg2"],
                  activebackground=t["accent"], activeforeground="#fff",
                  relief=tk.FLAT, cursor="hand2", width=3,
                  command=self._send).pack(side=tk.LEFT, padx=(6, 0))

        # Quick actions
        acts = tk.Frame(f, bg=t["bg"])
        acts.pack(fill=tk.X, pady=(6, 0))
        for label, cmd in [("📋 Paste", self._paste),
                            ("🗑 Clear", lambda: self.cmd_entry.delete(0, tk.END))]:
            tk.Button(acts, text=label, font=("Segoe UI", 8),
                      fg=t["text2"], bg=t["bg2"],
                      activebackground=t["bg3"],
                      relief=tk.FLAT, cursor="hand2",
                      command=cmd).pack(side=tk.LEFT, padx=(0, 6))

    # ──────────────────────────────────────────────
    # Prompt Templates
    # ──────────────────────────────────────────────

    def _build_templates(self, parent):
        t = self.t
        f = self._section(parent, "TEMPLATES")
        row = tk.Frame(f, bg=t["bg"])
        row.pack(fill=tk.X)
        for cat in PROMPT_TEMPLATES:
            tk.Button(row, text=cat, font=("Segoe UI", 8),
                      fg=t["text"], bg=t["bg2"],
                      activebackground=t["accent"], activeforeground="#fff",
                      relief=tk.FLAT, cursor="hand2", padx=6, pady=3,
                      command=lambda c=cat: self._show_templates(c)
                      ).pack(side=tk.LEFT, padx=(0, 4), pady=2)

    def _show_templates(self, cat):
        t = self.t
        win = tk.Toplevel(self.root)
        win.title(cat)
        win.geometry("360x380")
        win.configure(bg=t["bg"])
        win.attributes("-alpha", 1.0)
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text=cat, font=("Segoe UI", 11, "bold"),
                 fg=t["text"], bg=t["bg2"], pady=10).pack(fill=tk.X)

        frame = tk.Frame(win, bg=t["bg"])
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        for name, tmpl in PROMPT_TEMPLATES[cat]:
            tk.Button(frame, text=name, font=("Segoe UI", 10),
                      fg=t["text"], bg=t["bg2"],
                      activebackground=t["accent"], activeforeground="#fff",
                      relief=tk.FLAT, cursor="hand2", pady=7, anchor="w",
                      command=lambda tp=tmpl: [self.cmd_entry.delete(0, tk.END),
                                               self.cmd_entry.insert(0, tp),
                                               win.destroy()]
                      ).pack(fill=tk.X, pady=2)

    # ──────────────────────────────────────────────
    # Output / Terminal
    # ──────────────────────────────────────────────

    def _build_output(self, parent):
        t = self.t
        f = self._section(parent, "OUTPUT")

        ctrl = tk.Frame(f, bg=t["bg"])
        ctrl.pack(fill=tk.X, pady=(0, 4))
        for label, cmd in [("📋 Copy", self._copy_output),
                            ("🗑 Clear", self._clear_output)]:
            tk.Button(ctrl, text=label, font=("Segoe UI", 8),
                      fg=t["text2"], bg=t["bg2"],
                      relief=tk.FLAT, cursor="hand2",
                      command=cmd).pack(side=tk.RIGHT, padx=(4, 0))

        self.terminal = scrolledtext.ScrolledText(
            f, font=("Cascadia Code", 9),
            bg=t["term_bg"], fg=t["term_fg"],
            relief=tk.FLAT, wrap=tk.WORD, height=10,
            padx=8, pady=8, insertbackground=t["accent"])
        self.terminal.pack(fill=tk.BOTH, expand=True)
        self.terminal.config(state=tk.DISABLED)

        self.terminal.tag_config("cmd",     foreground=t["accent"])
        self.terminal.tag_config("error",   foreground=t["error"])
        self.terminal.tag_config("success", foreground=t["success"])
        self.terminal.tag_config("info",    foreground=t["text2"])
        self.terminal.tag_config("ts",      foreground=t["text2"],
                                             font=("Cascadia Code", 7))

        self._log("AI Hub v5 ready.\n", "success")
        self._log("Select a tool above, enter a prompt, press ▶ or Enter.\n", "info")

    # ──────────────────────────────────────────────
    # Status bar
    # ──────────────────────────────────────────────

    def _build_statusbar(self):
        t = self.t
        bar = tk.Frame(self.main, bg=t["bg2"], height=22)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)
        self._status = tk.Label(bar, text="Ready", font=("Segoe UI", 8),
                                fg=t["text2"], bg=t["bg2"])
        self._status.pack(side=tk.LEFT, padx=10)
        self._clock = tk.Label(bar, text="", font=("Segoe UI", 8),
                               fg=t["text2"], bg=t["bg2"])
        self._clock.pack(side=tk.RIGHT, padx=10)
        self._tick()

    def _tick(self):
        self._clock.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._tick)

    # ──────────────────────────────────────────────
    # Actions
    # ──────────────────────────────────────────────

    def _send(self):
        text = self.cmd_entry.get().strip()
        if not text:
            return
        self.cmd_entry.delete(0, tk.END)
        ai  = AI_TOOLS[self.selected_ai.get()]
        cmd = f'{ai["cmd"]} "{text}"'
        ts  = datetime.now().strftime("%H:%M")
        self._log(f"[{ts}] ", "ts")
        self._log(f"{self.selected_ai.get()}: {text}\n", "cmd")
        self._set_status(f"Running {self.selected_ai.get()}…")

        def run():
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, shell=True,
                                        text=True, encoding="utf-8", errors="replace")
                for line in proc.stdout:
                    self.root.after(0, lambda l=line: self._log(l))
                self.root.after(0, lambda: self._set_status("Ready"))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Error: {e}\n", "error"))
                self.root.after(0, lambda: self._set_status("Error"))

        threading.Thread(target=run, daemon=True).start()

    def _paste(self):
        try:
            self.cmd_entry.insert(tk.INSERT, self.root.clipboard_get())
        except Exception:
            pass

    def _log(self, text, tag=""):
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, text, tag)
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)

    def _clear_output(self):
        self.terminal.config(state=tk.NORMAL)
        self.terminal.delete(1.0, tk.END)
        self.terminal.config(state=tk.DISABLED)

    def _copy_output(self):
        self.terminal.config(state=tk.NORMAL)
        self.root.clipboard_clear()
        self.root.clipboard_append(self.terminal.get(1.0, tk.END))
        self.terminal.config(state=tk.DISABLED)
        self._set_status("Copied to clipboard")

    def _set_status(self, msg):
        self._status.config(text=msg)
        self.root.after(3000, lambda: self._status.config(text="Ready"))

    # ──────────────────────────────────────────────
    # System monitoring (background threads)
    # ──────────────────────────────────────────────

    def _start_monitors(self):
        self._poll_system()
        self._poll_sessions()

    def _poll_system(self):
        threading.Thread(target=self._fetch_system, daemon=True).start()
        self.root.after(2500, self._poll_system)

    def _fetch_system(self):
        try:
            cpu = ram = 0
            drives = []
            upstr  = "⏱ ─"

            if HAS_WMI:
                c      = wmi.WMI()
                cpu    = int(c.Win32_Processor()[0].LoadPercentage or 0)
                os_obj = c.Win32_OperatingSystem()[0]
                total  = int(os_obj.TotalVisibleMemorySize)
                free   = int(os_obj.FreePhysicalMemory)
                ram    = int(((total - free) / total) * 100)
                boot   = datetime.strptime(
                    os_obj.LastBootUpTime.split(".")[0], "%Y%m%d%H%M%S")
                up     = datetime.now() - boot
                upstr  = f"⏱ {up.days}d {up.seconds // 3600}h {(up.seconds // 60) % 60}m"

                for d in c.Win32_LogicalDisk(DriveType=3):
                    try:
                        pct = int(((int(d.Size) - int(d.FreeSpace)) / int(d.Size)) * 100)
                        drives.append((d.DeviceID, pct))
                    except Exception:
                        pass

            # Network via psutil
            dn_str = up_str = "─ KB/s"
            if HAS_PSUTIL:
                counters = psutil.net_io_counters()
                now      = time.monotonic()
                if self._net_prev and self._net_time:
                    dt = now - self._net_time
                    if dt > 0:
                        dn = (counters.bytes_recv - self._net_prev.bytes_recv) / dt / 1024
                        up = (counters.bytes_sent - self._net_prev.bytes_sent) / dt / 1024
                        dn_str = f"{dn:.1f} MB/s" if dn >= 1024 else f"{dn:.1f} KB/s"
                        up_str = f"{up:.1f} MB/s" if up >= 1024 else f"{up:.1f} KB/s"
                self._net_prev = counters
                self._net_time = now

            self.root.after(0, lambda: self._apply_system(
                cpu, ram, drives, upstr, dn_str, up_str))
        except Exception:
            pass

    def _apply_system(self, cpu, ram, drives, upstr, dn, up):
        cc = self._usage_color(cpu)
        self._draw_bar(self.cpu_bar, cpu, cc)
        self.cpu_lbl.config(text=f"{cpu} %", fg=cc)

        rc = self._usage_color(ram)
        self._draw_bar(self.ram_bar, ram, rc)
        self.ram_lbl.config(text=f"{ram} %", fg=rc)

        self.net_dn.config(text=dn)
        self.net_up.config(text=up)
        self.uptime_lbl.config(text=upstr)

        for w in self.drive_frame.winfo_children():
            w.destroy()
        for letter, pct in drives:
            row = tk.Frame(self.drive_frame, bg=self.t["bg"])
            row.pack(fill=tk.X, pady=1)
            clr = self._usage_color(pct)
            tk.Label(row, text=letter, font=("Segoe UI", 8),
                     fg=self.t["text2"], bg=self.t["bg"],
                     width=4, anchor="w").pack(side=tk.LEFT)
            c = tk.Canvas(row, width=100, height=4, bg=self.t["bg3"],
                          highlightthickness=0, bd=0)
            c.pack(side=tk.LEFT, padx=(4, 6))
            c.create_rectangle(0, 0, max(2, pct), 4, fill=clr, outline="")
            tk.Label(row, text=f"{pct}%", font=("Segoe UI", 8, "bold"),
                     fg=clr, bg=self.t["bg"], width=4).pack(side=tk.LEFT)

    def _poll_sessions(self):
        threading.Thread(target=self._check_sessions, daemon=True).start()
        self.root.after(3000, self._poll_sessions)

    def _check_sessions(self):
        try:
            out = subprocess.run("tasklist /fo csv /nh", capture_output=True,
                                 text=True, shell=True, timeout=5).stdout.lower()
            updates = {name: cfg["proc"].lower() in out
                       for name, cfg in AI_TOOLS.items()}
            self.root.after(0, lambda u=updates: self._apply_dots(u))
        except Exception:
            pass

    def _apply_dots(self, updates):
        t = self.t
        for name, active in updates.items():
            if name in self._ai_dots:
                self._ai_dots[name].config(fg=t["dot_on"] if active else t["dot_off"])

    # ──────────────────────────────────────────────
    # Theme switching
    # ──────────────────────────────────────────────

    def _switch_theme(self, _event=None):
        name = self._theme_var.get()
        self.config["theme"] = name
        self._save_config()
        self._set_status(f"Theme → {name}  (restarting…)")
        self.root.after(600, self._restart)

    def _restart(self):
        self._save_config()
        self.root.destroy()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # ──────────────────────────────────────────────
    # Window management
    # ──────────────────────────────────────────────

    def _drag_start(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _drag_move(self, event):
        self.root.geometry(
            f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def _on_close(self):
        self._save_config()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# ============================================================================
# ENTRY POINT
# ============================================================================

def _single_instance():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 57351))
        return s
    except OSError:
        print("AI Hub v5 is already running.")
        sys.exit(1)


if __name__ == "__main__":
    _sock = _single_instance()
    AIHub().run()
