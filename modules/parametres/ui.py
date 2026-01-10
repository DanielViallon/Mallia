"""
Interface utilisateur pour le module Paramètres
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import configparser
from pathlib import Path


class ParametresWidget(QWidget):
    """Widget principal pour le module Paramètres"""
    
    parametres_enregistres = Signal()  # Signal émis quand les paramètres sont sauvegardés
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_path = Path("config.ini")
        self.config = configparser.ConfigParser()
        
        self._init_ui()
        self._charger_parametres()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        # Layout principal avec scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Widget de contenu
        content_widget = QWidget()
        content_widget.setObjectName("parametres_content")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Titre
        titre_label = QLabel("PARAMÈTRES DE L'APPLICATION")
        titre_font = QFont()
        titre_font.setPointSize(18)
        titre_font.setBold(True)
        titre_label.setFont(titre_font)
        layout.addWidget(titre_label)
        
        # Description
        desc_label = QLabel(
            "Configurez les paramètres de votre salon et les objectifs pour un suivi optimal."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Section 1 : Identification du salon
        self._creer_section_identification(layout)
        
        # Section 2 : Objectifs Suivis Manager
        self._creer_section_objectifs(layout)
        
        # Boutons d'action
        self._creer_boutons_action(layout)
        
        layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def _creer_section_identification(self, parent_layout):
        """Crée la section d'identification du salon"""
        group = QGroupBox("🏢 Identification du Salon")
        group.setObjectName("parametres_group")
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Nom du salon
        self.nom_salon_input = QLineEdit()
        self.nom_salon_input.setPlaceholderText("Ex: Salon Élégance")
        self.nom_salon_input.setMinimumHeight(35)
        form_layout.addRow("Nom du salon :", self.nom_salon_input)
        
        # Ville du salon
        self.ville_salon_input = QLineEdit()
        self.ville_salon_input.setPlaceholderText("Ex: Paris")
        self.ville_salon_input.setMinimumHeight(35)
        form_layout.addRow("Ville :", self.ville_salon_input)
        
        group.setLayout(form_layout)
        parent_layout.addWidget(group)
    
    def _creer_section_objectifs(self, parent_layout):
        """Crée la section des objectifs Suivis Manager"""
        group = QGroupBox("🎯 Objectifs Suivis Manager")
        group.setObjectName("parametres_group")
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # C.A. Total
        self.ca_total_input = QLineEdit()
        self.ca_total_input.setPlaceholderText("Ex: 50000")
        self.ca_total_input.setMinimumHeight(35)
        form_layout.addRow("C.A. Total mensuel (€) :", self.ca_total_input)
        
        # C.A. / Jour
        self.ca_jour_input = QLineEdit()
        self.ca_jour_input.setPlaceholderText("Ex: 2000")
        self.ca_jour_input.setMinimumHeight(35)
        form_layout.addRow("C.A. / Jour (€) :", self.ca_jour_input)
        
        # Nombre de Clients
        self.nb_clients_input = QLineEdit()
        self.nb_clients_input.setPlaceholderText("Ex: 500")
        self.nb_clients_input.setMinimumHeight(35)
        form_layout.addRow("Nombre de Clients :", self.nb_clients_input)
        
        # % Ventes
        self.pct_ventes_input = QLineEdit()
        self.pct_ventes_input.setPlaceholderText("Ex: 30")
        self.pct_ventes_input.setMinimumHeight(35)
        form_layout.addRow("Pourcentage de Ventes (%) :", self.pct_ventes_input)
        
        # % Couleurs
        self.pct_couleurs_input = QLineEdit()
        self.pct_couleurs_input.setPlaceholderText("Ex: 50")
        self.pct_couleurs_input.setMinimumHeight(35)
        form_layout.addRow("Pourcentage de Couleurs (%) :", self.pct_couleurs_input)
        
        # % Soins
        self.pct_soins_input = QLineEdit()
        self.pct_soins_input.setPlaceholderText("Ex: 20")
        self.pct_soins_input.setMinimumHeight(35)
        form_layout.addRow("Pourcentage de Soins (%) :", self.pct_soins_input)
        
        group.setLayout(form_layout)
        parent_layout.addWidget(group)
    
    def _creer_boutons_action(self, parent_layout):
        """Crée les boutons d'action"""
        buttons_layout = QHBoxLayout()
        
        # Bouton Sauvegarder
        self.btn_sauvegarder = QPushButton("💾 Enregistrer les paramètres")
        self.btn_sauvegarder.setMinimumHeight(40)
        self.btn_sauvegarder.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4C6A94;
            }
            QPushButton:pressed {
                background-color: #3D5577;
            }
        """)
        self.btn_sauvegarder.clicked.connect(self._sauvegarder_parametres)
        buttons_layout.addWidget(self.btn_sauvegarder)
        
        # Bouton Réinitialiser
        self.btn_reinitialiser = QPushButton("🔄 Réinitialiser")
        self.btn_reinitialiser.setMinimumHeight(40)
        self.btn_reinitialiser.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #A74D56;
            }
            QPushButton:pressed {
                background-color: #8F3A42;
            }
        """)
        self.btn_reinitialiser.clicked.connect(self._reinitialiser_formulaire)
        buttons_layout.addWidget(self.btn_reinitialiser)
        
        parent_layout.addLayout(buttons_layout)
    
    def _charger_parametres(self):
        """Charge les paramètres depuis le fichier config.ini"""
        if self.config_path.exists():
            self.config.read(self.config_path, encoding='utf-8')
            
            # Identification
            if self.config.has_section('Salon'):
                self.nom_salon_input.setText(self.config.get('Salon', 'nom', fallback=''))
                self.ville_salon_input.setText(self.config.get('Salon', 'ville', fallback=''))
            
            # Objectifs
            if self.config.has_section('Objectifs_Suivis_Manager'):
                self.ca_total_input.setText(self.config.get('Objectifs_Suivis_Manager', 'ca_total', fallback=''))
                self.ca_jour_input.setText(self.config.get('Objectifs_Suivis_Manager', 'ca_jour', fallback=''))
                self.nb_clients_input.setText(self.config.get('Objectifs_Suivis_Manager', 'nb_clients', fallback=''))
                self.pct_ventes_input.setText(self.config.get('Objectifs_Suivis_Manager', 'pct_ventes', fallback=''))
                self.pct_couleurs_input.setText(self.config.get('Objectifs_Suivis_Manager', 'pct_couleurs', fallback=''))
                self.pct_soins_input.setText(self.config.get('Objectifs_Suivis_Manager', 'pct_soins', fallback=''))
    
    def _sauvegarder_parametres(self):
        """Sauvegarde les paramètres dans le fichier config.ini"""
        
        # DEBUG : Afficher les valeurs récupérées
        print("=== DEBUG SAUVEGARDE ===")
        print(f"Nom salon: '{self.nom_salon_input.text()}'")
        print(f"Ville salon: '{self.ville_salon_input.text()}'")
        print(f"CA Total: '{self.ca_total_input.text()}'")
        print("========================")
        
        # Validation
        nom_salon = self.nom_salon_input.text().strip()
        ville_salon = self.ville_salon_input.text().strip()
        
        if not nom_salon:
            QMessageBox.warning(
                self, "Champ requis",
                "Le nom du salon est obligatoire."
            )
            return
        
        if not ville_salon:
            QMessageBox.warning(
                self, "Champ requis",
                "La ville du salon est obligatoire."
            )
            return
        
        try:
            # Créer un nouveau ConfigParser
            config = configparser.ConfigParser()
            
            # Charger le fichier existant s'il existe
            if self.config_path.exists():
                config.read(self.config_path, encoding='utf-8')
            
            # Section Application
            if not config.has_section('Application'):
                config.add_section('Application')
            
            # Conserver ou créer les valeurs de Application
            for key, default in [('name', 'Mallia'), ('version', '1.0.0'), 
                                 ('window_width', '1000'), ('window_height', '700')]:
                if not config.has_option('Application', key):
                    config.set('Application', key, default)
            
            config.set('Application', 'configured', 'true')
            
            # Section Theme
            if not config.has_section('Theme'):
                config.add_section('Theme')
            if not config.has_option('Theme', 'current'):
                config.set('Theme', 'current', 'light')
            
            # Section Menu
            if not config.has_section('Menu'):
                config.add_section('Menu')
            for key, default in [('is_expanded', 'true'), ('width_expanded', '250'),
                                 ('width_collapsed', '70'), ('animation_duration', '300')]:
                if not config.has_option('Menu', key):
                    config.set('Menu', key, default)
            
            # Section Database
            if not config.has_section('Database'):
                config.add_section('Database')
            if not config.has_option('Database', 'path'):
                config.set('Database', 'path', 'data/mallia.db')
            
            # Section Salon
            if not config.has_section('Salon'):
                config.add_section('Salon')
            
            config.set('Salon', 'nom', nom_salon)
            config.set('Salon', 'ville', ville_salon)
            
            # Section Objectifs
            if not config.has_section('Objectifs_Suivis_Manager'):
                config.add_section('Objectifs_Suivis_Manager')
            
            config.set('Objectifs_Suivis_Manager', 'ca_total', self.ca_total_input.text().strip())
            config.set('Objectifs_Suivis_Manager', 'ca_jour', self.ca_jour_input.text().strip())
            config.set('Objectifs_Suivis_Manager', 'nb_clients', self.nb_clients_input.text().strip())
            config.set('Objectifs_Suivis_Manager', 'pct_ventes', self.pct_ventes_input.text().strip())
            config.set('Objectifs_Suivis_Manager', 'pct_couleurs', self.pct_couleurs_input.text().strip())
            config.set('Objectifs_Suivis_Manager', 'pct_soins', self.pct_soins_input.text().strip())
            
            # Sauvegarder dans le fichier
            with open(self.config_path, 'w', encoding='utf-8') as f:
                config.write(f)
            
            print(f"Configuration sauvegardée dans {self.config_path.absolute()}")
            
            QMessageBox.information(
                self, "Paramètres enregistrés",
                "Les paramètres ont été enregistrés avec succès !"
            )
            
            # Émettre le signal
            self.parametres_enregistres.emit()
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Erreur de sauvegarde",
                f"Une erreur est survenue lors de la sauvegarde:\n{str(e)}"
            )
    
    def _reinitialiser_formulaire(self):
        """Réinitialise le formulaire"""
        reply = QMessageBox.question(
            self, "Réinitialiser",
            "Voulez-vous vraiment réinitialiser tous les champs ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.nom_salon_input.clear()
            self.ville_salon_input.clear()
            self.ca_total_input.clear()
            self.ca_jour_input.clear()
            self.nb_clients_input.clear()
            self.pct_ventes_input.clear()
            self.pct_couleurs_input.clear()
            self.pct_soins_input.clear()
    
    def est_configure(self) -> bool:
        """Vérifie si l'application est déjà configurée"""
        if self.config_path.exists():
            self.config.read(self.config_path, encoding='utf-8')
            
            # Vérifier que les informations du salon sont renseignées
            if self.config.has_section('Salon'):
                nom = self.config.get('Salon', 'nom', fallback='').strip()
                ville = self.config.get('Salon', 'ville', fallback='').strip()
                
                # Si le nom et la ville sont renseignés, considérer comme configuré
                if nom and ville:
                    return True
            
            return False
        return False