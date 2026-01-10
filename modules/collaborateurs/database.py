"""
Gestion de la base de données pour le module Collaborateurs
"""

from modules.bdd import Database
from typing import List, Dict, Any, Optional
from datetime import datetime


class CollaborateursDB:
    """Classe pour gérer les données des collaborateurs"""
    
    def __init__(self):
        self.db = Database()
        self._create_tables()
        self._migrate_database()
    
    def _create_tables(self):
        """Crée les tables nécessaires pour le module Collaborateurs"""
        
        # Table des collaborateurs
        collaborateurs_table = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "nom": "TEXT NOT NULL",
            "prenom": "TEXT NOT NULL",
            "etat": "TEXT NOT NULL DEFAULT 'Actif'",  # 'Actif' ou 'Inactif'
            "ordre": "INTEGER DEFAULT 0",  # Ordre d'affichage
            "date_entree": "DATE",  # Date d'entrée du collaborateur
            "date_inactivation": "TIMESTAMP",  # Date à laquelle le collaborateur a été déclaré inactif
            "date_creation": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "date_modification": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        
        if not self.db.table_exists("collaborateurs"):
            self.db.create_table("collaborateurs", collaborateurs_table)
            print("Table 'collaborateurs' créée avec succès")
    
    def _migrate_database(self):
        """Migre la base de données pour ajouter les colonnes manquantes"""
        try:
            # Vérifie si les colonnes existent déjà
            query = "PRAGMA table_info(collaborateurs)"
            columns = self.db.fetch_all(query)
            column_names = [col['name'] for col in columns] if columns else []
            
            # Ajouter la colonne date_inactivation si elle n'existe pas
            if 'date_inactivation' not in column_names:
                alter_query = "ALTER TABLE collaborateurs ADD COLUMN date_inactivation TIMESTAMP"
                self.db.execute_query(alter_query)
                print("Colonne 'date_inactivation' ajoutée avec succès")
            
            # Ajouter la colonne ordre si elle n'existe pas
            if 'ordre' not in column_names:
                alter_query = "ALTER TABLE collaborateurs ADD COLUMN ordre INTEGER DEFAULT 0"
                self.db.execute_query(alter_query)
                print("Colonne 'ordre' ajoutée avec succès")
                
                # Initialiser l'ordre pour les collaborateurs existants
                self._initialiser_ordre()
            
            # Ajouter la colonne date_entree si elle n'existe pas
            if 'date_entree' not in column_names:
                alter_query = "ALTER TABLE collaborateurs ADD COLUMN date_entree DATE"
                self.db.execute_query(alter_query)
                print("Colonne 'date_entree' ajoutée avec succès")
                
        except Exception as e:
            print(f"Erreur lors de la migration: {e}")
    
    def _initialiser_ordre(self):
        """Initialise l'ordre pour les collaborateurs existants"""
        try:
            # Récupérer tous les collaborateurs sans ordre défini
            query = "SELECT id FROM collaborateurs ORDER BY id"
            collaborateurs = self.db.fetch_all(query)
            
            # Attribuer un ordre séquentiel
            for index, collab in enumerate(collaborateurs):
                update_query = "UPDATE collaborateurs SET ordre = ? WHERE id = ?"
                self.db.execute_query(update_query, (index, collab['id']))
            
            print(f"Ordre initialisé pour {len(collaborateurs)} collaborateurs")
        except Exception as e:
            print(f"Erreur lors de l'initialisation de l'ordre: {e}")
    
    def ajouter_collaborateur(self, nom: str, prenom: str, etat: str = "Actif", 
                            date_entree: str = None) -> Optional[int]:
        """
        Ajoute un nouveau collaborateur
        
        Args:
            nom: Nom du collaborateur
            prenom: Prénom du collaborateur
            etat: État du collaborateur ('Actif' ou 'Inactif')
            date_entree: Date d'entrée (format YYYY-MM-DD)
            
        Returns:
            ID du collaborateur créé ou None si erreur
        """
        # Récupérer le prochain ordre
        max_ordre_query = "SELECT MAX(ordre) as max_ordre FROM collaborateurs"
        result = self.db.fetch_one(max_ordre_query)
        nouvel_ordre = (result['max_ordre'] or -1) + 1
        
        # Si le collaborateur est créé directement en Inactif, enregistrer la date
        if etat == "Inactif":
            query = """
                INSERT INTO collaborateurs (nom, prenom, etat, ordre, date_entree, date_inactivation)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            cursor = self.db.execute_query(query, (nom.strip(), prenom.strip(), etat, nouvel_ordre, date_entree))
        else:
            query = """
                INSERT INTO collaborateurs (nom, prenom, etat, ordre, date_entree)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor = self.db.execute_query(query, (nom.strip(), prenom.strip(), etat, nouvel_ordre, date_entree))
        
        if cursor:
            return cursor.lastrowid
        return None
    
    def modifier_collaborateur(self, collaborateur_id: int, nom: str, prenom: str, 
                              etat: str, date_entree: str = None) -> bool:
        """
        Modifie un collaborateur existant
        
        Args:
            collaborateur_id: ID du collaborateur
            nom: Nouveau nom
            prenom: Nouveau prénom
            etat: Nouvel état
            date_entree: Date d'entrée (format YYYY-MM-DD)
            
        Returns:
            True si succès, False sinon
        """
        # Récupère l'état actuel
        current = self.get_collaborateur(collaborateur_id)
        
        # Si le collaborateur passe de 'Actif' à 'Inactif', enregistre la date
        if current and current['etat'] == 'Actif' and etat == 'Inactif':
            query = """
                UPDATE collaborateurs 
                SET nom = ?, prenom = ?, etat = ?, date_entree = ?,
                    date_inactivation = CURRENT_TIMESTAMP,
                    date_modification = CURRENT_TIMESTAMP
                WHERE id = ?
            """
        # Si le collaborateur passe de 'Inactif' à 'Actif', supprime la date d'inactivation
        elif current and current['etat'] == 'Inactif' and etat == 'Actif':
            query = """
                UPDATE collaborateurs 
                SET nom = ?, prenom = ?, etat = ?, date_entree = ?,
                    date_inactivation = NULL,
                    date_modification = CURRENT_TIMESTAMP
                WHERE id = ?
            """
        else:
            # Pas de changement d'état
            query = """
                UPDATE collaborateurs 
                SET nom = ?, prenom = ?, etat = ?, date_entree = ?,
                    date_modification = CURRENT_TIMESTAMP
                WHERE id = ?
            """
        
        cursor = self.db.execute_query(query, (nom.strip(), prenom.strip(), etat, date_entree, collaborateur_id))
        return cursor is not None
    
    def deplacer_collaborateur_haut(self, collaborateur_id: int) -> bool:
        """
        Déplace un collaborateur vers le haut (ordre - 1)
        
        Args:
            collaborateur_id: ID du collaborateur à déplacer
            
        Returns:
            True si succès, False sinon
        """
        # Récupérer le collaborateur actuel
        current = self.get_collaborateur(collaborateur_id)
        if not current:
            return False
        
        ordre_actuel = current.get('ordre', 0)
        
        # Si déjà en premier, ne rien faire
        if ordre_actuel == 0:
            return False
        
        # Trouver le collaborateur juste au-dessus
        query = "SELECT id, ordre FROM collaborateurs WHERE ordre = ? LIMIT 1"
        au_dessus = self.db.fetch_one(query, (ordre_actuel - 1,))
        
        if au_dessus:
            # Échanger les ordres
            self.db.execute_query("UPDATE collaborateurs SET ordre = ? WHERE id = ?", 
                                (ordre_actuel, au_dessus['id']))
            self.db.execute_query("UPDATE collaborateurs SET ordre = ? WHERE id = ?", 
                                (ordre_actuel - 1, collaborateur_id))
            return True
        
        return False
    
    def deplacer_collaborateur_bas(self, collaborateur_id: int) -> bool:
        """
        Déplace un collaborateur vers le bas (ordre + 1)
        
        Args:
            collaborateur_id: ID du collaborateur à déplacer
            
        Returns:
            True si succès, False sinon
        """
        # Récupérer le collaborateur actuel
        current = self.get_collaborateur(collaborateur_id)
        if not current:
            return False
        
        ordre_actuel = current.get('ordre', 0)
        
        # Trouver le collaborateur juste en dessous
        query = "SELECT id, ordre FROM collaborateurs WHERE ordre = ? LIMIT 1"
        en_dessous = self.db.fetch_one(query, (ordre_actuel + 1,))
        
        if en_dessous:
            # Échanger les ordres
            self.db.execute_query("UPDATE collaborateurs SET ordre = ? WHERE id = ?", 
                                (ordre_actuel, en_dessous['id']))
            self.db.execute_query("UPDATE collaborateurs SET ordre = ? WHERE id = ?", 
                                (ordre_actuel + 1, collaborateur_id))
            return True
        
        return False
    
    def supprimer_collaborateur(self, collaborateur_id: int) -> bool:
        """
        Supprime un collaborateur et réorganise les ordres
        
        Args:
            collaborateur_id: ID du collaborateur à supprimer
            
        Returns:
            True si succès, False sinon
        """
        # Récupérer l'ordre du collaborateur à supprimer
        current = self.get_collaborateur(collaborateur_id)
        if not current:
            return False
        
        ordre_supprime = current.get('ordre', 0)
        
        # Supprimer le collaborateur
        query = "DELETE FROM collaborateurs WHERE id = ?"
        cursor = self.db.execute_query(query, (collaborateur_id,))
        
        if cursor:
            # Décaler tous les collaborateurs après celui supprimé
            update_query = "UPDATE collaborateurs SET ordre = ordre - 1 WHERE ordre > ?"
            self.db.execute_query(update_query, (ordre_supprime,))
            return True
        
        return False
    
    def get_collaborateur(self, collaborateur_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un collaborateur par son ID
        
        Args:
            collaborateur_id: ID du collaborateur
            
        Returns:
            Dictionnaire avec les données du collaborateur ou None
        """
        query = "SELECT * FROM collaborateurs WHERE id = ?"
        return self.db.fetch_one(query, (collaborateur_id,))
    
    def get_tous_collaborateurs(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les collaborateurs triés par ordre
        
        Returns:
            Liste des collaborateurs
        """
        query = "SELECT * FROM collaborateurs ORDER BY ordre"
        return self.db.fetch_all(query)
    
    def get_collaborateurs_actifs(self) -> List[Dict[str, Any]]:
        """
        Récupère uniquement les collaborateurs actifs triés par ordre
        
        Returns:
            Liste des collaborateurs actifs
        """
        query = "SELECT * FROM collaborateurs WHERE etat = 'Actif' ORDER BY ordre"
        return self.db.fetch_all(query)
    
    def compter_collaborateurs(self) -> int:
        """
        Compte le nombre total de collaborateurs
        
        Returns:
            Nombre de collaborateurs
        """
        query = "SELECT COUNT(*) as count FROM collaborateurs"
        result = self.db.fetch_one(query)
        return result['count'] if result else 0
    
    def compter_collaborateurs_actifs(self) -> int:
        """
        Compte le nombre de collaborateurs actifs
        
        Returns:
            Nombre de collaborateurs actifs
        """
        query = "SELECT COUNT(*) as count FROM collaborateurs WHERE etat = 'Actif'"
        result = self.db.fetch_one(query)
        return result['count'] if result else 0
