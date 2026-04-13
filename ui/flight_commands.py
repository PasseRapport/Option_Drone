# flight_commands.py — Gestion des commandes de vol
#
# Protocole trame de vol : $ABCDEFGH  (9 chars)
#   [1] monter    [2] descendre
#   [3] avant     [4] arrière
#   [5] gauche    [6] droite
#   [7] yaw CCW   [8] yaw CW
#
# Exemples :
#   $10000000  -> monter
#   $00110000  -> avant + gauche
#   $11111111  -> arrêt d'urgence

# ── Indices des axes ──────────────────────────────────
UP, DOWN, FORWARD, BACKWARD, LEFT, RIGHT, YAW_CCW, YAW_CW = range(8)

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

    def build_frame(self) -> str:
        """Retourne la trame prête à l'envoi, ex: '$10000000'."""
        bits = ''.join('1' if k else '0' for k in self._keys)
        return f"${bits}"

    def any_active(self) -> bool:
        return any(self._keys)

    def reset(self) -> None:
        self._keys = [False] * 8
