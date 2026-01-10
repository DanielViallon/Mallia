================================================================================
                                MALLIA
                    Gestion de Salon de Coiffure
                              Version 1.0.0
================================================================================

DESCRIPTION
-----------
Mallia est une application de gestion pour salon de coiffure permettant de :
- Gérer les suivis des managers
- Gérer les suivis des collaborateurs
- Gérer les fins de mois
- Créer et gérer des plannings
- Générer des rapports PDF

TECHNOLOGIES
------------
- Langage : Python 3.9+
- Framework GUI : PySide6 (Qt for Python)
- Base de données : SQLite
- IDE recommandé : Visual Studio Code

STRUCTURE DU PROJET
-------------------
Mallia/
├── main.py                 # Point d'entrée de l'application
├── config.ini              # Configuration de l'application
├── requirements.txt        # Dépendances Python
├── readme.txt             # Ce fichier
│
├── assets/                # Ressources (images, icônes)
│   ├── images/
│   └── icons/
│
├── data/                  # Base de données SQLite
│   └── mallia.db
│
├── interface/             # Interface graphique
│   ├── main_window.py    # Fenêtre principale
│   ├── components/       # Composants UI réutilisables
│   │   ├── sidebar_menu.py
│   │   ├── title_bar.py
│   │   └── content_area.py
│   └── themes/           # Thèmes clair/sombre
│       ├── theme_manager.py
│       ├── light/
│       │   └── style.qss
│       └── dark/
│           └── style.qss
│
└── modules/              # Modules métier
    └── bdd/             # Gestion base de données
        ├── database.py
        └── models.py

INSTALLATION
------------
1. Créer un environnement virtuel :
   python -m venv venv

2. Activer l'environnement virtuel :
   - Windows : venv\Scripts\activate
   - macOS/Linux : source venv/bin/activate

3. Installer les dépendances :
   pip install -r requirements.txt

LANCEMENT
---------
python main.py

CONFIGURATION
-------------
Le fichier config.ini permet de personnaliser :
- Taille de la fenêtre (par défaut : 1000x700)
- Thème (clair/sombre)
- Largeur du menu (étendu/réduit)
- Durée des animations

FONCTIONNALITÉS
---------------
✓ Interface graphique moderne et épurée
✓ Menu vertical escamotable avec animations fluides
✓ Barre de titre personnalisée (style macOS)
✓ Thèmes clair et sombre
✓ Base de données SQLite
✓ Architecture modulaire

MODULES À DÉVELOPPER
--------------------
[ ] Suivis Manager
[ ] Suivis Collaborateurs
[ ] Fins de mois
[ ] Plannings
[ ] Génération de PDF

DÉVELOPPEMENT
-------------
Pour ajouter un nouveau module :
1. Créer un dossier dans modules/
2. Définir le schéma de base de données
3. Créer l'interface du module
4. Intégrer au menu principal

NOTES TECHNIQUES
----------------
- Résolution cible : 1920x1080
- Fenêtre sans bordure système (frameless)
- Animations : 300ms (easing cubic)
- Menu étendu : 250px / réduit : 70px
- Icônes : Emojis Unicode (à remplacer par Lucide si nécessaire)

AUTEUR
------
Développé pour la gestion de salon de coiffure Mallia

VERSION
-------
1.0.0 - Janvier 2026
- Version initiale avec interface de base
- Structure du projet et base de données
- Thèmes clair et sombre

================================================================================