# ============================================================
#  pipeline.py — Pipeline principal de data marketing
#  Projet Huile d'Olive — MSc2 INSEEC 2026
#
#  Ce script :
#  1. Charge les données depuis MySQL
#  2. Enrichit les pays via l'API REST Countries
#  3. Calcule l'algorithme RFM (Récence / Fréquence / Montant)
#  4. Segmente les clients en Gold / Silver / Bronze
#  5. Détecte les clients à risque (inactifs)
#  6. Écrit les résultats dans une nouvelle table MySQL
# ============================================================

import pandas as pd
import numpy as np
from datetime import datetime, date
from db import run_query, execute_many, execute_write, create_table_if_not_exists
from api import get_all_client_countries, get_all_producer_countries


# Date de référence pour le calcul de récence
# On utilise la fin de l'année 2024 (dernière date des données)
DATE_REFERENCE = date(2024, 12, 31)


# ============================================================
# ÉTAPE 1 — CHARGEMENT DES DONNÉES DEPUIS MYSQL
# ============================================================

def load_clients() -> pd.DataFrame:
    """
    Charge tous les clients depuis MySQL.

    Returns:
        pd.DataFrame : table clients complète
    """
    query = "SELECT * FROM clients"
    df = run_query(query)
    print(f"📋 {len(df)} clients chargés.")
    return df


def load_commandes() -> pd.DataFrame:
    """
    Charge toutes les commandes non annulées avec le détail client.

    Returns:
        pd.DataFrame : commandes enrichies avec infos client
    """
    query = """
        SELECT
            o.id_commande,
            o.id_client,
            c.nom_societe,
            c.pays_client,
            c.type_client,
            c.segment       AS segment_actuel,
            o.date_commande,
            o.montant_total,
            o.statut,
            o.pays_livraison
        FROM commandes o
        INNER JOIN clients c ON o.id_client = c.id_client
        WHERE o.statut != 'Annulée'
    """
    df = run_query(query)
    # Convertit la colonne date en type datetime
    df["date_commande"] = pd.to_datetime(df["date_commande"])
    print(f"📦 {len(df)} commandes chargées.")
    return df


def load_produits_vendus() -> pd.DataFrame:
    """
    Charge le détail des produits vendus (jointure 3 tables).

    Returns:
        pd.DataFrame : détail produits par commande
    """
    query = """
        SELECT
            cp.id_commande,
            cp.id_produit,
            p.nom_produit,
            p.type_huile,
            pp.nom_pays     AS pays_origine,
            cp.quantite_litres,
            cp.prix_unitaire,
            (cp.quantite_litres * cp.prix_unitaire) AS total_ligne
        FROM commande_produit cp
        INNER JOIN produits p            ON cp.id_produit    = p.id_produit
        INNER JOIN producteurs pr        ON p.id_producteur  = pr.id_producteur
        INNER JOIN pays_producteurs pp   ON pr.id_pays       = pp.id_pays
    """
    df = run_query(query)
    print(f"🫒 {len(df)} lignes de produits vendus chargées.")
    return df


def load_pays_producteurs() -> pd.DataFrame:
    """
    Charge les pays producteurs depuis MySQL.

    Returns:
        pd.DataFrame : table pays_producteurs
    """
    return run_query("SELECT * FROM pays_producteurs")


# ============================================================
# ÉTAPE 2 — ENRICHISSEMENT VIA API
# ============================================================

