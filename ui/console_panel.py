# ui/console_panel.py — Panneau console (log série)

import customtkinter as ctk
from config import COLORS


class ConsolePanel(ctk.CTkFrame):
    """Zone de log scrollable affichant les messages TX/RX et info."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(self, text="Console",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS['ACC']).pack(anchor="w")

        self._text = ctk.CTkTextbox(
            self, height=140,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8,
            state="disabled",
        )
        self._text.pack(fill="both", expand=True, pady=(4, 0))

        ctk.CTkButton(self, text="Effacer", width=80, height=26,
                      font=ctk.CTkFont(size=11),
                      fg_color="gray70", hover_color="gray60",
                      text_color="gray20", corner_radius=6,
                      command=self.clear).pack(anchor="e", pady=(4, 0))

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
