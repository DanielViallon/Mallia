"""
Interface utilisateur pour le module Suivis Manager
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QLineEdit, QFileDialog
)
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QBrush
from datetime import datetime
import calendar

from .pdf_export import SuivisManagerPDFExporter
from .database import SuivisManagerDB
from .utils import (
    calculer_periodes_mois, formater_periode, formater_montant,
    formater_pourcentage, parser_montant, parser_pourcentage,
    charger_objectifs, charger_info_salon, nettoyer_nom_fichier
)


class SuivisManagerWidget(QWidget):
    """Widget principal pour le module Suivis Manager"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = SuivisManagerDB()
        self.suivi_id_courant = None
        self.periodes_dates = []  # Stocke les dates des périodes
        self.objectifs = {}  # Sera chargé dynamiquement
        
        self._init_ui()
        self._charger_mois_courant()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête avec sélection mois/année
        header_layout = QHBoxLayout()
        
        # Titre
        self.titre_label = QLabel("TABLEAU SUIVI MANAGER")
        titre_font = QFont()
        titre_font.setPointSize(18)
        titre_font.setBold(True)
        self.titre_label.setFont(titre_font)
        header_layout.addWidget(self.titre_label)
        
        header_layout.addStretch()
        
        # Sélecteur de mois
        header_layout.addWidget(QLabel("Mois :"))
        self.mois_combo = QComboBox()
        self.mois_combo.addItems([
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ])
        self.mois_combo.currentIndexChanged.connect(self._on_mois_annee_change)
        header_layout.addWidget(self.mois_combo)
        
        # Sélecteur d'année
        header_layout.addWidget(QLabel("Année :"))
        self.annee_combo = QComboBox()
        annee_actuelle = datetime.now().year
        for annee in range(annee_actuelle - 5, annee_actuelle + 5):
            self.annee_combo.addItem(str(annee))
        self.annee_combo.setCurrentText(str(annee_actuelle))
        self.annee_combo.currentIndexChanged.connect(self._on_mois_annee_change)
        header_layout.addWidget(self.annee_combo)
        
        layout.addLayout(header_layout)
        
        # Barre de boutons
        buttons_layout = QHBoxLayout()
        
        self.btn_nouveau = QPushButton("📝 Nouveau Mois")
        self.btn_nouveau.clicked.connect(self._nouveau_mois)
        buttons_layout.addWidget(self.btn_nouveau)
        
        self.btn_sauvegarder = QPushButton("💾 Sauvegarder")
        self.btn_sauvegarder.clicked.connect(self._sauvegarder_donnees)
        buttons_layout.addWidget(self.btn_sauvegarder)
        
        self.btn_exporter = QPushButton("📄 Exporter PDF")
        self.btn_exporter.clicked.connect(self._exporter_pdf)
        buttons_layout.addWidget(self.btn_exporter)
        
        self.btn_reinitialiser = QPushButton("🔄 Réinitialiser le mois")
        self.btn_reinitialiser.clicked.connect(self._reinitialiser_mois)
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
    
    def _appliquer_couleur_objectif(self, item: QTableWidgetItem, valeur: Optional[float], 
                                     objectif: Optional[float], is_pourcentage: bool = False):
        """
        Applique la couleur à un item en fonction de l'objectif
        
        Args:
            item: QTableWidgetItem à colorer
            valeur: Valeur actuelle
            objectif: Valeur objectif
            is_pourcentage: True si c'est un pourcentage
        """
        if valeur is None or objectif is None:
            return
        
        if valeur >= objectif:
            # Objectif atteint ou dépassé : vert et gras
            item.setForeground(QColor(34, 139, 34))  # Vert forêt
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        else:
            # Objectif non atteint : rouge
            item.setForeground(QColor(178, 34, 34))  # Rouge brique
            font = item.font()
            font.setBold(False)
            item.setFont(font)
    
    def _creer_tableau(self):
        """Crée le tableau des données"""
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Périodes", "C.A. Total", "C.A. /Jour", "Nombre de Visites",
            "% Ventes", "% Couleurs", "% Soins"
        ])
        
        # Masquer les numéros de lignes
        self.table.verticalHeader().setVisible(False)
        
        # Configurer l'en-tête
        header = self.table.horizontalHeader()
        
        # Colonne Périodes : largeur fixe basée sur le contenu
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        # Autres colonnes : même largeur proportionnelle
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # Hauteur des lignes
        self.table.verticalHeader().setDefaultSectionSize(50)
        
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
        
        # Connecter le signal de modification
        self.table.itemChanged.connect(self._on_item_changed)
    
    def _charger_mois_courant(self):
        """Charge les données du mois courant"""
        now = datetime.now()
        self.mois_combo.setCurrentIndex(now.month - 1)
        self.annee_combo.setCurrentText(str(now.year))
        self._charger_donnees()
    
    def _on_mois_annee_change(self):
        """Appelé quand le mois ou l'année change"""
        self._charger_donnees()
    
    def _charger_donnees(self):
        """Charge les données pour le mois/année sélectionné"""
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        
        # Charger les objectifs pour ce mois/année
        self.objectifs = charger_objectifs(annee, mois)
        
        # Mettre à jour le titre
        mois_nom = self.mois_combo.currentText()
        self.titre_label.setText(f"TABLEAU SUIVI MANAGER {mois_nom.upper()} {annee}")
        
        # Calculer les périodes
        self.periodes_dates = calculer_periodes_mois(mois, annee)
        
        # Récupérer ou créer le suivi
        suivi = self.db.get_suivi_by_mois_annee(mois, annee)
        
        if suivi:
            self.suivi_id_courant = suivi['id']
            periodes_data = self.db.get_periodes_by_suivi_id(self.suivi_id_courant)
        else:
            self.suivi_id_courant = None
            periodes_data = []
        
        # Remplir le tableau
        self._remplir_tableau(periodes_data)
    
    def _remplir_tableau(self, periodes_data: list):
        """Remplit le tableau avec les données"""
        # Bloquer les signaux pendant le remplissage
        self.table.blockSignals(True)
        
        self.table.setRowCount(len(self.periodes_dates))
        
        # Créer un dictionnaire des données par numéro de période
        data_dict = {p['numero_periode']: p for p in periodes_data}
        
        # Récupérer le premier jour travaillé (première date de la première période)
        premier_jour_travaille = self.periodes_dates[0][0] if self.periodes_dates else None
        
        for i, (date_debut, date_fin) in enumerate(self.periodes_dates):
            numero_periode = i + 1
            
            # Colonne Périodes (non éditable, en gras) - cumulatif depuis le premier jour travaillé
            periode_item = QTableWidgetItem(formater_periode(date_debut, date_fin, premier_jour_travaille))
            periode_item.setFlags(periode_item.flags() & ~Qt.ItemIsEditable)
            periode_item.setBackground(Qt.lightGray)
            
            # Mettre en gras
            font = periode_item.font()
            font.setBold(True)
            periode_item.setFont(font)
            
            self.table.setItem(i, 0, periode_item)
            
            # Récupérer les données si elles existent
            data = data_dict.get(numero_periode, {})
            
            # C.A. Total
            ca_total = data.get('ca_total')
            ca_total_item = QTableWidgetItem(formater_montant(ca_total) if ca_total else "")
            ca_total_item.setTextAlignment(Qt.AlignCenter)
            self._appliquer_couleur_objectif(ca_total_item, ca_total, self.objectifs.get('ca_total'))
            self.table.setItem(i, 1, ca_total_item)
            
            # C.A. /Jour
            ca_jour = data.get('ca_par_jour')
            ca_jour_item = QTableWidgetItem(formater_montant(ca_jour) if ca_jour else "")
            ca_jour_item.setTextAlignment(Qt.AlignCenter)
            self._appliquer_couleur_objectif(ca_jour_item, ca_jour, self.objectifs.get('ca_jour'))
            self.table.setItem(i, 2, ca_jour_item)
            
            # Nombre de Visites
            nb_visites = data.get('nombre_visites')
            nb_visites_item = QTableWidgetItem(str(nb_visites) if nb_visites else "")
            nb_visites_item.setTextAlignment(Qt.AlignCenter)
            self._appliquer_couleur_objectif(nb_visites_item, float(nb_visites) if nb_visites else None, 
                                            self.objectifs.get('nb_clients'))
            self.table.setItem(i, 3, nb_visites_item)
            
            # % Ventes
            pct_ventes = data.get('pourcentage_ventes')
            pct_ventes_item = QTableWidgetItem(formater_pourcentage(pct_ventes) if pct_ventes else "")
            pct_ventes_item.setTextAlignment(Qt.AlignCenter)
            self._appliquer_couleur_objectif(pct_ventes_item, pct_ventes, self.objectifs.get('pct_ventes'), True)
            self.table.setItem(i, 4, pct_ventes_item)
            
            # % Couleurs
            pct_couleurs = data.get('pourcentage_couleurs')
            pct_couleurs_item = QTableWidgetItem(formater_pourcentage(pct_couleurs) if pct_couleurs else "")
            pct_couleurs_item.setTextAlignment(Qt.AlignCenter)
            self._appliquer_couleur_objectif(pct_couleurs_item, pct_couleurs, self.objectifs.get('pct_couleurs'), True)
            self.table.setItem(i, 5, pct_couleurs_item)
            
            # % Soins
            pct_soins = data.get('pourcentage_soins')
            pct_soins_item = QTableWidgetItem(formater_pourcentage(pct_soins) if pct_soins else "")
            pct_soins_item.setTextAlignment(Qt.AlignCenter)
            self._appliquer_couleur_objectif(pct_soins_item, pct_soins, self.objectifs.get('pct_soins'), True)
            self.table.setItem(i, 6, pct_soins_item)
        
        # Débloquer les signaux
        self.table.blockSignals(False)
    
    def _on_item_changed(self, item):
        """Appelé quand une cellule est modifiée"""
        if item.column() == 0:  # Colonne Périodes non éditable
            return
        
        # Formater automatiquement selon la colonne
        text = item.text()
        
        if item.column() in [1, 2]:  # C.A. Total, C.A. /Jour
            valeur = parser_montant(text)
            if valeur is not None:
                self.table.blockSignals(True)
                item.setText(formater_montant(valeur))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Appliquer la couleur
                if item.column() == 1:
                    self._appliquer_couleur_objectif(item, valeur, self.objectifs.get('ca_total'))
                else:
                    self._appliquer_couleur_objectif(item, valeur, self.objectifs.get('ca_jour'))
                
                self.table.blockSignals(False)
        
        elif item.column() == 3:  # Nombre de Visites
            item.setTextAlignment(Qt.AlignCenter)
            try:
                valeur = float(text) if text.strip() else None
                self._appliquer_couleur_objectif(item, valeur, self.objectifs.get('nb_clients'))
            except ValueError:
                pass
        
        elif item.column() in [4, 5, 6]:  # Pourcentages
            valeur = parser_pourcentage(text)
            if valeur is not None:
                self.table.blockSignals(True)
                item.setText(formater_pourcentage(valeur))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Appliquer la couleur
                if item.column() == 4:
                    self._appliquer_couleur_objectif(item, valeur, self.objectifs.get('pct_ventes'), True)
                elif item.column() == 5:
                    self._appliquer_couleur_objectif(item, valeur, self.objectifs.get('pct_couleurs'), True)
                else:
                    self._appliquer_couleur_objectif(item, valeur, self.objectifs.get('pct_soins'), True)
                
                self.table.blockSignals(False)
    
    def _nouveau_mois(self):
        """Crée un nouveau mois"""
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        
        # Vérifier si existe déjà
        suivi = self.db.get_suivi_by_mois_annee(mois, annee)
        
        if suivi:
            reply = QMessageBox.question(
                self, "Mois existant",
                f"Un suivi existe déjà pour {self.mois_combo.currentText()} {annee}.\n"
                "Voulez-vous le réinitialiser ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.db.supprimer_suivi(suivi['id'])
                self.suivi_id_courant = self.db.creer_suivi(mois, annee)
                self._charger_donnees()
        else:
            self.suivi_id_courant = self.db.creer_suivi(mois, annee)
            QMessageBox.information(
                self, "Nouveau mois",
                f"Nouveau suivi créé pour {self.mois_combo.currentText()} {annee}"
            )
            self._charger_donnees()
    
    def _reinitialiser_mois(self):
        """Réinitialise le mois en cours (supprime toutes les données)"""
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        mois_nom = self.mois_combo.currentText()
        
        # Vérifier s'il y a des données à supprimer
        suivi = self.db.get_suivi_by_mois_annee(mois, annee)
        
        if not suivi:
            QMessageBox.information(
                self, "Aucune donnée",
                f"Il n'y a aucune donnée à réinitialiser pour {mois_nom} {annee}."
            )
            return
        
        # Demander confirmation avec avertissement
        reply = QMessageBox.warning(
            self, "⚠️ Confirmation de réinitialisation",
            f"<b>Attention !</b><br><br>"
            f"Vous êtes sur le point de <b>supprimer définitivement</b> toutes les données "
            f"du mois de <b>{mois_nom} {annee}</b>.<br><br>"
            f"Cette action est <b>irréversible</b>.<br><br>"
            f"Voulez-vous vraiment continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Bouton par défaut
        )
        
        if reply == QMessageBox.Yes:
            # Supprimer le suivi (cascade supprimera aussi les périodes)
            if self.db.supprimer_suivi(suivi['id']):
                self.suivi_id_courant = None
                
                # Vider le tableau
                self._charger_donnees()
                
                QMessageBox.information(
                    self, "Réinitialisation réussie",
                    f"Toutes les données de {mois_nom} {annee} ont été supprimées.\n"
                    f"Le tableau a été réinitialisé."
                )
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Une erreur est survenue lors de la réinitialisation."
                )
    
    def _sauvegarder_donnees(self):
        """Sauvegarde les données du tableau"""
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        
        # Créer le suivi s'il n'existe pas
        if not self.suivi_id_courant:
            self.suivi_id_courant = self.db.creer_suivi(mois, annee)
        
        # Sauvegarder chaque période
        for i in range(self.table.rowCount()):
            date_debut, date_fin = self.periodes_dates[i]
            
            # Récupérer les valeurs
            ca_total = parser_montant(self.table.item(i, 1).text() if self.table.item(i, 1) else "")
            ca_jour = parser_montant(self.table.item(i, 2).text() if self.table.item(i, 2) else "")
            
            nb_visites_text = self.table.item(i, 3).text() if self.table.item(i, 3) else ""
            nb_visites = int(nb_visites_text) if nb_visites_text.strip() else None
            
            pct_ventes = parser_pourcentage(self.table.item(i, 4).text() if self.table.item(i, 4) else "")
            pct_couleurs = parser_pourcentage(self.table.item(i, 5).text() if self.table.item(i, 5) else "")
            pct_soins = parser_pourcentage(self.table.item(i, 6).text() if self.table.item(i, 6) else "")
            
            # Sauvegarder dans la BDD
            self.db.sauvegarder_periode(
                self.suivi_id_courant,
                i + 1,  # numero_periode
                date_debut.strftime("%Y-%m-%d"),
                date_fin.strftime("%Y-%m-%d"),
                ca_total,
                ca_jour,
                nb_visites,
                pct_ventes,
                pct_couleurs,
                pct_soins
            )
        
        QMessageBox.information(
            self, "Sauvegarde",
            "Les données ont été sauvegardées avec succès !"
        )
    
    def _exporter_pdf(self):
        """Exporte le tableau en PDF"""
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        mois_nom = self.mois_combo.currentText()
        
        # Vérifier qu'il y a des données
        if not self.periodes_dates:
            QMessageBox.warning(
                self, "Aucune donnée",
                "Aucune donnée à exporter pour ce mois."
            )
            return
        
        # Charger les infos du salon
        info_salon = charger_info_salon()
        
        # Créer le nom de fichier avec le format : [NOM SALON] [VILLE] - Suivi Manager - [ANNEE] [MOIS].pdf
        nom_salon_clean = nettoyer_nom_fichier(info_salon['nom']) if info_salon['nom'] else "Salon"
        ville_clean = nettoyer_nom_fichier(info_salon['ville']) if info_salon['ville'] else ""
        mois_chiffre = f"{mois:02d}"  # Format 01, 02, etc.
        
        if ville_clean:
            filename_suggestion = f"{nom_salon_clean} {ville_clean} - Suivi Manager - {annee} {mois_chiffre}.pdf"
        else:
            filename_suggestion = f"{nom_salon_clean} - Suivi Manager - {annee} {mois_chiffre}.pdf"
        
        # Demander où sauvegarder le fichier
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le PDF",
            filename_suggestion,
            "Fichiers PDF (*.pdf)"
        )
        
        if not filepath:
            return  # L'utilisateur a annulé
        
        # Récupérer les données du suivi
        suivi = self.db.get_suivi_by_mois_annee(mois, annee)
        
        if suivi:
            periodes_data = self.db.get_periodes_by_suivi_id(suivi['id'])
        else:
            periodes_data = []
        
        # Créer un dictionnaire des données par numéro de période
        data_dict = {p['numero_periode']: p for p in periodes_data}
        
        # Préparer les données dans l'ordre des périodes
        donnees_ordonnees = []
        for i in range(len(self.periodes_dates)):
            donnees_ordonnees.append(data_dict.get(i + 1, {}))
        
        # Générer le PDF
        exporter = SuivisManagerPDFExporter(self.objectifs)  # Passer les objectifs
        success = exporter.generer_pdf(
            filepath,
            mois_nom,
            annee,
            self.periodes_dates,
            donnees_ordonnees
        )
        
        if success:
            QMessageBox.information(
                self, "Export réussi",
                f"Le PDF a été généré avec succès :\n{filepath}"
            )
            
            # Demander si l'utilisateur veut ouvrir le fichier
            reply = QMessageBox.question(
                self, "Ouvrir le PDF",
                "Voulez-vous ouvrir le fichier PDF ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                import os
                import platform
                
                if platform.system() == 'Windows':
                    os.startfile(filepath)
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{filepath}"')
                else:  # Linux
                    os.system(f'xdg-open "{filepath}"')
        else:
            QMessageBox.critical(
                self, "Erreur",
                "Une erreur est survenue lors de la génération du PDF."
            )
    
    def recharger_objectifs(self):
        """Recharge les objectifs et rafraîchit l'affichage"""
        self._charger_donnees()