# ui/connection_panel.py — Panneau gauche : connexion serie + controle drone

import customtkinter as ctk
from tkinter import messagebox, StringVar
from config import COLORS, TRANSLATIONS, DEFAULT_LANG
from serial_comm import DroneSerial


class ConnectionPanel(ctk.CTkFrame):
    """
    Panneau de connexion serie et de controle haut niveau du drone.

    Callbacks attendus
    ------------------
    on_connect(port)  : appele quand l'utilisateur clique "Connecter"
    on_disconnect()   : appele quand l'utilisateur clique "Deconnecter"
    on_start()        : envoi de $start
    on_stop()         : envoi de $stop
    on_emergency()    : arret d'urgence $11111111
    """

    def __init__(self, parent, *, on_connect, on_disconnect,
                 on_start, on_stop, on_emergency, lang=DEFAULT_LANG):
        super().__init__(parent, corner_radius=10)

        self._on_connect    = on_connect
        self._on_disconnect = on_disconnect
        self._on_start      = on_start
        self._on_stop       = on_stop
        self._on_emergency  = on_emergency
        self._connected     = False
        self._connecting    = False
        self._anim_job      = None
        self._anim_frame    = 0
        self._lang          = lang

        self._build()

    # ── Construction ──────────────────────────────────
    def _build(self):
        T   = TRANSLATIONS[self._lang]
        pad = dict(padx=14, pady=(0, 2))

        # CONNEXION
        self._lbl_section_conn = self._section_label(T['section_conn'], **pad)

        port_row = ctk.CTkFrame(self, fg_color="transparent")
        port_row.pack(fill="x", **pad)
        self._lbl_port = ctk.CTkLabel(port_row, text=T['port_label'],
                                      font=ctk.CTkFont(size=12))
        self._lbl_port.pack(side="left", padx=(0, 6))

        self.port_var   = StringVar()
        self.port_combo = ctk.CTkComboBox(
            port_row, variable=self.port_var, width=120,
            state="readonly", corner_radius=6,
        )
        self.port_combo.pack(side="left")
        ctk.CTkButton(port_row, text="↻", width=32, height=28,
                      corner_radius=6, command=self.refresh_ports,
                      fg_color="gray70", hover_color="gray60",
                      text_color="gray20").pack(side="left", padx=(4, 0))

        self.btn_connect = ctk.CTkButton(
            self, text=T['btn_connect'], height=32, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS['GREEN'], hover_color="#15803d",
            command=self._toggle_connect,
        )
        self.btn_connect.pack(fill="x", **pad)

        self.lbl_status = ctk.CTkLabel(
            self, text=T['status_disconn'],
            font=ctk.CTkFont(size=12), text_color=COLORS['RED'],
        )
        self.lbl_status.pack(anchor="w", padx=14, pady=(0, 6))

        self._separator()

        # DRONE
        self._lbl_section_drone = self._section_label(T['section_drone'], **pad)

        self.btn_start = ctk.CTkButton(
            self, text=T['btn_start'], height=36, corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['GREEN'], hover_color="#15803d",
            command=self._on_start, state="disabled",
        )
        self.btn_start.pack(fill="x", **pad)

        self.btn_stop = ctk.CTkButton(
            self, text=T['btn_stop'], height=36, corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['RED'], hover_color="#b91c1c",
            command=self._on_stop, state="disabled",
        )
        self.btn_stop.pack(fill="x", **pad)

        self._btn_emergency = ctk.CTkButton(
            self, text=T['btn_emergency'], height=40, corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['EMERGENCY'], hover_color="#cc0000",
            command=self._on_emergency,
        )
        self._btn_emergency.pack(fill="x", padx=14, pady=(8, 4))

        self._separator()

        # CLAVIER
        self._lbl_section_kb = self._section_label(T['section_keyboard'], **pad)

        self._key_rows: list[tuple] = []
        for key, action in T['keys_info']:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=14)
            lbl_key = ctk.CTkLabel(row, text=key, width=80,
                                   font=ctk.CTkFont(family="Consolas", size=11),
                                   text_color=COLORS['ACC'], anchor="w")
            lbl_key.pack(side="left")
            lbl_action = ctk.CTkLabel(row, text=action,
                                      font=ctk.CTkFont(size=11), anchor="w")
            lbl_action.pack(side="left")
            self._key_rows.append((lbl_key, lbl_action))

    def _section_label(self, title: str, **pack_kw) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(self, text=title,
                           font=ctk.CTkFont(size=12, weight="bold"),
                           text_color=COLORS['ACC'])
        lbl.pack(anchor="w", **pack_kw)
        return lbl

    def _separator(self):
        ctk.CTkFrame(self, height=2, fg_color="gray75").pack(
            fill="x", padx=14, pady=8)

    # ── Animation de connexion ────────────────────────
    def _start_connecting_anim(self):
        self._connecting  = True
        self._anim_frame  = 0
        self.btn_connect.configure(state="disabled",
                                   fg_color="gray60", hover_color="gray60")
        self.lbl_status.configure(
            text=TRANSLATIONS[self._lang]['status_connecting'],
            text_color="gray50",
        )
        self._tick_anim()

    def _tick_anim(self):
        if not self._connecting:
            return
        frames = TRANSLATIONS[self._lang]['connecting_frames']
        self.btn_connect.configure(text=frames[self._anim_frame % len(frames)])
        self._anim_frame += 1
        self._anim_job = self.after(350, self._tick_anim)

    def _stop_anim(self):
        self._connecting = False
        if self._anim_job:
            self.after_cancel(self._anim_job)
            self._anim_job = None

    # ── Actions ───────────────────────────────────────
    def _toggle_connect(self):
        if self._connected:
            self._on_disconnect()
        else:
            port = self.port_var.get()
            if not port:
                T = TRANSLATIONS[self._lang]
                messagebox.showwarning(T['warn_port_title'], T['warn_port_msg'])
                return
            self._start_connecting_anim()
            self._on_connect(port)

    # ── API publique ──────────────────────────────────
    def refresh_ports(self):
        ports = DroneSerial.list_ports()
        self.port_combo.configure(values=ports)
        if ports:
            self.port_var.set(ports[0])

    def set_connected(self, connected: bool):
        """Arrete l'animation et met a jour l'apparence."""
        self._stop_anim()
        self._connected = connected
        T = TRANSLATIONS[self._lang]
        self.btn_connect.configure(state="normal")
        if connected:
            self.btn_connect.configure(text=T['btn_disconnect'],
                                       fg_color=COLORS['RED'],
                                       hover_color="#b91c1c")
            self.lbl_status.configure(text=T['status_connected'],
                                      text_color=COLORS['GREEN'])
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="normal")
        else:
            self.btn_connect.configure(text=T['btn_connect'],
                                       fg_color=COLORS['GREEN'],
                                       hover_color="#15803d")
            self.lbl_status.configure(text=T['status_disconn'],
                                      text_color=COLORS['RED'])
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="disabled")

    def set_language(self, lang: str):
        """Met a jour tous les textes du panneau."""
        self._lang = lang
        T = TRANSLATIONS[lang]

        self._lbl_section_conn.configure(text=T['section_conn'])
        self._lbl_section_drone.configure(text=T['section_drone'])
        self._lbl_section_kb.configure(text=T['section_keyboard'])
        self._lbl_port.configure(text=T['port_label'])
        self.btn_start.configure(text=T['btn_start'])
        self.btn_stop.configure(text=T['btn_stop'])
        self._btn_emergency.configure(text=T['btn_emergency'])

        # Etat dynamique
        if self._connecting:
            self.lbl_status.configure(text=T['status_connecting'])
        elif self._connected:
            self.btn_connect.configure(text=T['btn_disconnect'])
            self.lbl_status.configure(text=T['status_connected'])
        else:
            self.btn_connect.configure(text=T['btn_connect'])
            self.lbl_status.configure(text=T['status_disconn'])

        # Legende clavier
        for i, (lbl_key, lbl_action) in enumerate(self._key_rows):
            key, action = T['keys_info'][i]
            lbl_key.configure(text=key)
            lbl_action.configure(text=action)
