# ui/control_panel.py — Panneau centre : altitude, dpad directionnel, yaw

import customtkinter as ctk
from config import COLORS
from flight_commands import UP, DOWN, FORWARD, BACKWARD, LEFT, RIGHT, YAW_CCW, YAW_CW


class ControlPanel(ctk.CTkFrame):
    """
    Pad de controle de vol :
      - Altitude  : monter / descendre
      - Direction : avant / arriere / gauche / droite
      - Yaw       : rotation gauche (CCW) / droite (CW)

    Callbacks attendus
    ------------------
    on_press(key_index)   : touche enfoncee
    on_release(key_index) : touche relachee
    """

    def __init__(self, parent, *, on_press, on_release):
        super().__init__(parent, corner_radius=10)
        self._on_press   = on_press
        self._on_release = on_release
        self._build()

    # ── Construction ──────────────────────────────────
    def _build(self):
        pad = dict(padx=14, pady=(0, 2))

        ctk.CTkLabel(self, text="CONTROLE DE VOL",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS['ACC']).pack(anchor="w", **pad)

        # ── Altitude ─────────────────────────────────
        alt_frame = ctk.CTkFrame(self, corner_radius=8)
        alt_frame.pack(fill="x", padx=14, pady=6)
        ctk.CTkLabel(alt_frame, text="Altitude",
                     font=ctk.CTkFont(size=11, weight="bold")).pack(
                         anchor="w", padx=10, pady=(6, 2))

        alt_btns = ctk.CTkFrame(alt_frame, fg_color="transparent")
        alt_btns.pack(padx=10, pady=(0, 8))
        self._action_btn(alt_btns, "▲  MONTER",    UP,
                         fg=COLORS['ACC'], hover=COLORS['ACC_HOVER'], col=0)
        self._action_btn(alt_btns, "▼  DESCENDRE", DOWN,
                         fg=COLORS['ACC'], hover=COLORS['ACC_HOVER'], col=1)

        # ── Direction (dpad) ─────────────────────────
        dir_frame = ctk.CTkFrame(self, corner_radius=8)
        dir_frame.pack(fill="x", padx=14, pady=6)
        ctk.CTkLabel(dir_frame, text="Direction",
                     font=ctk.CTkFont(size=11, weight="bold")).pack(
                         anchor="w", padx=10, pady=(6, 2))

        dpad = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dpad.pack(padx=10, pady=(0, 8))

        self._dpad_btn(dpad, "↑", FORWARD,  row=0, col=1)
        self._dpad_btn(dpad, "←", LEFT,     row=1, col=0)
        # Centre decoratif
        center = ctk.CTkLabel(dpad, text="●", width=54, height=54,
                              font=ctk.CTkFont(size=18),
                              fg_color=COLORS['DPAD_BG'],
                              corner_radius=8, text_color="gray50")
        center.grid(row=1, column=1, padx=3, pady=3)
        self._dpad_btn(dpad, "→", RIGHT,    row=1, col=2)
        self._dpad_btn(dpad, "↓", BACKWARD, row=2, col=1)

        # ── Yaw ──────────────────────────────────────
        yaw_frame = ctk.CTkFrame(self, corner_radius=8)
        yaw_frame.pack(fill="x", padx=14, pady=6)
        ctk.CTkLabel(yaw_frame, text="Lacet (Yaw)",
                     font=ctk.CTkFont(size=11, weight="bold")).pack(
                         anchor="w", padx=10, pady=(6, 2))

        yaw_btns = ctk.CTkFrame(yaw_frame, fg_color="transparent")
        yaw_btns.pack(padx=10, pady=(0, 8))
        self._action_btn(yaw_btns, "↺  CCW", YAW_CCW,
                         fg=COLORS['YAW'], hover=COLORS['YAW_HOVER'], col=0)
        self._action_btn(yaw_btns, "↻  CW",  YAW_CW,
                         fg=COLORS['YAW'], hover=COLORS['YAW_HOVER'], col=1)

    # ── Bouton d'action (altitude / yaw) ──────────────
    def _action_btn(self, parent, text: str, key_idx: int,
                    fg: str, hover: str, col: int):
        b = ctk.CTkButton(parent, text=text, width=120, height=34,
                          corner_radius=8,
                          font=ctk.CTkFont(size=12, weight="bold"),
                          fg_color=fg, hover_color=hover)
        b.grid(row=0, column=col, padx=4, pady=2)
        b.bind("<ButtonPress-1>",   lambda e, k=key_idx: self._on_press(k))
        b.bind("<ButtonRelease-1>", lambda e, k=key_idx: self._on_release(k))
        return b

    # ── Bouton dpad (direction) ───────────────────────
    def _dpad_btn(self, parent, symbol: str, key_idx: int,
                  row: int, col: int):
        b = ctk.CTkButton(parent, text=symbol, width=54, height=54,
                          corner_radius=8,
                          font=ctk.CTkFont(size=20),
                          fg_color=COLORS['DPAD_BG'],
                          hover_color=COLORS['DPAD_HOVER'],
                          text_color=COLORS['DPAD_FG'],
                          text_color_disabled="gray50")
        b.grid(row=row, column=col, padx=3, pady=3)
        b.bind("<ButtonPress-1>",   lambda e, k=key_idx: self._on_press(k))
        b.bind("<ButtonRelease-1>", lambda e, k=key_idx: self._on_release(k))
        return b
