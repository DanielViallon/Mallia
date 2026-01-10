"""
Interface utilisateur pour le module Gestion Collaborateurs
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox,
    QDateEdit
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont
from datetime import datetime

from .database import CollaborateursDB


class AjouterCollaborateurDialog(QDialog):
    """Dialog pour ajouter ou modifier un collaborateur"""
    
    def __init__(self, parent=None, collaborateur_data=None):
        super().__init__(parent)
        self.collaborateur_data = collaborateur_data
        self.setWindowTitle("Modifier le collaborateur" if collaborateur_data else "Ajouter un collaborateur")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self._init_ui()
        
        if collaborateur_data:
            self._charger_donnees()
    
    def _init_ui(self):
        """Initialise l'interface du dialog"""
        layout = QVBoxLayout(self)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Nom
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Ex: Dupont")
        form_layout.addRow("Nom :", self.nom_input)
        
        # Prénom
        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Ex: Marie")
        form_layout.addRow("Prénom :", self.prenom_input)
        
        # Date d'entrée
        self.date_entree_input = QDateEdit()
        self.date_entree_input.setCalendarPopup(True)
        self.date_entree_input.setDisplayFormat("dd/MM/yyyy")
        self.date_entree_input.setDate(QDate.currentDate())
        form_layout.addRow("Date d'entrée :", self.date_entree_input)
        
        # État
        self.etat_combo = QComboBox()
        self.etat_combo.addItems(["Actif", "Inactif"])
        form_layout.addRow("État :", self.etat_combo)
        
        layout.addLayout(form_layout)
        
        # Boutons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _charger_donnees(self):
        """Charge les données du collaborateur à modifier"""
        self.nom_input.setText(self.collaborateur_data['nom'])
        self.prenom_input.setText(self.collaborateur_data['prenom'])
        self.etat_combo.setCurrentText(self.collaborateur_data['etat'])
        
        # Date d'entrée
        if self.collaborateur_data.get('date_entree'):
            try:
                date_entree = datetime.strptime(self.collaborateur_data['date_entree'], '%Y-%m-%d')
                self.date_entree_input.setDate(QDate(date_entree.year, date_entree.month, date_entree.day))
            except:
                pass
    
    def get_data(self):
        """Récupère les données du formulaire"""
        # Formater la date au format YYYY-MM-DD
        date_entree = self.date_entree_input.date()
        date_entree_str = f"{date_entree.year()}-{date_entree.month():02d}-{date_entree.day():02d}"
        
        return {
            'nom': self.nom_input.text().strip(),
            'prenom': self.prenom_input.text().strip(),
            'etat': self.etat_combo.currentText(),
            'date_entree': date_entree_str
        }
    
    def accept(self):
        """Valide le formulaire"""
        data = self.get_data()
        
        if not data['nom']:
            QMessageBox.warning(self, "Champ requis", "Le nom est obligatoire.")
            return
        
        if not data['prenom']:
            QMessageBox.warning(self, "Champ requis", "Le prénom est obligatoire.")
            return
        
        super().accept()


