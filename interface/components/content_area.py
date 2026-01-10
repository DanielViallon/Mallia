"""
Zone de contenu principale où s'affichent les modules
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap


class ContentArea(QWidget):
    """Zone de contenu avec gestion des différents modules"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("content_area")
        
        # Dictionnaire pour stocker les modules (DOIT ÊTRE AVANT _create_home_page)
        self.modules = {}
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # StackedWidget pour gérer les différentes pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Créer la page d'accueil par défaut
        self._create_home_page()
    
    def _create_home_page(self):
        """Crée la page d'accueil avec un message de bienvenue"""
        home_page = QWidget()
        home_page.setObjectName("home_page")
        
        home_layout = QVBoxLayout(home_page)
        home_layout.setAlignment(Qt.AlignCenter)
        
        # Message de bienvenue
        welcome_label = QLabel("Bienvenue dans Mallia")
        welcome_label.setObjectName("watermark_logo")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 48px; font-weight: 300; opacity: 0.3;")
        
        home_layout.addWidget(welcome_label)
        
        # Ajouter la page d'accueil au StackedWidget
        self.stacked_widget.addWidget(home_page)
        self.modules["home"] = 0
    
    def show_home(self):
        """Affiche la page d'accueil"""
        self.stacked_widget.setCurrentIndex(self.modules["home"])
    
    def add_module(self, name: str, widget: QWidget):
        """
        Ajoute un module à la zone de contenu
        
        Args:
            name: Nom du module
            widget: Widget du module à afficher
        """
        index = self.stacked_widget.addWidget(widget)
        self.modules[name] = index
    
    def show_module(self, name: str):
        """
        Affiche un module spécifique
        
        Args:
            name: Nom du module à afficher
        """
        if name in self.modules:
            # Petit délai pour éviter les problèmes d'affichage au démarrage
            QTimer.singleShot(100, lambda: self.stacked_widget.setCurrentIndex(self.modules[name]))
        else:
            print(f"Module '{name}' non trouvé")
    
    def get_current_module(self) -> str:
        """Retourne le nom du module actuellement affiché"""
        current_index = self.stacked_widget.currentIndex()
        for name, index in self.modules.items():
            if index == current_index:
                return name
        return "home"