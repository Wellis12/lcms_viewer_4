# mzML loader placeholder

"""
core/loader.py
Gestione del caricamento file mzML tramite pyteomics.
Versione riscritta 2026 – Python 3.12
"""

from pyteomics import mzml
import numpy as np


class MZMLLoader:
    """
    Responsabile di:
    - caricare file mzML
    - estrarre TIC
    - estrarre BPC
    - ottenere il primo MS1 come default
    - registrare spettrogrammi MS1 multipli
    - registrare spettrogrammi MS2
    - fornire dati ai moduli plotting / zoom
    """

    def __init__(self):
        self.reset()

    # ----------------------------------------------------------
    # RESET DATI
    # ----------------------------------------------------------
    def reset(self):
        """Reset completo di tutti i contenuti."""
        self.file_path = None

        # TIC / BPC
        self.tic_times = []
        self.tic_values = []
        self.bpc_times = []
        self.bpc_values = []

        # MS1
        self.ms1_mz = None
        self.ms1_int = None
        self.ms1_spectra = []      # lista di tuple: (rt, mz_array, int_array)

        # MS2
        self.ms2_spectra = []      # lista dict: { rt, precursor, mz[], int[] }

    # ----------------------------------------------------------
    # CARICAMENTO MZML
    # ----------------------------------------------------------
    def load(self, file_path: str):
        """
        Carica un file mzML e popola TIC, BPC, MS1, MS2.
        Mantiene comportamento identico al viewer originale,
        ma con struttura molto più robusta.
        """

        self.reset()
        self.file_path = file_path

        try:
            with mzml.read(file_path) as reader:
                for spectrum in reader:

                    # MS level
                    level = spectrum.get("ms level")
                    if level is None:
                        continue

                    # Tempo di ritenzione
                    try:
                        rt = spectrum["scanList"]["scan"][0]["scan start time"]
                    except Exception:
                        continue

                    # Dati spettrali
                    mz = spectrum.get("m/z array")
                    intensities = spectrum.get("intensity array")

                    if mz is None or intensities is None:
                        continue

                    # ----------------------------
                    # MS1
                    # ----------------------------
                    if level == 1:
                        tic = float(np.sum(intensities))
                        bpc = float(np.max(intensities))

                        self.tic_times.append(rt)
                        self.tic_values.append(tic)

                        self.bpc_times.append(rt)
                        self.bpc_values.append(bpc)

                        # Salva primo MS1 come default
                        if self.ms1_mz is None:
                            self.ms1_mz = mz
                            self.ms1_int = intensities

                        # Salva tutti gli MS1 (per zoom / sync MS1)
                        self.ms1_spectra.append((rt, mz, intensities))

                    # ----------------------------
                    # MS2
                    # ----------------------------
                    elif level == 2:
                        try:
                            precursor = spectrum["precursorList"]["precursor"][0][
                                "selectedIonList"
                            ]["selectedIon"][0]["selected ion m/z"]
                        except Exception:
                            precursor = None

                        self.ms2_spectra.append({
                            "rt": rt,
                            "precursor": precursor,
                            "mz": mz,
                            "int": intensities,
                        })

        except Exception as e:
            raise RuntimeError(f"Errore caricando il file mzML:\n{e}")

    # ----------------------------------------------------------
    # FUNZIONI UTILI PER ALTRI MODULI
    # ----------------------------------------------------------
    def get_closest_ms1(self, rt_query: float):
        """
        Restituisce lo spettro MS1 più vicino al tempo RT richiesto.
        Utilizzato da:
        - zoom sincronizzato
        - click su TIC/BPC
        """
        if not self.ms1_spectra:
            return None

        rts = np.array([t for t, _, _ in self.ms1_spectra])
        idx = np.abs(rts - rt_query).argmin()
        return self.ms1_spectra[idx]

    def has_data(self):
        """Usato dai moduli per verificare se il caricamento è avvenuto."""
        return bool(self.tic_times)
