"""
Gestion de la base de données pour le module Objectifs
"""

from modules.bdd import Database
from typing import List, Dict, Any, Optional


class ObjectifsDB:
    """Classe pour gérer les objectifs mensuels et annuels"""
    
    def __init__(self):
        self.db = Database()
        self._create_tables()
    
    def _create_tables(self):
        """Crée les tables nécessaires pour le module Objectifs"""
        
        # Table des objectifs mensuels (Manager)
        objectifs_table = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "annee": "INTEGER NOT NULL",
            "mois": "INTEGER NOT NULL",  # 1-12
            "ca_total": "REAL",
            "ca_jour": "REAL",
            "nb_clients": "INTEGER",
            "pct_ventes": "REAL",
            "pct_couleurs": "REAL",
            "pct_soins": "REAL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "UNIQUE": "(annee, mois)"
        }
        
        # Table des objectifs annuels (Collaborateurs)
        objectifs_collab_table = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "annee": "INTEGER NOT NULL UNIQUE",
            "ca_prestation": "REAL",
            "ca_jour": "REAL",
            "nb_visites": "REAL",  # Peut être décimal (moyenne)
            "pct_ventes": "REAL",
            "pct_couleurs": "REAL",
            "pct_soins": "REAL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        
        if not self.db.table_exists("objectifs_mensuels"):
            self.db.create_table("objectifs_mensuels", objectifs_table)
            print("Table 'objectifs_mensuels' créée avec succès")
        
        if not self.db.table_exists("objectifs_collaborateurs"):
            self.db.create_table("objectifs_collaborateurs", objectifs_collab_table)
            print("Table 'objectifs_collaborateurs' créée avec succès")
    
    # ========== OBJECTIFS MANAGER ==========
    
    def sauvegarder_objectif(self, annee: int, mois: int, 
                            ca_total: Optional[float] = None,
                            ca_jour: Optional[float] = None,
                            nb_clients: Optional[int] = None,
                            pct_ventes: Optional[float] = None,
                            pct_couleurs: Optional[float] = None,
                            pct_soins: Optional[float] = None) -> bool:
        """
        Sauvegarde ou met à jour les objectifs Manager d'un mois
        
        Args:
            annee: Année
            mois: Mois (1-12)
            ca_total: Objectif CA Total
            ca_jour: Objectif CA /Jour
            nb_clients: Objectif Nombre de Clients
            pct_ventes: Objectif % Ventes
            pct_couleurs: Objectif % Couleurs
            pct_soins: Objectif % Soins
            
        Returns:
            True si succès, False sinon
        """
        query_check = "SELECT id FROM objectifs_mensuels WHERE annee = ? AND mois = ?"
        existing = self.db.fetch_one(query_check, (annee, mois))
        
        if existing:
            query = """
                UPDATE objectifs_mensuels 
                SET ca_total = ?, ca_jour = ?, nb_clients = ?, 
                    pct_ventes = ?, pct_couleurs = ?, pct_soins = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE annee = ? AND mois = ?
            """
            cursor = self.db.execute_query(query, (
                ca_total, ca_jour, nb_clients,
                pct_ventes, pct_couleurs, pct_soins,
                annee, mois
            ))
        else:
            query = """
                INSERT INTO objectifs_mensuels 
                (annee, mois, ca_total, ca_jour, nb_clients, 
                 pct_ventes, pct_couleurs, pct_soins)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor = self.db.execute_query(query, (
                annee, mois, ca_total, ca_jour, nb_clients,
                pct_ventes, pct_couleurs, pct_soins
            ))
        
        return cursor is not None
    
    def get_objectifs_annee(self, annee: int) -> List[Dict[str, Any]]:
        """
        Récupère tous les objectifs Manager d'une année
        
        Args:
            annee: Année
            
        Returns:
            Liste des objectifs par mois
        """
        query = """
            SELECT * FROM objectifs_mensuels 
            WHERE annee = ? 
            ORDER BY mois
        """
        return self.db.fetch_all(query, (annee,))
    
    def get_objectif_mois(self, annee: int, mois: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les objectifs Manager d'un mois spécifique
        
        Args:
            annee: Année
            mois: Mois (1-12)
            
        Returns:
            Dictionnaire avec les objectifs ou None
        """
        query = "SELECT * FROM objectifs_mensuels WHERE annee = ? AND mois = ?"
        return self.db.fetch_one(query, (annee, mois))
    
    def supprimer_objectifs_annee(self, annee: int) -> bool:
        """
        Supprime tous les objectifs Manager d'une année
        
        Args:
            annee: Année
            
        Returns:
            True si succès, False sinon
        """
        query = "DELETE FROM objectifs_mensuels WHERE annee = ?"
        cursor = self.db.execute_query(query, (annee,))
        return cursor is not None
    
    # ========== OBJECTIFS COLLABORATEURS ==========
    
    def sauvegarder_objectif_collab(self, annee: int,
                                    ca_prestation: Optional[float] = None,
                                    ca_jour: Optional[float] = None,
                                    nb_visites: Optional[float] = None,
                                    pct_ventes: Optional[float] = None,
                                    pct_couleurs: Optional[float] = None,
                                    pct_soins: Optional[float] = None) -> bool:
        """
        Sauvegarde ou met à jour les objectifs Collaborateurs d'une année
        
        Args:
            annee: Année
            ca_prestation: Objectif CA Prestation
            ca_jour: Objectif CA /Jour
            nb_visites: Objectif Nombre de Visites (peut être décimal)
            pct_ventes: Objectif % Ventes
            pct_couleurs: Objectif % Couleurs
            pct_soins: Objectif % Soins
            
        Returns:
            True si succès, False sinon
        """
        query_check = "SELECT id FROM objectifs_collaborateurs WHERE annee = ?"
        existing = self.db.fetch_one(query_check, (annee,))
        
        if existing:
            query = """
                UPDATE objectifs_collaborateurs 
                SET ca_prestation = ?, ca_jour = ?, nb_visites = ?, 
                    pct_ventes = ?, pct_couleurs = ?, pct_soins = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE annee = ?
            """
            cursor = self.db.execute_query(query, (
                ca_prestation, ca_jour, nb_visites,
                pct_ventes, pct_couleurs, pct_soins,
                annee
            ))
        else:
            query = """
                INSERT INTO objectifs_collaborateurs 
                (annee, ca_prestation, ca_jour, nb_visites, 
                 pct_ventes, pct_couleurs, pct_soins)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor = self.db.execute_query(query, (
                annee, ca_prestation, ca_jour, nb_visites,
                pct_ventes, pct_couleurs, pct_soins
            ))
        
        return cursor is not None
    
    def get_objectif_collab_annee(self, annee: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les objectifs Collaborateurs d'une année
        
        Args:
            annee: Année
            
        Returns:
            Dictionnaire avec les objectifs ou None
        """
        query = "SELECT * FROM objectifs_collaborateurs WHERE annee = ?"
        return self.db.fetch_one(query, (annee,))
    
    def supprimer_objectif_collab_annee(self, annee: int) -> bool:
        """
        Supprime les objectifs Collaborateurs d'une année
        
        Args:
            annee: Année
            
        Returns:
            True si succès, False sinon
        """
        query = "DELETE FROM objectifs_collaborateurs WHERE annee = ?"
        cursor = self.db.execute_query(query, (annee,))
        return cursor is not None