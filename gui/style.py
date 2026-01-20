# Style definitions placeholder

"""
gui/style.py
Stile Fluent UI per LC–MS Viewer (rewrite 2026)
Python 3.12
"""

import tkinter as tk
from tkinter import ttk

# Palette Fluent UI
FLUENT_BG = "#f3f3f5"
FLUENT_SIDEBAR = "#e1e2e5"
FLUENT_HEADER = "#d6d7da"
FLUENT_ACCENT = "#2b579a"
FLUENT_ACCENT_HOVER = "#1f4e8f"
FLUENT_TEXT = "#1a1a1a"
FLUENT_TEXT_LIGHT = "#ffffff"


class FluentStyle:
    """
    Applica uno stile moderno Fluent UI all'intera applicazione.
    Deve essere inizializzato *prima* della creazione di widget complessi.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style()
        self._configure_global()
        self._configure_buttons()
        self._configure_labels()
        self._configure_scales()
        self._configure_frames()
        self._configure_theme()

    # ==========================================================
    # GLOBAL SETTINGS
    # ==========================================================
    def _configure_global(self):
        """
        Impostazioni globali: font, bg generale.
        """
        default_font = ("Segoe UI", 10)
        self.root.option_add("*Font", default_font)
        self.root.configure(bg=FLUENT_BG)

        try:
            self.style.theme_use("clam")
        except Exception:
            pass

    # ==========================================================
    # BUTTONS (TTK)
    # ==========================================================
    def _configure_buttons(self):
        self.style.configure(
            "TButton",
            padding=6,
            background=FLUENT_SIDEBAR,
            foreground=FLUENT_TEXT,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        self.style.map(
            "TButton",
            background=[("active", FLUENT_ACCENT_HOVER)],
            foreground=[("active", FLUENT_TEXT_LIGHT)]
        )

        # Bottoni speciali (ad esempio nel Style Editor)
        self.style.configure(
            "Accent.TButton",
            padding=6,
            background=FLUENT_ACCENT,
            foreground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold")
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", FLUENT_ACCENT_HOVER)]
        )

    # ==========================================================
    # LABELS
    # ==========================================================
    def _configure_labels(self):
        self.style.configure(
            "Header.TLabel",
            background=FLUENT_HEADER,
            foreground=FLUENT_ACCENT,
            font=("Segoe UI", 16, "bold")
        )

        self.style.configure(
            "Sidebar.TLabel",
            background=FLUENT_SIDEBAR,
            foreground=FLUENT_ACCENT,
            font=("Segoe UI", 11, "bold")
        )

        self.style.configure(
            "TLabel",
            background=FLUENT_BG,
            foreground=FLUENT_TEXT
        )

    # ==========================================================
    # SCALES / SLIDERS
    # ==========================================================
    def _configure_scales(self):
        self.style.configure(
            "Horizontal.TScale",
            background=FLUENT_BG,
            troughcolor="#d0d1d3"
        )

    # ==========================================================
    # FRAMES / SEPARATORS
    # ==========================================================
    def _configure_frames(self):
        self.style.configure(
            "TFrame",
            background=FLUENT_BG
        )
        self.style.configure(
            "Card.TFrame",
            background=FLUENT_SIDEBAR,
            relief="flat"
        )

    # ==========================================================
    # THEME WRAPPER
    # ==========================================================
    def _configure_theme(self):
        """
        Imposta alcune varianti generiche di stile usate nel layout.
        """
        self.style.configure(
            "SidebarButton.TButton",
            background=FLUENT_SIDEBAR,
            foreground=FLUENT_TEXT,
            anchor="w",
            padding=8
        )
        self.style.map(
            "SidebarButton.TButton",
            background=[("active", FLUENT_ACCENT_HOVER)],
            foreground=[("active", FLUENT_TEXT_LIGHT)]
        )
