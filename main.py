"""
Point d'entrée de l'application Mallia
Salon de coiffure - Gestion et planification
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Ajouter le dossier du projet au path
sys.path.insert(0, str(Path(__file__).parent))

from interface.main_window import MainWindow
from modules.bdd import Database


def initialize_application():
    """Initialise l'application et la base de données"""
    print("=" * 50)
    print("Démarrage de Mallia")
    print("=" * 50)
    
    # Initialiser la base de données
    try:
        with Database() as db:
            db.initialize_database()
            print("Base de données initialisée avec succès")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        return False
    
    # Initialiser le module Suivis Manager
    try:
        from modules.suivis_manager import SuivisManagerDB
        suivis_db = SuivisManagerDB()
        print("Module Suivis Manager initialisé avec succès")
    except Exception as e:
        print(f"Erreur lors de l'initialisation du module Suivis Manager: {e}")
        return False
    
    # Initialiser le module Collaborateurs
    try:
        from modules.collaborateurs import CollaborateursDB
        collaborateurs_db = CollaborateursDB()
        print("Module Collaborateurs initialisé avec succès")
    except Exception as e:
        print(f"Erreur lors de l'initialisation du module Collaborateurs: {e}")
        return False
    
    # Initialiser le module Objectifs
    try:
        from modules.objectifs import ObjectifsDB
        objectifs_db = ObjectifsDB()
        print("Module Objectifs initialisé avec succès")
    except Exception as e:
        print(f"Erreur lors de l'initialisation du module Objectifs: {e}")
        return False
    
    return True


def main():
    """Fonction principale"""
    
    # Créer l'application Qt
    app = QApplication(sys.argv)
    
    # Configurer l'application
    app.setApplicationName("Mallia")
    app.setOrganizationName("Mallia")
    app.setApplicationVersion("1.0.0")
    
    # Initialiser l'application
    if not initialize_application():
        print("Erreur lors de l'initialisation de l'application")
        return 1
    
    # Créer et afficher la fenêtre principale
    window = MainWindow()
    window.show()
    
    print("\nApplication prête !")
    print("=" * 50)
    
    # Lancer la boucle d'événements
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())