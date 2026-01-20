# plotting functions placeholder

"""
core/plotting.py
Gestione del plotting TIC / BPC / MS1
Versione riscritta 2026 – Python 3.12
"""

import numpy as np
import matplotlib.pyplot as plt


class PlotManager:
    """
    Responsabile del disegno dei tre pannelli principali:
    - TIC
    - BPC
    - MS1

    Gli stili sono centralizzati e modificabili tramite StyleEditor.
    """

    def __init__(self):
        # Stili di default (Fluent UI oriented)
        self.style_tic = {"color": "#2b579a", "linewidth": 1.7}
        self.style_bpc = {"color": "#107c10", "linewidth": 1.7}
        self.style_ms1 = {"color": "#000000", "linewidth": 1.2}

        # Etichette picchi (registrate dal PeakPickingCore)
        self.peak_labels = {
            "tic": [],
            "bpc": [],
            "ms1": []
        }

    # ==========================================================
    # RESET PANNELLI
    # ==========================================================
    def reset_axes(self, ax, title: str):
        """
        Pulisce un asse e lo prepara con una griglia sobria in stile Fluent.
        """
        ax.clear()
        ax.set_title(title, pad=10)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.grid(True, alpha=0.25)

    # ==========================================================
    # TIC
    # ==========================================================
    def plot_tic(self, ax, loader):
        """
        Disegna TIC con stile moderno.
        """
        ax.clear()
        ax.plot(
            loader.tic_times,
            loader.tic_values,
            color=self.style_tic["color"],
            linewidth=self.style_tic["linewidth"]
        )

        ax.set_title("Total Ion Chromatogram (TIC)", pad=10)
        ax.set_xlabel("Tempo (min)")
        ax.set_ylabel("Intensità")
        ax.grid(True, alpha=0.25)

    # ==========================================================
    # BPC
    # ==========================================================
    def plot_bpc(self, ax, loader):
        """
        Disegna BPC con stile moderno.
        """
        ax.clear()
        ax.plot(
            loader.bpc_times,
            loader.bpc_values,
            color=self.style_bpc["color"],
            linewidth=self.style_bpc["linewidth"]
        )

        ax.set_title("Base Peak Chromatogram (BPC)", pad=10)
        ax.set_xlabel("Tempo (min)")
        ax.set_ylabel("Intensità")
        ax.grid(True, alpha=0.25)

    # ==========================================================
    # MS1
    # ==========================================================
    def plot_ms1(self, ax, loader, mz=None, intensities=None, rt=None):
        """
        Disegna lo spettro MS1.
        Se vengono passati mz e intensities → spettro specifico (es. dal click).
        Se no → usa il primo MS1 del loader.
        """
        ax.clear()

        if mz is None:
            if loader.ms1_mz is None:
                return
            mz = loader.ms1_mz
            intensities = loader.ms1_int
            ax.set_title("Spettro MS1 (primo scan)", pad=10)
        else:
            ax.set_title(f"MS1 @ RT = {rt:.2f} min", pad=10)

        markerline, stemlines, baseline = ax.stem(
            mz, intensities,
            basefmt=" ",
            markerfmt=" ",
            linefmt=self.style_ms1["color"]
        )

        # Uniform stem linewidth
        try:
            for s in stemlines:
                s.set_linewidth(self.style_ms1["linewidth"])
        except Exception:
            stemlines.set_linewidth(self.style_ms1["linewidth"])

        ax.set_xlabel("m/z")
        ax.set_ylabel("Intensità")
        ax.grid(True, alpha=0.25)

        # Autoscale margins
        ymax = float(np.max(intensities))
        ax.set_ylim(0, ymax * 1.25)

    # ==========================================================
    # STYLE UPDATE (usato da Style Editor)
    # ==========================================================
    def set_style(self, spectrum, color=None, linewidth=None):
        """
        Aggiorna lo stile di un determinato spettro.
        spectrum: "tic" | "bpc" | "ms1"
        """
        mapping = {
            "tic": self.style_tic,
            "bpc": self.style_bpc,
            "ms1": self.style_ms1
        }

        if spectrum not in mapping:
            return

        style = mapping[spectrum]

        if color:
            style["color"] = color
        if linewidth is not None:
            style["linewidth"] = linewidth

    # ==========================================================
    # PEAK LABEL MANAGEMENT
    # gestiti in modo collaborativo con PeakPickingCore
    # ==========================================================
    def clear_peak_labels(self, ax_key: str, ax):
        """
        Rimuove tutte le etichette dei picchi presenti su un asse.
        """
        if ax_key not in self.peak_labels:
            return

        for label in self.peak_labels[ax_key]:
            try:
                label.remove()
            except Exception:
                pass

        self.peak_labels[ax_key] = []
        ax.figure.canvas.draw_idle()

    def add_peak_label(self, ax_key: str, ax, x, y, text,
                       color="red", fontsize=8):
        """
        Aggiunge un'etichetta di picco sopra lo spettro.
        """
        lbl = ax.text(
            x, y, text,
            ha="center",
            va="bottom",
            fontsize=fontsize,
            color=color
        )
        self.peak_labels[ax_key].append(lbl)

    # ==========================================================
    # SUPPORTO UTILITY
    # ==========================================================
    def apply_y_padding(self, ax, factor=0.12):
        """
        Aggiunge padding verticale per dare spazio a label e T-bars.
        """
        ymin, ymax = ax.get_ylim()
        yr = ymax - ymin
        ax.set_ylim(ymin, ymax + yr * factor)
