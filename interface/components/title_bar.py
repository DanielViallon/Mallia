"""
Barre de titre personnalisée avec boutons macOS style
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap


class TitleBar(QWidget):
    """Barre de titre personnalisée sans bordure système"""
    
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()
    menu_toggle_clicked = Signal()
    theme_toggle_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("title_bar")
        self.setFixedHeight(50)
        
        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)
        
        # Bouton toggle menu (hamburger)
        self.menu_toggle_btn = QPushButton("☰")
        self.menu_toggle_btn.setObjectName("menu_toggle_button")
        self.menu_toggle_btn.setFixedSize(32, 32)
        self.menu_toggle_btn.clicked.connect(self.menu_toggle_clicked.emit)
        self.menu_toggle_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.menu_toggle_btn)
        
        layout.addSpacing(10)
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setScaledContents(False)
        self.logo_label.setFixedSize(38, 38)
        
        # Tenter de charger le logo
        try:
            pixmap = QPixmap("assets/images/logo.png")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_label.setPixmap(scaled_pixmap)
        except:
            pass
        
        layout.addWidget(self.logo_label)
        
        # Nom de l'application
        self.app_name_label = QLabel("Mallia")
        self.app_name_label.setObjectName("app_title_label")
        layout.addWidget(self.app_name_label)
        
        # Espace central (pour le drag)
        self.title_label = QLabel("")
        layout.addWidget(self.title_label, 1)
        
        # Bouton changement de thème
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("theme_toggle_button")
        self.theme_btn.setFixedSize(32, 32)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setToolTip("Changer de thème")
        self.theme_btn.clicked.connect(self.theme_toggle_clicked.emit)
        layout.addWidget(self.theme_btn)
        
        layout.addSpacing(15)
        
        # Boutons macOS style (à droite)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Bouton réduire (jaune orangé)
        self.minimize_btn = QPushButton()
        self.minimize_btn.setObjectName("minimize_button")
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        self.minimize_btn.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(self.minimize_btn)
        
        # Bouton agrandir/réduire (vert)
        self.maximize_btn = QPushButton()
        self.maximize_btn.setObjectName("maximize_button")
        self.maximize_btn.clicked.connect(self.maximize_clicked.emit)
        self.maximize_btn.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(self.maximize_btn)
        
         # Bouton fermer (rouge)
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("close_button")
        self.close_btn.clicked.connect(self.close_clicked.emit)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Variables pour le drag de la fenêtre
        self.drag_position = None
    
    def mousePressEvent(self, event):
        """Permet de déplacer la fenêtre en cliquant sur la barre de titre"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Déplace la fenêtre lors du drag"""
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.window().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Réinitialise la position de drag"""
        self.drag_position = None