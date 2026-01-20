# helpers placeholder

"""
utils/helpers.py
Utility generiche per LC–MS Viewer (rewrite 2026)
Python 3.12
"""

import time


# ==========================================================
# NUMERIC HELPERS
# ==========================================================
def clamp(value, min_val, max_val):
    """
    Restringe un valore entro i limiti [min_val, max_val].
    """
    return max(min_val, min(value, max_val))


def safe_max(arr, default=0.0):
    """
    Restituisce max(arr) oppure default se l'array è vuoto.
    """
    try:
        return max(arr)
    except Exception:
        return default


def safe_min(arr, default=0.0):
    """
    Restituisce min(arr) oppure default se vuoto/malf.
    """
    try:
        return min(arr)
    except Exception:
        return default


# ==========================================================
# FORMATTING HELPERS
# ==========================================================
def format_rt(rt):
    """
    Format RT (retention time) con 2 decimali.
    """
    try:
        return f"{float(rt):.2f}"
    except Exception:
        return "n/a"


def format_mz(mz):
    """
    Format m/z con 4 decimali.
    """
    try:
        return f"{float(mz):.4f}"
    except Exception:
        return "n/a"


# ==========================================================
# TIMING / DEBOUNCING
# ==========================================================
class Debouncer:
    """
    Debounce per funzioni chiamate ad alta frequenza.
    Utile per eventi matplotlib / motion / scroll.
    """

    def __init__(self, interval_sec=1/60):
        self.interval = interval_sec
        self._last_ts = 0

    def ready(self):
        """
        Ritorna True se è passato abbastanza tempo (interval).
        """
        now = time.perf_counter()
        if now - self._last_ts >= self.interval:
            self._last_ts = now
            return True
        return False
