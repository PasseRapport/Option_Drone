# ui/console_panel.py — Panneau console (log serie)

import customtkinter as ctk
from config import COLORS, TRANSLATIONS, DEFAULT_LANG


class ConsolePanel(ctk.CTkFrame):
    """Zone de log scrollable affichant les messages TX/RX et info."""

    def __init__(self, parent, lang=DEFAULT_LANG):
        super().__init__(parent, fg_color="transparent")
        self._lang = lang
        self._build()

    def _build(self):
        T = TRANSLATIONS[self._lang]

        self._lbl_title = ctk.CTkLabel(
            self, text=T['console_title'],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['ACC'],
        )
        self._lbl_title.pack(anchor="w")

        self._text = ctk.CTkTextbox(
            self, height=140,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8, state="disabled",
        )
        self._text.pack(fill="both", expand=True, pady=(4, 0))

        self._btn_clear = ctk.CTkButton(
            self, text=T['btn_clear'], width=80, height=26,
            font=ctk.CTkFont(size=11),
            fg_color="gray70", hover_color="gray60",
            text_color="gray20", corner_radius=6,
            command=self.clear,
        )
        self._btn_clear.pack(anchor="e", pady=(4, 0))

    def append(self, message: str) -> None:
        """Ajoute une ligne a la console (thread-safe via after())."""
        self._text.configure(state="normal")
        self._text.insert("end", message + "\n")
        self._text.see("end")
        self._text.configure(state="disabled")

    def clear(self) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")

    def set_language(self, lang: str):
        self._lang = lang
        T = TRANSLATIONS[lang]
        self._lbl_title.configure(text=T['console_title'])
        self._btn_clear.configure(text=T['btn_clear'])
