# ui/pid_panel.py — Panneau droite : reglage des coefficients PID

import customtkinter as ctk
from tkinter import StringVar
import time
from config import COLORS, TRANSLATIONS, DEFAULT_LANG


class PidPanel(ctk.CTkFrame):
    """
    Grille d'edition des coefficients PID pour les 4 axes.

    Callback attendu
    ----------------
    on_send(axis, coeff, raw_str)
    """

    COEFFS     = ('P', 'I', 'D')
    AXIS_KEYS  = ('H', 'P', 'R', 'Y')   # ordre fixe, independant de la langue

    def __init__(self, parent, *, on_send, log_callback=None, lang=DEFAULT_LANG):
        super().__init__(parent, corner_radius=10)
        self._on_send  = on_send
        self._log      = log_callback or (lambda _: None)
        self._lang     = lang
        self._pid_vars: dict[str, dict[str, StringVar]] = {}
        self._axis_labels: dict[str, ctk.CTkLabel] = {}   # pour set_language
        self._build()

    # ── Construction ──────────────────────────────────
    def _build(self):
        T   = TRANSLATIONS[self._lang]
        pad = dict(padx=14)

        self._lbl_title = ctk.CTkLabel(
            self, text=T['section_pid'],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['ACC'],
        )
        self._lbl_title.pack(anchor="w", **pad, pady=(10, 4))

        # En-tetes colonnes
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", **pad)
        self._lbl_col_axis = ctk.CTkLabel(
            hdr, text=T['col_axis'], width=70,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray50", anchor="center",
        )
        self._lbl_col_axis.grid(row=0, column=0, padx=2)
        for ci, col_txt in enumerate(('Kp', 'Ki', 'Kd')):
            ctk.CTkLabel(hdr, text=col_txt, width=70,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="gray50",
                         anchor="center").grid(row=0, column=ci + 1, padx=2)

        # Lignes par axe
        axis_labels_dict = T['axis_labels']
        for axis in self.AXIS_KEYS:
            self._pid_vars[axis] = {}
            row_f = ctk.CTkFrame(self, fg_color="transparent")
            row_f.pack(fill="x", **pad, pady=3)

            lbl = ctk.CTkLabel(row_f, text=axis_labels_dict[axis],
                               width=70, font=ctk.CTkFont(size=12), anchor="w")
            lbl.grid(row=0, column=0, padx=2)
            self._axis_labels[axis] = lbl

            for ci, coeff in enumerate(self.COEFFS):
                var = StringVar(value="0.0")
                self._pid_vars[axis][coeff] = var
                ctk.CTkEntry(row_f, textvariable=var, width=70, height=30,
                             corner_radius=6,
                             font=ctk.CTkFont(family="Consolas", size=12),
                             justify="center").grid(row=0, column=ci + 1, padx=2)

            ctk.CTkButton(row_f, text="✓", width=36, height=30,
                          corner_radius=6,
                          font=ctk.CTkFont(size=13, weight="bold"),
                          fg_color=COLORS['PID_BTN'], hover_color="#c2410c",
                          command=lambda a=axis: self._send_axis(a)).grid(
                              row=0, column=4, padx=2)

        ctk.CTkFrame(self, height=2, fg_color="gray75").pack(
            fill="x", padx=14, pady=8)

        self._btn_send_all = ctk.CTkButton(
            self, text=T['btn_send_all'], height=34, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS['ACC'], hover_color=COLORS['ACC_HOVER'],
            command=self._send_all,
        )
        self._btn_send_all.pack(fill="x", padx=14, pady=(0, 10))

    # ── Actions ───────────────────────────────────────
    def _send_axis(self, axis: str):
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
        for axis in self.AXIS_KEYS:
            self._send_axis(axis)

    # ── API publique ──────────────────────────────────
    def set_language(self, lang: str):
        self._lang = lang
        T = TRANSLATIONS[lang]
        self._lbl_title.configure(text=T['section_pid'])
        self._lbl_col_axis.configure(text=T['col_axis'])
        self._btn_send_all.configure(text=T['btn_send_all'])
        for axis, lbl in self._axis_labels.items():
            lbl.configure(text=T['axis_labels'][axis])

    def get_values(self) -> dict[str, dict[str, str]]:
        return {
            axis: {c: self._pid_vars[axis][c].get() for c in self.COEFFS}
            for axis in self.AXIS_KEYS
        }

    def set_values(self, values: dict[str, dict[str, float]]):
        for axis, coeffs in values.items():
            for coeff, val in coeffs.items():
                if axis in self._pid_vars and coeff in self._pid_vars[axis]:
                    self._pid_vars[axis][coeff].set(str(val))
