"""
Génération de PDF pour le module Suivis Collaborateurs
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime
from typing import List, Dict, Any

from modules.suivis_manager.utils import (
    formater_montant, formater_pourcentage, formater_periode,
    charger_info_salon
)


class SuivisCollaborateursPDFExporter:
    """Classe pour exporter les données du Suivis Collaborateurs en PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configure les styles pour le PDF"""
        # Style pour le titre
        self.titre_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2E3440'),
            spaceAfter=10,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        # Style pour les sous-titres
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#4C566A'),
            spaceAfter=20,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        # Style pour la date
        self.date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4C566A'),
            spaceAfter=20,
            alignment=1,
            fontName='Helvetica'
        )
        
        # Style pour le nom du collaborateur
        self.nom_collab_style = ParagraphStyle(
            'NomCollabStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2E3440'),
            spaceAfter=8,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
    
    def generer_pdf(self, filepath: str, mois: str, annee: int, 
                    periodes_data: List[tuple], 
                    donnees_collaborateurs: List[Dict[str, Any]]) -> bool:
        """
        Génère un PDF avec les données de tous les collaborateurs
        
        Args:
            filepath: Chemin du fichier PDF à créer
            mois: Nom du mois
            annee: Année
            periodes_data: Liste des tuples (date_debut, date_fin)
            donnees_collaborateurs: Liste des dictionnaires avec données par collaborateur
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Créer le document en mode PORTRAIT
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,  # Portrait par défaut
                rightMargin=0,
                leftMargin=0,
                topMargin=0,
                bottomMargin=0
            )
            
            # Éléments du document
            elements = []
            
            # Titre
            titre = f"SUIVIS COLLABORATEURS {mois.upper()} {annee}"
            elements.append(Paragraph(titre, self.titre_style))
            
            # Nom et ville du salon
            info_salon = charger_info_salon()
            if info_salon['nom'] or info_salon['ville']:
                salon_text = f"{info_salon['nom']}"
                if info_salon['ville']:
                    salon_text += f" - {info_salon['ville']}"
                elements.append(Paragraph(salon_text, self.subtitle_style))
            
            # Date de génération
            date_generation = datetime.now().strftime("%d/%m/%Y à %H:%M")
            subtitle = f"Généré le {date_generation}"
            elements.append(Paragraph(subtitle, self.date_style))
            
            # Pour chaque collaborateur
            for idx, collab_data in enumerate(donnees_collaborateurs):
                # Nom du collaborateur
                nom_complet = f"{collab_data['prenom']} {collab_data['nom']}"
                elements.append(Paragraph(nom_complet, self.nom_collab_style))
                
                # Créer le tableau (filtrer les lignes vides)
                table_data = self._creer_donnees_tableau_filtrees(periodes_data, collab_data['donnees'])
                
                # Si pas de données, ne pas afficher ce collaborateur
                if len(table_data) <= 1:  # Seulement l'en-tête
                    continue
                
                # Largeur totale disponible : 21cm (A4) sans marges
                largeur_totale = 21*cm
                
                # Répartition des colonnes
                col_widths = [
                    largeur_totale * 0.25,  # Périodes: 25%
                    largeur_totale * 0.125, # C.A. Prestation: 12.5%
                    largeur_totale * 0.125, # C.A. /Jour: 12.5%
                    largeur_totale * 0.125, # Nb Visites: 12.5%
                    largeur_totale * 0.125, # % Ventes: 12.5%
                    largeur_totale * 0.125, # % Couleurs: 12.5%
                    largeur_totale * 0.125  # % Soins: 12.5%
                ]
                
                table = Table(table_data, colWidths=col_widths)
                
                # Style du tableau
                font_size = 8
                padding = 4
                
                style_commands = [
                    # En-tête
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5E81AC')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), font_size + 1),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), padding + 2),
                    ('TOPPADDING', (0, 0), (-1, 0), padding + 2),
                    
                    # Colonne Périodes
                    ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#E5E9F0')),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('FONTSIZE', (0, 1), (0, -1), font_size),
                    
                    # Autres colonnes
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('FONTSIZE', (1, 1), (-1, -1), font_size),
                    
                    # Lignes alternées
                    ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
                    
                    # Bordures
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E9F0')),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#5E81AC')),
                    
                    # Padding
                    ('LEFTPADDING', (0, 0), (-1, -1), padding),
                    ('RIGHTPADDING', (0, 0), (-1, -1), padding),
                    ('TOPPADDING', (0, 1), (-1, -1), padding),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), padding),
                ]
                
                table.setStyle(TableStyle(style_commands))
                elements.append(table)
                
                # Ajouter un espace entre les collaborateurs
                if idx < len(donnees_collaborateurs) - 1:
                    elements.append(Spacer(1, 0.3*cm))
            
            # Générer le PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la génération du PDF : {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _creer_donnees_tableau_filtrees(self, periodes_data: List[tuple], 
                                        donnees: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Crée les données du tableau pour le PDF en filtrant les lignes vides
        
        Args:
            periodes_data: Liste des tuples (date_debut, date_fin)
            donnees: Liste des dictionnaires de données
            
        Returns:
            Liste de listes représentant le tableau
        """
        # En-tête
        data = [[
            'Périodes',
            'C.A. Prestation',
            'C.A. /Jour',
            'Nb Visites',
            '% Ventes',
            '% Couleurs',
            '% Soins'
        ]]
        
        # Premier jour travaillé
        premier_jour_travaille = periodes_data[0][0] if periodes_data else None
        
        # Données (filtrer les lignes vides)
        for i, (date_debut, date_fin) in enumerate(periodes_data):
            periode_data = donnees[i] if i < len(donnees) else {}
            
            # Vérifier si la ligne a au moins une donnée
            has_data = (
                periode_data.get('ca_prestation') or 
                periode_data.get('ca_par_jour') or 
                periode_data.get('nombre_visites') or 
                periode_data.get('pourcentage_ventes') or 
                periode_data.get('pourcentage_couleurs') or 
                periode_data.get('pourcentage_soins')
            )
            
            # Ne pas inclure la ligne si elle est vide
            if not has_data:
                continue
            
            row = [
                formater_periode(date_debut, date_fin, premier_jour_travaille),
                formater_montant(periode_data.get('ca_prestation')) if periode_data.get('ca_prestation') else '',
                formater_montant(periode_data.get('ca_par_jour')) if periode_data.get('ca_par_jour') else '',
                str(periode_data.get('nombre_visites')) if periode_data.get('nombre_visites') else '',
                formater_pourcentage(periode_data.get('pourcentage_ventes')) if periode_data.get('pourcentage_ventes') else '',
                formater_pourcentage(periode_data.get('pourcentage_couleurs')) if periode_data.get('pourcentage_couleurs') else '',
                formater_pourcentage(periode_data.get('pourcentage_soins')) if periode_data.get('pourcentage_soins') else ''
            ]
            
            data.append(row)
        
        return data