# zoom logic placeholder

"""
core/zoom.py
Modulo di gestione zoom, click e scroll del LC–MS Viewer.
Versione riscritta 2026 – Python 3.12
"""

import numpy as np
from matplotlib.patches import Rectangle
import time


class ZoomController:
    """
    Gestisce:
    - zoom rettangolare TIC/BPC (solo asse X)
    - scroll verticale (asse Y)
    - sincronizzazione TIC ↔ BPC
    - aggiornamento MS1 in base al range RT visibile
    - click → cerca MS1 più vicino
    """

    def __init__(self):
        # Stato zoom rettangolare
        self.zoom_active = False
        self.x0 = None
        self.rect_artist = None
        self._last_motion_ts = 0

    # ==========================================================
    # EVENTI PRINCIPALI
    # ==========================================================
    def on_click(self, event, ax_tic, ax_bpc, ax_ms1, loader, plotting):
        """
        Click sinistro:
        - se click sui cromatogrammi → MS1 @ RT più vicino
        - prepara zoom rettangolare
        """
        if event.button != 1:
            return

        # CLICK SU TIC / BPC → aggiorna MS1
        if event.inaxes in [ax_tic, ax_bpc]:
            if event.xdata is not None:
                closest = loader.get_closest_ms1(event.xdata)
                if closest:
                    rt, mz, intens = closest
                    plotting.plot_ms1(ax_ms1, loader, mz=mz,
                                      intensities=intens, rt=rt)
            # Preparazione zoom rettangolare
            self.zoom_active = True
            self.x0 = event.xdata
            self._draw_zoom_rect(event.inaxes, self.x0, self.x0)

    def on_motion(self, event):
        """
        Ridisegna in tempo reale il rettangolo di zoom.
        """
        if not self.zoom_active:
            return
        if event.inaxes is None or event.xdata is None:
            return

        # Limite frequenza aggiornamento (60 FPS)
        now = time.perf_counter()
        if now - self._last_motion_ts < (1 / 60):
            return
        self._last_motion_ts = now

        self._draw_zoom_rect(event.inaxes, self.x0, event.xdata)

    def on_release(self, event, ax_tic, ax_bpc, ax_ms1, loader, plotting):
        """
        Alla fine del drag:
        - calcola nuovo range X
        - sincronizza TIC ↔ BPC
        - aggiorna MS1 alla finestra RT
        """
        if not self.zoom_active:
            return

        self.zoom_active = False
        if event.inaxes not in [ax_tic, ax_bpc]:
            self._clear_rect()
            return

        if self.x0 is None or event.xdata is None:
            self._clear_rect()
            return

        xmin, xmax = sorted([self.x0, event.xdata])
        if abs(xmax - xmin) < 1e-9:
            self._clear_rect()
            return

        # Imposta zoom sull’asse selezionato
        target = event.inaxes
        target.set_xlim(xmin, xmax)

        # Sync TIC ↔ BPC
        if target is ax_tic:
            ax_bpc.set_xlim(xmin, xmax)
        elif target is ax_bpc:
            ax_tic.set_xlim(xmin, xmax)

        # MS1 alla finestra
        self._update_ms1_range(ax_ms1, loader, xmin, xmax, plotting)

        self._clear_rect()

    def on_scroll(self, event):
        """
        Scroll del mouse:
        - zoom verticale (asse Y)
        """
        if event.inaxes is None:
            return

        ax = event.inaxes
        ymin, ymax = ax.get_ylim()
        center = (ymin + ymax) / 2

        # Scroll up = zoom in verticale
        scale = 0.9 if event.button == "up" else 1.1

        rng = (ymax - ymin) * scale
        new_ymin = center - rng / 2
        new_ymax = center + rng / 2

        ax.set_ylim(new_ymin, new_ymax)

    # ==========================================================
    # SUPPORTO ZOOM RETTANGOLARE
    # ==========================================================
    def _draw_zoom_rect(self, ax, x0, x1):
        """Disegna o aggiorna il rettangolo di zoom."""
        self._clear_rect()

        xmin, xmax = sorted([x0, x1])
        ymin, ymax = ax.get_ylim()

        rect = Rectangle((xmin, ymin),
                         xmax - xmin,
                         ymax - ymin,
                         fill=False,
                         edgecolor="red",
                         linestyle="--",
                         linewidth=1.3,
                         alpha=0.8)
        ax.add_patch(rect)
        self.rect_artist = rect
        ax.figure.canvas.draw_idle()

    def _clear_rect(self):
        """Elimina il rettangolo di zoom."""
        if self.rect_artist is not None:
            try:
                self.rect_artist.remove()
            except Exception:
                pass
            self.rect_artist = None

    # ==========================================================
    # MS1 SYNC
    # ==========================================================
    def _update_ms1_range(self, ax_ms1, loader, xmin, xmax, plotting):
        """
        Trova lo spettro MS1 più vicino al centro della finestra RT zoomata.
        """
        if not loader.ms1_spectra:
            return

        center = (xmin + xmax) / 2
        closest = loader.get_closest_ms1(center)
        if closest:
            rt, mz, intens = closest
            plotting.plot_ms1(ax_ms1, loader, mz=mz,
                              intensities=intens, rt=rt)

    # ==========================================================
    # RESET
    # ==========================================================
    def reset_all(self, ax_tic, ax_bpc, ax_ms1, loader, plotting):
        """
        Reset globale dello zoom:
        - TIC/BPC: limiti interi
        - MS1: primo spettro
        """
        if loader.tic_times:
            ax_tic.set_xlim(min(loader.tic_times), max(loader.tic_times))
        if loader.bpc_times:
            ax_bpc.set_xlim(min(loader.bpc_times), max(loader.bpc_times))

        # Reset MS1
        if loader.ms1_mz is not None:
            plotting.plot_ms1(ax_ms1, loader)
