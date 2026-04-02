"""
ENSEA Drone Controller - Interface Graphique PC
================================================
Protocole de communication (via UART 115200 baud vers STM32 émetteur NRF24L01) :

  Commandes de vol   : $ABCDEFGH  (9 chars total)
    [1] = monter      (1=actif, 0=inactif)
    [2] = descendre   (1=actif, 0=inactif)
    [3] = avant       (pitch+)
    [4] = arrière     (pitch-)
    [5] = gauche      (roll+)
    [6] = droite      (roll-)
    [7] = yaw CCW     (rotation gauche)
    [8] = yaw CW      (rotation droite)
  Ex: $10000000 = monter uniquement

  Commandes spéciales :
    $start            -> initialisation + passage en FLYING_STATE
    $stop             -> arrêt du drone (STOP_STATE)
    $11111111         -> arrêt d'urgence

  Modification PID   : *[axe][coeff][valeur 6 chars]
    axe   : H(height), P(pitch), R(roll), Y(yaw)
    coeff : P(Kp), I(Ki), D(Kd)
    Ex: *HP0.500  -> Kp hauteur = 0.5

Touches clavier :
  Z / Flèche Haut    -> Avant
  S / Flèche Bas     -> Arrière
  Q / Flèche Gauche  -> Gauche
  D / Flèche Droite  -> Droite
  Espace             -> Monter
  Shift              -> Descendre
  A                  -> Yaw gauche (CCW)
  E                  -> Yaw droit  (CW)
  Entrée             -> Start
  Échap              -> Stop d'urgence
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import threading
import time


# ─────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────
BAUD_RATE     = 115200
SEND_INTERVAL = 0.05   # 50 ms entre chaque envoi de commande (20 Hz)

AXIS_LABELS = {
    'H': 'Hauteur',
    'P': 'Pitch',
    'R': 'Roll',
    'Y': 'Yaw',
}


# ─────────────────────────────────────────────
#  Logique de communication série
# ─────────────────────────────────────────────
class DroneSerial:
    def __init__(self, log_callback):
        self.ser = None
        self.log = log_callback
        self._read_thread = None
        self._stop_read = threading.Event()

    def connect(self, port):
        try:
            self.ser = serial.Serial(port, BAUD_RATE, timeout=0.1)
            self._stop_read.clear()
            self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._read_thread.start()
            self.log(f"[OK] Connecté sur {port} à {BAUD_RATE} baud")
            return True
        except serial.SerialException as e:
            self.log(f"[ERREUR] Connexion impossible : {e}")
            return False

    def disconnect(self):
        self._stop_read.set()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None
        self.log("[INFO] Déconnecté")

    def is_connected(self):
        return self.ser is not None and self.ser.is_open

    def send(self, message: str):
        if not self.is_connected():
            return
        try:
            data = (message + '\n').encode('ascii')
            self.ser.write(data)
            self.log(f"[TX] {message}")
        except serial.SerialException as e:
            self.log(f"[ERREUR] Envoi : {e}")

    def _read_loop(self):
        while not self._stop_read.is_set():
            if self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline()
                    if line:
                        decoded = line.decode('ascii', errors='replace').strip()
                        self.log(f"[RX] {decoded}")
                except serial.SerialException:
                    break


# ─────────────────────────────────────────────
#  Gestion des commandes de vol
# ─────────────────────────────────────────────
class FlightCommands:
    """Maintient l'état des touches pressées et génère la trame $ABCDEFGH."""

    def __init__(self):
        # Ordre : monter, descendre, avant, arrière, gauche, droite, yaw_ccw, yaw_cw
        self._keys = [False] * 8

    def set_key(self, index: int, pressed: bool):
        self._keys[index] = pressed

    def build_frame(self) -> str:
        bits = ''.join('1' if k else '0' for k in self._keys)
        return f"${bits}"

    def any_active(self) -> bool:
        return any(self._keys)

    def reset(self):
        self._keys = [False] * 8


# Index des touches
UP, DOWN, FORWARD, BACKWARD, LEFT, RIGHT, YAW_CCW, YAW_CW = range(8)

