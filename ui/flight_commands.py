# flight_commands.py — Gestion des commandes de vol
#
# Protocole trame de vol — BINAIRE : 2 octets
#   [0] 0x24 ('$') — identifiant
#   [1] octet de bits :
#         bit 7 : monter     bit 6 : descendre
#         bit 5 : avant      bit 4 : arrière
#         bit 3 : gauche     bit 2 : droite
#         bit 1 : yaw CCW    bit 0 : yaw CW
#
# Exemples :
#   24 80  -> monter        (0b10000000)
#   24 28  -> avant+gauche  (0b00101000)
#   24 FF  -> arrêt d'urgence

# ── Indices des axes ──────────────────────────────────
UP, DOWN, FORWARD, BACKWARD, LEFT, RIGHT, YAW_CCW, YAW_CW = range(8)

# ── Commandes spéciales ───────────────────────────────
CMD_ID    = 0x24   # '$' — identifiant trame de vol
CMD_START = bytes([CMD_ID, 0x01])
CMD_STOP  = bytes([CMD_ID, 0x02])
CMD_EMERGENCY = bytes([CMD_ID, 0xFF])

# ── Mapping clavier → indice ──────────────────────────
KEY_MAP: dict[str, int] = {
    'z':       FORWARD,
    'Up':      FORWARD,
    's':       BACKWARD,
    'Down':    BACKWARD,
    'q':       LEFT,
    'Left':    LEFT,
    'd':       RIGHT,
    'Right':   RIGHT,
    'space':   UP,
    'shift':   DOWN,
    'Shift_L': DOWN,
    'Shift_R': DOWN,
    'a':       YAW_CCW,
    'e':       YAW_CW,
}


class FlightCommands:
    """Maintient l'état des touches actives et construit la trame de commande."""

    # Paires de commandes opposées : activer l'une désactive l'autre
    _OPPOSITES: dict[int, int] = {
        UP:      DOWN,     DOWN:     UP,
        FORWARD: BACKWARD, BACKWARD: FORWARD,
        LEFT:    RIGHT,    RIGHT:    LEFT,
        YAW_CCW: YAW_CW,  YAW_CW:   YAW_CCW,
    }

    def __init__(self):
        self._keys: list[bool] = [False] * 8

    def set_key(self, index: int, pressed: bool) -> None:
        if pressed:
            # Annule automatiquement la commande opposée
            opposite = self._OPPOSITES.get(index)
            if opposite is not None:
                self._keys[opposite] = False
        self._keys[index] = pressed

    def build_frame(self) -> bytes:
        """Retourne la trame binaire prête à l'envoi.

        Structure : [0x24, bits] où bits est un octet avec :
          bit 7 = UP, bit 6 = DOWN, bit 5 = FWD, bit 4 = BWD,
          bit 3 = LEFT, bit 2 = RIGHT, bit 1 = YAW_CCW, bit 0 = YAW_CW
        """
        bits = sum(1 << (7 - i) for i, k in enumerate(self._keys) if k)
        return bytes([CMD_ID, bits])

    def any_active(self) -> bool:
        return any(self._keys)

    def reset(self) -> None:
        self._keys = [False] * 8
