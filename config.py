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

# ── Palette graphique (thème bleu ardoise clair) ──────
PALETTE = {
    'BG':         '#eef2f7',   # fond principal
    'PANEL':      '#dde4ef',   # fond des panneaux
    'ACC':        '#2563eb',   # accent bleu
    'RED':        '#dc2626',   # rouge (stop, erreur)
    'GREEN':      '#16a34a',   # vert (connexion, start)
    'TEXT':       '#1e293b',   # texte principal
    'SUB':        '#64748b',   # texte secondaire / séparateurs
    'DPAD_BG':    '#b8c9e0',   # fond boutons dpad
    'DPAD_FG':    '#1e40af',   # icône boutons dpad
    'DPAD_HOVER': '#2563eb',   # fond boutons dpad au survol
    'ENTRY_BG':   '#c8d5e8',   # fond champs de saisie
    'CONSOLE_BG': '#f0f5fb',   # fond console
    'YAW':        '#7c3aed',   # violet — boutons yaw
    'PID_BTN':    '#ea580c',   # orange — bouton appliquer PID
}
