# peak picking placeholder

"""
core/peak_picking.py
Peak picking moderno e modulare per LC–MS Viewer (rewrite 2026)
Python 3.12
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.signal import find_peaks


class PeakPickingCore:
    """
    Gestisce il peak picking per:
    - TIC
    - BPC
    - MS1

    Delegando il disegno delle T-bars e delle etichette al PlotManager.
    """

    def __init__(self):
        # Parametri default
        self.default_percent_threshold = 5.0

    # ==========================================================
    # FINESTRA PARAMETRI PEAK PICKING
    # ==========================================================
    def open_window(self, root, figure, canvas):
        """
        Crea una piccola finestra per impostare la soglia %.
        """
        win = tk.Toplevel(root)
        win.title("Peak Picking Automatico")
        win.geometry("330x140")
        win.resizable(False, False)
        win.attributes("-topmost", True)

        ttk.Label(win, text="Soglia (% del massimo):",
                  font=("Segoe UI", 10)).pack(pady=8)

        percent_var = tk.StringVar(value=str(self.default_percent_threshold))
        entry = ttk.Entry(win, width=10, textvariable=percent_var)
        entry.pack()

        ttk.Button(
            win,
            text="Esegui Peak Picking",
            command=lambda: self._run_pp(
                percent_var, figure, canvas, root, win
            ),
            style="TButton"
        ).pack(pady=10)

    # ==========================================================
    # ESECUZIONE PEAK PICKING
    # ==========================================================
    def _run_pp(self, percent_var, figure, canvas, root, win_param):
        """
        Avvia effettivamente il peak picking sull’asse corrente.
        """
        try:
            percent = float(percent_var.get())
        except ValueError:
            messagebox.showwarning("Valore non valido",
                                   "La soglia deve essere numerica.")
            return

        ax = figure.gca()
        lines = ax.get_lines()
        if not lines:
            messagebox.showwarning(
                "Nessuna curva",
                "Non c’è alcun grafico visibile."
            )
            return

        # Dati dell’asse corrente
        x = np.array(lines[0].get_xdata())
        y = np.array(lines[0].get_ydata())

        peaks, threshold = self._detect_peaks(y, percent)

        if peaks.size == 0:
            messagebox.showinfo("Peak Picking", "Nessun picco trovato.")
            return

        # Rimuovi eventuali etichette precedenti
        ax_key = self._axis_key(ax, figure)
        plotman = root.app.plotting if hasattr(root, "app") else None
        if plotman:
            plotman.clear_peak_labels(ax_key, ax)

        # Disegna T-bars e labels
        if plotman:
            self._draw_peak_bars(ax_key, ax, x, y, peaks, plotman)

        canvas.draw_idle()

        # Mostra lista picchi
        self._list_window(root, x, y, peaks)

    # ==========================================================
    # RICONOSCIMENTO PICCHI
    # ==========================================================
    def _detect_peaks(self, y, percent):
        """
        Riconosce picchi usando find_peaks con:
        - soglia (% del massimo)
        - distanza minima proporzionale alla lunghezza del vettore
        - limitata prominenza minima per evitare falsi positivi
        """
        if len(y) < 5:
            return np.array([], dtype=int), 0

        max_y = float(np.max(y))
        threshold = max_y * (percent / 100.0)

        distance = max(1, len(y) // 200)
        prominence = (max_y - float(np.min(y))) * 0.05

        peaks, properties = find_peaks(
            y,
            height=threshold,
            distance=distance,
            prominence=prominence
        )

        return peaks, threshold

    # ==========================================================
    # DISEGNO PICCHI (T‑bars + label)
    # ==========================================================
    def _draw_peak_bars(self, ax_key, ax, x, y, peaks, plotman):
        """
        Disegna le T-bar dei picchi delegando il disegno a PlotManager.
        """
        x_peaks = x[peaks]
        y_peaks = y[peaks]

        # Altezza delle T-bars (stile semplice, short)
        ymin, ymax = ax.get_ylim()
        yr = ymax - ymin
        cap_height = yr * 0.03
        label_offset = yr * 0.04

        # Disegna T-bar
        for xp, yp in zip(x_peaks, y_peaks):
            # Linea verticale
            ax.vlines(xp, yp, yp + cap_height,
                      colors="red", linewidth=1.5)

            # Cap orizzontale
            ax.hlines(yp + cap_height,
                      xp - (x.max() - x.min()) * 0.002,
                      xp + (x.max() - x.min()) * 0.002,
                      colors="red", linewidth=1.5)

        # Label
        for xp, yp in zip(x_peaks, y_peaks):
            label_y = yp + cap_height + label_offset
            lbl_text = f"{xp:.4f}" if ax_key == "ms1" else f"{xp:.2f}"
            plotman.add_peak_label(ax_key, ax, xp, label_y, lbl_text,
                                   color="red", fontsize=8)

        ax.set_ylim(ymin, ymax + yr * 0.15)

    # ==========================================================
    # LISTA PICCHI (finestra)
    # ==========================================================
    def _list_window(self, root, x, y, peaks):
        """
        Mostra finestra con risultato del peak picking.
        """
        win = tk.Toplevel(root)
        win.title("Picchi rilevati")
        win.geometry("360x320")
        win.attributes("-topmost", True)

        tk.Label(win, text="Lista picchi:",
                 font=("Segoe UI", 11, "bold")).pack(pady=6)

        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(
            frame,
            width=45,
            height=15,
            yscrollcommand=scrollbar.set
        )
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        for i, p in enumerate(peaks):
            listbox.insert(
                tk.END,
                f"Picco {i+1:02d} → x = {x[p]:.4f}, y = {y[p]:.2f}"
            )

    # ==========================================================
    # UTILITY
    # ==========================================================
    def _axis_key(self, ax, figure):
        """
        Restituisce quale asse è stato analizzato:
        'tic', 'bpc', 'ms1'
        Serve al PlotManager per sapere dove memorizzare le label.
        """
        axes = figure.get_axes()
        if ax is axes[0]:
            return "tic"
        elif ax is axes[1]:
            return "bpc"
        else:
            return "ms1"
