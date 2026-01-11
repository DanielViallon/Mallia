"""
Gestion de la base de données pour le module Suivis Collaborateurs
"""

from modules.bdd import Database
from typing import List, Dict, Any, Optional
from datetime import datetime


class SuivisCollaborateursDB:
    """Classe pour gérer les données des suivis collaborateurs"""
    
    def __init__(self):
        self.db = Database()
        self._create_tables()
    
    def _create_tables(self):
        """Crée les tables nécessaires pour le module Suivis Collaborateurs"""
        
        # Table principale pour les suivis mensuels par collaborateur
        suivis_table = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "collaborateur_id": "INTEGER NOT NULL",
            "mois": "INTEGER NOT NULL",  # 1-12
            "annee": "INTEGER NOT NULL",  # 2024, 2025, etc.
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "FOREIGN KEY (collaborateur_id)": "REFERENCES collaborateurs(id) ON DELETE CASCADE"
        }
        
        # Table pour les périodes de chaque suivi collaborateur
        periodes_table = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "suivi_id": "INTEGER NOT NULL",
            "numero_periode": "INTEGER NOT NULL",  # 1, 2, 3, 4...
            "date_debut": "TEXT NOT NULL",  # Format YYYY-MM-DD
            "date_fin": "TEXT NOT NULL",  # Format YYYY-MM-DD
            "ca_prestation": "REAL",  # Chiffre d'affaires prestations
            "ca_par_jour": "REAL",  # CA par jour
            "nombre_visites": "INTEGER",  # Nombre de visites
            "pourcentage_ventes": "REAL",  # %
            "pourcentage_couleurs": "REAL",  # %
            "pourcentage_soins": "REAL",  # %
            "FOREIGN KEY (suivi_id)": "REFERENCES suivis_collaborateurs(id) ON DELETE CASCADE"
        }
        
        if not self.db.table_exists("suivis_collaborateurs"):
            self.db.create_table("suivis_collaborateurs", suivis_table)
            print("Table 'suivis_collaborateurs' créée avec succès")
        
        if not self.db.table_exists("suivis_collaborateurs_periodes"):
            self.db.create_table("suivis_collaborateurs_periodes", periodes_table)
            print("Table 'suivis_collaborateurs_periodes' créée avec succès")
    
    def creer_suivi(self, collaborateur_id: int, mois: int, annee: int) -> Optional[int]:
        """
        Crée un nouveau suivi pour un collaborateur et un mois/année
        
        Args:
            collaborateur_id: ID du collaborateur
            mois: Numéro du mois (1-12)
            annee: Année (ex: 2025)
            
        Returns:
            ID du suivi créé ou None si erreur
        """
        # Vérifier si le suivi existe déjà
        existing = self.get_suivi_by_collaborateur_mois_annee(collaborateur_id, mois, annee)
        if existing:
            return existing['id']
        
        query = """
            INSERT INTO suivis_collaborateurs (collaborateur_id, mois, annee)
            VALUES (?, ?, ?)
        """
        cursor = self.db.execute_query(query, (collaborateur_id, mois, annee))
        
        if cursor:
            return cursor.lastrowid
        return None
    
    def get_suivi_by_collaborateur_mois_annee(self, collaborateur_id: int, 
                                               mois: int, annee: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un suivi par collaborateur, mois et année
        
        Args:
            collaborateur_id: ID du collaborateur
            mois: Numéro du mois (1-12)
            annee: Année
            
        Returns:
            Dictionnaire avec les données du suivi ou None
        """
        query = """
            SELECT * FROM suivis_collaborateurs 
            WHERE collaborateur_id = ? AND mois = ? AND annee = ?
        """
        return self.db.fetch_one(query, (collaborateur_id, mois, annee))
    
    def get_periodes_by_suivi_id(self, suivi_id: int) -> List[Dict[str, Any]]:
        """
        Récupère toutes les périodes d'un suivi
        
        Args:
            suivi_id: ID du suivi
            
        Returns:
            Liste des périodes
        """
        query = """
            SELECT * FROM suivis_collaborateurs_periodes 
            WHERE suivi_id = ? 
            ORDER BY numero_periode
        """
        return self.db.fetch_all(query, (suivi_id,))
    
    def sauvegarder_periode(self, suivi_id: int, numero_periode: int, 
                           date_debut: str, date_fin: str,
                           ca_prestation: Optional[float] = None,
                           ca_par_jour: Optional[float] = None,
                           nombre_visites: Optional[int] = None,
                           pourcentage_ventes: Optional[float] = None,
                           pourcentage_couleurs: Optional[float] = None,
                           pourcentage_soins: Optional[float] = None) -> bool:
        """
        Sauvegarde ou met à jour une période
        
        Returns:
            True si succès, False sinon
        """
        # Vérifier si la période existe
        query_check = """
            SELECT id FROM suivis_collaborateurs_periodes 
            WHERE suivi_id = ? AND numero_periode = ?
        """
        existing = self.db.fetch_one(query_check, (suivi_id, numero_periode))
        
        if existing:
            # Mise à jour
            query = """
                UPDATE suivis_collaborateurs_periodes 
                SET date_debut = ?, date_fin = ?, ca_prestation = ?, ca_par_jour = ?,
                    nombre_visites = ?, pourcentage_ventes = ?, 
                    pourcentage_couleurs = ?, pourcentage_soins = ?
                WHERE suivi_id = ? AND numero_periode = ?
            """
            cursor = self.db.execute_query(query, (
                date_debut, date_fin, ca_prestation, ca_par_jour,
                nombre_visites, pourcentage_ventes, pourcentage_couleurs,
                pourcentage_soins, suivi_id, numero_periode
            ))
        else:
            # Insertion
            query = """
                INSERT INTO suivis_collaborateurs_periodes 
                (suivi_id, numero_periode, date_debut, date_fin, ca_prestation, 
                 ca_par_jour, nombre_visites, pourcentage_ventes, 
                 pourcentage_couleurs, pourcentage_soins)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor = self.db.execute_query(query, (
                suivi_id, numero_periode, date_debut, date_fin, ca_prestation,
                ca_par_jour, nombre_visites, pourcentage_ventes,
                pourcentage_couleurs, pourcentage_soins
            ))
        
        # Mettre à jour la date de modification du suivi
        if cursor:
            update_query = """
                UPDATE suivis_collaborateurs 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """
            self.db.execute_query(update_query, (suivi_id,))
            return True
        
        return False
    
    def supprimer_suivi(self, suivi_id: int) -> bool:
        """
        Supprime un suivi et toutes ses périodes
        
        Args:
            suivi_id: ID du suivi à supprimer
            
        Returns:
            True si succès, False sinon
        """
        query = "DELETE FROM suivis_collaborateurs WHERE id = ?"
        cursor = self.db.execute_query(query, (suivi_id,))
        return cursor is not None
    
    def supprimer_suivis_mois(self, mois: int, annee: int) -> bool:
        """
        Supprime tous les suivis d'un mois (tous collaborateurs)
        
        Args:
            mois: Numéro du mois (1-12)
            annee: Année
            
        Returns:
            True si succès, False sinon
        """
        query = "DELETE FROM suivis_collaborateurs WHERE mois = ? AND annee = ?"
        cursor = self.db.execute_query(query, (mois, annee))
        return cursor is not None
    
    def get_collaborateurs_actifs_mois(self, mois: int, annee: int) -> List[Dict[str, Any]]:
        """
        Récupère les collaborateurs actifs pour un mois donné
        
        Un collaborateur est considéré actif si :
        - Il est actuellement actif (etat = 'Actif')
        - OU il était actif durant ce mois (date_inactivation >= dernier jour du mois)
        - ET sa date d'entrée est <= dernier jour du mois
        
        Args:
            mois: Numéro du mois (1-12)
            annee: Année
            
        Returns:
            Liste des collaborateurs triés par ordre
        """
        from datetime import datetime
        import calendar
        
        # Dernier jour du mois sélectionné
        dernier_jour = calendar.monthrange(annee, mois)[1]
        date_limite = f"{annee}-{mois:02d}-{dernier_jour:02d}"
        
        query = """
            SELECT * FROM collaborateurs 
            WHERE (etat = 'Actif' OR (etat = 'Inactif' AND date_inactivation >= ?))
              AND (date_entree IS NULL OR date_entree <= ?)
            ORDER BY ordre
        """
        return self.db.fetch_all(query, (date_limite, date_limite))
    
    def get_tous_les_suivis_mois(self, mois: int, annee: int) -> List[Dict[str, Any]]:
        """
        Récupère tous les suivis d'un mois avec les infos des collaborateurs
        
        Args:
            mois: Numéro du mois (1-12)
            annee: Année
            
        Returns:
            Liste des suivis avec infos collaborateurs triés par ordre
        """
        query = """
            SELECT sc.*, c.nom, c.prenom, c.etat, c.ordre
            FROM suivis_collaborateurs sc
            JOIN collaborateurs c ON sc.collaborateur_id = c.id
            WHERE sc.mois = ? AND sc.annee = ?
            ORDER BY c.ordre
        """
        return self.db.fetch_all(query, (mois, annee))