# ui/connection_panel.py — Panneau gauche : connexion série + contrôle drone

import tkinter as tk
from tkinter import ttk, messagebox
from config import PALETTE
from serial_comm import DroneSerial


class ConnectionPanel(tk.Frame):
    """
    Panneau de connexion série et de contrôle haut niveau du drone.

    Callbacks attendus
    ------------------
    on_connect(port)  : appelé quand l'utilisateur clique "Connecter"
    on_disconnect()   : appelé quand l'utilisateur clique "Déconnecter"
    on_start()        : envoi de $start
    on_stop()         : envoi de $stop
    on_emergency()    : arrêt d'urgence $11111111
    """

    KEYS_INFO = [
        ("Z / ↑",   "Avant"),
        ("S / ↓",   "Arrière"),
        ("Q / ←",   "Gauche"),
        ("D / →",   "Droite"),
        ("Espace",  "Monter"),
        ("Shift",   "Descendre"),
        ("A",       "Yaw gauche"),
        ("E",       "Yaw droit"),
        ("Entrée",  "Start"),
        ("Échap",   "Urgence"),
    ]

    def __init__(self, parent, *, on_connect, on_disconnect,
                 on_start, on_stop, on_emergency):
        P = PALETTE
        super().__init__(parent, bg=P['PANEL'], padx=12, pady=10)

        self._on_connect    = on_connect
        self._on_disconnect = on_disconnect
        self._on_start      = on_start
        self._on_stop       = on_stop
        self._on_emergency  = on_emergency
        self._connected     = False

        self._build()

    # ── Construction ──────────────────────────────────
    def _build(self):
        P = PALETTE
        self._section("CONNEXION")

        # Sélection port COM
        port_row = tk.Frame(self, bg=P['PANEL'])
        port_row.pack(fill="x", pady=2)
        tk.Label(port_row, text="Port COM", bg=P['PANEL'], fg=P['TEXT'],
                 font=("Segoe UI", 9), width=9, anchor="w").pack(side="left")
        self.port_var   = tk.StringVar()
        self.port_combo = ttk.Combobox(port_row, textvariable=self.port_var,
                                       width=10, state="readonly")
        self.port_combo.pack(side="left")
        ttk.Button(port_row, text="↻", width=3,
                   command=self.refresh_ports).pack(side="left", padx=2)

        # Bouton connecter
        btn_row = tk.Frame(self, bg=P['PANEL'])
        btn_row.pack(fill="x", pady=6)
        self.btn_connect = tk.Button(
            btn_row, text="Connecter", bg=P['GREEN'], fg="white",
            font=("Segoe UI", 9, "bold"), relief="flat",
            padx=8, command=self._toggle_connect,
        )
        self.btn_connect.pack(side="left")

        # Indicateur d'état
        self.lbl_status = tk.Label(self, text="● Déconnecté",
                                   bg=P['PANEL'], fg=P['RED'],
                                   font=("Segoe UI", 9))
        self.lbl_status.pack(anchor="w", pady=4)

        self._separator()
        self._section("DRONE")

        self.btn_start = tk.Button(
            self, text="▶  START", bg=P['GREEN'], fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat",
            padx=10, pady=4, command=self._on_start, state="disabled",
        )
        self.btn_start.pack(fill="x", pady=2)

        self.btn_stop = tk.Button(
            self, text="■  STOP", bg=P['RED'], fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat",
            padx=10, pady=4, command=self._on_stop, state="disabled",
        )
        self.btn_stop.pack(fill="x", pady=2)

        tk.Button(
            self, text="⚠  URGENCE", bg="#ff0000", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat",
            padx=10, pady=6, command=self._on_emergency,
        ).pack(fill="x", pady=(8, 2))

        self._separator()
        self._section("CLAVIER")

        for key, action in self.KEYS_INFO:
            row = tk.Frame(self, bg=P['PANEL'])
            row.pack(fill="x")
            tk.Label(row, text=key, bg=P['PANEL'], fg=P['ACC'],
                     font=("Consolas", 8), width=10, anchor="w").pack(side="left")
            tk.Label(row, text=action, bg=P['PANEL'], fg=P['TEXT'],
                     font=("Segoe UI", 8), anchor="w").pack(side="left")

    def _section(self, title: str):
        P = PALETTE
        tk.Label(self, text=title, font=("Segoe UI", 9, "bold"),
                 bg=P['PANEL'], fg=P['ACC']).pack(anchor="w")
        tk.Frame(self, bg=P['ACC'], height=1).pack(fill="x", pady=(0, 8))

    def _separator(self):
        tk.Frame(self, bg=PALETTE['SUB'], height=1).pack(fill="x", pady=8)

    # ── Actions ───────────────────────────────────────
    def _toggle_connect(self):
        if self._connected:
            self._on_disconnect()
        else:
            port = self.port_var.get()
            if not port:
                messagebox.showwarning("Port manquant",
                                       "Sélectionnez un port COM.")
                return
            self._on_connect(port)

    # ── API publique ──────────────────────────────────
    def refresh_ports(self):
        """Met à jour la liste des ports COM disponibles."""
        ports = DroneSerial.list_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])

    def set_connected(self, connected: bool):
        """Met à jour l'apparence selon l'état de connexion."""
        P = PALETTE
        self._connected = connected
        if connected:
            self.btn_connect.configure(text="Déconnecter", bg=P['RED'])
            self.lbl_status.configure(text="● Connecté",   fg=P['GREEN'])
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="normal")
        else:
            self.btn_connect.configure(text="Connecter",    bg=P['GREEN'])
            self.lbl_status.configure(text="● Déconnecté", fg=P['RED'])
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="disabled")
