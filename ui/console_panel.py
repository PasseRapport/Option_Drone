# ui/console_panel.py — Panneau console (log série)

import tkinter as tk
from tkinter import scrolledtext
from config import PALETTE


class ConsolePanel(tk.Frame):
    """Zone de log scrollable affichant les messages TX/RX et info."""

    def __init__(self, parent):
        P = PALETTE
        super().__init__(parent, bg=P['BG'])

        tk.Label(self, text="Console", font=("Segoe UI", 9, "bold"),
                 bg=P['BG'], fg=P['ACC']).pack(anchor="w")

        self._text = scrolledtext.ScrolledText(
            self, height=7,
            bg=P['CONSOLE_BG'], fg=P['TEXT'],
            font=("Consolas", 8), relief="flat",
            state="disabled", insertbackground=P['TEXT'],
        )
        self._text.pack(fill="both")

        tk.Button(self, text="Effacer", bg=P['PANEL'], fg=P['SUB'],
                  font=("Segoe UI", 8), relief="flat", padx=6,
                  command=self.clear).pack(anchor="e", pady=2)

    def append(self, message: str) -> None:
        """Ajoute une ligne à la console (thread-safe via after())."""
        self._text.configure(state="normal")
        self._text.insert("end", message + "\n")
        self._text.see("end")
        self._text.configure(state="disabled")

    def clear(self) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")
