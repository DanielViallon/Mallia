"""
Gestionnaire de thèmes pour l'application Mallia
"""

import os
from pathlib import Path
from PySide6.QtWidgets import QApplication


class ThemeManager:
    """Gère le chargement et l'application des thèmes"""
    
    def __init__(self):
        self.themes_dir = Path(__file__).parent
        self.current_theme = "light"
        
    def load_theme(self, theme_name: str) -> str:
        """
        Charge un thème depuis son fichier QSS
        
        Args:
            theme_name: Nom du thème ('light' ou 'dark')
            
        Returns:
            Contenu du fichier QSS
        """
        theme_path = self.themes_dir / theme_name / "style.qss"
        
        if not theme_path.exists():
            print(f"Thème '{theme_name}' introuvable à {theme_path}")
            return ""
        
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Erreur lors du chargement du thème: {e}")
            return ""
    
    def apply_theme(self, app: QApplication, theme_name: str):
        """
        Applique un thème à l'application
        
        Args:
            app: Instance de QApplication
            theme_name: Nom du thème à appliquer
        """
        stylesheet = self.load_theme(theme_name)
        if stylesheet:
            app.setStyleSheet(stylesheet)
            self.current_theme = theme_name
            print(f"Thème '{theme_name}' appliqué avec succès")
        else:
            print(f"Impossible d'appliquer le thème '{theme_name}'")
    
    def toggle_theme(self, app: QApplication):
        """
        Bascule entre le thème clair et sombre
        
        Args:
            app: Instance de QApplication
        """
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(app, new_theme)
        
    def get_current_theme(self) -> str:
        """Retourne le nom du thème actuel"""
        return self.current_theme