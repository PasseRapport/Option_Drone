# ui/pid_panel.py — Panneau droite : réglage des coefficients PID
#
# Protocole PID : *[axe][coeff][valeur 6 chars]
#   axe   : H (hauteur) | P (pitch) | R (roll) | Y (yaw)
#   coeff : P (Kp) | I (Ki) | D (Kd)
#   Ex: *HP0.5000  -> Kp du contrôleur Hauteur = 0.5

import tkinter as tk
import time
from config import PALETTE, AXIS_LABELS


class PidPanel(tk.Frame):
    """
    Grille d'édition des coefficients PID pour les 4 axes.

    Callback attendu
    ----------------
    on_send(axis, coeff, raw_str) : appelé pour chaque coefficient à envoyer.
        axis     : 'H' | 'P' | 'R' | 'Y'
        coeff    : 'P' | 'I' | 'D'
        raw_str  : valeur saisie (str, validée par l'appelant)
    """

    COEFFS = ('P', 'I', 'D')

    def __init__(self, parent, *, on_send, log_callback=None):
        P = PALETTE
        super().__init__(parent, bg=P['PANEL'], padx=14, pady=10)
        self._on_send     = on_send
        self._log         = log_callback or (lambda _: None)
        self._pid_vars: dict[str, dict[str, tk.StringVar]] = {}
        self._build()

    # ── Construction ──────────────────────────────────
    def _build(self):
        P = PALETTE
        tk.Label(self, text="RÉGLAGE PID", font=("Segoe UI", 9, "bold"),
                 bg=P['PANEL'], fg=P['ACC']).pack(anchor="w")
        tk.Frame(self, bg=P['ACC'], height=1).pack(fill="x", pady=(0, 8))

        # En-têtes colonnes
        hdr = tk.Frame(self, bg=P['PANEL'])
        hdr.pack(fill="x")
        widths = [7, 7, 7, 7, 5]
        for col, (txt, w) in enumerate(zip(["Axe", "Kp", "Ki", "Kd", ""], widths)):
            tk.Label(hdr, text=txt, bg=P['PANEL'], fg=P['SUB'],
                     font=("Segoe UI", 8, "bold"),
                     width=w, anchor="center").grid(row=0, column=col, padx=2)

        # Lignes par axe
        for axis, label in AXIS_LABELS.items():
            self._pid_vars[axis] = {}
            row_f = tk.Frame(self, bg=P['PANEL'])
            row_f.pack(fill="x", pady=3)

            tk.Label(row_f, text=label, bg=P['PANEL'], fg=P['TEXT'],
                     font=("Segoe UI", 9), width=7, anchor="w").grid(
                         row=0, column=0, padx=2)

            for ci, coeff in enumerate(self.COEFFS):
                var = tk.StringVar(value="0.0")
                self._pid_vars[axis][coeff] = var
                tk.Entry(row_f, textvariable=var, width=7,
                         bg=P['ENTRY_BG'], fg=P['TEXT'],
                         insertbackground=P['TEXT'],
                         relief="flat", font=("Consolas", 9),
                         justify="center").grid(row=0, column=ci + 1, padx=2)

            tk.Button(row_f, text="✓", bg=P['PID_BTN'], fg="white",
                      font=("Segoe UI", 9, "bold"), relief="flat", padx=4,
                      command=lambda a=axis: self._send_axis(a)).grid(
                          row=0, column=4, padx=2)

        tk.Frame(self, bg=PALETTE['SUB'], height=1).pack(fill="x", pady=8)
        tk.Button(self, text="Envoyer tout", bg=PALETTE['ACC'], fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat",
                  padx=8, pady=4,
                  command=self._send_all).pack(fill="x")

    # ── Actions ───────────────────────────────────────
    def _send_axis(self, axis: str):
        """Envoie les 3 coefficients d'un axe."""
        for coeff in self.COEFFS:
            raw = self._pid_vars[axis][coeff].get().strip()
            try:
                float(raw)   # validation
            except ValueError:
                self._log(f"[ERREUR] PID {axis}/{coeff} — valeur invalide : '{raw}'")
                continue
            self._on_send(axis, coeff, raw)
            time.sleep(0.05)  # laisse le temps à l'émetteur

    def _send_all(self):
        for axis in AXIS_LABELS:
            self._send_axis(axis)

    # ── API publique ──────────────────────────────────
    def get_values(self) -> dict[str, dict[str, str]]:
        """Retourne toutes les valeurs saisies sous forme de dict."""
        return {
            axis: {c: self._pid_vars[axis][c].get() for c in self.COEFFS}
            for axis in AXIS_LABELS
        }

    def set_values(self, values: dict[str, dict[str, float]]):
        """Charge des valeurs dans les champs (utile pour import de config)."""
        for axis, coeffs in values.items():
            for coeff, val in coeffs.items():
                if axis in self._pid_vars and coeff in self._pid_vars[axis]:
                    self._pid_vars[axis][coeff].set(str(val))
