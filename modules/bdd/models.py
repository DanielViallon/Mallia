"""
Modèles de données pour la base de données
Ce fichier sera enrichi au fur et à mesure du développement des modules
"""

from typing import Dict, Any, Optional
from datetime import datetime


class BaseModel:
    """Classe de base pour tous les modèles"""
    
    def __init__(self, **kwargs):
        """
        Initialise le modèle avec les données fournies
        
        Args:
            **kwargs: Données du modèle
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le modèle en dictionnaire
        
        Returns:
            Dictionnaire représentant le modèle
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Crée une instance du modèle depuis un dictionnaire
        
        Args:
            data: Dictionnaire de données
            
        Returns:
            Instance du modèle
        """
        return cls(**data)


class ConfigModel(BaseModel):
    """Modèle pour la table config"""
    
    def __init__(self, id: Optional[int] = None, key: str = "", value: str = "",
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.key = key
        self.value = value
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def __repr__(self):
        return f"ConfigModel(id={self.id}, key='{self.key}', value='{self.value}')"


# Les autres modèles seront ajoutés ici au fur et à mesure
# du développement des modules (Utilisateurs, Collaborateurs, Planning, etc.)