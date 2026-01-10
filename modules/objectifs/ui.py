"""
Interface utilisateur pour le module Objectifs
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from datetime import datetime

from .database import ObjectifsDB


class ObjectifsWidget(QWidget):
    """Widget principal pour le module Objectifs"""
    
    objectifs_modifies = Signal()  # Signal émis quand les objectifs sont modifiés
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = ObjectifsDB()
        
        self._init_ui()
        self._charger_annee_courante()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        # Titre
        titre_label = QLabel("OBJECTIFS ANNUELS")
        titre_font = QFont()
        titre_font.setPointSize(18)
        titre_font.setBold(True)
        titre_label.setFont(titre_font)
        header_layout.addWidget(titre_label)
        
        header_layout.addStretch()
        
        # Sélecteur d'année
        header_layout.addWidget(QLabel("Année :"))
        self.annee_combo = QComboBox()
        annee_actuelle = datetime.now().year
        for annee in range(annee_actuelle - 2, annee_actuelle + 3):
            self.annee_combo.addItem(str(annee))
        self.annee_combo.setCurrentText(str(annee_actuelle))
        self.annee_combo.currentIndexChanged.connect(self._charger_donnees)
        header_layout.addWidget(self.annee_combo)
        
        layout.addLayout(header_layout)
        
        # Barre de boutons
        buttons_layout = QHBoxLayout()
        
        self.btn_sauvegarder = QPushButton("💾 Sauvegarder")
        self.btn_sauvegarder.clicked.connect(self._sauvegarder_objectifs)
        buttons_layout.addWidget(self.btn_sauvegarder)
        
        self.btn_copier_annee = QPushButton("📋 Copier vers année suivante")
        self.btn_copier_annee.clicked.connect(self._copier_vers_annee_suivante)
        buttons_layout.addWidget(self.btn_copier_annee)
        
        self.btn_reinitialiser = QPushButton("🔄 Réinitialiser l'année")
        self.btn_reinitialiser.clicked.connect(self._reinitialiser_annee)
        self.btn_reinitialiser.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: white;
            }
            QPushButton:hover {
                background-color: #D08770;
            }
        """)
        buttons_layout.addWidget(self.btn_reinitialiser)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Tableau
        self._creer_tableau()
        layout.addWidget(self.table)
    
    def _creer_tableau(self):
        """Crée le tableau des objectifs"""
        self.table = QTableWidget()
        self.table.setRowCount(12)  # 12 mois
        self.table.setColumnCount(7)
        
        self.table.setHorizontalHeaderLabels([
            "Mois", "C.A. Total", "C.A. /Jour", "Nombre de Clients",
            "% Ventes", "% Couleurs", "% Soins"
        ])
        
        # Labels des mois en première colonne
        mois_noms = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        
        for i, nom in enumerate(mois_noms):
            item = QTableWidgetItem(nom)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setBackground(Qt.lightGray)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            self.table.setItem(i, 0, item)
        
        # Masquer les numéros de lignes
        self.table.verticalHeader().setVisible(False)
        
        # Configurer l'en-tête
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # Hauteur des lignes
        self.table.verticalHeader().setDefaultSectionSize(45)
        
        # Style
        self.table.setAlternatingRowColors(True)
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
    
    def _charger_annee_courante(self):
        """Charge les données de l'année courante"""
        now = datetime.now()
        self.annee_combo.setCurrentText(str(now.year))
        self._charger_donnees()
    
    def _charger_donnees(self):
        """Charge les objectifs de l'année sélectionnée"""
        annee = int(self.annee_combo.currentText())
        
        # Récupérer les objectifs de l'année
        objectifs_annee = self.db.get_objectifs_annee(annee)
        
        # Créer un dictionnaire par mois
        objectifs_dict = {obj['mois']: obj for obj in objectifs_annee}
        
        # Bloquer les signaux pendant le remplissage
        self.table.blockSignals(True)
        
        # Remplir le tableau
        for mois in range(1, 13):
            objectifs = objectifs_dict.get(mois, {})
            
            # C.A. Total
            ca_total = objectifs.get('ca_total', '')
            self.table.setItem(mois - 1, 1, QTableWidgetItem(
                str(int(ca_total)) if ca_total else ""
            ))
            
            # C.A. /Jour
            ca_jour = objectifs.get('ca_jour', '')
            self.table.setItem(mois - 1, 2, QTableWidgetItem(
                str(int(ca_jour)) if ca_jour else ""
            ))
            
            # Nombre de Clients
            nb_clients = objectifs.get('nb_clients', '')
            self.table.setItem(mois - 1, 3, QTableWidgetItem(
                str(int(nb_clients)) if nb_clients else ""
            ))
            
            # % Ventes
            pct_ventes = objectifs.get('pct_ventes', '')
            self.table.setItem(mois - 1, 4, QTableWidgetItem(
                str(float(pct_ventes)) if pct_ventes else ""
            ))
            
            # % Couleurs
            pct_couleurs = objectifs.get('pct_couleurs', '')
            self.table.setItem(mois - 1, 5, QTableWidgetItem(
                str(float(pct_couleurs)) if pct_couleurs else ""
            ))
            
            # % Soins
            pct_soins = objectifs.get('pct_soins', '')
            self.table.setItem(mois - 1, 6, QTableWidgetItem(
                str(float(pct_soins)) if pct_soins else ""
            ))
        
        # Centrer toutes les cellules éditables
        for row in range(12):
            for col in range(1, 7):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
        
        # Débloquer les signaux
        self.table.blockSignals(False)
    
    def _reinitialiser_annee(self):
        """Réinitialise tous les objectifs de l'année en cours (supprime toutes les données)"""
        annee = int(self.annee_combo.currentText())
        
        # Vérifier s'il y a des données à supprimer
        objectifs = self.db.get_objectifs_annee(annee)
        
        if not objectifs:
            QMessageBox.information(
                self, "Aucune donnée",
                f"Il n'y a aucun objectif à réinitialiser pour l'année {annee}."
            )
            return
        
        # Demander confirmation avec avertissement
        reply = QMessageBox.warning(
            self, "⚠️ Confirmation de réinitialisation",
            f"<b>Attention !</b><br><br>"
            f"Vous êtes sur le point de <b>supprimer définitivement</b> tous les objectifs "
            f"de l'année <b>{annee}</b> (12 mois).<br><br>"
            f"Cette action est <b>irréversible</b>.<br><br>"
            f"Voulez-vous vraiment continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Bouton par défaut
        )
        
        if reply == QMessageBox.Yes:
            # Supprimer tous les objectifs de l'année
            if self.db.supprimer_objectifs_annee(annee):
                # Vider le tableau
                self._charger_donnees()
                
                QMessageBox.information(
                    self, "Réinitialisation réussie",
                    f"Tous les objectifs de l'année {annee} ont été supprimés.\n"
                    f"Le tableau a été réinitialisé."
                )
                
                # Émettre le signal pour notifier les autres modules
                self.objectifs_modifies.emit()
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Une erreur est survenue lors de la réinitialisation."
                )
    
    def _sauvegarder_objectifs(self):
        """Sauvegarde tous les objectifs du tableau"""
        annee = int(self.annee_combo.currentText())
        
        for mois in range(1, 13):
            # Récupérer les valeurs
            try:
                ca_total_text = self.table.item(mois - 1, 1).text() if self.table.item(mois - 1, 1) else ""
                ca_total = float(ca_total_text) if ca_total_text.strip() else None
            except (ValueError, AttributeError):
                ca_total = None
            
            try:
                ca_jour_text = self.table.item(mois - 1, 2).text() if self.table.item(mois - 1, 2) else ""
                ca_jour = float(ca_jour_text) if ca_jour_text.strip() else None
            except (ValueError, AttributeError):
                ca_jour = None
            
            try:
                nb_clients_text = self.table.item(mois - 1, 3).text() if self.table.item(mois - 1, 3) else ""
                nb_clients = int(nb_clients_text) if nb_clients_text.strip() else None
            except (ValueError, AttributeError):
                nb_clients = None
            
            try:
                pct_ventes_text = self.table.item(mois - 1, 4).text() if self.table.item(mois - 1, 4) else ""
                pct_ventes = float(pct_ventes_text) if pct_ventes_text.strip() else None
            except (ValueError, AttributeError):
                pct_ventes = None
            
            try:
                pct_couleurs_text = self.table.item(mois - 1, 5).text() if self.table.item(mois - 1, 5) else ""
                pct_couleurs = float(pct_couleurs_text) if pct_couleurs_text.strip() else None
            except (ValueError, AttributeError):
                pct_couleurs = None
            
            try:
                pct_soins_text = self.table.item(mois - 1, 6).text() if self.table.item(mois - 1, 6) else ""
                pct_soins = float(pct_soins_text) if pct_soins_text.strip() else None
            except (ValueError, AttributeError):
                pct_soins = None
            
            # Sauvegarder dans la BDD
            self.db.sauvegarder_objectif(
                annee, mois,
                ca_total, ca_jour, nb_clients,
                pct_ventes, pct_couleurs, pct_soins
            )
        
        QMessageBox.information(
            self, "Sauvegarde",
            f"Les objectifs de l'année {annee} ont été sauvegardés avec succès !"
        )
        
        # Émettre le signal
        self.objectifs_modifies.emit()
    
    def _copier_vers_annee_suivante(self):
        """Copie les objectifs vers l'année suivante"""
        annee_actuelle = int(self.annee_combo.currentText())
        annee_suivante = annee_actuelle + 1
        
        reply = QMessageBox.question(
            self, "Copier vers année suivante",
            f"Voulez-vous copier les objectifs de {annee_actuelle} vers {annee_suivante} ?\n"
            "Cela écrasera les objectifs existants de l'année suivante.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            objectifs = self.db.get_objectifs_annee(annee_actuelle)
            
            for obj in objectifs:
                self.db.sauvegarder_objectif(
                    annee_suivante,
                    obj['mois'],
                    obj.get('ca_total'),
                    obj.get('ca_jour'),
                    obj.get('nb_clients'),
                    obj.get('pct_ventes'),
                    obj.get('pct_couleurs'),
                    obj.get('pct_soins')
                )
            
            QMessageBox.information(
                self, "Copie terminée",
                f"Les objectifs ont été copiés vers {annee_suivante}."
            )