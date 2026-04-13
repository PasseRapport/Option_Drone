# main.py — Point d'entrée de l'interface graphique ENSEA Drone Controller
from ui.app import DroneController

if __name__ == "__main__":
    app = DroneController()
    app.mainloop()
