"""
Gestion de la base de données pour le module Suivis Manager
"""

from modules.bdd import Database
from typing import List, Dict, Any, Optional
from datetime import datetime


class SuivisManagerDB:
    """Classe pour gérer les données des suivis manager"""
    
    def __init__(self):
        self.db = Database()
        self._create_tables()
    
    def _create_tables(self):
        """Crée les tables nécessaires pour le module Suivis Manager"""
        
        # Table principale pour les suivis mensuels
        suivis_table = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "mois": "INTEGER NOT NULL",  # 1-12
            "annee": "INTEGER NOT NULL",  # 2024, 2025, etc.
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        
        # Table pour les périodes de chaque mois
        periodes_table = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "suivi_id": "INTEGER NOT NULL",
            "numero_periode": "INTEGER NOT NULL",  # 1, 2, 3, 4...
            "date_debut": "TEXT NOT NULL",  # Format YYYY-MM-DD
            "date_fin": "TEXT NOT NULL",  # Format YYYY-MM-DD
            "ca_total": "REAL",  # Chiffre d'affaires total
            "ca_par_jour": "REAL",  # CA par jour
            "nombre_visites": "INTEGER",  # Nombre de visites
            "pourcentage_ventes": "REAL",  # %
            "pourcentage_couleurs": "REAL",  # %
            "pourcentage_soins": "REAL",  # %
            "FOREIGN KEY (suivi_id)": "REFERENCES suivis_manager(id) ON DELETE CASCADE"
        }
        
        if not self.db.table_exists("suivis_manager"):
            self.db.create_table("suivis_manager", suivis_table)
            print("Table 'suivis_manager' créée avec succès")
        
        if not self.db.table_exists("suivis_manager_periodes"):
            self.db.create_table("suivis_manager_periodes", periodes_table)
            print("Table 'suivis_manager_periodes' créée avec succès")
    
    def creer_suivi(self, mois: int, annee: int) -> Optional[int]:
        """
        Crée un nouveau suivi pour un mois/année
        
        Args:
            mois: Numéro du mois (1-12)
            annee: Année (ex: 2025)
            
        Returns:
            ID du suivi créé ou None si erreur
        """
        # Vérifier si le suivi existe déjà
        existing = self.get_suivi_by_mois_annee(mois, annee)
        if existing:
            print(f"Un suivi existe déjà pour {mois}/{annee}")
            return existing['id']
        
        query = """
            INSERT INTO suivis_manager (mois, annee)
            VALUES (?, ?)
        """
        cursor = self.db.execute_query(query, (mois, annee))
        
        if cursor:
            return cursor.lastrowid
        return None
    
    def get_suivi_by_mois_annee(self, mois: int, annee: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un suivi par mois et année
        
        Args:
            mois: Numéro du mois (1-12)
            annee: Année
            
        Returns:
            Dictionnaire avec les données du suivi ou None
        """
        query = "SELECT * FROM suivis_manager WHERE mois = ? AND annee = ?"
        return self.db.fetch_one(query, (mois, annee))
    
    def get_periodes_by_suivi_id(self, suivi_id: int) -> List[Dict[str, Any]]:
        """
        Récupère toutes les périodes d'un suivi
        
        Args:
            suivi_id: ID du suivi
            
        Returns:
            Liste des périodes
        """
        query = """
            SELECT * FROM suivis_manager_periodes 
            WHERE suivi_id = ? 
            ORDER BY numero_periode
        """
        return self.db.fetch_all(query, (suivi_id,))
    
    def sauvegarder_periode(self, suivi_id: int, numero_periode: int, 
                           date_debut: str, date_fin: str,
                           ca_total: Optional[float] = None,
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
            SELECT id FROM suivis_manager_periodes 
            WHERE suivi_id = ? AND numero_periode = ?
        """
        existing = self.db.fetch_one(query_check, (suivi_id, numero_periode))
        
        if existing:
            # Mise à jour
            query = """
                UPDATE suivis_manager_periodes 
                SET date_debut = ?, date_fin = ?, ca_total = ?, ca_par_jour = ?,
                    nombre_visites = ?, pourcentage_ventes = ?, 
                    pourcentage_couleurs = ?, pourcentage_soins = ?
                WHERE suivi_id = ? AND numero_periode = ?
            """
            cursor = self.db.execute_query(query, (
                date_debut, date_fin, ca_total, ca_par_jour,
                nombre_visites, pourcentage_ventes, pourcentage_couleurs,
                pourcentage_soins, suivi_id, numero_periode
            ))
        else:
            # Insertion
            query = """
                INSERT INTO suivis_manager_periodes 
                (suivi_id, numero_periode, date_debut, date_fin, ca_total, 
                 ca_par_jour, nombre_visites, pourcentage_ventes, 
                 pourcentage_couleurs, pourcentage_soins)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor = self.db.execute_query(query, (
                suivi_id, numero_periode, date_debut, date_fin, ca_total,
                ca_par_jour, nombre_visites, pourcentage_ventes,
                pourcentage_couleurs, pourcentage_soins
            ))
        
        # Mettre à jour la date de modification du suivi
        if cursor:
            update_query = """
                UPDATE suivis_manager 
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
        query = "DELETE FROM suivis_manager WHERE id = ?"
        cursor = self.db.execute_query(query, (suivi_id,))
        return cursor is not None
    
    def get_tous_les_suivis(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les suivis existants
        
        Returns:
            Liste des suivis
        """
        query = "SELECT * FROM suivis_manager ORDER BY annee DESC, mois DESC"
        return self.db.fetch_all(query)