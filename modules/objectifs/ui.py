"""
Interface utilisateur pour le module Objectifs
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from datetime import datetime
from typing import Optional

from .database import ObjectifsDB


def normaliser_decimal(texte: str) -> str:
    """Convertit les points en virgules pour la saisie française"""
    return texte.replace('.', ',')


def parser_decimal(texte: str) -> Optional[float]:
    """Parse un nombre avec virgule ou point"""
    if not texte or texte.strip() == "":
        return None
    texte_nettoye = texte.replace(',', '.').replace(' ', '').strip()
    try:
        return float(texte_nettoye)
    except ValueError:
        return None


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
        titre_label = QLabel("🎯 OBJECTIFS ANNUELS")
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
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.addTab(self._creer_onglet_manager(), "Objectifs Manager")
        self.tabs.addTab(self._creer_onglet_collaborateurs(), "Objectifs Collaborateurs")
        
        layout.addWidget(self.tabs)
    
    def _creer_onglet_manager(self):
        """Crée l'onglet des objectifs Manager (mensuels)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Barre de boutons
        buttons_layout = QHBoxLayout()
        
        self.btn_sauvegarder_manager = QPushButton("💾 Sauvegarder")
        self.btn_sauvegarder_manager.clicked.connect(self._sauvegarder_objectifs_manager)
        buttons_layout.addWidget(self.btn_sauvegarder_manager)
        
        self.btn_reinitialiser_manager = QPushButton("🔄 Réinitialiser l'année")
        self.btn_reinitialiser_manager.clicked.connect(self._reinitialiser_manager)
        self.btn_reinitialiser_manager.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: white;
            }
            QPushButton:hover {
                background-color: #D08770;
            }
        """)
        buttons_layout.addWidget(self.btn_reinitialiser_manager)
        
        self.btn_copier_annee = QPushButton("📋 Copier vers année suivante")
        self.btn_copier_annee.clicked.connect(self._copier_vers_annee_suivante)
        buttons_layout.addWidget(self.btn_copier_annee)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Tableau
        self.table_manager = self._creer_tableau_manager()
        layout.addWidget(self.table_manager)
        
        return widget
    
    def _creer_onglet_collaborateurs(self):
        """Crée l'onglet des objectifs Collaborateurs (annuels)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Barre de boutons
        buttons_layout = QHBoxLayout()
        
        self.btn_sauvegarder_collab = QPushButton("💾 Sauvegarder")
        self.btn_sauvegarder_collab.clicked.connect(self._sauvegarder_objectifs_collab)
        buttons_layout.addWidget(self.btn_sauvegarder_collab)
        
        self.btn_reinitialiser_collab = QPushButton("🔄 Réinitialiser l'année")
        self.btn_reinitialiser_collab.clicked.connect(self._reinitialiser_collab)
        self.btn_reinitialiser_collab.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: white;
            }
            QPushButton:hover {
                background-color: #D08770;
            }
        """)
        buttons_layout.addWidget(self.btn_reinitialiser_collab)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Tableau
        self.table_collab = self._creer_tableau_collab()
        layout.addWidget(self.table_collab)
        
        return widget
    
    def _creer_tableau_manager(self):
        """Crée le tableau des objectifs Manager (mensuels)"""
        table = QTableWidget()
        table.setRowCount(12)  # 12 mois
        table.setColumnCount(7)
        
        table.setHorizontalHeaderLabels([
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
            table.setItem(i, 0, item)
        
        table.verticalHeader().setVisible(False)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        table.verticalHeader().setDefaultSectionSize(45)
        
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
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
        
        return table
    
    def _creer_tableau_collab(self):
        """Crée le tableau des objectifs Collaborateurs (1 ligne pour l'année)"""
        table = QTableWidget()
        table.setRowCount(1)  # 1 seule ligne pour l'année
        table.setColumnCount(7)
        
        table.setHorizontalHeaderLabels([
            "Année", "C.A. Prestation", "C.A. /Jour", "Nombre de Visites",
            "% Ventes", "% Couleurs", "% Soins"
        ])
        
        # Label de l'année en première colonne
        item = QTableWidgetItem("Objectifs annuels")
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        item.setBackground(Qt.lightGray)
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        table.setItem(0, 0, item)
        
        table.verticalHeader().setVisible(False)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        table.verticalHeader().setDefaultSectionSize(45)
        
        table.setStyleSheet("""
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
        
        return table
    
    def _charger_annee_courante(self):
        """Charge les données de l'année courante"""
        now = datetime.now()
        self.annee_combo.setCurrentText(str(now.year))
        self._charger_donnees()
    
    def _charger_donnees(self):
        """Charge les objectifs de l'année sélectionnée"""
        self._charger_donnees_manager()
        self._charger_donnees_collab()
    
    def _charger_donnees_manager(self):
        """Charge les objectifs Manager"""
        annee = int(self.annee_combo.currentText())
        
        objectifs_annee = self.db.get_objectifs_annee(annee)
        objectifs_dict = {obj['mois']: obj for obj in objectifs_annee}
        
        self.table_manager.blockSignals(True)
        
        for mois in range(1, 13):
            objectifs = objectifs_dict.get(mois, {})
            
            ca_total = objectifs.get('ca_total', '')
            self.table_manager.setItem(mois - 1, 1, QTableWidgetItem(
                normaliser_decimal(str(int(ca_total))) if ca_total else ""
            ))
            
            ca_jour = objectifs.get('ca_jour', '')
            self.table_manager.setItem(mois - 1, 2, QTableWidgetItem(
                normaliser_decimal(str(int(ca_jour))) if ca_jour else ""
            ))
            
            nb_clients = objectifs.get('nb_clients', '')
            self.table_manager.setItem(mois - 1, 3, QTableWidgetItem(
                str(int(nb_clients)) if nb_clients else ""
            ))
            
            pct_ventes = objectifs.get('pct_ventes', '')
            self.table_manager.setItem(mois - 1, 4, QTableWidgetItem(
                normaliser_decimal(str(float(pct_ventes))) if pct_ventes else ""
            ))
            
            pct_couleurs = objectifs.get('pct_couleurs', '')
            self.table_manager.setItem(mois - 1, 5, QTableWidgetItem(
                normaliser_decimal(str(float(pct_couleurs))) if pct_couleurs else ""
            ))
            
            pct_soins = objectifs.get('pct_soins', '')
            self.table_manager.setItem(mois - 1, 6, QTableWidgetItem(
                normaliser_decimal(str(float(pct_soins))) if pct_soins else ""
            ))
        
        for row in range(12):
            for col in range(1, 7):
                item = self.table_manager.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
        
        self.table_manager.blockSignals(False)
    
    def _charger_donnees_collab(self):
        """Charge les objectifs Collaborateurs"""
        annee = int(self.annee_combo.currentText())
        
        objectifs = self.db.get_objectif_collab_annee(annee)
        
        self.table_collab.blockSignals(True)
        
        if objectifs:
            ca_prestation = objectifs.get('ca_prestation', '')
            self.table_collab.setItem(0, 1, QTableWidgetItem(
                normaliser_decimal(str(int(ca_prestation))) if ca_prestation else ""
            ))
            
            ca_jour = objectifs.get('ca_jour', '')
            self.table_collab.setItem(0, 2, QTableWidgetItem(
                normaliser_decimal(str(int(ca_jour))) if ca_jour else ""
            ))
            
            nb_visites = objectifs.get('nb_visites', '')
            self.table_collab.setItem(0, 3, QTableWidgetItem(
                normaliser_decimal(str(float(nb_visites))) if nb_visites else ""
            ))
            
            pct_ventes = objectifs.get('pct_ventes', '')
            self.table_collab.setItem(0, 4, QTableWidgetItem(
                normaliser_decimal(str(float(pct_ventes))) if pct_ventes else ""
            ))
            
            pct_couleurs = objectifs.get('pct_couleurs', '')
            self.table_collab.setItem(0, 5, QTableWidgetItem(
                normaliser_decimal(str(float(pct_couleurs))) if pct_couleurs else ""
            ))
            
            pct_soins = objectifs.get('pct_soins', '')
            self.table_collab.setItem(0, 6, QTableWidgetItem(
                normaliser_decimal(str(float(pct_soins))) if pct_soins else ""
            ))
        else:
            # Vider la ligne si aucun objectif
            for col in range(1, 7):
                self.table_collab.setItem(0, col, QTableWidgetItem(""))
        
        for col in range(1, 7):
            item = self.table_collab.item(0, col)
            if item:
                item.setTextAlignment(Qt.AlignCenter)
        
        self.table_collab.blockSignals(False)
    
    def _sauvegarder_objectifs_manager(self):
        """Sauvegarde tous les objectifs Manager du tableau"""
        annee = int(self.annee_combo.currentText())
        
        for mois in range(1, 13):
            try:
                ca_total_text = self.table_manager.item(mois - 1, 1).text() if self.table_manager.item(mois - 1, 1) else ""
                ca_total = parser_decimal(ca_total_text)
            except (ValueError, AttributeError):
                ca_total = None
            
            try:
                ca_jour_text = self.table_manager.item(mois - 1, 2).text() if self.table_manager.item(mois - 1, 2) else ""
                ca_jour = parser_decimal(ca_jour_text)
            except (ValueError, AttributeError):
                ca_jour = None
            
            try:
                nb_clients_text = self.table_manager.item(mois - 1, 3).text() if self.table_manager.item(mois - 1, 3) else ""
                nb_clients = int(parser_decimal(nb_clients_text)) if nb_clients_text.strip() else None
            except (ValueError, AttributeError):
                nb_clients = None
            
            try:
                pct_ventes_text = self.table_manager.item(mois - 1, 4).text() if self.table_manager.item(mois - 1, 4) else ""
                pct_ventes = parser_decimal(pct_ventes_text)
            except (ValueError, AttributeError):
                pct_ventes = None
            
            try:
                pct_couleurs_text = self.table_manager.item(mois - 1, 5).text() if self.table_manager.item(mois - 1, 5) else ""
                pct_couleurs = parser_decimal(pct_couleurs_text)
            except (ValueError, AttributeError):
                pct_couleurs = None
            
            try:
                pct_soins_text = self.table_manager.item(mois - 1, 6).text() if self.table_manager.item(mois - 1, 6) else ""
                pct_soins = parser_decimal(pct_soins_text)
            except (ValueError, AttributeError):
                pct_soins = None
            
            self.db.sauvegarder_objectif(
                annee, mois,
                ca_total, ca_jour, nb_clients,
                pct_ventes, pct_couleurs, pct_soins
            )
        
        QMessageBox.information(
            self, "Sauvegarde",
            f"Les objectifs Manager de l'année {annee} ont été sauvegardés avec succès !"
        )
        
        self.objectifs_modifies.emit()
    
    def _sauvegarder_objectifs_collab(self):
        """Sauvegarde les objectifs Collaborateurs"""
        annee = int(self.annee_combo.currentText())
        
        try:
            ca_prestation_text = self.table_collab.item(0, 1).text() if self.table_collab.item(0, 1) else ""
            ca_prestation = parser_decimal(ca_prestation_text)
        except (ValueError, AttributeError):
            ca_prestation = None
        
        try:
            ca_jour_text = self.table_collab.item(0, 2).text() if self.table_collab.item(0, 2) else ""
            ca_jour = parser_decimal(ca_jour_text)
        except (ValueError, AttributeError):
            ca_jour = None
        
        try:
            nb_visites_text = self.table_collab.item(0, 3).text() if self.table_collab.item(0, 3) else ""
            nb_visites = parser_decimal(nb_visites_text)
        except (ValueError, AttributeError):
            nb_visites = None
        
        try:
            pct_ventes_text = self.table_collab.item(0, 4).text() if self.table_collab.item(0, 4) else ""
            pct_ventes = parser_decimal(pct_ventes_text)
        except (ValueError, AttributeError):
            pct_ventes = None
        
        try:
            pct_couleurs_text = self.table_collab.item(0, 5).text() if self.table_collab.item(0, 5) else ""
            pct_couleurs = parser_decimal(pct_couleurs_text)
        except (ValueError, AttributeError):
            pct_couleurs = None
        
        try:
            pct_soins_text = self.table_collab.item(0, 6).text() if self.table_collab.item(0, 6) else ""
            pct_soins = parser_decimal(pct_soins_text)
        except (ValueError, AttributeError):
            pct_soins = None
        
        self.db.sauvegarder_objectif_collab(
            annee,
            ca_prestation, ca_jour, nb_visites,
            pct_ventes, pct_couleurs, pct_soins
        )
        
        QMessageBox.information(
            self, "Sauvegarde",
            f"Les objectifs Collaborateurs de l'année {annee} ont été sauvegardés avec succès !"
        )
        
        self.objectifs_modifies.emit()
    
    def _reinitialiser_manager(self):
        """Réinitialise tous les objectifs Manager de l'année"""
        annee = int(self.annee_combo.currentText())
        
        objectifs = self.db.get_objectifs_annee(annee)
        
        if not objectifs:
            QMessageBox.information(
                self, "Aucune donnée",
                f"Il n'y a aucun objectif Manager à réinitialiser pour l'année {annee}."
            )
            return
        
        reply = QMessageBox.warning(
            self, "⚠️ Confirmation de réinitialisation",
            f"<b>Attention !</b><br><br>"
            f"Vous êtes sur le point de <b>supprimer définitivement</b> tous les objectifs Manager "
            f"de l'année <b>{annee}</b> (12 mois).<br><br>"
            f"Cette action est <b>irréversible</b>.<br><br>"
            f"Voulez-vous vraiment continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.supprimer_objectifs_annee(annee):
                self._charger_donnees_manager()
                
                QMessageBox.information(
                    self, "Réinitialisation réussie",
                    f"Tous les objectifs Manager de l'année {annee} ont été supprimés."
                )
                
                self.objectifs_modifies.emit()
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Une erreur est survenue lors de la réinitialisation."
                )
    
    def _reinitialiser_collab(self):
        """Réinitialise les objectifs Collaborateurs de l'année"""
        annee = int(self.annee_combo.currentText())
        
        objectifs = self.db.get_objectif_collab_annee(annee)
        
        if not objectifs:
            QMessageBox.information(
                self, "Aucune donnée",
                f"Il n'y a aucun objectif Collaborateurs à réinitialiser pour l'année {annee}."
            )
            return
        
        reply = QMessageBox.warning(
            self, "⚠️ Confirmation de réinitialisation",
            f"<b>Attention !</b><br><br>"
            f"Vous êtes sur le point de <b>supprimer définitivement</b> tous les objectifs Collaborateurs "
            f"de l'année <b>{annee}</b>.<br><br>"
            f"Cette action est <b>irréversible</b>.<br><br>"
            f"Voulez-vous vraiment continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.supprimer_objectif_collab_annee(annee):
                self._charger_donnees_collab()
                
                QMessageBox.information(
                    self, "Réinitialisation réussie",
                    f"Tous les objectifs Collaborateurs de l'année {annee} ont été supprimés."
                )
                
                self.objectifs_modifies.emit()
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Une erreur est survenue lors de la réinitialisation."
                )
    
    def _copier_vers_annee_suivante(self):
        """Copie les objectifs Manager vers l'année suivante"""
        annee_actuelle = int(self.annee_combo.currentText())
        annee_suivante = annee_actuelle + 1
        
        reply = QMessageBox.question(
            self, "Copier vers année suivante",
            f"Voulez-vous copier les objectifs Manager de {annee_actuelle} vers {annee_suivante} ?\n"
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
                f"Les objectifs Manager ont été copiés vers {annee_suivante}."
            )