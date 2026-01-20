# ms2 viewer placeholder

"""
core/ms2_viewer.py
Viewer MS2 moderno – LC–MS Viewer (rewrite 2026)
Python 3.12
"""

import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class MS2Viewer:
    """
    Finestra interattiva per visualizzare gli spettri MS2.

    Riceve dal loader una lista di dict con:
    - rt
    - precursor
    - mz[]
    - int[]
    """

    def __init__(self):
        self.window = None

    # ==========================================================
    # APERTURA VIEWER
    # ==========================================================
    def open(self, root, ms2_list):
        """
        Apre la finestra MS2 viewer.
        ms2_list = lista di spettri MS2 caricati dal loader
        """
        if not ms2_list:
            return

        # Se già aperta → focus
        if self.window and tk.Toplevel.winfo_exists(self.window):
            self.window.lift()
            return

        self.window = tk.Toplevel(root)
        self.window.title("MS2 – Visualizzatore Interattivo")
        self.window.geometry("980x540")
        self.window.minsize(900, 500)

        # UI setup
        self._build_ui(ms2_list)

    # ==========================================================
    # UI
    # ==========================================================
    def _build_ui(self, ms2_list):
        # ---------------- LEFT LIST ----------------
        frame_left = tk.Frame(self.window, bg="#e1e2e5")
        frame_left.pack(side="left", fill="y", padx=10, pady=10)

        lbl = tk.Label(
            frame_left,
            text="Spettri MS2:",
            bg="#e1e2e5",
            fg="#2b579a",
            font=("Segoe UI", 12, "bold")
        )
        lbl.pack(anchor="w", pady=(0, 5))

        scrollbar = tk.Scrollbar(frame_left)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            frame_left,
            width=42,
            height=25,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 10)
        )
        self.listbox.pack(side="left", fill="y")
        scrollbar.config(command=self.listbox.yview)

        # Popola lista
        for i, spec in enumerate(ms2_list):
            rt = spec["rt"]
            prec = spec["precursor"]
            self.listbox.insert(
                tk.END,
                f"Scan {i+1} • RT={rt:.2f} min • Prec={prec:.4f}"
            )

        # ---------------- RIGHT PLOT ----------------
        frame_plot = tk.Frame(self.window, bg="#f3f3f5")
        frame_plot.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.fig = Figure(figsize=(6, 4), dpi=100, layout="constrained")
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_plot)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Event binding
        self.listbox.bind("<<ListboxSelect>>",
                          lambda e: self._on_selection(ms2_list))

    # ==========================================================
    # PLOT MS2
    # ==========================================================
    def _on_selection(self, ms2_list):
        sel = self.listbox.curselection()
        if not sel:
            return

        idx = sel[0]
        spec = ms2_list[idx]

        mz = spec["mz"]
        intens = spec["int"]
        rt = spec["rt"]
        precursor = spec["precursor"]

        self._plot_spectrum(mz, intens, rt, precursor)

    def _plot_spectrum(self, mz, intens, rt, precursor):
        """
        Disegna spettro MS2 singolo.
        """
        self.ax.clear()

        markerline, stemlines, baseline = self.ax.stem(
            mz, intens,
            basefmt=" ",
            markerfmt=" ",
            linefmt="#2b579a"
        )

        try:
            for s in stemlines:
                s.set_linewidth(1.3)
        except Exception:
            stemlines.set_linewidth(1.3)

        self.ax.set_title(
            f"Spettro MS2\nPrec={precursor:.4f} m/z • RT={rt:.2f} min",
            pad=10,
            fontsize=11
        )
        self.ax.set_xlabel("m/z")
        self.ax.set_ylabel("Intensità")
        self.ax.grid(True, alpha=0.25)

        # Autoscale
        if len(intens) > 0:
            ymax = float(max(intens))
            self.ax.set_ylim(0, ymax * 1.25)

        self.canvas.draw_idle()
