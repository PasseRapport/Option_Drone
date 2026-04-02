# ui/pid_panel.py — Panneau droite : reglage des coefficients PID
#
# Protocole PID : *[axe][coeff][valeur 6 chars]
#   axe   : H (hauteur) | P (pitch) | R (roll) | Y (yaw)
#   coeff : P (Kp) | I (Ki) | D (Kd)
#   Ex: *HP0.5000  -> Kp du controleur Hauteur = 0.5

import customtkinter as ctk
from tkinter import StringVar
import time
from config import COLORS, AXIS_LABELS


class PidPanel(ctk.CTkFrame):
    """
    Grille d'edition des coefficients PID pour les 4 axes.

    Callback attendu
    ----------------
    on_send(axis, coeff, raw_str) : appele pour chaque coefficient a envoyer.
    """

    COEFFS = ('P', 'I', 'D')

    def __init__(self, parent, *, on_send, log_callback=None):
        super().__init__(parent, corner_radius=10)
        self._on_send = on_send
        self._log     = log_callback or (lambda _: None)
        self._pid_vars: dict[str, dict[str, StringVar]] = {}
        self._build()

    # ── Construction ──────────────────────────────────
    def _build(self):
        pad = dict(padx=14)

        ctk.CTkLabel(self, text="REGLAGE PID",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS['ACC']).pack(anchor="w", **pad, pady=(10, 4))

        # En-tetes colonnes
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", **pad)
        for col, (txt, w) in enumerate(
                zip(["Axe", "Kp", "Ki", "Kd", ""], [70, 70, 70, 70, 40])):
            ctk.CTkLabel(hdr, text=txt, width=w,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="gray50",
                         anchor="center").grid(row=0, column=col, padx=2)

        # Lignes par axe
        for axis, label in AXIS_LABELS.items():
            self._pid_vars[axis] = {}
            row_f = ctk.CTkFrame(self, fg_color="transparent")
            row_f.pack(fill="x", **pad, pady=3)

            ctk.CTkLabel(row_f, text=label, width=70,
                         font=ctk.CTkFont(size=12),
                         anchor="w").grid(row=0, column=0, padx=2)

            for ci, coeff in enumerate(self.COEFFS):
                var = StringVar(value="0.0")
                self._pid_vars[axis][coeff] = var
                ctk.CTkEntry(row_f, textvariable=var, width=70, height=30,
                             corner_radius=6,
                             font=ctk.CTkFont(family="Consolas", size=12),
                             justify="center").grid(
                                 row=0, column=ci + 1, padx=2)

            ctk.CTkButton(row_f, text="✓", width=36, height=30,
                          corner_radius=6,
                          font=ctk.CTkFont(size=13, weight="bold"),
                          fg_color=COLORS['PID_BTN'],
                          hover_color="#c2410c",
                          command=lambda a=axis: self._send_axis(a)).grid(
                              row=0, column=4, padx=2)

        # Separateur + bouton global
        ctk.CTkFrame(self, height=2, fg_color="gray75").pack(
            fill="x", padx=14, pady=8)

        ctk.CTkButton(self, text="Envoyer tout", height=34,
                      corner_radius=8,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=COLORS['ACC'],
                      hover_color=COLORS['ACC_HOVER'],
                      command=self._send_all).pack(
                          fill="x", padx=14, pady=(0, 10))

    # ── Actions ───────────────────────────────────────
    def _send_axis(self, axis: str):
        """Envoie les 3 coefficients d'un axe."""
        for coeff in self.COEFFS:
            raw = self._pid_vars[axis][coeff].get().strip()
            try:
                float(raw)
            except ValueError:
                self._log(f"[ERREUR] PID {axis}/{coeff} — valeur invalide : '{raw}'")
                continue
            self._on_send(axis, coeff, raw)
            time.sleep(0.05)

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
