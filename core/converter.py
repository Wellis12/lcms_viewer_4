# RAW to mzML converter placeholder

"""
core/converter.py
Gestione conversione RAW → mzML tramite msconvert
Versione riscritta 2026 – Python 3.12
"""

import os
import sys
import subprocess
from tkinter import messagebox, filedialog


class RAWConverter:
    """
    Convertitore RAW → mzML usando msconvert.
    Compatibile con:
    - Thermo RAW
    - msconvert.exe di ProteoWizard

    Logica:
    1. Selezione dei file RAW
    2. Scelta cartella di output
    3. Individuazione msconvert
    4. Conversione multipla
    5. Ritorna l’ultimo file convertito (per loading automatico)
    """

    # ==========================================================
    # ENTRY POINT
    # ==========================================================
    def batch_convert(self):
        raw_files = filedialog.askopenfilenames(
            title="Seleziona file RAW",
            filetypes=[("Thermo RAW", "*.raw"), ("Tutti i file", "*.*")]
        )
        if not raw_files:
            messagebox.showwarning("Nessun file", "Nessun file RAW selezionato.")
            return None

        out_folder = self._choose_output_folder()
        if not out_folder:
            return None

        msconvert_path = self._get_msconvert_path()
        if not msconvert_path:
            return None

        converted_files = []

        for raw in raw_files:
            try:
                out = self._convert_single(raw, out_folder, msconvert_path)
                if out:
                    converted_files.append(out)
            except Exception as e:
                messagebox.showerror(
                    "Errore",
                    f"Errore durante la conversione di:\n{raw}\n\n{e}"
                )

        if not converted_files:
            messagebox.showwarning("Conversione", "Nessun file è stato convertito.")
            return None

        last = converted_files[-1]

        messagebox.showinfo(
            "Conversione completata",
            f"Conversione completata con successo.\n\n"
            f"File convertiti: {len(converted_files)}\n"
            f"Ultimo file:\n{last}"
        )

        return last

    # ==========================================================
    # SOTTOFUNZIONI
    # ==========================================================
    def _choose_output_folder(self):
        folder = filedialog.askdirectory(title="Seleziona cartella di output")
        if not folder:
            messagebox.showwarning("Cartella mancante", "Nessuna cartella selezionata.")
            return None
        return folder

    # ----------------------------------------------------------
    # TROVA MSCONVERT
    # ----------------------------------------------------------
    def _get_msconvert_path(self):
        """
        Cerca msconvert.exe nella sottocartella /msconvert accanto allo script
        o accanto all’eseguibile (se distribuito con PyInstaller).
        """
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        exe_path = os.path.join(base_dir, "msconvert", "msconvert.exe")

        if not os.path.exists(exe_path):
            messagebox.showerror(
                "msconvert non trovato",
                "Impossibile trovare msconvert.exe nella cartella:\n\n"
                f"{exe_path}\n\nAssicurati che sia presente."
            )
            return None

        return exe_path

    # ----------------------------------------------------------
    # CONVERSIONE DEL SINGOLO FILE
    # ----------------------------------------------------------
    def _convert_single(self, raw_path, out_folder, msconvert_path):
        base = os.path.basename(raw_path)
        name_no_ext = os.path.splitext(base)[0]
        out_file = os.path.join(out_folder, name_no_ext + ".mzML")

        cmd = [
            msconvert_path,
            raw_path,
            "--mzML",
            "--outdir", out_folder,
            "--outfile", name_no_ext + ".mzML"
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            messagebox.showerror(
                "Errore conversione",
                f"Errore convertendo:\n{raw_path}\n\n{result.stderr}"
            )
            return None

        if not os.path.exists(out_file):
            messagebox.showerror(
                "Errore",
                f"Il file convertito non è stato trovato:\n{out_file}"
            )
            return None

        return out_file
