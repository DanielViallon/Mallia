"""
Interface utilisateur pour le module Suivis Collaborateurs
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from datetime import datetime
from typing import Optional
import calendar

from .pdf_export import SuivisCollaborateursPDFExporter
from .database import SuivisCollaborateursDB
from modules.collaborateurs.database import CollaborateursDB

# Réutilisation des utils de suivis_manager
from modules.suivis_manager.utils import (
    calculer_periodes_mois, formater_periode, formater_montant,
    formater_pourcentage, charger_info_salon, nettoyer_nom_fichier
)


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


class SuivisCollaborateursWidget(QWidget):
    """Widget principal pour le module Suivis Collaborateurs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = SuivisCollaborateursDB()
        self.collab_db = CollaborateursDB()
        self.collaborateur_courant = None
        self.periodes_dates = []
        self.donnees_modifiees = False
        
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
        titre_label = QLabel("👥 SUIVIS COLLABORATEURS")
        titre_font = QFont()
        titre_font.setPointSize(18)
        titre_font.setBold(True)
        titre_label.setFont(titre_font)
        header_layout.addWidget(titre_label)
        
        header_layout.addStretch()
        
        # Sélecteur de mois
        header_layout.addWidget(QLabel("Mois :"))
        self.mois_combo = QComboBox()
        self.mois_combo.addItems([
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ])
        self.mois_combo.currentIndexChanged.connect(self._on_mois_annee_change_with_save)
        header_layout.addWidget(self.mois_combo)
        
        # Sélecteur d'année
        header_layout.addWidget(QLabel("Année :"))
        self.annee_combo = QComboBox()
        annee_actuelle = datetime.now().year
        for annee in range(annee_actuelle - 5, annee_actuelle + 5):
            self.annee_combo.addItem(str(annee))
        self.annee_combo.setCurrentText(str(annee_actuelle))
        self.annee_combo.currentIndexChanged.connect(self._on_mois_annee_change_with_save)
        header_layout.addWidget(self.annee_combo)
        
        layout.addLayout(header_layout)
        
        # Barre de boutons
        buttons_layout = QHBoxLayout()
        
        self.btn_sauvegarder = QPushButton("💾 Sauvegarder")
        self.btn_sauvegarder.clicked.connect(self._sauvegarder_donnees)
        buttons_layout.addWidget(self.btn_sauvegarder)
        
        self.btn_exporter = QPushButton("📄 Exporter PDF")
        self.btn_exporter.clicked.connect(self._exporter_pdf_with_save)
        buttons_layout.addWidget(self.btn_exporter)
        
        self.btn_reinitialiser = QPushButton("🔄 Réinitialiser le mois")
        self.btn_reinitialiser.clicked.connect(self._reinitialiser_mois_with_save)
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
        
        # Sélecteur de collaborateur
        buttons_layout.addWidget(QLabel("Collaborateur :"))
        self.collaborateur_combo = QComboBox()
        self.collaborateur_combo.currentIndexChanged.connect(self._on_collaborateur_change_with_save)
        buttons_layout.addWidget(self.collaborateur_combo)
        
        layout.addLayout(buttons_layout)
        
        # Zone du tableau (avec nom du collaborateur)
        self.tableau_container = QWidget()
        self.tableau_layout = QVBoxLayout(self.tableau_container)
        self.tableau_layout.setContentsMargins(0, 0, 0, 0)
        
        # Nom du collaborateur
        self.nom_collaborateur_label = QLabel()
        nom_font = QFont()
        nom_font.setPointSize(14)
        nom_font.setBold(True)
        self.nom_collaborateur_label.setFont(nom_font)
        self.tableau_layout.addWidget(self.nom_collaborateur_label)
        
        # Tableau
        self.table = None
        self._creer_tableau()
        self.tableau_layout.addWidget(self.table)
        
        layout.addWidget(self.tableau_container)
    
    def _creer_tableau(self):
        """Crée le tableau des données"""
        if self.table:
            self.tableau_layout.removeWidget(self.table)
            self.table.deleteLater()
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Périodes", "C.A. Prestation", "C.A. /Jour", "Nombre de Visites",
            "% Ventes", "% Couleurs", "% Soins"
        ])
        
        self.table.verticalHeader().setVisible(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        self.table.verticalHeader().setDefaultSectionSize(50)
        
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
        
        self.table.itemChanged.connect(self._on_item_changed)
        self.table.currentCellChanged.connect(self._on_cell_exit)
    
    def _charger_mois_courant(self):
        """Charge les données du mois courant"""
        now = datetime.now()
        self.mois_combo.blockSignals(True)
        self.annee_combo.blockSignals(True)
        self.mois_combo.setCurrentIndex(now.month - 1)
        self.annee_combo.setCurrentText(str(now.year))
        self.mois_combo.blockSignals(False)
        self.annee_combo.blockSignals(False)
        self._charger_collaborateurs()
    
    def _on_mois_annee_change_with_save(self):
        """Sauvegarde automatique avant changement de mois/année"""
        if self.donnees_modifiees:
            self._sauvegarder_donnees_silencieuse()
        self._charger_collaborateurs()
    
    def _charger_collaborateurs(self):
        """Charge la liste des collaborateurs actifs pour le mois sélectionné"""
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        
        self.periodes_dates = calculer_periodes_mois(mois, annee)
        
        collaborateurs = self.db.get_collaborateurs_actifs_mois(mois, annee)
        
        self.collaborateur_combo.blockSignals(True)
        self.collaborateur_combo.clear()
        
        if not collaborateurs:
            self.collaborateur_combo.addItem("Aucun collaborateur actif")
            self.collaborateur_combo.setEnabled(False)
            self.nom_collaborateur_label.setText("")
            self._vider_tableau()
        else:
            self.collaborateur_combo.setEnabled(True)
            for collab in collaborateurs:
                self.collaborateur_combo.addItem(
                    f"{collab['prenom']} {collab['nom']}",
                    collab['id']
                )
            
            self._charger_donnees_collaborateur()
        
        self.collaborateur_combo.blockSignals(False)
        self.donnees_modifiees = False
    
    def _on_collaborateur_change_with_save(self):
        """Sauvegarde automatique avant changement de collaborateur"""
        if self.donnees_modifiees:
            self._sauvegarder_donnees_silencieuse()
        self._on_collaborateur_change()
    
    def _on_collaborateur_change(self):
        """Appelé quand le collaborateur sélectionné change"""
        if self.collaborateur_combo.isEnabled():
            self._charger_donnees_collaborateur()
    
    def _charger_donnees_collaborateur(self):
        """Charge les données du collaborateur sélectionné"""
        if not self.collaborateur_combo.isEnabled() or self.collaborateur_combo.count() == 0:
            return
        
        collaborateur_id = self.collaborateur_combo.currentData()
        if not collaborateur_id:
            return
        
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        
        collaborateur = self.collab_db.get_collaborateur(collaborateur_id)
        if not collaborateur:
            return
        
        self.collaborateur_courant = collaborateur
        
        self.nom_collaborateur_label.setText(
            f"{collaborateur['prenom']} {collaborateur['nom']}"
        )
        
        suivi = self.db.get_suivi_by_collaborateur_mois_annee(collaborateur_id, mois, annee)
        
        if suivi:
            periodes_data = self.db.get_periodes_by_suivi_id(suivi['id'])
        else:
            periodes_data = []
        
        self._remplir_tableau(periodes_data)
        self.donnees_modifiees = False
    
    def _remplir_tableau(self, periodes_data: list):
        """Remplit le tableau avec les données"""
        self.table.blockSignals(True)
        
        self.table.setRowCount(len(self.periodes_dates))
        
        data_dict = {p['numero_periode']: p for p in periodes_data}
        
        premier_jour_travaille = self.periodes_dates[0][0] if self.periodes_dates else None
        
        for i, (date_debut, date_fin) in enumerate(self.periodes_dates):
            numero_periode = i + 1
            
            periode_item = QTableWidgetItem(formater_periode(date_debut, date_fin, premier_jour_travaille))
            periode_item.setFlags(periode_item.flags() & ~Qt.ItemIsEditable)
            periode_item.setBackground(Qt.lightGray)
            font = periode_item.font()
            font.setBold(True)
            periode_item.setFont(font)
            self.table.setItem(i, 0, periode_item)
            
            data = data_dict.get(numero_periode, {})
            
            # C.A. Prestation
            ca_prestation = data.get('ca_prestation')
            ca_prestation_item = QTableWidgetItem(normaliser_decimal(formater_montant(ca_prestation)) if ca_prestation else "")
            ca_prestation_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, ca_prestation_item)
            
            # C.A. /Jour
            ca_jour = data.get('ca_par_jour')
            ca_jour_item = QTableWidgetItem(normaliser_decimal(formater_montant(ca_jour)) if ca_jour else "")
            ca_jour_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, ca_jour_item)
            
            # Nombre de Visites (peut avoir des décimales)
            nb_visites = data.get('nombre_visites')
            nb_visites_str = str(nb_visites).replace('.', ',') if nb_visites else ""
            nb_visites_item = QTableWidgetItem(nb_visites_str)
            nb_visites_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, nb_visites_item)
            
            # % Ventes
            pct_ventes = data.get('pourcentage_ventes')
            pct_ventes_item = QTableWidgetItem(normaliser_decimal(formater_pourcentage(pct_ventes)) if pct_ventes else "")
            pct_ventes_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, pct_ventes_item)
            
            # % Couleurs
            pct_couleurs = data.get('pourcentage_couleurs')
            pct_couleurs_item = QTableWidgetItem(normaliser_decimal(formater_pourcentage(pct_couleurs)) if pct_couleurs else "")
            pct_couleurs_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, pct_couleurs_item)
            
            # % Soins
            pct_soins = data.get('pourcentage_soins')
            pct_soins_item = QTableWidgetItem(normaliser_decimal(formater_pourcentage(pct_soins)) if pct_soins else "")
            pct_soins_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 6, pct_soins_item)
        
        self.table.blockSignals(False)
    
    def _vider_tableau(self):
        """Vide le tableau"""
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.table.blockSignals(False)
    
    def _on_item_changed(self, item):
        """Appelé quand une cellule est modifiée"""
        if item.column() == 0:
            return
        
        self.donnees_modifiees = True
        text = item.text()
        
        if item.column() in [1, 2]:  # Montants
            valeur = parser_decimal(text.replace("€", "").strip())
            if valeur is not None:
                self.table.blockSignals(True)
                item.setText(normaliser_decimal(formater_montant(valeur)))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.blockSignals(False)
        
        elif item.column() == 3:  # Nombre de Visites (avec décimales)
            item.setTextAlignment(Qt.AlignCenter)
            valeur = parser_decimal(text)
            if valeur is not None:
                self.table.blockSignals(True)
                item.setText(str(valeur).replace('.', ','))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.blockSignals(False)
        
        elif item.column() in [4, 5, 6]:  # Pourcentages
            valeur = parser_decimal(text.replace("%", "").strip())
            if valeur is not None:
                self.table.blockSignals(True)
                item.setText(normaliser_decimal(formater_pourcentage(valeur)))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.blockSignals(False)
    
    def _on_cell_exit(self, currentRow, currentColumn, previousRow, previousColumn):
        """Sauvegarde automatique quand on quitte une cellule"""
        if self.donnees_modifiees and previousRow >= 0:
            self._sauvegarder_donnees_silencieuse()
    
    def _sauvegarder_donnees_silencieuse(self):
        """Sauvegarde sans message de confirmation"""
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        
        if not self.collaborateur_courant:
            return
        
        collaborateur_id = self.collaborateur_courant['id']
        
        suivi = self.db.get_suivi_by_collaborateur_mois_annee(collaborateur_id, mois, annee)
        if not suivi:
            suivi_id = self.db.creer_suivi(collaborateur_id, mois, annee)
        else:
            suivi_id = suivi['id']
        
        for i in range(self.table.rowCount()):
            date_debut, date_fin = self.periodes_dates[i]
            
            ca_prestation = parser_decimal((self.table.item(i, 1).text() if self.table.item(i, 1) else "").replace("€", ""))
            ca_jour = parser_decimal((self.table.item(i, 2).text() if self.table.item(i, 2) else "").replace("€", ""))
            
            nb_visites_text = self.table.item(i, 3).text() if self.table.item(i, 3) else ""
            nb_visites = parser_decimal(nb_visites_text)
            
            pct_ventes = parser_decimal((self.table.item(i, 4).text() if self.table.item(i, 4) else "").replace("%", ""))
            pct_couleurs = parser_decimal((self.table.item(i, 5).text() if self.table.item(i, 5) else "").replace("%", ""))
            pct_soins = parser_decimal((self.table.item(i, 6).text() if self.table.item(i, 6) else "").replace("%", ""))
            
            self.db.sauvegarder_periode(
                suivi_id,
                i + 1,
                date_debut.strftime("%Y-%m-%d"),
                date_fin.strftime("%Y-%m-%d"),
                ca_prestation,
                ca_jour,
                nb_visites,
                pct_ventes,
                pct_couleurs,
                pct_soins
            )
        
        self.donnees_modifiees = False
    
    def _sauvegarder_donnees(self):
        """Sauvegarde les données de tous les collaborateurs"""
        self._sauvegarder_donnees_silencieuse()
        QMessageBox.information(
            self, "Sauvegarde",
            "Les données ont été sauvegardées avec succès !"
        )
    
    def _reinitialiser_mois_with_save(self):
        """Réinitialisation sans sauvegarde"""
        self._reinitialiser_mois()
    
    def _reinitialiser_mois(self):
        """Réinitialise tous les suivis du mois (tous collaborateurs)"""
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        mois_nom = self.mois_combo.currentText()
        
        suivis = self.db.get_tous_les_suivis_mois(mois, annee)
        
        if not suivis:
            QMessageBox.information(
                self, "Aucune donnée",
                f"Il n'y a aucune donnée à réinitialiser pour {mois_nom} {annee}."
            )
            return
        
        reply = QMessageBox.warning(
            self, "⚠️ Confirmation de réinitialisation",
            f"<b>Attention !</b><br><br>"
            f"Vous êtes sur le point de <b>supprimer définitivement</b> toutes les données "
            f"de <b>tous les collaborateurs</b> pour le mois de <b>{mois_nom} {annee}</b>.<br><br>"
            f"Cette action est <b>irréversible</b>.<br><br>"
            f"Voulez-vous vraiment continuer ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.supprimer_suivis_mois(mois, annee):
                self._charger_donnees_collaborateur()
                self.donnees_modifiees = False
                
                QMessageBox.information(
                    self, "Réinitialisation réussie",
                    f"Toutes les données de {mois_nom} {annee} ont été supprimées."
                )
            else:
                QMessageBox.critical(
                    self, "Erreur",
                    "Une erreur est survenue lors de la réinitialisation."
                )
    
    def _exporter_pdf_with_save(self):
        """Sauvegarde automatique avant export PDF"""
        if self.donnees_modifiees:
            self._sauvegarder_donnees_silencieuse()
        self._exporter_pdf()
    
    def _exporter_pdf(self):
        """Exporte tous les tableaux en PDF"""
        mois = self.mois_combo.currentIndex() + 1
        annee = int(self.annee_combo.currentText())
        mois_nom = self.mois_combo.currentText()
        
        collaborateurs = self.db.get_collaborateurs_actifs_mois(mois, annee)
        
        if not collaborateurs:
            QMessageBox.warning(
                self, "Aucun collaborateur",
                "Aucun collaborateur actif pour ce mois."
            )
            return
        
        # Filtrer les collaborateurs qui ont des données
        collaborateurs_avec_donnees = []
        for collab in collaborateurs:
            suivi = self.db.get_suivi_by_collaborateur_mois_annee(collab['id'], mois, annee)
            if suivi:
                periodes_data = self.db.get_periodes_by_suivi_id(suivi['id'])
                has_data = any(
                    p.get('ca_prestation') or p.get('ca_par_jour') or 
                    p.get('nombre_visites') or p.get('pourcentage_ventes') or 
                    p.get('pourcentage_couleurs') or p.get('pourcentage_soins')
                    for p in periodes_data
                )
                if has_data:
                    collaborateurs_avec_donnees.append(collab)
        
        if not collaborateurs_avec_donnees:
            QMessageBox.warning(
                self, "Aucune donnée",
                "Aucune donnée à exporter pour ce mois."
            )
            return
        
        info_salon = charger_info_salon()
        
        nom_salon_clean = nettoyer_nom_fichier(info_salon['nom']) if info_salon['nom'] else "Salon"
        ville_clean = nettoyer_nom_fichier(info_salon['ville']) if info_salon['ville'] else ""
        mois_chiffre = f"{mois:02d}"
        
        if ville_clean:
            filename_suggestion = f"{nom_salon_clean} {ville_clean} - Suivis Collaborateurs - {annee} {mois_chiffre}.pdf"
        else:
            filename_suggestion = f"{nom_salon_clean} - Suivis Collaborateurs - {annee} {mois_chiffre}.pdf"
        
        import configparser
        from pathlib import Path
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        
        dernier_chemin = config.get('PDF', 'dernier_chemin', fallback='')
        if dernier_chemin and Path(dernier_chemin).exists():
            chemin_initial = str(Path(dernier_chemin) / filename_suggestion)
        else:
            chemin_initial = filename_suggestion
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le PDF",
            chemin_initial,
            "Fichiers PDF (*.pdf)"
        )
        
        if not filepath:
            return
        
        dossier_pdf = str(Path(filepath).parent)
        if not config.has_section('PDF'):
            config.add_section('PDF')
        config.set('PDF', 'dernier_chemin', dossier_pdf)
        with open('config.ini', 'w', encoding='utf-8') as f:
            config.write(f)
        
        donnees_collaborateurs = []
        for collab in collaborateurs_avec_donnees:
            suivi = self.db.get_suivi_by_collaborateur_mois_annee(collab['id'], mois, annee)
            periodes_data = self.db.get_periodes_by_suivi_id(suivi['id'])
            
            data_dict = {p['numero_periode']: p for p in periodes_data}
            donnees_ordonnees = []
            for i in range(len(self.periodes_dates)):
                donnees_ordonnees.append(data_dict.get(i + 1, {}))
            
            donnees_collaborateurs.append({
                'nom': collab['nom'],
                'prenom': collab['prenom'],
                'donnees': donnees_ordonnees
            })
        
        exporter = SuivisCollaborateursPDFExporter()
        success = exporter.generer_pdf(
            filepath,
            mois_nom,
            annee,
            self.periodes_dates,
            donnees_collaborateurs
        )
        
        if success:
            QMessageBox.information(
                self, "Export réussi",
                f"Le PDF a été généré avec succès :\n{filepath}"
            )
            
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
                elif platform.system() == 'Darwin':
                    os.system(f'open "{filepath}"')
                else:
                    os.system(f'xdg-open "{filepath}"')
        else:
            QMessageBox.critical(
                self, "Erreur",
                "Une erreur est survenue lors de la génération du PDF."
            )
    
    def closeEvent(self, event):
        """Sauvegarde automatique à la fermeture"""
        if self.donnees_modifiees:
            self._sauvegarder_donnees_silencieuse()
        event.accept()