def enrich_with_api(df_clients: pd.DataFrame,
                    df_pays: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Enrichit les clients et pays producteurs avec l'API REST Countries.
    Ajoute : devise, capitale, population, région géographique.

    Args:
        df_clients : DataFrame des clients
        df_pays    : DataFrame des pays producteurs

    Returns:
        tuple : (df_clients_enrichi, df_pays_enrichi)
    """
    print("\n🌍 === Enrichissement API REST Countries ===")

    # Enrichissement des pays clients
    df_pays_clients = get_all_client_countries(df_clients)
    df_clients_enrichi = df_clients.merge(
        df_pays_clients[["nom_pays_bdd", "devise_code", "capitale",
                          "region_api", "population"]],
        left_on  = "pays_client",
        right_on = "nom_pays_bdd",
        how      = "left"
    ).drop(columns=["nom_pays_bdd"])

    # Enrichissement des pays producteurs
    df_pays_enrichi_api = get_all_producer_countries(df_pays)
    df_pays_enrichi = df_pays.merge(
        df_pays_enrichi_api[["nom_pays_bdd", "devise_code", "capitale", "population"]],
        left_on  = "nom_pays",
        right_on = "nom_pays_bdd",
        how      = "left"
    ).drop(columns=["nom_pays_bdd"])

    print("✅ Enrichissement API terminé.")
    return df_clients_enrichi, df_pays_enrichi


# ============================================================
# ÉTAPE 3 — ALGORITHME RFM
# ============================================================

def calculer_rfm(df_commandes: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les métriques RFM pour chaque client.

    RFM = Récence / Fréquence / Montant
    - Récence  : nombre de jours depuis le dernier achat (moins = mieux)
    - Fréquence : nombre total de commandes
    - Montant  : chiffre d'affaires total généré

    Args:
        df_commandes : DataFrame des commandes avec date_commande et montant_total

    Returns:
        pd.DataFrame : une ligne par client avec ses métriques RFM
    """
    print("\n📊 === Calcul RFM ===")

    # Agrégation par client
    rfm = df_commandes.groupby(
        ["id_client", "nom_societe", "pays_client", "type_client"]
    ).agg(
        derniere_commande = ("date_commande", "max"),
        frequence         = ("id_commande", "count"),
        valeur_totale     = ("montant_total", "sum"),
        panier_moyen      = ("montant_total", "mean"),
        nb_pays_livraison = ("pays_livraison", "nunique")
    ).reset_index()

    # Calcul de la récence en jours
    rfm["recence_jours"] = (
        pd.Timestamp(DATE_REFERENCE) - rfm["derniere_commande"]
    ).dt.days

    # Arrondi du panier moyen
    rfm["valeur_totale"] = rfm["valeur_totale"].round(2)
    rfm["panier_moyen"]  = rfm["panier_moyen"].round(2)

    print(f"  ✅ RFM calculé pour {len(rfm)} clients.")
    return rfm


def scorer_rfm(df_rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Attribue un score R, F et M à chaque client (échelle 1 à 3).
    Puis calcule le score total et le segment final.

    Règles de scoring :
        Score R (Récence)  : 3 = < 30j, 2 = 30-90j, 1 = > 90j
        Score F (Fréquence): 3 = ≥ 4 cmd, 2 = 2-3 cmd, 1 = 1 cmd
        Score M (Montant)  : 3 = ≥ 10000€, 2 = 3000-9999€, 1 = < 3000€

    Args:
        df_rfm : DataFrame issu de calculer_rfm()

    Returns:
        pd.DataFrame enrichi avec les scores et le segment RFM
    """
    df = df_rfm.copy()

    # Score R — Récence (plus récent = meilleur score)
    df["score_r"] = np.where(df["recence_jours"] <= 30,  3,
                    np.where(df["recence_jours"] <= 90,  2, 1))

    # Score F — Fréquence
    df["score_f"] = np.where(df["frequence"] >= 4, 3,
                    np.where(df["frequence"] >= 2, 2, 1))

    # Score M — Montant
    df["score_m"] = np.where(df["valeur_totale"] >= 10000, 3,
                    np.where(df["valeur_totale"] >= 3000,  2, 1))

    # Score total RFM (max = 9, min = 3)
    df["score_rfm"] = df["score_r"] + df["score_f"] + df["score_m"]

    # Segmentation finale
    df["segment_rfm"] = np.where(df["score_rfm"] >= 8, "Gold",
                        np.where(df["score_rfm"] >= 5, "Silver", "Bronze"))

    # Détection des clients à risque (inactifs depuis > 180 jours)
    df["client_a_risque"] = df["recence_jours"] > 180

    print(f"\n  🏆 Répartition des segments :")
    print(df["segment_rfm"].value_counts().to_string())
    print(f"\n  ⚠️  Clients à risque : {df['client_a_risque'].sum()}")

    return df


# ============================================================
# ÉTAPE 4 — ANALYSES COMPLÉMENTAIRES PANDAS
# ============================================================

def analyser_ventes_par_type(df_produits: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse le CA et les volumes vendus par type d'huile.

    Args:
        df_produits : DataFrame du détail produits vendus

    Returns:
        pd.DataFrame : synthèse par type d'huile
    """
    analyse = df_produits.groupby("type_huile").agg(
        litres_vendus  = ("quantite_litres", "sum"),
        ca_total       = ("total_ligne", "sum"),
        nb_commandes   = ("id_commande", "nunique"),
        prix_moy_litre = ("prix_unitaire", "mean")
    ).reset_index()

    analyse["ca_total"]       = analyse["ca_total"].round(2)
    analyse["prix_moy_litre"] = analyse["prix_moy_litre"].round(2)
    analyse = analyse.sort_values("ca_total", ascending=False)

    print("\n📈 Ventes par type d'huile :")
    print(analyse.to_string(index=False))
    return analyse


def analyser_ca_par_pays_origine(df_produits: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse le CA généré par pays producteur (origine des huiles).

    Args:
        df_produits : DataFrame du détail produits vendus

    Returns:
        pd.DataFrame : CA par pays d'origine, trié décroissant
    """
    analyse = df_produits.groupby("pays_origine").agg(
        litres_vendus = ("quantite_litres", "sum"),
        ca_total      = ("total_ligne", "sum"),
        nb_produits   = ("id_produit", "nunique")
    ).reset_index()

    analyse["ca_total"] = analyse["ca_total"].round(2)
    analyse = analyse.sort_values("ca_total", ascending=False)

    print("\n🌍 CA par pays d'origine :")
    print(analyse.head(10).to_string(index=False))
    return analyse


# ============================================================
# ÉTAPE 5 — ÉCRITURE DES RÉSULTATS DANS MYSQL
# ============================================================

def creer_table_rfm_resultats() -> None:
    """
    Crée la table rfm_resultats dans MySQL si elle n'existe pas.
    Cette table stocke les scores RFM calculés par Python.
    """
    sql = """
        CREATE TABLE IF NOT EXISTS rfm_resultats (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            id_client        INT          NOT NULL,
            nom_societe      VARCHAR(150),
            pays_client      VARCHAR(100),
            type_client      VARCHAR(50),
            recence_jours    INT,
            frequence        INT,
            valeur_totale    DECIMAL(10,2),
            panier_moyen     DECIMAL(10,2),
            score_r          INT,
            score_f          INT,
            score_m          INT,
            score_rfm        INT,
            segment_rfm      VARCHAR(20),
            client_a_risque  TINYINT(1),
            date_calcul      DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_client (id_client)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    create_table_if_not_exists(sql)
    print("✅ Table rfm_resultats prête.")


def sauvegarder_rfm(df_rfm_scores: pd.DataFrame) -> None:
    """
    Sauvegarde les résultats RFM dans la table MySQL rfm_resultats.
    Utilise INSERT ... ON DUPLICATE KEY UPDATE pour gérer les relances.

    Args:
        df_rfm_scores : DataFrame avec les scores RFM calculés
    """
    creer_table_rfm_resultats()

    # Vide la table avant réinsertion (pour une analyse fraîche)
    execute_write("DELETE FROM rfm_resultats")

    # Prépare les données à insérer
    colonnes = [
        "id_client", "nom_societe", "pays_client", "type_client",
        "recence_jours", "frequence", "valeur_totale", "panier_moyen",
        "score_r", "score_f", "score_m", "score_rfm",
        "segment_rfm", "client_a_risque"
    ]

    data = [
        tuple(
            bool(row["client_a_risque"]) if col == "client_a_risque"
            else row[col]
            for col in colonnes
        )
        for _, row in df_rfm_scores.iterrows()
    ]

    query = f"""
        INSERT INTO rfm_resultats
            ({', '.join(colonnes)})
        VALUES
            ({', '.join(['%s'] * len(colonnes))})
    """

    nb = execute_many(query, data)
    print(f"💾 {nb} résultats RFM sauvegardés dans MySQL.")


def mettre_a_jour_segments_clients(df_rfm_scores: pd.DataFrame) -> None:
    """
    Met à jour le champ 'segment' dans la table clients
    avec les segments calculés par l'algorithme RFM.

    Args:
        df_rfm_scores : DataFrame avec colonnes id_client et segment_rfm
    """
    print("\n🔄 Mise à jour des segments clients...")

    data = [
        (row["segment_rfm"], int(row["id_client"]))
        for _, row in df_rfm_scores.iterrows()
    ]

    query = "UPDATE clients SET segment = %s WHERE id_client = %s"

    for segment, id_client in data:
        execute_write(query, (segment, id_client))

    print(f"✅ Segments mis à jour pour {len(data)} clients.")


# ============================================================
# PIPELINE PRINCIPAL — orchestre toutes les étapes
# ============================================================

def run_pipeline() -> None:
    """
    Lance le pipeline complet dans l'ordre :
    1. Chargement MySQL
    2. Enrichissement API
    3. Calcul RFM
    4. Analyses complémentaires
    5. Sauvegarde MySQL
    """
    print("=" * 60)
    print("  🫒 PIPELINE DATA MARKETING — HUILE D'OLIVE")
    print(f"  Date de référence : {DATE_REFERENCE}")
    print("=" * 60)

    # ── 1. Chargement ─────────────────────────────────────────
    print("\n📥 ÉTAPE 1 — Chargement des données MySQL")
    df_clients      = load_clients()
    df_commandes    = load_commandes()
    df_produits     = load_produits_vendus()
    df_pays         = load_pays_producteurs()

    # ── 2. Enrichissement API ─────────────────────────────────
    print("\n🌍 ÉTAPE 2 — Enrichissement via REST Countries API")
    df_clients_enrichi, df_pays_enrichi = enrich_with_api(df_clients, df_pays)

    # Affiche un aperçu de l'enrichissement
    print("\nAperçu clients enrichis :")
    print(df_clients_enrichi[
        ["nom_societe", "pays_client", "devise_code", "population"]
    ].head(5).to_string(index=False))

    # ── 3. Calcul RFM ─────────────────────────────────────────
    print("\n📊 ÉTAPE 3 — Calcul algorithme RFM")
    df_rfm       = calculer_rfm(df_commandes)
    df_rfm_score = scorer_rfm(df_rfm)

    # ── 4. Analyses pandas ────────────────────────────────────
    print("\n📈 ÉTAPE 4 — Analyses complémentaires")
    df_ventes_type   = analyser_ventes_par_type(df_produits)
    df_ca_origine    = analyser_ca_par_pays_origine(df_produits)

    # ── 5. Sauvegarde MySQL ───────────────────────────────────
    print("\n💾 ÉTAPE 5 — Sauvegarde dans MySQL")
    sauvegarder_rfm(df_rfm_score)
    mettre_a_jour_segments_clients(df_rfm_score)

    # ── Résumé final ──────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✅ PIPELINE TERMINÉ AVEC SUCCÈS")
    print("=" * 60)
    print(f"\n  Clients analysés  : {len(df_rfm_score)}")
    print(f"  Commandes traitées: {len(df_commandes)}")
    print(f"  Gold              : {(df_rfm_score['segment_rfm'] == 'Gold').sum()}")
    print(f"  Silver            : {(df_rfm_score['segment_rfm'] == 'Silver').sum()}")
    print(f"  Bronze            : {(df_rfm_score['segment_rfm'] == 'Bronze').sum()}")
    print(f"  Clients à risque  : {df_rfm_score['client_a_risque'].sum()}")
    print(f"\n  📊 Les résultats sont dans la table : rfm_resultats")
    print(f"  🎛️  Lance maintenant : python dashboard/app.py")


# ── Point d'entrée ─────────────────────────────────────────────
if __name__ == "__main__":
    run_pipeline()
