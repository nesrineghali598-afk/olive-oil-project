# ============================================================
#  api.py — Enrichissement via API externe
#  API utilisée : REST Countries (https://restcountries.com)
#  Complètement gratuite, sans clé API, sans inscription
#  Enrichit les données avec : devise, capitale, population,
#  langue officielle, région géographique
# ============================================================

import requests
import pandas as pd
import time
from typing import Optional

# URL de base de l'API REST Countries
API_BASE_URL = "https://restcountries.com/v3.1"

# Mapping nom pays (notre BDD) → code ISO 2 lettres
# Nécessaire car l'API utilise les noms anglais ou codes ISO
PAYS_TO_ISO = {
    "Espagne":           "ES",
    "Italie":            "IT",
    "Grèce":             "GR",
    "Portugal":          "PT",
    "Tunisie":           "TN",
    "Turquie":           "TR",
    "Maroc":             "MA",
    "Syrie":             "SY",
    "Algérie":           "DZ",
    "Jordanie":          "JO",
    "Argentine":         "AR",
    "Chili":             "CL",
    "Croatie":           "HR",
    "Chypre":            "CY",
    "France":            "FR",
    "Albanie":           "AL",
    "Égypte":            "EG",
    "Libye":             "LY",
    "Liban":             "LB",
    "Israël":            "IL",
    "Palestine":         "PS",
    "Iran":              "IR",
    "USA":               "US",
    "Mexique":           "MX",
    "Pérou":             "PE",
    "Australie":         "AU",
    "Nouvelle-Zélande":  "NZ",
    "Afrique du Sud":    "ZA",
    "Chine":             "CN",
    "Inde":              "IN",
    # Pays clients supplémentaires
    "Allemagne":         "DE",
    "Royaume-Uni":       "GB",
    "États-Unis":        "US",
    "Japon":             "JP",
    "Suède":             "SE",
    "Canada":            "CA",
    "Pays-Bas":          "NL",
    "Belgique":          "BE",
    "Suisse":            "CH",
    "Émirats":           "AE",
    "Singapour":         "SG",
    "Corée du Sud":      "KR",
    "Brésil":            "BR",
    "Italie":            "IT",
}


def get_country_info(iso_code: str) -> Optional[dict]:
    """
    Récupère les informations d'un pays via l'API REST Countries.

    Args:
        iso_code : code ISO 2 lettres du pays (ex: 'FR', 'ES')

    Returns:
        dict avec les infos du pays, ou None si erreur

    Example:
        info = get_country_info('FR')
        # {'nom_anglais': 'France', 'capitale': 'Paris',
        #  'devise': 'EUR', 'population': 67391582, ...}
    """
    try:
        url = f"{API_BASE_URL}/alpha/{iso_code}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # lève une exception si status != 200

        data = response.json()[0]

        # Extraction des champs utiles
        # Devise : on prend la première devise disponible
        currencies = data.get("currencies", {})
        devise_code = list(currencies.keys())[0] if currencies else "N/A"
        devise_nom  = currencies.get(devise_code, {}).get("name", "N/A") if currencies else "N/A"

        # Langue officielle : on prend la première
        languages = data.get("languages", {})
        langue = list(languages.values())[0] if languages else "N/A"

        return {
            "iso_code"   : iso_code,
            "nom_anglais": data.get("name", {}).get("common", "N/A"),
            "capitale"   : data.get("capital", ["N/A"])[0] if data.get("capital") else "N/A",
            "region_api" : data.get("region", "N/A"),
            "sous_region": data.get("subregion", "N/A"),
            "population" : data.get("population", 0),
            "devise_code": devise_code,
            "devise_nom" : devise_nom,
            "langue"     : langue,
        }

    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout pour le pays {iso_code}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur API pour {iso_code} : {e}")
        return None

    except (KeyError, IndexError) as e:
        print(f"⚠️  Données manquantes pour {iso_code} : {e}")
        return None


def enrich_countries(pays_list: list) -> pd.DataFrame:
    """
    Enrichit une liste de noms de pays avec les données de l'API.
    Appelle get_country_info() pour chaque pays avec une pause
    de 0.3s entre chaque appel pour ne pas surcharger l'API.

    Args:
        pays_list : liste de noms de pays (en français, selon notre BDD)

    Returns:
        pd.DataFrame avec les infos enrichies pour chaque pays

    Example:
        df = enrich_countries(['France', 'Espagne', 'Italie'])
    """
    results = []
    total = len(pays_list)

    print(f"🌍 Enrichissement de {total} pays via REST Countries API...")

    for i, pays in enumerate(pays_list, 1):
        iso = PAYS_TO_ISO.get(pays)

        if not iso:
            print(f"  [{i}/{total}] ⚠️  Pas de code ISO pour : {pays} — ignoré")
            results.append({
                "nom_pays_bdd": pays,
                "iso_code"    : None,
                "nom_anglais" : pays,
                "capitale"    : "N/A",
                "region_api"  : "N/A",
                "sous_region" : "N/A",
                "population"  : 0,
                "devise_code" : "N/A",
                "devise_nom"  : "N/A",
                "langue"      : "N/A",
            })
            continue

        info = get_country_info(iso)

        if info:
            info["nom_pays_bdd"] = pays
            results.append(info)
            print(f"  [{i}/{total}] ✅ {pays} → {info['capitale']} | {info['devise_code']} | pop. {info['population']:,}")
        else:
            results.append({
                "nom_pays_bdd": pays,
                "iso_code"    : iso,
                "nom_anglais" : pays,
                "capitale"    : "N/A",
                "region_api"  : "N/A",
                "sous_region" : "N/A",
                "population"  : 0,
                "devise_code" : "N/A",
                "devise_nom"  : "N/A",
                "langue"      : "N/A",
            })

        # Pause entre les appels API (bonne pratique)
        time.sleep(0.3)

    df = pd.DataFrame(results)
    print(f"\n✅ Enrichissement terminé : {len(df)} pays traités.")
    return df


def get_all_client_countries(df_clients: pd.DataFrame) -> pd.DataFrame:
    """
    Récupère les infos API pour tous les pays clients uniques.

    Args:
        df_clients : DataFrame des clients avec colonne 'pays_client'

    Returns:
        pd.DataFrame avec les données enrichies par pays
    """
    pays_uniques = df_clients["pays_client"].unique().tolist()
    print(f"📦 {len(pays_uniques)} pays clients uniques trouvés.")
    return enrich_countries(pays_uniques)


def get_all_producer_countries(df_pays: pd.DataFrame) -> pd.DataFrame:
    """
    Récupère les infos API pour tous les pays producteurs.

    Args:
        df_pays : DataFrame des pays producteurs avec colonne 'nom_pays'

    Returns:
        pd.DataFrame avec les données enrichies
    """
    pays_list = df_pays["nom_pays"].tolist()
    print(f"🫒 {len(pays_list)} pays producteurs à enrichir.")
    return enrich_countries(pays_list)


# ── Test si on exécute ce fichier directement ──────────────────
if __name__ == "__main__":
    print("=== Test API REST Countries ===\n")

    # Test sur quelques pays clés du projet
    test_pays = ["France", "Espagne", "Tunisie", "Japon", "États-Unis"]
    df_test = enrich_countries(test_pays)

    print("\n=== Résultat ===")
    print(df_test[["nom_pays_bdd", "capitale", "devise_code", "population"]].to_string())
