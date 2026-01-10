"""
Menu vertical escamotable avec animations
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPixmap


class SidebarMenu(QWidget):
    """Menu latéral avec animation slide in/out"""
    
    menu_item_clicked = Signal(str)  # Émet le nom du bouton cliqué
    quit_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        
        # Configuration
        self.expanded_width = 250
        self.collapsed_width = 70
        self.is_expanded = True
        self.animation_duration = 300
        
        # Définir la largeur initiale
        self.setFixedWidth(self.expanded_width)
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Ajouter un espacement en haut
        self.layout.addSpacing(20)
        
        # Conteneur pour les boutons du menu
        self.menu_buttons = []
        self._create_menu_buttons()
        
        # Spacer pour pousser les boutons en bas
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer)
        
        # Bouton Paramètres (avant Quitter)
        self._create_parametres_button()
        
        # Bouton quitter
        self._create_quit_button()
        
        # Animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(self.animation_duration)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        
        self.animation2 = QPropertyAnimation(self, b"maximumWidth")
        self.animation2.setDuration(self.animation_duration)
        self.animation2.setEasingCurve(QEasingCurve.InOutCubic)
    
    def _create_menu_buttons(self):
        """Crée les boutons du menu"""
        menu_items = [
            ("Gestion Collaborateurs", "👥"),
            ("Objectifs Annuels", "🎯"),
            ("Suivis Manager", "👔"),
            ("Suivis Collaborateurs", "📊"),
            ("Fins de mois", "💰"),
            ("Plannings", "📅")
        ]
        
        for text, icon in menu_items:
            # Conteneur pour chaque bouton
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(10, 0, 10, 0)
            
            btn = QPushButton(f"{icon}  {text}")
            btn.setObjectName("menu_button")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked, t=text: self._on_menu_click(t))
            
            # Stocker l'icône et le texte séparément pour la gestion du collapse
            btn.setProperty("menu_icon", icon)
            btn.setProperty("menu_text", text)
            
            btn_layout.addWidget(btn)
            
            self.layout.addWidget(btn_container)
            self.menu_buttons.append(btn)
            self.layout.addSpacing(5)
            
    def _create_parametres_button(self):
        """Crée le bouton paramètres"""
        self.parametres_btn = QPushButton("⚙️  Paramètres")
        self.parametres_btn.setObjectName("parametres_button")
        self.parametres_btn.setCursor(Qt.PointingHandCursor)
        self.parametres_btn.setFixedHeight(50)
        self.parametres_btn.clicked.connect(lambda: self.menu_item_clicked.emit("Paramètres"))
        
        self.layout.addWidget(self.parametres_btn)
        self.layout.addSpacing(5)
    
    def _create_quit_button(self):
        """Crée le bouton quitter en bas du menu"""
        self.quit_btn = QPushButton("❌  Quitter")
        self.quit_btn.setObjectName("quit_button")
        self.quit_btn.setCursor(Qt.PointingHandCursor)
        self.quit_btn.setFixedHeight(50)
        self.quit_btn.setStyleSheet("font-weight: 700;")
        self.quit_btn.clicked.connect(self.quit_clicked.emit)
        
        self.layout.addWidget(self.quit_btn)
        self.layout.addSpacing(10)
    
    def _on_menu_click(self, menu_name: str):
        """Gère le clic sur un bouton du menu"""
        # Réinitialiser tous les boutons
        for btn in self.menu_buttons:
            btn.setObjectName("menu_button")
            btn.setStyle(btn.style())
        
        # Activer le bouton cliqué
        sender = self.sender()
        if sender:
            sender.setObjectName("menu_button_active")
            sender.setStyle(sender.style())
        
        # Émettre le signal
        self.menu_item_clicked.emit(menu_name)
    
    def toggle(self):
        """Bascule entre état étendu et réduit"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
    
    def expand(self):
        """Étend le menu"""
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.expanded_width)
        
        self.animation2.setStartValue(self.width())
        self.animation2.setEndValue(self.expanded_width)
        
        self.animation.start()
        self.animation2.start()
        
        self.is_expanded = True
        
        # Restaurer le texte complet des boutons
        for btn in self.menu_buttons:
            icon = btn.property("menu_icon")
            text = btn.property("menu_text")
            if icon and text:
                btn.setText(f"{icon}  {text}")
        
        # Restaurer le texte des boutons système
        self.parametres_btn.setText("⚙️  Paramètres")
        self.quit_btn.setText("❌  Quitter")
    
    def collapse(self):
        """Réduit le menu"""
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.collapsed_width)
        
        self.animation2.setStartValue(self.width())
        self.animation2.setEndValue(self.collapsed_width)
        
        self.animation.start()
        self.animation2.start()
        
        self.is_expanded = False
        
        # Afficher uniquement les icônes
        for btn in self.menu_buttons:
            icon = btn.property("menu_icon")
            if icon:
                btn.setText(icon)
        
        # Réduire le texte des boutons système
        self.parametres_btn.setText("⚙️")
        self.quit_btn.setText("❌")