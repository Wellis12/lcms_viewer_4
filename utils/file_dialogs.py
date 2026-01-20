# file dialogs placeholder

"""
utils/file_dialogs.py
Dialoghi file per LC–MS Viewer (rewrite 2026)
Python 3.12
"""

import os
from tkinter import filedialog, messagebox


class FileDialogs:
    """
    Wrapper semplice per tutti i dialoghi di apertura/salvataggio file.
    Non contiene logica del viewer: solo I/O di file.
    """

    # ==========================================================
    # APERTURA FILE MZML
    # ==========================================================
    def open_mzml(self):
        """
        Mostra dialogo per aprire un file mzML.
        Ritorna path string, oppure None.
        """
        file_path = filedialog.askopenfilename(
            title="Seleziona un file mzML",
            filetypes=[("File mzML", "*.mzML"), ("Tutti i file", "*.*")]
        )
        if not file_path:
            return None
        return file_path

    # ==========================================================
    # ESPORTAZIONE FIGURA
    # ==========================================================
    def export_figure(self, figure):
        """
        Esporta la figura matplotlib in PNG / SVG / PDF / JPG.
        """
        file_path = filedialog.asksaveasfilename(
            title="Esporta grafico",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("SVG", "*.svg"),
                ("JPEG", "*.jpg"),
                ("PDF", "*.pdf")
            ]
        )
        if not file_path:
            return

        try:
            figure.savefig(file_path, dpi=300, bbox_inches="tight")
            messagebox.showinfo(
                "Esportazione completata",
                f"Grafico esportato correttamente in:\n\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror(
                "Errore",
                f"Errore durante l'esportazione del grafico:\n\n{e}"
            )

    # ==========================================================
    # SALVATAGGI GENERICI (opzionale, riutilizzabile)
    # ==========================================================
    def save_json(self):
        """
        Dialogo generico per salvare un file JSON.
        Utilizzato da StyleEditor.
        """
        path = filedialog.asksaveasfilename(
            title="Salva stile",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        return path if path else None

    def open_json(self):
        """
        Dialogo generico per aprire un file JSON.
        Utilizzato da StyleEditor.
        """
        path = filedialog.askopenfilename(
            title="Carica stile",
            filetypes=[("JSON files", "*.json")]
        )
        return path if path else None
