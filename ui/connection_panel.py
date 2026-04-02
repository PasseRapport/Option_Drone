# ui/connection_panel.py — Panneau gauche : connexion serie + controle drone

import customtkinter as ctk
from tkinter import messagebox, StringVar
from config import COLORS
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

    KEYS_INFO = [
        ("Z / Up",     "Avant"),
        ("S / Down",   "Arriere"),
        ("Q / Left",   "Gauche"),
        ("D / Right",  "Droite"),
        ("Espace",     "Monter"),
        ("Shift",      "Descendre"),
        ("A",          "Yaw gauche"),
        ("E",          "Yaw droit"),
        ("Entree",     "Start"),
        ("Echap",      "Urgence"),
    ]

    def __init__(self, parent, *, on_connect, on_disconnect,
                 on_start, on_stop, on_emergency):
        super().__init__(parent, corner_radius=10)

        self._on_connect    = on_connect
        self._on_disconnect = on_disconnect
        self._on_start      = on_start
        self._on_stop       = on_stop
        self._on_emergency  = on_emergency
        self._connected     = False

        self._build()

    # ── Construction ──────────────────────────────────
    def _build(self):
        pad = dict(padx=14, pady=(0, 2))

        self._section_label("CONNEXION", **pad)

        # Selection port COM
        port_row = ctk.CTkFrame(self, fg_color="transparent")
        port_row.pack(fill="x", **pad)

        ctk.CTkLabel(port_row, text="Port COM",
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 6))

        self.port_var = StringVar()
        self.port_combo = ctk.CTkComboBox(
            port_row, variable=self.port_var, width=120,
            state="readonly", corner_radius=6,
        )
        self.port_combo.pack(side="left")

        ctk.CTkButton(port_row, text="↻", width=32, height=28,
                      corner_radius=6, command=self.refresh_ports,
                      fg_color="gray70", hover_color="gray60",
                      text_color="gray20").pack(side="left", padx=(4, 0))

        # Bouton connecter
        self.btn_connect = ctk.CTkButton(
            self, text="Connecter", height=32, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS['GREEN'], hover_color="#15803d",
            command=self._toggle_connect,
        )
        self.btn_connect.pack(fill="x", **pad)

        # Indicateur d'etat
        self.lbl_status = ctk.CTkLabel(
            self, text="●  Deconnecte",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['RED'],
        )
        self.lbl_status.pack(anchor="w", padx=14, pady=(0, 6))

        self._separator()
        self._section_label("DRONE", **pad)

        self.btn_start = ctk.CTkButton(
            self, text="▶  START", height=36, corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['GREEN'], hover_color="#15803d",
            command=self._on_start, state="disabled",
        )
        self.btn_start.pack(fill="x", **pad)

        self.btn_stop = ctk.CTkButton(
            self, text="■  STOP", height=36, corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['RED'], hover_color="#b91c1c",
            command=self._on_stop, state="disabled",
        )
        self.btn_stop.pack(fill="x", **pad)

        ctk.CTkButton(
            self, text="⚠  URGENCE", height=40, corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['EMERGENCY'], hover_color="#cc0000",
            command=self._on_emergency,
        ).pack(fill="x", padx=14, pady=(8, 4))

        self._separator()
        self._section_label("CLAVIER", **pad)

        for key, action in self.KEYS_INFO:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=14)
            ctk.CTkLabel(row, text=key, width=80,
                         font=ctk.CTkFont(family="Consolas", size=11),
                         text_color=COLORS['ACC'],
                         anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=action,
                         font=ctk.CTkFont(size=11),
                         anchor="w").pack(side="left")

    def _section_label(self, title: str, **pack_kw):
        ctk.CTkLabel(self, text=title,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS['ACC']).pack(anchor="w", **pack_kw)

    def _separator(self):
        ctk.CTkFrame(self, height=2, fg_color="gray75").pack(
            fill="x", padx=14, pady=8)

    # ── Actions ───────────────────────────────────────
    def _toggle_connect(self):
        if self._connected:
            self._on_disconnect()
        else:
            port = self.port_var.get()
            if not port:
                messagebox.showwarning("Port manquant",
                                       "Selectionnez un port COM.")
                return
            self._on_connect(port)

    # ── API publique ──────────────────────────────────
    def refresh_ports(self):
        """Met a jour la liste des ports COM disponibles."""
        ports = DroneSerial.list_ports()
        self.port_combo.configure(values=ports)
        if ports:
            self.port_var.set(ports[0])

    def set_connected(self, connected: bool):
        """Met a jour l'apparence selon l'etat de connexion."""
        self._connected = connected
        if connected:
            self.btn_connect.configure(text="Deconnecter",
                                       fg_color=COLORS['RED'],
                                       hover_color="#b91c1c")
            self.lbl_status.configure(text="●  Connecte",
                                      text_color=COLORS['GREEN'])
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="normal")
        else:
            self.btn_connect.configure(text="Connecter",
                                       fg_color=COLORS['GREEN'],
                                       hover_color="#15803d")
            self.lbl_status.configure(text="●  Deconnecte",
                                      text_color=COLORS['RED'])
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="disabled")
