# config.py — Constantes globales de l'application

# ── Série ─────────────────────────────────────────────
BAUD_RATE     = 115200
SEND_INTERVAL = 0.05   # secondes entre deux trames de vol (20 Hz)

# ── Protocole drone ───────────────────────────────────
AXIS_LABELS = {
    'H': 'Hauteur',
    'P': 'Pitch',
    'R': 'Roll',
    'Y': 'Yaw',
}

# ── CustomTkinter — apparence ─────────────────────────
CTK_APPEARANCE = "light"     # "light", "dark", ou "system"
CTK_THEME      = "blue"      # thème couleur par défaut de CTk

# ── Couleurs personnalisées ───────────────────────────
COLORS = {
    'ACC':        '#2563eb',   # accent bleu
    'ACC_HOVER':  '#1d4ed8',   # accent bleu foncé au survol
    'RED':        '#dc2626',   # rouge (stop, erreur)
    'GREEN':      '#16a34a',   # vert (connexion, start)
    'EMERGENCY':  '#ff0000',   # rouge vif urgence
    'YAW':        '#7c3aed',   # violet — boutons yaw
    'YAW_HOVER':  '#6d28d9',   # violet foncé survol
    'PID_BTN':    '#ea580c',   # orange — appliquer PID
    'DPAD_BG':    '#b8c9e0',   # fond boutons dpad
    'DPAD_FG':    '#1e40af',   # texte boutons dpad
    'DPAD_HOVER': '#2563eb',   # fond boutons dpad survol
}
