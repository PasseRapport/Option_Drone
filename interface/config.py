# config.py — Constantes globales de l'application

# ── Série ─────────────────────────────────────────────
BAUD_RATE      = 115200
SEND_INTERVAL  = 0.05   # secondes entre deux trames de vol (20 Hz)

# Doit correspondre exactement à NRF24L01P_PAYLOAD_LENGTH dans le firmware STM32.
# Le STM32 lit toujours ce nombre fixe d'octets — une trame plus courte ou plus
# longue laisse des octets résiduels dans le buffer UART et corrompt la suivante.
PAYLOAD_LENGTH = 8     # à ajuster si la valeur change dans nrf24l01p.h

DEFAULT_LANG  = 'en'

# ── CustomTkinter — apparence ─────────────────────────
CTK_APPEARANCE = "light"     # "light", "dark", ou "system"
CTK_THEME      = "blue"

# ── Couleurs personnalisées ───────────────────────────
COLORS = {
    'ACC':        '#2563eb',
    'ACC_HOVER':  '#1d4ed8',
    'RED':        '#dc2626',
    'GREEN':      '#16a34a',
    'EMERGENCY':  '#ff0000',
    'YAW':        '#7c3aed',
    'YAW_HOVER':  '#6d28d9',
    'PID_BTN':    '#ea580c',
    'DPAD_BG':    '#b8c9e0',
    'DPAD_FG':    '#1e40af',
    'DPAD_HOVER': '#2563eb',
}

# ── Traductions FR / EN ───────────────────────────────
TRANSLATIONS: dict[str, dict] = {
    'fr': {
        # App
        'app_title':         'ENSEA Drone Controller',
        'lang_btn':          '🌐 EN',
        # Connexion
        'section_conn':      'CONNEXION',
        'section_drone':     'DRONE',
        'section_keyboard':  'CLAVIER',
        'port_label':        'Port COM',
        'btn_connect':       'Connecter',
        'btn_disconnect':    'Déconnecter',
        'status_connected':  '●  Connecté',
        'status_disconn':    '●  Déconnecté',
        'status_connecting': '●  Connexion en cours...',
        'connecting_frames': ['Connexion ·  ', 'Connexion  · ', 'Connexion   ·'],
        'btn_start':         '▶  START',
        'btn_stop':          '■  STOP',
        'btn_emergency':     '⚠  URGENCE',
        'warn_port_title':   'Port manquant',
        'warn_port_msg':     'Sélectionnez un port COM.',
        'keys_info': [
            ('Z / ↑',   'Avant'),
            ('S / ↓',   'Arrière'),
            ('Q / ←',   'Gauche'),
            ('D / →',   'Droite'),
            ('Espace',  'Monter'),
            ('Shift',   'Descendre'),
            ('A',       'Yaw gauche'),
            ('E',       'Yaw droit'),
            ('Entrée',  'Start'),
            ('Échap',   'Urgence'),
        ],
        # Contrôle de vol
        'section_flight':    'CONTRÔLE DE VOL',
        'sub_altitude':      'Altitude',
        'btn_up':            '▲  MONTER',
        'btn_down':          '▼  DESCENDRE',
        'sub_direction':     'Direction',
        'sub_yaw':           'Lacet (Yaw)',
        # PID
        'section_pid':       'RÉGLAGE PID',
        'col_axis':          'Axe',
        'btn_send_all':      'Envoyer tout',
        'axis_labels':       {'H': 'Hauteur', 'P': 'Pitch', 'R': 'Roll', 'Y': 'Yaw'},
        # Console
        'console_title':     'Console',
        'btn_clear':         'Effacer',
        # Avertissements
        'warn_not_conn':     '[ATTENTION] Non connecté — commande ignorée',
    },
    'en': {
        # App
        'app_title':         'ENSEA Drone Controller',
        'lang_btn':          '🌐 FR',
        # Connection
        'section_conn':      'CONNECTION',
        'section_drone':     'DRONE',
        'section_keyboard':  'KEYBOARD',
        'port_label':        'COM Port',
        'btn_connect':       'Connect',
        'btn_disconnect':    'Disconnect',
        'status_connected':  '●  Connected',
        'status_disconn':    '●  Disconnected',
        'status_connecting': '●  Connecting...',
        'connecting_frames': ['Connecting ·  ', 'Connecting  · ', 'Connecting   ·'],
        'btn_start':         '▶  START',
        'btn_stop':          '■  STOP',
        'btn_emergency':     '⚠  EMERGENCY',
        'warn_port_title':   'Missing port',
        'warn_port_msg':     'Please select a COM port.',
        'keys_info': [
            ('Z / ↑',   'Forward'),
            ('S / ↓',   'Backward'),
            ('Q / ←',   'Left'),
            ('D / →',   'Right'),
            ('Space',   'Ascend'),
            ('Shift',   'Descend'),
            ('A',       'Yaw left'),
            ('E',       'Yaw right'),
            ('Enter',   'Start'),
            ('Escape',  'Emergency'),
        ],
        # Flight control
        'section_flight':    'FLIGHT CONTROL',
        'sub_altitude':      'Altitude',
        'btn_up':            '▲  ASCEND',
        'btn_down':          '▼  DESCEND',
        'sub_direction':     'Direction',
        'sub_yaw':           'Yaw',
        # PID
        'section_pid':       'PID TUNING',
        'col_axis':          'Axis',
        'btn_send_all':      'Send all',
        'axis_labels':       {'H': 'Height', 'P': 'Pitch', 'R': 'Roll', 'Y': 'Yaw'},
        # Console
        'console_title':     'Console',
        'btn_clear':         'Clear',
        # Warnings
        'warn_not_conn':     '[WARNING] Not connected — command ignored',
    },
}

# Raccourci : labels d'axes par défaut (langue initiale)
AXIS_LABELS = TRANSLATIONS[DEFAULT_LANG]['axis_labels']
