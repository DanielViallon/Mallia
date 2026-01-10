"""
Fonctions utilitaires pour le module Suivis Manager
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
import calendar


def calculer_periodes_mois(mois: int, annee: int) -> List[Tuple[datetime, datetime]]:
    """
    Calcule les périodes d'un mois selon les règles métier
    
    Règles :
    - Si le 1er du mois est un dimanche, commencer le lundi 2
    - Si commence jeudi, vendredi ou samedi : inclut le samedi de la semaine suivante
    - Sinon : première période va jusqu'au samedi de la semaine courante
    - Périodes suivantes : toujours du même jour de départ jusqu'au samedi suivant
    - Dernière période : si se termine lundi/mardi/mercredi, fusionner avec période précédente
    
    Args:
        mois: Numéro du mois (1-12)
        annee: Année (ex: 2025)
        
    Returns:
        Liste de tuples (date_debut, date_fin) pour chaque période
    """
    # Premier et dernier jour du mois
    premier_jour_mois = datetime(annee, mois, 1)
    dernier_jour = datetime(annee, mois, calendar.monthrange(annee, mois)[1])
    
    periodes = []
    
    # Déterminer le premier jour de travail
    jour_semaine_premier = premier_jour_mois.weekday()  # 0=Lundi, 6=Dimanche
    
    # Si dimanche (6), commencer lundi
    if jour_semaine_premier == 6:
        premier_jour_travaille = premier_jour_mois + timedelta(days=1)
    else:
        premier_jour_travaille = premier_jour_mois
    
    # Calculer la première période
    jour_semaine_debut = premier_jour_travaille.weekday()
    
    # Si commence jeudi (3), vendredi (4) ou samedi (5)
    if jour_semaine_debut >= 3:
        # Aller jusqu'au samedi de la semaine suivante
        jours_jusqua_samedi = (5 - jour_semaine_debut) % 7
        if jour_semaine_debut == 5:  # Si samedi
            jours_jusqua_samedi = 7
        else:
            jours_jusqua_samedi = (5 - jour_semaine_debut) + 7
        
        date_fin_periode = premier_jour_travaille + timedelta(days=jours_jusqua_samedi)
    else:
        # Aller jusqu'au samedi de la semaine courante
        jours_jusqua_samedi = 5 - jour_semaine_debut
        date_fin_periode = premier_jour_travaille + timedelta(days=jours_jusqua_samedi)
    
    # S'assurer de ne pas dépasser le dernier jour du mois
    if date_fin_periode > dernier_jour:
        date_fin_periode = dernier_jour
    
    periodes.append((premier_jour_travaille, date_fin_periode))
    
    # Calculer les périodes suivantes
    date_courante = date_fin_periode + timedelta(days=1)
    
    while date_courante <= dernier_jour:
        # Aller jusqu'au samedi (5)
        jours_jusqua_samedi = (5 - date_courante.weekday()) % 7
        if jours_jusqua_samedi == 0:
            jours_jusqua_samedi = 7
        
        date_fin_periode = date_courante + timedelta(days=jours_jusqua_samedi)
        
        # Si on dépasse le dernier jour du mois
        if date_fin_periode > dernier_jour:
            date_fin_periode = dernier_jour
            
            # Vérifier si le dernier jour est lundi (0), mardi (1) ou mercredi (2)
            if dernier_jour.weekday() <= 2 and len(periodes) > 0:
                # Fusionner avec la période précédente
                periodes[-1] = (periodes[-1][0], dernier_jour)
                break
        
        periodes.append((date_courante, date_fin_periode))
        date_courante = date_fin_periode + timedelta(days=1)
    
    return periodes


def formater_periode(date_debut: datetime, date_fin: datetime, premier_jour_travaille: datetime) -> str:
    """
    Formate une période pour l'affichage (cumulatif depuis le début du mois)
    
    Args:
        date_debut: Date de début de la période (non utilisée, gardée pour compatibilité)
        date_fin: Date de fin de la période
        premier_jour_travaille: Premier jour travaillé du mois (le vrai début)
        
    Returns:
        Chaîne formatée "Du X au Y Mois"
    """
    mois_noms = [
        "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]
    
    mois_nom = mois_noms[premier_jour_travaille.month]
    return f"Du {premier_jour_travaille.day} au {date_fin.day} {mois_nom}"


def formater_montant(valeur: float) -> str:
    """
    Formate un montant avec le symbole €
    
    Args:
        valeur: Montant à formater
        
    Returns:
        Chaîne formatée avec €
    """
    if valeur is None:
        return ""
    return f"{valeur:,.2f} €".replace(",", " ")


def formater_pourcentage(valeur: float) -> str:
    """
    Formate un pourcentage avec le symbole %
    
    Args:
        valeur: Pourcentage à formater
        
    Returns:
        Chaîne formatée avec %
    """
    if valeur is None:
        return ""
    return f"{valeur:.2f} %"


def parser_montant(texte: str) -> Optional[float]:
    """
    Parse un montant depuis une chaîne
    
    Args:
        texte: Texte à parser
        
    Returns:
        Valeur numérique ou None
    """
    if not texte or texte.strip() == "":
        return None
    
    # Enlever les espaces, € et autres caractères
    texte_nettoye = texte.replace("€", "").replace(" ", "").strip()
    
    try:
        return float(texte_nettoye)
    except ValueError:
        return None


def parser_pourcentage(texte: str) -> Optional[float]:
    """
    Parse un pourcentage depuis une chaîne
    
    Args:
        texte: Texte à parser
        
    Returns:
        Valeur numérique ou None
    """
    if not texte or texte.strip() == "":
        return None
    
    # Enlever les espaces, % et autres caractères
    texte_nettoye = texte.replace("%", "").replace(" ", "").strip()
    
    try:
        return float(texte_nettoye)
    except ValueError:
        return None


def charger_objectifs(annee: int = None, mois: int = None) -> Dict[str, float]:
    """
    Charge les objectifs depuis la base de données
    
    Args:
        annee: Année (par défaut: année courante)
        mois: Mois (par défaut: mois courant)
    
    Returns:
        Dictionnaire avec les objectifs
    """
    from modules.bdd import Database
    
    # Valeurs par défaut
    if annee is None or mois is None:
        now = datetime.now()
        annee = annee or now.year
        mois = mois or now.month
    
    objectifs = {
        'ca_total': None,
        'ca_jour': None,
        'nb_clients': None,
        'pct_ventes': None,
        'pct_couleurs': None,
        'pct_soins': None
    }
    
    try:
        db = Database()
        query = "SELECT * FROM objectifs_mensuels WHERE annee = ? AND mois = ?"
        result = db.fetch_one(query, (annee, mois))
        
        if result:
            objectifs['ca_total'] = result.get('ca_total')
            objectifs['ca_jour'] = result.get('ca_jour')
            objectifs['nb_clients'] = float(result.get('nb_clients')) if result.get('nb_clients') else None
            objectifs['pct_ventes'] = result.get('pct_ventes')
            objectifs['pct_couleurs'] = result.get('pct_couleurs')
            objectifs['pct_soins'] = result.get('pct_soins')
    except Exception as e:
        print(f"Erreur lors du chargement des objectifs: {e}")
    
    return objectifs


def charger_info_salon() -> Dict[str, str]:
    """
    Charge les informations du salon depuis config.ini
    
    Returns:
        Dictionnaire avec nom et ville
    """
    import configparser
    from pathlib import Path
    
    config = configparser.ConfigParser()
    config_path = Path("config.ini")
    
    info = {
        'nom': '',
        'ville': ''
    }
    
    if config_path.exists():
        config.read(config_path, encoding='utf-8')
        
        if config.has_section('Salon'):
            info['nom'] = config.get('Salon', 'nom', fallback='').strip()
            info['ville'] = config.get('Salon', 'ville', fallback='').strip()
    
    return info


def nettoyer_nom_fichier(texte: str) -> str:
    """
    Nettoie un texte pour qu'il soit valide comme nom de fichier
    
    Args:
        texte: Texte à nettoyer
        
    Returns:
        Texte nettoyé
    """
    import re
    
    # Remplacements spécifiques
    replacements = {
        '&': 'and',
        'é': 'e',
        'è': 'e',
        'ê': 'e',
        'ë': 'e',
        'à': 'a',
        'â': 'a',
        'ä': 'a',
        'ù': 'u',
        'û': 'u',
        'ü': 'u',
        'ï': 'i',
        'î': 'i',
        'ô': 'o',
        'ö': 'o',
        'ç': 'c',
        'É': 'E',
        'È': 'E',
        'Ê': 'E',
        'Ë': 'E',
        'À': 'A',
        'Â': 'A',
        'Ä': 'A',
        'Ù': 'U',
        'Û': 'U',
        'Ü': 'U',
        'Ï': 'I',
        'Î': 'I',
        'Ô': 'O',
        'Ö': 'O',
        'Ç': 'C'
    }
    
    for old, new in replacements.items():
        texte = texte.replace(old, new)
    
    # Supprimer les caractères invalides pour un nom de fichier
    texte = re.sub(r'[<>:"/\\|?*]', '', texte)
    
    return texte.strip()