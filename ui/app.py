# ui/app.py — Fenêtre principale : assemble les panneaux et orchestre la logique

import threading
import time
import tkinter as tk

from config import PALETTE, SEND_INTERVAL
from serial_comm import DroneSerial
from flight_commands import FlightCommands, KEY_MAP

from ui.connection_panel import ConnectionPanel
from ui.control_panel    import ControlPanel
from ui.pid_panel        import PidPanel
from ui.console_panel    import ConsolePanel


class DroneController(tk.Tk):
    """Fenêtre principale de l'interface drone."""

    def __init__(self):
        super().__init__()
        self.title("ENSEA Drone Controller")
        self.resizable(False, False)
        self.configure(bg=PALETTE['BG'])

        # Modèles métier
        self.flight = FlightCommands()
        self.drone  = DroneSerial(log_callback=self._log)

        # État d'envoi continu
        self._send_active = False
        self._send_thread: threading.Thread | None = None

        self._build_ui()
        self._bind_keys()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Construction de l'interface ───────────────────
    def _build_ui(self):
        P = PALETTE

        tk.Label(self, text="ENSEA Drone Controller",
                 font=("Segoe UI", 16, "bold"),
                 bg=P['BG'], fg=P['ACC']).pack(pady=(12, 4))

        body = tk.Frame(self, bg=P['BG'])
        body.pack(padx=12, pady=4, fill="both")

        # Panneau gauche — connexion + contrôle drone
        self.conn_panel = ConnectionPanel(
            body,
            on_connect    = self._on_connect,
            on_disconnect = self._on_disconnect,
            on_start      = self._start_drone,
            on_stop       = self._stop_drone,
            on_emergency  = self._emergency_stop,
        )
        self.conn_panel.grid(row=0, column=0, sticky="ns", padx=(0, 8))

        # Panneau centre — pad de vol
        self.ctrl_panel = ControlPanel(
            body,
            on_press   = self._key_press,
            on_release = self._key_release,
        )
        self.ctrl_panel.grid(row=0, column=1, sticky="ns", padx=(0, 8))

        # Panneau droite — PID
        self.pid_panel = PidPanel(
            body,
            on_send      = self._send_pid_coeff,
            log_callback = self._log,
        )
        self.pid_panel.grid(row=0, column=2, sticky="ns")

        # Console bas de page
        self.console = ConsolePanel(self)
        self.console.pack(padx=12, pady=(6, 10), fill="both")

        self.conn_panel.refresh_ports()

    # ── Clavier ───────────────────────────────────────
    def _bind_keys(self):
        self.bind("<KeyPress>",   self._on_keypress)
        self.bind("<KeyRelease>", self._on_keyrelease)
        self.bind("<Return>",     lambda _: self._start_drone())
        self.bind("<Escape>",     lambda _: self._emergency_stop())

    def _on_keypress(self, event):
        key = event.keysym.lower() if len(event.keysym) == 1 else event.keysym
        if key in KEY_MAP:
            self._key_press(KEY_MAP[key])

    def _on_keyrelease(self, event):
        key = event.keysym.lower() if len(event.keysym) == 1 else event.keysym
        if key in KEY_MAP:
            self._key_release(KEY_MAP[key])

    def _key_press(self, idx: int):
        self.flight.set_key(idx, True)
        if not self._send_active:
            self._start_sending()

    def _key_release(self, idx: int):
        self.flight.set_key(idx, False)
        if not self.flight.any_active():
            self._stop_sending()

    # ── Envoi continu (thread séparé) ─────────────────
    def _start_sending(self):
        self._send_active = True
        self._send_thread = threading.Thread(
            target=self._send_loop, daemon=True
        )
        self._send_thread.start()

    def _stop_sending(self):
        self._send_active = False

    def _send_loop(self):
        while self._send_active:
            self.drone.send(self.flight.build_frame())
            time.sleep(SEND_INTERVAL)

    # ── Callbacks connexion ───────────────────────────
    def _on_connect(self, port: str):
        ok = self.drone.connect(port)
        self.conn_panel.set_connected(ok)

    def _on_disconnect(self):
        self.drone.disconnect()
        self.conn_panel.set_connected(False)

    # ── Callbacks contrôle drone ──────────────────────
    def _start_drone(self):
        self.drone.send("$start")

    def _stop_drone(self):
        self.flight.reset()
        self._stop_sending()
        self.drone.send("$stop")

    def _emergency_stop(self):
        self.flight.reset()
        self._stop_sending()
        self.drone.send("$11111111")
        self._log("[⚠] ARRÊT D'URGENCE ENVOYÉ")

    # ── Callback PID ──────────────────────────────────
    def _send_pid_coeff(self, axis: str, coeff: str, raw_str: str):
        """Formate et envoie un coefficient PID : *[axe][coeff][6 chars]."""
        val_str = f"{float(raw_str):.4f}"[:6].ljust(6, '0')
        self.drone.send(f"*{axis}{coeff}{val_str}")

    # ── Log (thread-safe) ─────────────────────────────
    def _log(self, message: str):
        self.after(0, self.console.append, message)

    # ── Fermeture propre ──────────────────────────────
    def _on_close(self):
        self._stop_sending()
        if self.drone.is_connected():
            self.drone.send("$stop")
            time.sleep(0.1)
            self.drone.disconnect()
        self.destroy()