class CollaborateursWidget(QWidget):
    """Widget principal pour le module Gestion Collaborateurs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = CollaborateursDB()
        
        self._init_ui()
        self._charger_donnees()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        # Titre
        titre_label = QLabel("GESTION DES COLLABORATEURS")
        titre_font = QFont()
        titre_font.setPointSize(18)
        titre_font.setBold(True)
        titre_label.setFont(titre_font)
        header_layout.addWidget(titre_label)
        
        header_layout.addStretch()
        
        # Statistiques
        self.stats_label = QLabel()
        header_layout.addWidget(self.stats_label)
        
        layout.addLayout(header_layout)
        
        # Barre de boutons
        buttons_layout = QHBoxLayout()
        
        self.btn_ajouter = QPushButton("➕ Ajouter un collaborateur")
        self.btn_ajouter.clicked.connect(self._ajouter_collaborateur)
        buttons_layout.addWidget(self.btn_ajouter)
        
        self.btn_modifier = QPushButton("✏️ Modifier")
        self.btn_modifier.clicked.connect(self._modifier_collaborateur)
        self.btn_modifier.setEnabled(False)
        buttons_layout.addWidget(self.btn_modifier)
        
        self.btn_monter = QPushButton("⬆️ Monter")
        self.btn_monter.clicked.connect(self._monter_collaborateur)
        self.btn_monter.setEnabled(False)
        buttons_layout.addWidget(self.btn_monter)
        
        self.btn_descendre = QPushButton("⬇️ Descendre")
        self.btn_descendre.clicked.connect(self._descendre_collaborateur)
        self.btn_descendre.setEnabled(False)
        buttons_layout.addWidget(self.btn_descendre)
        
        self.btn_supprimer = QPushButton("🗑️ Supprimer")
        self.btn_supprimer.clicked.connect(self._supprimer_collaborateur)
        self.btn_supprimer.setEnabled(False)
        buttons_layout.addWidget(self.btn_supprimer)
        
        buttons_layout.addStretch()
        
        # Filtre
        buttons_layout.addWidget(QLabel("Afficher :"))
        self.filtre_combo = QComboBox()
        self.filtre_combo.addItems(["Tous", "Actifs uniquement", "Inactifs uniquement"])
        self.filtre_combo.currentIndexChanged.connect(self._charger_donnees)
        buttons_layout.addWidget(self.filtre_combo)
        
        layout.addLayout(buttons_layout)
        
        # Tableau
        self._creer_tableau()
        layout.addWidget(self.table)
    
    def _creer_tableau(self):
        """Crée le tableau des collaborateurs"""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prénom", "Date d'entrée", "État", "Date d'inactivation"])
        
        # Masquer les numéros de lignes
        self.table.verticalHeader().setVisible(False)
        
        # Configurer l'en-tête
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        # Hauteur des lignes
        self.table.verticalHeader().setDefaultSectionSize(50)
        
        # Style
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E5E9F0;
                border: 1px solid #E5E9F0;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #5E81AC;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Connecter les signaux
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.itemDoubleClicked.connect(self._modifier_collaborateur)
    
    def _formater_date(self, date_str):
        """Formate une date au format français DD/MM/YYYY HH:MM"""
        if not date_str:
            return "-"
        
        try:
            # SQLite stocke les dates au format 'YYYY-MM-DD HH:MM:SS'
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return date_obj.strftime('%d/%m/%Y %H:%M')
        except ValueError:
            # Si le format est différent, essayer d'autres formats
            try:
                date_obj = datetime.strptime(date_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                return date_obj.strftime('%d/%m/%Y %H:%M')
            except:
                return date_str
    
    def _formater_date_simple(self, date_str):
        """Formate une date simple au format français DD/MM/YYYY"""
        if not date_str:
            return "-"
        
        try:
            # Format YYYY-MM-DD
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except:
            return date_str
    
    def _charger_donnees(self):
        """Charge les collaborateurs depuis la base de données"""
        # Récupérer le filtre
        filtre = self.filtre_combo.currentText()
        
        if filtre == "Actifs uniquement":
            collaborateurs = self.db.get_collaborateurs_actifs()
        elif filtre == "Inactifs uniquement":
            tous = self.db.get_tous_collaborateurs()
            collaborateurs = [c for c in tous if c['etat'] == 'Inactif']
        else:
            collaborateurs = self.db.get_tous_collaborateurs()
        
        # Remplir le tableau
        self.table.setRowCount(len(collaborateurs))
        
        for i, collab in enumerate(collaborateurs):
            # ID (caché mais stocké)
            id_item = QTableWidgetItem(str(collab['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, id_item)
            
            # Nom
            nom_item = QTableWidgetItem(collab['nom'])
            nom_item.setFlags(nom_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 1, nom_item)
            
            # Prénom
            prenom_item = QTableWidgetItem(collab['prenom'])
            prenom_item.setFlags(prenom_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 2, prenom_item)
            
            # Date d'entrée
            date_entree = collab.get('date_entree', None)
            date_entree_formatted = self._formater_date_simple(date_entree)
            date_entree_item = QTableWidgetItem(date_entree_formatted)
            date_entree_item.setTextAlignment(Qt.AlignCenter)
            date_entree_item.setFlags(date_entree_item.flags() & ~Qt.ItemIsEditable)
            if date_entree_formatted == "-":
                date_entree_item.setForeground(Qt.gray)
            self.table.setItem(i, 3, date_entree_item)
            
            # État
            etat_item = QTableWidgetItem(collab['etat'])
            etat_item.setTextAlignment(Qt.AlignCenter)
            etat_item.setFlags(etat_item.flags() & ~Qt.ItemIsEditable)
            
            # Colorer selon l'état
            if collab['etat'] == 'Actif':
                etat_item.setForeground(Qt.darkGreen)
            else:
                etat_item.setForeground(Qt.red)
            
            self.table.setItem(i, 4, etat_item)
            
            # Date d'inactivation
            date_inactivation = collab.get('date_inactivation', None)
            date_formatted = self._formater_date(date_inactivation)
            date_item = QTableWidgetItem(date_formatted)
            date_item.setTextAlignment(Qt.AlignCenter)
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            
            # Griser la date si vide
            if date_formatted == "-":
                date_item.setForeground(Qt.gray)
            
            self.table.setItem(i, 5, date_item)
        
        # Mettre à jour les statistiques
        self._update_stats()
    
    def _update_stats(self):
        """Met à jour les statistiques affichées"""
        total = self.db.compter_collaborateurs()
        actifs = self.db.compter_collaborateurs_actifs()
        self.stats_label.setText(f"Total: {total} | Actifs: {actifs}")
    
    def _on_selection_changed(self):
        """Appelé quand la sélection change"""
        has_selection = len(self.table.selectedItems()) > 0
        self.btn_modifier.setEnabled(has_selection)
        self.btn_supprimer.setEnabled(has_selection)
        self.btn_monter.setEnabled(has_selection)
        self.btn_descendre.setEnabled(has_selection)
    
    def _ajouter_collaborateur(self):
        """Ajoute un nouveau collaborateur"""
        dialog = AjouterCollaborateurDialog(self)
        
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            collaborateur_id = self.db.ajouter_collaborateur(
                data['nom'],
                data['prenom'],
                data['etat'],
                data['date_entree']
            )
            
            if collaborateur_id:
                QMessageBox.information(
                    self, "Collaborateur ajouté",
                    f"{data['prenom']} {data['nom']} a été ajouté avec succès."
                )
                self._charger_donnees()
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Une erreur est survenue lors de l'ajout du collaborateur."
                )
    
    def _modifier_collaborateur(self):
        """Modifie le collaborateur sélectionné"""
        if not self.table.selectedItems():
            return
        
        row = self.table.currentRow()
        collaborateur_id = int(self.table.item(row, 0).text())
        
        # Récupérer les données du collaborateur
        collaborateur_data = self.db.get_collaborateur(collaborateur_id)
        
        if not collaborateur_data:
            QMessageBox.warning(self, "Erreur", "Collaborateur introuvable.")
            return
        
        dialog = AjouterCollaborateurDialog(self, collaborateur_data)
        
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            if self.db.modifier_collaborateur(
                collaborateur_id,
                data['nom'],
                data['prenom'],
                data['etat'],
                data['date_entree']
            ):
                QMessageBox.information(
                    self, "Collaborateur modifié",
                    f"{data['prenom']} {data['nom']} a été modifié avec succès."
                )
                self._charger_donnees()
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Une erreur est survenue lors de la modification."
                )
    
    def _monter_collaborateur(self):
        """Monte le collaborateur sélectionné dans la liste"""
        if not self.table.selectedItems():
            return
        
        row = self.table.currentRow()
        if row == 0:
            QMessageBox.information(
                self, "Déplacement impossible",
                "Le collaborateur est déjà en première position."
            )
            return
        
        collaborateur_id = int(self.table.item(row, 0).text())
        
        if self.db.deplacer_collaborateur_haut(collaborateur_id):
            self._charger_donnees()
            # Sélectionner la nouvelle position
            self.table.selectRow(row - 1)
    
    def _descendre_collaborateur(self):
        """Descend le collaborateur sélectionné dans la liste"""
        if not self.table.selectedItems():
            return
        
        row = self.table.currentRow()
        if row == self.table.rowCount() - 1:
            QMessageBox.information(
                self, "Déplacement impossible",
                "Le collaborateur est déjà en dernière position."
            )
            return
        
        collaborateur_id = int(self.table.item(row, 0).text())
        
        if self.db.deplacer_collaborateur_bas(collaborateur_id):
            self._charger_donnees()
            # Sélectionner la nouvelle position
            self.table.selectRow(row + 1)
    
    def _supprimer_collaborateur(self):
        """Supprime le collaborateur sélectionné"""
        if not self.table.selectedItems():
            return
        
        row = self.table.currentRow()
        collaborateur_id = int(self.table.item(row, 0).text())
        nom = self.table.item(row, 1).text()
        prenom = self.table.item(row, 2).text()
        
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Voulez-vous vraiment supprimer {prenom} {nom} ?\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.supprimer_collaborateur(collaborateur_id):
                QMessageBox.information(
                    self, "Collaborateur supprimé",
                    f"{prenom} {nom} a été supprimé."
                )
                self._charger_donnees()
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Une erreur est survenue lors de la suppression."
                )
    
    def a_des_collaborateurs(self) -> bool:
        """Vérifie s'il y a au moins un collaborateur"""
        return self.db.compter_collaborateurs() > 0
    