KEY_MAP = {
    'z': FORWARD,   'Up': FORWARD,
    's': BACKWARD,  'Down': BACKWARD,
    'q': LEFT,      'Left': LEFT,
    'd': RIGHT,     'Right': RIGHT,
    'space': UP,
    'shift': DOWN,  'Shift_L': DOWN, 'Shift_R': DOWN,
    'a': YAW_CCW,
    'e': YAW_CW,
}


# ─────────────────────────────────────────────
#  Interface graphique principale
# ─────────────────────────────────────────────
class DroneController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ENSEA Drone Controller")
        self.resizable(False, False)
        self.configure(bg="#eef2f7")

        self.flight = FlightCommands()
        self.drone  = DroneSerial(log_callback=self._log)
        self._send_active = False
        self._send_thread = None
        self._drone_started = False

        self._build_ui()
        self._bind_keys()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Construction UI ──────────────────────
    def _build_ui(self):
        # Palette - thème bleu ardoise clair
        BG    = "#eef2f7"
        PANEL = "#dde4ef"
        ACC   = "#2563eb"   # bleu accent
        RED   = "#dc2626"
        GREEN = "#16a34a"
        TEXT  = "#1e293b"
        SUB   = "#64748b"

        # ── Titre ────────────────────────────
        tk.Label(self, text="ENSEA Drone Controller", font=("Segoe UI", 16, "bold"),
                 bg=BG, fg=ACC).pack(pady=(12, 4))

        # ── Corps principal ──────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(padx=12, pady=4, fill="both")

        # ─ Colonne gauche : connexion + état ─
        left = tk.Frame(body, bg=PANEL, bd=0, relief="flat", padx=12, pady=10)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 8))

        tk.Label(left, text="CONNEXION", font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=ACC).pack(anchor="w")
        tk.Frame(left, bg=ACC, height=1).pack(fill="x", pady=(0, 8))

        # Port
        port_row = tk.Frame(left, bg=PANEL)
        port_row.pack(fill="x", pady=2)
        tk.Label(port_row, text="Port COM", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 9), width=9, anchor="w").pack(side="left")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_row, textvariable=self.port_var,
                                       width=10, state="readonly")
        self.port_combo.pack(side="left")
        ttk.Button(port_row, text="↻", width=3,
                   command=self._refresh_ports).pack(side="left", padx=2)

        # Boutons connexion
        btn_row = tk.Frame(left, bg=PANEL)
        btn_row.pack(fill="x", pady=6)
        self.btn_connect = tk.Button(btn_row, text="Connecter", bg=GREEN, fg="white",
                                     font=("Segoe UI", 9, "bold"), relief="flat",
                                     padx=8, command=self._toggle_connect)
        self.btn_connect.pack(side="left", padx=(0, 4))

        # Status
        self.lbl_status = tk.Label(left, text="● Déconnecté", bg=PANEL, fg=RED,
                                   font=("Segoe UI", 9))
        self.lbl_status.pack(anchor="w", pady=4)

        tk.Frame(left, bg=SUB, height=1).pack(fill="x", pady=8)

        # Boutons démarrage drone
        tk.Label(left, text="DRONE", font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=ACC).pack(anchor="w")
        tk.Frame(left, bg=ACC, height=1).pack(fill="x", pady=(0, 8))

        self.btn_start = tk.Button(left, text="▶  START", bg=GREEN, fg="white",
                                   font=("Segoe UI", 10, "bold"), relief="flat",
                                   padx=10, pady=4, command=self._start_drone,
                                   state="disabled")
        self.btn_start.pack(fill="x", pady=2)

        self.btn_stop = tk.Button(left, text="■  STOP", bg=RED, fg="white",
                                  font=("Segoe UI", 10, "bold"), relief="flat",
                                  padx=10, pady=4, command=self._stop_drone,
                                  state="disabled")
        self.btn_stop.pack(fill="x", pady=2)

        self.btn_emergency = tk.Button(left, text="⚠ URGENCE", bg="#ff0000", fg="white",
                                       font=("Segoe UI", 10, "bold"), relief="flat",
                                       padx=10, pady=6, command=self._emergency_stop)
        self.btn_emergency.pack(fill="x", pady=(8, 2))

        # Légende clavier
        tk.Frame(left, bg=SUB, height=1).pack(fill="x", pady=8)
        tk.Label(left, text="CLAVIER", font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=ACC).pack(anchor="w")
        tk.Frame(left, bg=ACC, height=1).pack(fill="x", pady=(0, 6))
        keys_info = [
            ("Z / ↑", "Avant"),
            ("S / ↓", "Arrière"),
            ("Q / ←", "Gauche"),
            ("D / →", "Droite"),
            ("Espace", "Monter"),
            ("Shift", "Descendre"),
            ("A", "Yaw gauche"),
            ("E", "Yaw droit"),
            ("Entrée", "Start"),
            ("Échap", "Stop urgence"),
        ]
        for k, v in keys_info:
            row = tk.Frame(left, bg=PANEL)
            row.pack(fill="x")
            tk.Label(row, text=k, bg=PANEL, fg=ACC, font=("Consolas", 8),
                     width=10, anchor="w").pack(side="left")
            tk.Label(row, text=v, bg=PANEL, fg=TEXT, font=("Segoe UI", 8),
                     anchor="w").pack(side="left")

        # ─ Colonne centre : pad de contrôle ──
        mid = tk.Frame(body, bg=PANEL, bd=0, relief="flat", padx=16, pady=10)
        mid.grid(row=0, column=1, sticky="ns", padx=(0, 8))

        tk.Label(mid, text="CONTRÔLE DE VOL", font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=ACC).pack(anchor="w")
        tk.Frame(mid, bg=ACC, height=1).pack(fill="x", pady=(0, 8))

        # Altitude
        alt_frame = tk.LabelFrame(mid, text="Altitude", bg=PANEL, fg=SUB,
                                  font=("Segoe UI", 8), bd=1, padx=6, pady=4)
        alt_frame.pack(fill="x", pady=4)
        alt_inner = tk.Frame(alt_frame, bg=PANEL)
        alt_inner.pack()
        self.btn_up = self._flight_btn(alt_inner, "▲  MONTER", UP,   bg=ACC, row=0, col=0)
        self.btn_dn = self._flight_btn(alt_inner, "▼  DESCENDRE", DOWN, bg=ACC, row=0, col=1)

        # Direction
        dir_frame = tk.LabelFrame(mid, text="Direction", bg=PANEL, fg=SUB,
                                  font=("Segoe UI", 8), bd=1, padx=6, pady=4)
        dir_frame.pack(fill="x", pady=4)

        pad = tk.Frame(dir_frame, bg=PANEL)
        pad.pack()

        SIZE = 54
        BTN_CFG = dict(font=("Segoe UI", 14), relief="flat", width=3, height=1)

        self.btn_fwd  = self._dpad_btn(pad, "↑", FORWARD,  0, 1, SIZE, BTN_CFG)
        self.btn_lft  = self._dpad_btn(pad, "←", LEFT,     1, 0, SIZE, BTN_CFG)
        self.btn_ctr  = tk.Label(pad, text="●", font=("Segoe UI", 14), bg="#b8c9e0",
                                 fg=SUB, width=3, height=1)
        self.btn_ctr.grid(row=1, column=1, padx=2, pady=2, ipadx=4, ipady=4)
        self.btn_rgt  = self._dpad_btn(pad, "→", RIGHT,    1, 2, SIZE, BTN_CFG)
        self.btn_bck  = self._dpad_btn(pad, "↓", BACKWARD, 2, 1, SIZE, BTN_CFG)

        # Yaw
        yaw_frame = tk.LabelFrame(mid, text="Lacet (Yaw)", bg=PANEL, fg=SUB,
                                  font=("Segoe UI", 8), bd=1, padx=6, pady=4)
        yaw_frame.pack(fill="x", pady=4)
        yaw_inner = tk.Frame(yaw_frame, bg=PANEL)
        yaw_inner.pack()
        self.btn_yccw = self._flight_btn(yaw_inner, "↺  CCW", YAW_CCW, bg="#7c3aed", row=0, col=0)
        self.btn_ycw  = self._flight_btn(yaw_inner, "↻  CW",  YAW_CW,  bg="#7c3aed", row=0, col=1)

        # ─ Colonne droite : PID ──────────────
        right = tk.Frame(body, bg=PANEL, bd=0, relief="flat", padx=14, pady=10)
        right.grid(row=0, column=2, sticky="ns")

        tk.Label(right, text="RÉGLAGE PID", font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=ACC).pack(anchor="w")
        tk.Frame(right, bg=ACC, height=1).pack(fill="x", pady=(0, 8))

        # Headers
        hdr = tk.Frame(right, bg=PANEL)
        hdr.pack(fill="x")
        for col, txt in enumerate(["Axe", "Kp", "Ki", "Kd", ""]):
            tk.Label(hdr, text=txt, bg=PANEL, fg=SUB, font=("Segoe UI", 8, "bold"),
                     width=[5, 7, 7, 7, 6][col], anchor="center").grid(row=0, column=col, padx=2)

        self._pid_vars = {}
        for axis, label in AXIS_LABELS.items():
            row_f = tk.Frame(right, bg=PANEL)
            row_f.pack(fill="x", pady=3)
            tk.Label(row_f, text=label, bg=PANEL, fg=TEXT,
                     font=("Segoe UI", 9), width=7, anchor="w").grid(row=0, column=0, padx=2)
            self._pid_vars[axis] = {}
            for ci, coeff in enumerate(['P', 'I', 'D']):
                var = tk.StringVar(value="0.0")
                e = tk.Entry(row_f, textvariable=var, width=7,
                             bg="#c8d5e8", fg=TEXT, insertbackground=TEXT,
                             relief="flat", font=("Consolas", 9), justify="center")
                e.grid(row=0, column=ci + 1, padx=2)
                self._pid_vars[axis][coeff] = var
            tk.Button(row_f, text="✓", bg="#ea580c", fg="white",
                      font=("Segoe UI", 9, "bold"), relief="flat", padx=4,
                      command=lambda a=axis: self._send_pid(a)).grid(row=0, column=4, padx=2)

        tk.Frame(right, bg=SUB, height=1).pack(fill="x", pady=8)
        tk.Button(right, text="Envoyer tout", bg=ACC, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=4,
                  command=self._send_all_pid).pack(fill="x")

        # ── Console ──────────────────────────
        console_frame = tk.Frame(self, bg=BG)
        console_frame.pack(padx=12, pady=(6, 10), fill="both")
        tk.Label(console_frame, text="Console", font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=ACC).pack(anchor="w")
        self.console = scrolledtext.ScrolledText(
            console_frame, height=7, bg="#f0f5fb", fg=TEXT,
            font=("Consolas", 8), relief="flat", state="disabled",
            insertbackground=TEXT
        )
        self.console.pack(fill="both")
        tk.Button(console_frame, text="Effacer", bg=PANEL, fg=SUB,
                  font=("Segoe UI", 8), relief="flat", padx=6,
                  command=self._clear_console).pack(anchor="e", pady=2)

        self._refresh_ports()

    def _flight_btn(self, parent, text, key_idx, bg, row, col):
        b = tk.Button(parent, text=text, bg=bg, fg="white",
                      font=("Segoe UI", 9, "bold"), relief="flat",
                      padx=8, pady=4)
        b.grid(row=row, column=col, padx=4, pady=2)
        b.bind("<ButtonPress-1>",   lambda e, k=key_idx: self._key_press(k))
        b.bind("<ButtonRelease-1>", lambda e, k=key_idx: self._key_release(k))
        return b

    def _dpad_btn(self, parent, symbol, key_idx, row, col, size, cfg):
        b = tk.Button(parent, text=symbol, bg="#b8c9e0", fg="#1e40af",
                      activebackground="#2563eb", activeforeground="white",
                      **cfg)
        b.grid(row=row, column=col, padx=2, pady=2, ipadx=4, ipady=4)
        b.bind("<ButtonPress-1>",   lambda e, k=key_idx: self._key_press(k))
        b.bind("<ButtonRelease-1>", lambda e, k=key_idx: self._key_release(k))
        return b

    # ── Liaison clavier ──────────────────────
    def _bind_keys(self):
        self.bind("<KeyPress>",   self._on_keypress)
        self.bind("<KeyRelease>", self._on_keyrelease)
        self.bind("<Return>",     lambda e: self._start_drone())
        self.bind("<Escape>",     lambda e: self._emergency_stop())

    def _on_keypress(self, event):
        key = event.keysym.lower() if len(event.keysym) == 1 else event.keysym
        if key in KEY_MAP:
            self._key_press(KEY_MAP[key])

    def _on_keyrelease(self, event):
        key = event.keysym.lower() if len(event.keysym) == 1 else event.keysym
        if key in KEY_MAP:
            self._key_release(KEY_MAP[key])

    def _key_press(self, idx):
        self.flight.set_key(idx, True)
        if not self._send_active:
            self._start_sending()

    def _key_release(self, idx):
        self.flight.set_key(idx, False)
        if not self.flight.any_active():
            self._stop_sending()

    # ── Envoi continu ────────────────────────
    def _start_sending(self):
        self._send_active = True
        self._send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self._send_thread.start()

    def _stop_sending(self):
        self._send_active = False

    def _send_loop(self):
        while self._send_active:
            frame = self.flight.build_frame()
            self.drone.send(frame)
            time.sleep(SEND_INTERVAL)

    # ── Ports série ──────────────────────────
    def _refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])

    # ── Connexion ────────────────────────────
    def _toggle_connect(self):
        if self.drone.is_connected():
            self.drone.disconnect()
            self.btn_connect.configure(text="Connecter", bg="#16a34a")
            self.lbl_status.configure(text="● Déconnecté", fg="#dc2626")
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="disabled")
        else:
            port = self.port_var.get()
            if not port:
                messagebox.showwarning("Port manquant", "Sélectionnez un port COM.")
                return
            ok = self.drone.connect(port)
            if ok:
                self.btn_connect.configure(text="Déconnecter", bg="#dc2626")
                self.lbl_status.configure(text="● Connecté", fg="#16a34a")
                self.btn_start.configure(state="normal")
                self.btn_stop.configure(state="normal")

    # ── Contrôle drone ───────────────────────
    def _start_drone(self):
        self.drone.send("$start")
        self._drone_started = True

    def _stop_drone(self):
        self.drone.send("$stop")
        self.flight.reset()
        self._stop_sending()
        self._drone_started = False

    def _emergency_stop(self):
        self.flight.reset()
        self._stop_sending()
        self.drone.send("$11111111")
        self._log("[⚠] ARRÊT D'URGENCE ENVOYÉ")

    # ── PID ──────────────────────────────────
    def _send_pid(self, axis: str):
        for coeff in ['P', 'I', 'D']:
            raw = self._pid_vars[axis][coeff].get().strip()
            try:
                val = float(raw)
            except ValueError:
                self._log(f"[ERREUR] Valeur invalide pour {axis}/{coeff}: '{raw}'")
                continue
            # Format: *[axe][coeff][valeur 6 chars]
            val_str = f"{val:.4f}"[:6].ljust(6, '0')
            frame = f"*{axis}{coeff}{val_str}"
            self.drone.send(frame)
            time.sleep(0.05)

    def _send_all_pid(self):
        for axis in AXIS_LABELS:
            self._send_pid(axis)

    # ── Console ──────────────────────────────
    def _log(self, message: str):
        # Thread-safe
        self.after(0, self._append_log, message)

    def _append_log(self, message: str):
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def _clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    # ── Fermeture ────────────────────────────
    def _on_close(self):
        self._stop_sending()
        if self.drone.is_connected():
            self.drone.send("$stop")
            time.sleep(0.1)
            self.drone.disconnect()
        self.destroy()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = DroneController()
    app.mainloop()
