#Main placeholder
"""
LC–MS Scientific Viewer (rewrite 2026)
Main entry point – Python 3.12
"""

import tkinter as tk
from gui.layout import LCMSViewerApp


def main():
    """
    Avvia l'applicazione principale con finestra Tkinter.
    L'intera logica e il layout vengono gestiti nei moduli della cartella gui/.
    """
    root = tk.Tk()

    # Titolo base, il resto lo gestisce l'app
    root.title("LC–MS Scientific Viewer")

    # Inizializzazione applicazione
    app = LCMSViewerApp(root)

    # Avvia loop grafico
    root.mainloop()


if __name__ == "__main__":
    main()
