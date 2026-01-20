# GUI layout placeholder


"""
gui/layout.py
Layout Fluent UI per LC–MS Scientific Viewer (rewrite 2026)
Python 3.12
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import dei moduli core (saranno popolati successivamente)
from core.loader import MZMLLoader
from core.plotting import PlotManager
from core.zoom import ZoomController
from core.peak_picking import PeakPickingCore
from core.ms2_viewer import MS2Viewer
from core.converter import RAWConverter
from utils.styles_io import StylesIO
from utils.file_dialogs import FileDialogs

# -------------------------------------------------------------------
#  FLUENT UI COLOR PALETTE
# -------------------------------------------------------------------
FLUENT_BG = "#f3f3f5"
FLUENT_SIDEBAR = "#e1e2e5"
FLUENT_HEADER = "#d6d7da"
FLUENT_ACCENT = "#2b579a"
FLUENT_ACCENT_HOVER = "#1f4e8f"
FLUENT_TEXT = "#1a1a1a"


# -------------------------------------------------------------------
#  ICON LOADER
# -------------------------------------------------------------------
def load_icon(icon_name: str, size=(22, 22)):
    """
    Carica icone PNG dalla cartella icons/.
    Le SVG saranno presenti solo come risorsa futura.
    """
    base = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base, "icons", f"{icon_name}.png")

    if not os.path.exists(icon_path):
        # icona fallback (un quadrato grigio)
        img = tk.PhotoImage(width=size[0], height=size[1])
        img.put(("gray",), to=(0, 0, size[0], size[1]))
        return img

    img = tk.PhotoImage(file=icon_path)
    return img.subsample(max(1, img.width() // size[0]),
                         max(1, img.height() // size[1]))


# -------------------------------------------------------------------
#  APP CLASS
# -------------------------------------------------------------------
class LCMSViewerApp:
    def __init__(self, root: tk.Tk):
        from gui.style import FluentStyle
        
        self.root = root
        # Applica subito stile Fluent UI all’intera app
        FluentStyle(root)
        self.root.configure(bg=FLUENT_BG)
        self.root.geometry("1500x950")
        self.root.minsize(1200, 850)

        # -------------------------------
        # ISTANZA MODULI CORE
        # -------------------------------
        self.loader = MZMLLoader()
        self.plotting = PlotManager()
        self.zoom = ZoomController()
        self.peak_core = PeakPickingCore()
        self.ms2_viewer = MS2Viewer()
        self.converter = RAWConverter()
        self.styles_io = StylesIO()
        self.dialogs = FileDialogs()

        # Variabili di stato / stile
        self.current_mzml = None
        self.icons = {}
        self._load_all_icons()

        # Costruzione layout
        self._build_header()
        self._build_sidebar()
        self._build_main_area()

        # Collegamento iniziale degli eventi
        self._bind_plot_events()

    # ----------------------------------------------------------
    # ICONS LOADING
    # ----------------------------------------------------------
    def _load_all_icons(self):
        """
        Carica tutte le icone necessarie (PNG).
        Il file ZIP avrà anche le SVG, ma qui usiamo PNG.
        """
        icon_list = [
            "open", "convert", "close", "tic", "bpc", "ms1",
            "ms2", "zoom", "reset", "peak", "style", "export",
            "home"
        ]

        for name in icon_list:
            self.icons[name] = load_icon(name)

    # ----------------------------------------------------------
    # HEADER
    # ----------------------------------------------------------
    def _build_header(self):
        self.header = tk.Frame(self.root, bg=FLUENT_HEADER, height=58)
        self.header.pack(fill="x", side="top")

        title = tk.Label(
            self.header,
            text="LC–MS Scientific Viewer",
            bg=FLUENT_HEADER,
            fg=FLUENT_ACCENT,
            font=("Segoe UI", 18, "bold"),
            padx=20
        )
        title.pack(anchor="w", pady=10)

    # ----------------------------------------------------------
    # SIDEBAR (Fluent UI style)
    # ----------------------------------------------------------
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=FLUENT_SIDEBAR, width=260)
        self.sidebar.pack(fill="y", side="left")

        # CHAPTER: File
        self._sidebar_title("File")
        self._sidebar_button("Apri mzML", "open", self.open_file)
        self._sidebar_button("Converti RAW → mzML", "convert", self.convert_raw)
        self._sidebar_button("Chiudi spettro", "close", self.close_spectrum)

        self._sidebar_separator()

        # CHAPTER: Views
        self._sidebar_title("Visualizzazioni")
        self._sidebar_button("TIC", "tic", self.plot_tic)
        self._sidebar_button("BPC", "bpc", self.plot_bpc)
        self._sidebar_button("MS1", "ms1", self.plot_ms1)
        self._sidebar_button("MS2 Viewer", "ms2", self.open_ms2)

        self._sidebar_button("Reset Zoom", "reset", self.reset_zoom)

        self._sidebar_separator()

        # CHAPTER: Tools
        self._sidebar_title("Strumenti")
        self._sidebar_button("Peak Picking", "peak", self.open_peak_window)
        self._sidebar_button("Style Editor", "style", self.open_style_editor)
        self._sidebar_button("Esporta grafico", "export", self.export_plot)

    def _sidebar_title(self, text: str):
        lbl = tk.Label(
            self.sidebar,
            text=text,
            bg=FLUENT_SIDEBAR,
            fg=FLUENT_ACCENT,
            font=("Segoe UI", 12, "bold"),
            padx=14,
            pady=6,
            anchor="w"
        )
        lbl.pack(fill="x")

    def _sidebar_button(self, text: str, icon_name: str, command):
        img = self.icons.get(icon_name)
        btn = tk.Button(
            self.sidebar,
            text=f"  {text}",
            image=img,
            compound="left",
            anchor="w",
            bg=FLUENT_SIDEBAR,
            fg=FLUENT_TEXT,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
            padx=12,
            pady=6,
            command=command
        )
        btn.pack(fill="x", padx=10, pady=2)

        # Hover effect Fluent-like
        btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=FLUENT_ACCENT_HOVER, fg="white"))
        btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=FLUENT_SIDEBAR, fg=FLUENT_TEXT))

    def _sidebar_separator(self):
        sep = tk.Frame(self.sidebar, height=1, bg="#c7c8cc")
        sep.pack(fill="x", padx=8, pady=12)

    # ----------------------------------------------------------
    # MAIN AREA: Matplotlib layout
    # ----------------------------------------------------------
    def _build_main_area(self):
        self.main_area = tk.Frame(self.root, bg=FLUENT_BG)
        self.main_area.pack(fill="both", expand=True)

        # Matplotlib Figure
        self.figure = Figure(figsize=(14, 10), dpi=100, layout="constrained")
        self.ax_tic = self.figure.add_subplot(3, 1, 1)
        self.ax_bpc = self.figure.add_subplot(3, 1, 2)
        self.ax_ms1 = self.figure.add_subplot(3, 1, 3)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.main_area)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ----------------------------------------------------------
    # EVENT BINDING
    # ----------------------------------------------------------
    def _bind_plot_events(self):
        """
        Registra i listener di click, zoom e aggiornamento.
        Tutta la logica è delegata ai moduli core.
        """
        self.canvas.mpl_connect("button_press_event", self._on_click)
        self.canvas.mpl_connect("scroll_event", self._on_scroll)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.canvas.mpl_connect("button_release_event", self._on_release)

    # ----------------------------------------------------------
    # FILE OPERATIONS
    # ----------------------------------------------------------
    def open_file(self):
        file_path = self.dialogs.open_mzml()
        if not file_path:
            return

        self.current_mzml = file_path
        self.loader.load(file_path)

        messagebox.showinfo("File caricato",
                            f"Il file è stato caricato:\n\n{os.path.basename(file_path)}")

        self.plot_tic()
        self.plot_bpc()
        self.plot_ms1()

    def convert_raw(self):
        self.converter.batch_convert()

    def close_spectrum(self):
        self.current_mzml = None
        self.loader.reset()
        self.plotting.reset_axes(self.ax_tic, "TIC")
        self.plotting.reset_axes(self.ax_bpc, "BPC")
        self.plotting.reset_axes(self.ax_ms1, "MS1")
        self.canvas.draw_idle()

    # ----------------------------------------------------------
    # PLOTTING ACTIONS
    # ----------------------------------------------------------
    def plot_tic(self):
        if not self.loader.tic_times:
            messagebox.showwarning("Nessun dato", "Carica un file mzML.")
            return
        self.plotting.plot_tic(self.ax_tic, self.loader)
        self.canvas.draw_idle()

    def plot_bpc(self):
        if not self.loader.bpc_times:
            messagebox.showwarning("Nessun dato", "Carica un file mzML.")
            return
        self.plotting.plot_bpc(self.ax_bpc, self.loader)
        self.canvas.draw_idle()

    def plot_ms1(self):
        if self.loader.ms1_mz is None:
            messagebox.showwarning("Nessun dato", "Carica un file mzML.")
            return
        self.plotting.plot_ms1(self.ax_ms1, self.loader)
        self.canvas.draw_idle()

    def open_ms2(self):
        if not self.loader.ms2_spectra:
            messagebox.showwarning("Nessun MS2", "Nessuno spettro MS2 trovato.")
            return
        self.ms2_viewer.open(self.root, self.loader.ms2_spectra)

    # ----------------------------------------------------------
    # PEAK PICKING
    # ----------------------------------------------------------
    def open_peak_window(self):
        self.peak_core.open_window(self.root, self.figure, self.canvas)

    # ----------------------------------------------------------
    # STYLE EDITOR
    # ----------------------------------------------------------
    def open_style_editor(self):
        self.styles_io.open_editor(self.root, self.plotting, self.canvas)

    # ----------------------------------------------------------
    # EXPORT
    # ----------------------------------------------------------
    def export_plot(self):
        self.dialogs.export_figure(self.figure)

    # ----------------------------------------------------------
    # ZOOM + EVENTS
    # ----------------------------------------------------------
    def reset_zoom(self):
        self.zoom.reset_all(self.ax_tic, self.ax_bpc, self.ax_ms1, self.loader, self.plotting)
        self.canvas.draw_idle()

    def _on_click(self, event):
        self.zoom.on_click(event, self.ax_tic, self.ax_bpc, self.ax_ms1, self.loader, self.plotting)
        self.canvas.draw_idle()

    def _on_release(self, event):
        self.zoom.on_release(event, self.ax_tic, self.ax_bpc, self.ax_ms1, self.loader, self.plotting)
        self.canvas.draw_idle()

    def _on_motion(self, event):
        self.zoom.on_motion(event)
        self.canvas.draw_idle()

    def _on_scroll(self, event):
        self.zoom.on_scroll(event)
        self.canvas.draw_idle()
