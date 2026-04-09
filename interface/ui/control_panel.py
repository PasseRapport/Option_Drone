# ui/control_panel.py — Panneau centre : altitude, dpad directionnel, yaw

import customtkinter as ctk
from config import COLORS, TRANSLATIONS, DEFAULT_LANG
from flight_commands import UP, DOWN, FORWARD, BACKWARD, LEFT, RIGHT, YAW_CCW, YAW_CW


class ControlPanel(ctk.CTkFrame):
    """
    Pad de controle de vol : altitude, direction, yaw.

    Callbacks attendus
    ------------------
    on_press(key_index)   : touche enfoncee (maintien = commande continue)
    on_release(key_index) : touche relachee
    """

    def __init__(self, parent, *, on_press, on_release, lang=DEFAULT_LANG):
        super().__init__(parent, corner_radius=10)
        self._on_press   = on_press
        self._on_release = on_release
        self._lang       = lang
        self._build()

    # ── Construction ──────────────────────────────────
    def _build(self):
        T   = TRANSLATIONS[self._lang]
        pad = dict(padx=14, pady=(0, 2))

        self._lbl_title = ctk.CTkLabel(
            self, text=T['section_flight'],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['ACC'],
        )
        self._lbl_title.pack(anchor="w", **pad)

        # ── Altitude ─────────────────────────────────
        self._frame_alt = ctk.CTkFrame(self, corner_radius=8)
        self._frame_alt.pack(fill="x", padx=14, pady=6)
        self._lbl_alt = ctk.CTkLabel(self._frame_alt, text=T['sub_altitude'],
                                     font=ctk.CTkFont(size=11, weight="bold"))
        self._lbl_alt.pack(anchor="w", padx=10, pady=(6, 2))

        alt_btns = ctk.CTkFrame(self._frame_alt, fg_color="transparent")
        alt_btns.pack(padx=10, pady=(0, 8))
        self._btn_up   = self._action_btn(alt_btns, T['btn_up'],   UP,
                                          fg=COLORS['ACC'], hover=COLORS['ACC_HOVER'], col=0)
        self._btn_down = self._action_btn(alt_btns, T['btn_down'], DOWN,
                                          fg=COLORS['ACC'], hover=COLORS['ACC_HOVER'], col=1)

        # ── Direction (dpad) ─────────────────────────
        self._frame_dir = ctk.CTkFrame(self, corner_radius=8)
        self._frame_dir.pack(fill="x", padx=14, pady=6)
        self._lbl_dir = ctk.CTkLabel(self._frame_dir, text=T['sub_direction'],
                                     font=ctk.CTkFont(size=11, weight="bold"))
        self._lbl_dir.pack(anchor="w", padx=10, pady=(6, 2))

        dpad = ctk.CTkFrame(self._frame_dir, fg_color="transparent")
        dpad.pack(padx=10, pady=(0, 8))
        self._dpad_btn(dpad, "↑", FORWARD,  row=0, col=1)
        self._dpad_btn(dpad, "←", LEFT,     row=1, col=0)
        ctk.CTkLabel(dpad, text="●", width=54, height=54,
                     font=ctk.CTkFont(size=18),
                     fg_color=COLORS['DPAD_BG'], corner_radius=8,
                     text_color="gray50").grid(row=1, column=1, padx=3, pady=3)
        self._dpad_btn(dpad, "→", RIGHT,    row=1, col=2)
        self._dpad_btn(dpad, "↓", BACKWARD, row=2, col=1)

        # ── Yaw ──────────────────────────────────────
        self._frame_yaw = ctk.CTkFrame(self, corner_radius=8)
        self._frame_yaw.pack(fill="x", padx=14, pady=6)
        self._lbl_yaw = ctk.CTkLabel(self._frame_yaw, text=T['sub_yaw'],
                                     font=ctk.CTkFont(size=11, weight="bold"))
        self._lbl_yaw.pack(anchor="w", padx=10, pady=(6, 2))

        yaw_btns = ctk.CTkFrame(self._frame_yaw, fg_color="transparent")
        yaw_btns.pack(padx=10, pady=(0, 8))
        self._btn_yccw = self._action_btn(yaw_btns, "↺  CCW", YAW_CCW,
                                          fg=COLORS['YAW'], hover=COLORS['YAW_HOVER'], col=0)
        self._btn_ycw  = self._action_btn(yaw_btns, "↻  CW",  YAW_CW,
                                          fg=COLORS['YAW'], hover=COLORS['YAW_HOVER'], col=1)

    # ── Bouton d'action (altitude / yaw) ──────────────
    def _action_btn(self, parent, text: str, key_idx: int,
                    fg: str, hover: str, col: int) -> ctk.CTkButton:
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
                  row: int, col: int) -> ctk.CTkButton:
        b = ctk.CTkButton(parent, text=symbol, width=54, height=54,
                          corner_radius=8, font=ctk.CTkFont(size=20),
                          fg_color=COLORS['DPAD_BG'],
                          hover_color=COLORS['DPAD_HOVER'],
                          text_color=COLORS['DPAD_FG'])
        b.grid(row=row, column=col, padx=3, pady=3)
        b.bind("<ButtonPress-1>",   lambda e, k=key_idx: self._on_press(k))
        b.bind("<ButtonRelease-1>", lambda e, k=key_idx: self._on_release(k))
        return b

    # ── API publique ──────────────────────────────────
    def set_language(self, lang: str):
        self._lang = lang
        T = TRANSLATIONS[lang]
        self._lbl_title.configure(text=T['section_flight'])
        self._lbl_alt.configure(text=T['sub_altitude'])
        self._lbl_dir.configure(text=T['sub_direction'])
        self._lbl_yaw.configure(text=T['sub_yaw'])
        self._btn_up.configure(text=T['btn_up'])
        self._btn_down.configure(text=T['btn_down'])
