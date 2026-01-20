# style IO placeholder

"""
utils/styles_io.py
Style editor moderno per LC–MS Viewer (rewrite 2026)
Python 3.12
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.colorchooser import askcolor
import json


class StylesIO:
    """
    Gestisce:
    - Style Editor (finestra)
    - Salvataggio / caricamento stili JSON
    - Applicazione a PlotManager
    """

    # ==========================================================
    # STYLE EDITOR
    # ==========================================================
    def open_editor(self, root, plotman, canvas):
        win = tk.Toplevel(root)
        win.title("Style Editor — LC–MS Viewer")
        win.geometry("430x580")
        win.resizable(False, False)
        win.attributes("-topmost", True)

        # ------------------------------
        # SEZIONE: TITOLI
        # ------------------------------
        tk.Label(
            win, text="Editor Stili Spettri",
            font=("Segoe UI", 13, "bold")
        ).pack(pady=12)

        # ==========================================================
        # TIC
        # ==========================================================
        tk.Label(
            win, text="TIC — Total Ion Chromatogram",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(10, 4))

        ttk.Button(
            win, text="Colore TIC",
            command=lambda: self._pick_color("tic", plotman, canvas)
        ).pack(fill="x", padx=20, pady=3)

        self._make_linewidth_slider(win, "tic", plotman, canvas)

        # ==========================================================
        # BPC
        # ==========================================================
        tk.Label(
            win, text="BPC — Base Peak Chromatogram",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(18, 4))

        ttk.Button(
            win, text="Colore BPC",
            command=lambda: self._pick_color("bpc", plotman, canvas)
        ).pack(fill="x", padx=20, pady=3)

        self._make_linewidth_slider(win, "bpc", plotman, canvas)

        # ==========================================================
        # MS1
        # ==========================================================
        tk.Label(
            win, text="MS1 — Spettro di Massa",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(18, 4))

        ttk.Button(
            win, text="Colore MS1",
            command=lambda: self._pick_color("ms1", plotman, canvas)
        ).pack(fill="x", padx=20, pady=3)

        self._make_linewidth_slider(win, "ms1", plotman, canvas)

        # ==========================================================
        # GRIGLIA E SFONDO
        # ==========================================================
        tk.Label(
            win, text="Grafica",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=20)

        ttk.Button(
            win,
            text="Colore griglia",
            command=lambda: self._pick_grid_color(plotman, canvas)
        ).pack(fill="x", padx=20, pady=3)

        ttk.Button(
            win,
            text="Colore sfondo del pannello",
            command=lambda: self._pick_panel_color(plotman, canvas)
        ).pack(fill="x", padx=20, pady=3)

        # ==========================================================
        # SALVATAGGIO / CARICAMENTO
        # ==========================================================
        tk.Label(
            win, text="Salvataggio / Caricamento",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=20)

        ttk.Button(
            win, text="Salva stile",
            command=lambda: self.save_styles(plotman)
        ).pack(fill="x", padx=20, pady=5)

        ttk.Button(
            win, text="Carica stile",
            command=lambda: self.load_styles(plotman, canvas)
        ).pack(fill="x", padx=20, pady=5)

        # ==========================================================
        # CHIUDI EDITOR
        # ==========================================================
        ttk.Button(
            win, text="Chiudi",
            command=win.destroy
        ).pack(fill="x", padx=20, pady=20)

    # ==========================================================
    # SLIDER LINEWIDTH
    # ==========================================================
    def _make_linewidth_slider(self, win, spectrum, plotman, canvas):
        frame = tk.Frame(win)
        frame.pack(fill="x", padx=20, pady=2)

        tk.Label(frame, text="Spessore linea:", font=("Segoe UI", 9)).pack(anchor="w")
        slider = ttk.Scale(
            frame, from_=0.5, to=5.0, value=plotman.__dict__[f"style_{spectrum}"]["linewidth"],
            orient="horizontal",
            command=lambda value: self._update_linewidth(
                spectrum, float(value), plotman, canvas
            )
        )
        slider.pack(fill="x")

    # ==========================================================
    # PICK COLOR
    # ==========================================================
    def _pick_color(self, spectrum, plotman, canvas):
        color = askcolor(title=f"Colore {spectrum.upper()}")[1]
        if not color:
            return
        plotman.set_style(spectrum, color=color)
        canvas.draw_idle()

    def _update_linewidth(self, spectrum, lw, plotman, canvas):
        plotman.set_style(spectrum, linewidth=lw)
        canvas.draw_idle()

    # ==========================================================
    # GRIGLIA E SFONDO
    # ==========================================================
    def _pick_grid_color(self, plotman, canvas):
        color = askcolor(title="Colore griglia")[1]
        if not color:
            return

        # Applica a tutte le axes
        for ax in canvas.figure.get_axes():
            ax.grid(color=color)
        canvas.draw_idle()

    def _pick_panel_color(self, plotman, canvas):
        color = askcolor(title="Colore sfondo pannello")[1]
        if not color:
            return

        for ax in canvas.figure.get_axes():
            ax.set_facecolor(color)
        canvas.draw_idle()

    # ==========================================================
    # SALVATAGGIO STILI
    # ==========================================================
    def save_styles(self, plotman):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            title="Salva stile",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not path:
            return

        styles = {
            "tic": plotman.style_tic,
            "bpc": plotman.style_bpc,
            "ms1": plotman.style_ms1,
        }

        try:
            with open(path, "w") as f:
                json.dump(styles, f, indent=4)
            messagebox.showinfo("Stile salvato", "Stile salvato correttamente.")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare lo stile:\n\n{e}")

    # ==========================================================
    # CARICAMENTO STILI
    # ==========================================================
    def load_styles(self, plotman, canvas):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Carica stile",
            filetypes=[("JSON files", "*.json")]
        )
        if not path:
            return

        try:
            with open(path, "r") as f:
                styles = json.load(f)

            plotman.style_tic = styles.get("tic", plotman.style_tic)
            plotman.style_bpc = styles.get("bpc", plotman.style_bpc)
            plotman.style_ms1 = styles.get("ms1", plotman.style_ms1)

            canvas.draw_idle()
            messagebox.showinfo("Stile caricato", "Stile applicato correttamente.")

        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare lo stile:\n\n{e}")
