"""
Génération de PDF pour le module Suivis Manager
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime
from typing import List, Dict, Any

from .utils import formater_montant, formater_pourcentage, charger_objectifs, charger_info_salon


class SuivisManagerPDFExporter:
    """Classe pour exporter les données du Suivis Manager en PDF"""
    
    def __init__(self, objectifs: Dict[str, float] = None):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self.objectifs = objectifs or {}
    
    def _setup_styles(self):
        """Configure les styles pour le PDF"""
        # Style pour le titre
        self.titre_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2E3440'),
            spaceAfter=10,
            alignment=1,  # Centré
            fontName='Helvetica-Bold'
        )
        
        # Style pour les sous-titres (nom salon, ville)
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#4C566A'),
            spaceAfter=20,
            alignment=1,  # Centré
            fontName='Helvetica-Bold'
        )
        
        # Style pour la date
        self.date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4C566A'),
            spaceAfter=20,
            alignment=1,  # Centré
            fontName='Helvetica'
        )
    
    def _get_couleur_objectif(self, valeur: float, objectif: float) -> colors.Color:
        """
        Retourne la couleur en fonction de l'objectif
        
        Args:
            valeur: Valeur actuelle
            objectif: Valeur objectif
            
        Returns:
            Couleur pour le texte
        """
        if valeur >= objectif:
            return colors.HexColor('#228B22')  # Vert forêt
        else:
            return colors.HexColor('#B22222')  # Rouge brique
    
    def generer_pdf(self, filepath: str, mois: str, annee: int, 
                    periodes_data: List[tuple], donnees: List[Dict[str, Any]]) -> bool:
        """
        Génère un PDF avec les données du suivi manager
        
        Args:
            filepath: Chemin du fichier PDF à créer
            mois: Nom du mois
            annee: Année
            periodes_data: Liste des tuples (date_debut, date_fin)
            donnees: Liste des dictionnaires de données par période
            
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
            titre = f"TABLEAU SUIVI MANAGER {mois.upper()} {annee}"
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
            
            elements.append(Spacer(1, 0.3*cm))
            
            # Créer le tableau (filtrer les lignes vides)
            table_data = self._creer_donnees_tableau_filtrees(periodes_data, donnees)
            
            # Largeur totale disponible : 21cm (A4) - 2cm (marges) = 19cm
            largeur_totale = 19*cm
            
            # Répartition des colonnes
            col_widths = [
                largeur_totale * 0.25,  # Périodes: 25%
                largeur_totale * 0.125, # C.A. Total: 12.5%
                largeur_totale * 0.125, # C.A. /Jour: 12.5%
                largeur_totale * 0.125, # Nombre de Visites: 12.5%
                largeur_totale * 0.125, # % Ventes: 12.5%
                largeur_totale * 0.125, # % Couleurs: 12.5%
                largeur_totale * 0.125  # % Soins: 12.5%
            ]
            
            # Créer le tableau avec ReportLab
            table = Table(table_data, colWidths=col_widths)
            
            # Style de base du tableau
            style_commands = [
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5E81AC')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                
                # Colonne Périodes (gras, fond gris)
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#E5E9F0')),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('FONTSIZE', (0, 1), (0, -1), 8),
                
                # Autres colonnes (centrées)
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('FONTSIZE', (1, 1), (-1, -1), 8),
                
                # Lignes alternées
                ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
                
                # Bordures
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E9F0')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#5E81AC')),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]
            
            # Appliquer les couleurs selon les objectifs (ajuster les indices selon les lignes filtrées)
            ligne_actuelle = 1  # Commence à 1 car 0 est l'en-tête
            for i, data in enumerate(donnees):
                # Vérifier si cette ligne a été incluse (pas vide)
                has_data = (
                    data.get('ca_total') or data.get('ca_par_jour') or 
                    data.get('nombre_visites') or data.get('pourcentage_ventes') or 
                    data.get('pourcentage_couleurs') or data.get('pourcentage_soins')
                )
                
                if not has_data:
                    continue
                
                # C.A. Total (colonne 1)
                ca_total = data.get('ca_total')
                if ca_total and self.objectifs.get('ca_total'):
                    couleur = self._get_couleur_objectif(ca_total, self.objectifs['ca_total'])
                    style_commands.append(('TEXTCOLOR', (1, ligne_actuelle), (1, ligne_actuelle), couleur))
                    if ca_total >= self.objectifs['ca_total']:
                        style_commands.append(('FONTNAME', (1, ligne_actuelle), (1, ligne_actuelle), 'Helvetica-Bold'))
                
                # C.A. /Jour (colonne 2)
                ca_jour = data.get('ca_par_jour')
                if ca_jour and self.objectifs.get('ca_jour'):
                    couleur = self._get_couleur_objectif(ca_jour, self.objectifs['ca_jour'])
                    style_commands.append(('TEXTCOLOR', (2, ligne_actuelle), (2, ligne_actuelle), couleur))
                    if ca_jour >= self.objectifs['ca_jour']:
                        style_commands.append(('FONTNAME', (2, ligne_actuelle), (2, ligne_actuelle), 'Helvetica-Bold'))
                
                # Nombre de Visites (colonne 3)
                nb_visites = data.get('nombre_visites')
                if nb_visites and self.objectifs.get('nb_clients'):
                    couleur = self._get_couleur_objectif(float(nb_visites), self.objectifs['nb_clients'])
                    style_commands.append(('TEXTCOLOR', (3, ligne_actuelle), (3, ligne_actuelle), couleur))
                    if nb_visites >= self.objectifs['nb_clients']:
                        style_commands.append(('FONTNAME', (3, ligne_actuelle), (3, ligne_actuelle), 'Helvetica-Bold'))
                
                # % Ventes (colonne 4)
                pct_ventes = data.get('pourcentage_ventes')
                if pct_ventes and self.objectifs.get('pct_ventes'):
                    couleur = self._get_couleur_objectif(pct_ventes, self.objectifs['pct_ventes'])
                    style_commands.append(('TEXTCOLOR', (4, ligne_actuelle), (4, ligne_actuelle), couleur))
                    if pct_ventes >= self.objectifs['pct_ventes']:
                        style_commands.append(('FONTNAME', (4, ligne_actuelle), (4, ligne_actuelle), 'Helvetica-Bold'))
                
                # % Couleurs (colonne 5)
                pct_couleurs = data.get('pourcentage_couleurs')
                if pct_couleurs and self.objectifs.get('pct_couleurs'):
                    couleur = self._get_couleur_objectif(pct_couleurs, self.objectifs['pct_couleurs'])
                    style_commands.append(('TEXTCOLOR', (5, ligne_actuelle), (5, ligne_actuelle), couleur))
                    if pct_couleurs >= self.objectifs['pct_couleurs']:
                        style_commands.append(('FONTNAME', (5, ligne_actuelle), (5, ligne_actuelle), 'Helvetica-Bold'))
                
                # % Soins (colonne 6)
                pct_soins = data.get('pourcentage_soins')
                if pct_soins and self.objectifs.get('pct_soins'):
                    couleur = self._get_couleur_objectif(pct_soins, self.objectifs['pct_soins'])
                    style_commands.append(('TEXTCOLOR', (6, ligne_actuelle), (6, ligne_actuelle), couleur))
                    if pct_soins >= self.objectifs['pct_soins']:
                        style_commands.append(('FONTNAME', (6, ligne_actuelle), (6, ligne_actuelle), 'Helvetica-Bold'))
                
                ligne_actuelle += 1
            
            table.setStyle(TableStyle(style_commands))
            
            elements.append(table)
            
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
            'C.A. Total',
            'C.A. /Jour',
            'Nb Visites',
            '% Ventes',
            '% Couleurs',
            '% Soins'
        ]]
        
        # Récupérer le premier jour travaillé
        premier_jour_travaille = periodes_data[0][0] if periodes_data else None
        
        # Données (filtrer les lignes vides)
        from .utils import formater_periode
        
        for i, (date_debut, date_fin) in enumerate(periodes_data):
            periode_data = donnees[i] if i < len(donnees) else {}
            
            # Vérifier si la ligne a au moins une donnée
            has_data = (
                periode_data.get('ca_total') or 
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
                formater_montant(periode_data.get('ca_total')) if periode_data.get('ca_total') else '',
                formater_montant(periode_data.get('ca_par_jour')) if periode_data.get('ca_par_jour') else '',
                str(periode_data.get('nombre_visites')) if periode_data.get('nombre_visites') else '',
                formater_pourcentage(periode_data.get('pourcentage_ventes')) if periode_data.get('pourcentage_ventes') else '',
                formater_pourcentage(periode_data.get('pourcentage_couleurs')) if periode_data.get('pourcentage_couleurs') else '',
                formater_pourcentage(periode_data.get('pourcentage_soins')) if periode_data.get('pourcentage_soins') else ''
            ]
            
            data.append(row)
        
        return data