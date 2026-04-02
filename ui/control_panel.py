# ui/control_panel.py — Panneau centre : altitude, dpad directionnel, yaw

import tkinter as tk
from config import PALETTE
from flight_commands import UP, DOWN, FORWARD, BACKWARD, LEFT, RIGHT, YAW_CCW, YAW_CW


class ControlPanel(tk.Frame):
    """
    Pad de contrôle de vol :
      - Altitude  : monter / descendre
      - Direction : avant / arrière / gauche / droite
      - Yaw       : rotation gauche (CCW) / droite (CW)

    Callbacks attendus
    ------------------
    on_press(key_index)   : touche enfoncée
    on_release(key_index) : touche relâchée
    """

    def __init__(self, parent, *, on_press, on_release):
        P = PALETTE
        super().__init__(parent, bg=P['PANEL'], padx=16, pady=10)
        self._on_press   = on_press
        self._on_release = on_release
        self._build()

    # ── Construction ──────────────────────────────────
    def _build(self):
        P = PALETTE
        self._section("CONTRÔLE DE VOL")

        # Altitude
        alt_frame = tk.LabelFrame(self, text="Altitude", bg=P['PANEL'], fg=P['SUB'],
                                  font=("Segoe UI", 8), bd=1, padx=6, pady=4)
        alt_frame.pack(fill="x", pady=4)
        inner = tk.Frame(alt_frame, bg=P['PANEL'])
        inner.pack()
        self._action_btn(inner, "▲  MONTER",    UP,   bg=P['ACC'], row=0, col=0)
        self._action_btn(inner, "▼  DESCENDRE", DOWN, bg=P['ACC'], row=0, col=1)

        # Dpad directionnel
        dir_frame = tk.LabelFrame(self, text="Direction", bg=P['PANEL'], fg=P['SUB'],
                                  font=("Segoe UI", 8), bd=1, padx=6, pady=4)
        dir_frame.pack(fill="x", pady=4)
        pad = tk.Frame(dir_frame, bg=P['PANEL'])
        pad.pack()

        cfg = dict(font=("Segoe UI", 14), relief="flat", width=3, height=1)
        self._dpad_btn(pad, "↑", FORWARD,  row=0, col=1, cfg=cfg)
        self._dpad_btn(pad, "←", LEFT,     row=1, col=0, cfg=cfg)
        tk.Label(pad, text="●", font=("Segoe UI", 14),
                 bg=P['DPAD_BG'], fg=P['SUB'],
                 width=3, height=1).grid(row=1, column=1, padx=2, pady=2,
                                         ipadx=4, ipady=4)
        self._dpad_btn(pad, "→", RIGHT,    row=1, col=2, cfg=cfg)
        self._dpad_btn(pad, "↓", BACKWARD, row=2, col=1, cfg=cfg)

        # Yaw
        yaw_frame = tk.LabelFrame(self, text="Lacet (Yaw)", bg=P['PANEL'], fg=P['SUB'],
                                  font=("Segoe UI", 8), bd=1, padx=6, pady=4)
        yaw_frame.pack(fill="x", pady=4)
        yaw_inner = tk.Frame(yaw_frame, bg=P['PANEL'])
        yaw_inner.pack()
        self._action_btn(yaw_inner, "↺  CCW", YAW_CCW, bg=P['YAW'], row=0, col=0)
        self._action_btn(yaw_inner, "↻  CW",  YAW_CW,  bg=P['YAW'], row=0, col=1)

    def _section(self, title: str):
        P = PALETTE
        tk.Label(self, text=title, font=("Segoe UI", 9, "bold"),
                 bg=P['PANEL'], fg=P['ACC']).pack(anchor="w")
        tk.Frame(self, bg=P['ACC'], height=1).pack(fill="x", pady=(0, 8))

    def _action_btn(self, parent, text: str, key_idx: int,
                    bg: str, row: int, col: int) -> tk.Button:
        """Bouton maintenu = commande continue."""
        b = tk.Button(parent, text=text, bg=bg, fg="white",
                      font=("Segoe UI", 9, "bold"), relief="flat",
                      padx=8, pady=4)
        b.grid(row=row, column=col, padx=4, pady=2)
        b.bind("<ButtonPress-1>",   lambda e, k=key_idx: self._on_press(k))
        b.bind("<ButtonRelease-1>", lambda e, k=key_idx: self._on_release(k))
        return b

    def _dpad_btn(self, parent, symbol: str, key_idx: int,
                  row: int, col: int, cfg: dict) -> tk.Button:
        P = PALETTE
        b = tk.Button(parent, text=symbol,
                      bg=P['DPAD_BG'], fg=P['DPAD_FG'],
                      activebackground=P['DPAD_HOVER'], activeforeground="white",
                      **cfg)
        b.grid(row=row, column=col, padx=2, pady=2, ipadx=4, ipady=4)
        b.bind("<ButtonPress-1>",   lambda e, k=key_idx: self._on_press(k))
        b.bind("<ButtonRelease-1>", lambda e, k=key_idx: self._on_release(k))
        return b
