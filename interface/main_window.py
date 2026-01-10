"""
Fenêtre principale de l'application Mallia
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import configparser
from pathlib import Path

from .components import SidebarMenu, TitleBar, ContentArea
from .themes import ThemeManager
from modules.suivis_manager import SuivisManagerWidget
from modules.parametres import ParametresWidget
from modules.collaborateurs import CollaborateursWidget
from modules.objectifs import ObjectifsWidget
from modules.suivis_collaborateurs import SuivisCollaborateursWidget


class MainWindow(QMainWindow):
    """Fenêtre principale sans barre de titre système"""
    
    def __init__(self):
        super().__init__()
        
        # Charger la configuration
        self.config = self._load_config()
        
        # Configuration de la fenêtre
        self._setup_window()
        
        # Gestionnaire de thèmes
        self.theme_manager = ThemeManager()
        
        # Créer l'interface
        self._create_ui()
        
        # Connecter les signaux
        self._connect_signals()
        
        # Appliquer le thème initial
        self._apply_initial_theme()
        
        # Vérifier si c'est le premier lancement
        self._verifier_configuration_initiale()
    
    def _load_config(self) -> configparser.ConfigParser:
        """Charge le fichier de configuration"""
        config = configparser.ConfigParser()
        config_path = Path("config.ini")
        
        if config_path.exists():
            config.read(config_path, encoding='utf-8')
        
        return config
    
    def _setup_window(self):
        """Configure les propriétés de la fenêtre"""
        # Titre et icône
        self.setWindowTitle(self.config.get('Application', 'name', fallback='Mallia'))
        
        try:
            icon_path = Path("assets/images/icone.ico")
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except:
            pass
        
        # Taille de la fenêtre avec gestion des valeurs vides
        try:
            width_str = self.config.get('Application', 'window_width', fallback='1000')
            width = int(width_str) if width_str.strip() else 1000
        except (ValueError, AttributeError):
            width = 1000
        
        try:
            height_str = self.config.get('Application', 'window_height', fallback='700')
            height = int(height_str) if height_str.strip() else 700
        except (ValueError, AttributeError):
            height = 700
        
        self.resize(width, height)
        
        # Centrer la fenêtre
        self._center_window()
        
        # Supprimer la barre de titre système
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
    
    def _center_window(self):
        """Centre la fenêtre sur l'écran"""
        screen = self.screen().geometry()
        window = self.frameGeometry()
        center = screen.center()
        window.moveCenter(center)
        self.move(window.topLeft())
    
    def _create_ui(self):
        """Crée l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal vertical
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barre de titre en haut
        self.title_bar = TitleBar()
        main_layout.addWidget(self.title_bar)
        
        # Layout horizontal pour sidebar + contenu
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Menu latéral
        self.sidebar = SidebarMenu()
        content_layout.addWidget(self.sidebar)
        
        # Zone de contenu
        self.content_area = ContentArea()
        content_layout.addWidget(self.content_area)
        
        # Ajouter le module Paramètres
        self.parametres_widget = ParametresWidget()
        self.parametres_widget.parametres_enregistres.connect(self._on_parametres_enregistres)
        self.content_area.add_module("Paramètres", self.parametres_widget)
        
        # Ajouter le module Gestion Collaborateurs
        self.collaborateurs_widget = CollaborateursWidget()
        self.content_area.add_module("Gestion Collaborateurs", self.collaborateurs_widget)
        
        # Ajouter le module Objectifs Annuels
        self.objectifs_widget = ObjectifsWidget()
        self.objectifs_widget.objectifs_modifies.connect(self._on_objectifs_modifies)
        self.content_area.add_module("Objectifs Annuels", self.objectifs_widget)
        
        # Ajouter le module Suivis Manager
        self.suivis_manager_widget = SuivisManagerWidget()
        self.content_area.add_module("Suivis Manager", self.suivis_manager_widget)
        
        # Ajouter le module Suivis Collaborateurs
        self.suivis_collaborateurs_widget = SuivisCollaborateursWidget()
        self.content_area.add_module("Suivis Collaborateurs", self.suivis_collaborateurs_widget)
        
        main_layout.addLayout(content_layout)
    
    def _connect_signals(self):
        """Connecte les signaux et slots"""
        # Barre de titre
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)
        self.title_bar.menu_toggle_clicked.connect(self.sidebar.toggle)
        self.title_bar.theme_toggle_clicked.connect(self.toggle_theme)
        
        # Menu latéral
        self.sidebar.menu_item_clicked.connect(self._on_menu_item_clicked)
        self.sidebar.quit_clicked.connect(self.close)
    
    def _apply_initial_theme(self):
        """Applique le thème initial depuis la configuration"""
        theme_name = self.config.get('Theme', 'current', fallback='light')
        self.theme_manager.apply_theme(self, theme_name)
        
        # Mettre à jour l'icône du bouton thème
        if theme_name == "dark":
            self.title_bar.theme_btn.setText("☀️")
        else:
            self.title_bar.theme_btn.setText("🌙")
    
    def _verifier_configuration_initiale(self):
        """Vérifie si c'est le premier lancement et affiche les paramètres si nécessaire"""
        if not self.parametres_widget.est_configure():
            # Premier lancement : afficher la page paramètres
            self.content_area.show_module("Paramètres")
            
            # Message d'information
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Bienvenue dans Mallia",
                "Bienvenue ! Veuillez configurer les paramètres de votre salon\n"
                "pour commencer à utiliser l'application."
            )
        elif not self.collaborateurs_widget.a_des_collaborateurs():
            # Paramètres configurés mais aucun collaborateur : afficher la gestion collaborateurs
            self.content_area.show_module("Gestion Collaborateurs")
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Ajouter des collaborateurs",
                "Veuillez ajouter au moins un collaborateur pour commencer."
            )
        else:
            # Configuration déjà faite : afficher la page d'accueil
            self.content_area.show_home()
    
    def _on_parametres_enregistres(self):
        """Appelé quand les paramètres sont enregistrés"""
        # Retourner à la page d'accueil après enregistrement
        self.content_area.show_home()
    
    def _on_objectifs_modifies(self):
        """Appelé quand les objectifs sont modifiés"""
        # Recharger les objectifs dans le widget Suivis Manager
        if hasattr(self, 'suivis_manager_widget'):
            self.suivis_manager_widget.recharger_objectifs()
    
    def _toggle_maximize(self):
        """Bascule entre fenêtre maximisée et normale"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def _on_menu_item_clicked(self, menu_name: str):
        """
        Gère le clic sur un élément du menu
        
        Args:
            menu_name: Nom du menu cliqué
        """
        print(f"Menu cliqué: {menu_name}")
        
        # Afficher le module correspondant
        if menu_name == "Suivis Manager":
            self.content_area.show_module("Suivis Manager")
        elif menu_name == "Suivis Collaborateurs":
            self.content_area.show_module("Suivis Collaborateurs")
        elif menu_name == "Paramètres":
            self.content_area.show_module("Paramètres")
        elif menu_name == "Gestion Collaborateurs":
            self.content_area.show_module("Gestion Collaborateurs")
        elif menu_name == "Objectifs Annuels":
            self.content_area.show_module("Objectifs Annuels")
        else:
            # Pour les autres modules non encore implémentés
            self.content_area.show_home()
    
    def toggle_theme(self):
        """Bascule entre thème clair et sombre"""
        self.theme_manager.toggle_theme(self)
        
        # Mettre à jour l'icône du bouton
        if self.theme_manager.get_current_theme() == "dark":
            self.title_bar.theme_btn.setText("☀️")
        else:
            self.title_bar.theme_btn.setText("🌙")
        
        # Sauvegarder dans la configuration
        self._save_theme_config()
    
    def _save_theme_config(self):
        """Sauvegarde le thème actuel dans la configuration"""
        # IMPORTANT : Recharger le fichier pour ne pas écraser les autres modifications
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        
        # Modifier uniquement le thème
        if not config.has_section('Theme'):
            config.add_section('Theme')
        config.set('Theme', 'current', self.theme_manager.get_current_theme())
        
        with open('config.ini', 'w', encoding='utf-8') as f:
            config.write(f)
    
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        # IMPORTANT : Recharger le fichier pour ne pas écraser les autres modifications
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        
        # Modifier uniquement l'état du menu
        if not config.has_section('Menu'):
            config.add_section('Menu')
        config.set('Menu', 'is_expanded', str(self.sidebar.is_expanded).lower())
        
        with open('config.ini', 'w', encoding='utf-8') as f:
            config.write(f)
        
        event.accept()