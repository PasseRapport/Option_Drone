# serial_comm.py — Communication série avec le STM32 émetteur NRF24L01
#
# Le STM32 émetteur reçoit les trames via UART (115200 baud) et les
# retransmet au drone via NRF24L01+ (2.4 GHz, 250 kbps).
#
# Trames envoyées : ASCII + '\n'  (ex: "$10000000\n", "$start\n")
# Trames reçues   : messages de debug UART du drone (logs état, PID…)

import threading
import serial
import serial.tools.list_ports
from config import BAUD_RATE


class DroneSerial:
    """Gère la connexion série et l'envoi/réception de trames."""

    def __init__(self, log_callback):
        """
        Parameters
        ----------
        log_callback : callable(str)
            Fonction appelée pour afficher un message dans la console.
        """
        self._ser: serial.Serial | None = None
        self._log = log_callback
        self._read_thread: threading.Thread | None = None
        self._stop_read = threading.Event()

    # ── Connexion ─────────────────────────────────────
    def connect(self, port: str) -> bool:
        """Ouvre le port série. Retourne True si succès."""
        try:
            self._ser = serial.Serial(port, BAUD_RATE, timeout=0.1)
            self._stop_read.clear()
            self._read_thread = threading.Thread(
                target=self._read_loop, daemon=True
            )
            self._read_thread.start()
            self._log(f"[OK] Connecté sur {port} à {BAUD_RATE} baud")
            return True
        except serial.SerialException as exc:
            self._log(f"[ERREUR] Connexion impossible : {exc}")
            return False

    def disconnect(self) -> None:
        """Ferme proprement le port série."""
        self._stop_read.set()
        if self._ser and self._ser.is_open:
            self._ser.close()
        self._ser = None
        self._log("[INFO] Déconnecté")

    def is_connected(self) -> bool:
        return self._ser is not None and self._ser.is_open

    # ── Envoi ─────────────────────────────────────────
    def send(self, message: str) -> None:
        """Envoie une trame ASCII terminée par '\\n'."""
        if not self.is_connected():
            return
        try:
            self._ser.write((message + '\n').encode('ascii'))
            self._log(f"[TX] {message}")
        except serial.SerialException as exc:
            self._log(f"[ERREUR] Envoi : {exc}")

    # ── Réception (thread) ────────────────────────────
    def _read_loop(self) -> None:
        while not self._stop_read.is_set():
            if self._ser and self._ser.is_open:
                try:
                    line = self._ser.readline()
                    if line:
                        decoded = line.decode('ascii', errors='replace').strip()
                        self._log(f"[RX] {decoded}")
                except serial.SerialException:
                    break

    # ── Utilitaire ────────────────────────────────────
    @staticmethod
    def list_ports() -> list[str]:
        """Retourne la liste des ports COM disponibles."""
        return [p.device for p in serial.tools.list_ports.comports()]
