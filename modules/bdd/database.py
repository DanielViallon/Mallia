"""
Gestionnaire de base de données SQLite pour Mallia
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any


class Database:
    """Classe pour gérer la connexion et les opérations sur la base de données"""
    
    def __init__(self, db_path: str = "data/mallia.db"):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données
        """
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        
        # Créer le dossier data s'il n'existe pas
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Se connecter à la base de données
        self.connect()
    
    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
            self.cursor = self.connection.cursor()
            print(f"Connexion établie à la base de données: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Erreur lors de la connexion à la base de données: {e}")
            raise
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            print("Connexion à la base de données fermée")
    
    def execute_query(self, query: str, params: tuple = ()) -> Optional[sqlite3.Cursor]:
        """
        Exécute une requête SQL
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres de la requête
            
        Returns:
            Curseur avec les résultats ou None en cas d'erreur
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor
        except sqlite3.Error as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")
            print(f"Requête: {query}")
            return None
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """
        Exécute une requête SQL plusieurs fois avec différents paramètres
        
        Args:
            query: Requête SQL à exécuter
            params_list: Liste de tuples de paramètres
            
        Returns:
            True si succès, False sinon
        """
        try:
            self.cursor.executemany(query, params_list)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de l'exécution multiple: {e}")
            return False
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Récupère un seul enregistrement
        
        Args:
            query: Requête SQL SELECT
            params: Paramètres de la requête
            
        Returns:
            Dictionnaire avec les données ou None
        """
        cursor = self.execute_query(query, params)
        if cursor:
            row = cursor.fetchone()
            return dict(row) if row else None
        return None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Récupère tous les enregistrements
        
        Args:
            query: Requête SQL SELECT
            params: Paramètres de la requête
            
        Returns:
            Liste de dictionnaires avec les données
        """
        cursor = self.execute_query(query, params)
        if cursor:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        return []
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        Crée une table dans la base de données
        
        Args:
            table_name: Nom de la table
            columns: Dictionnaire {nom_colonne: type_colonne}
            
        Returns:
            True si succès, False sinon
        """
        columns_def = ", ".join([f"{name} {dtype}" for name, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        
        cursor = self.execute_query(query)
        return cursor is not None
    
    def table_exists(self, table_name: str) -> bool:
        """
        Vérifie si une table existe
        
        Args:
            table_name: Nom de la table
            
        Returns:
            True si la table existe, False sinon
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetch_one(query, (table_name,))
        return result is not None
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Récupère les informations sur les colonnes d'une table
        
        Args:
            table_name: Nom de la table
            
        Returns:
            Liste des informations sur les colonnes
        """
        query = f"PRAGMA table_info({table_name})"
        return self.fetch_all(query)
    
    def initialize_database(self):
        """
        Initialise la base de données avec les tables de base
        Cette méthode sera enrichie lors de la création des modules
        """
        print("Initialisation de la base de données...")
        
        # Pour l'instant, on crée juste une table de configuration
        config_columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "key": "TEXT UNIQUE NOT NULL",
            "value": "TEXT",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        
        if self.create_table("config", config_columns):
            print("Table 'config' créée avec succès")
        else:
            print("Erreur lors de la création de la table 'config'")
    
    def __enter__(self):
        """Permet d'utiliser la classe avec 'with'"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme automatiquement la connexion à la sortie du contexte"""
        self.disconnect()