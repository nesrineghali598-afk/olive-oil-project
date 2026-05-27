-- ============================================================
--  queries.sql — Requêtes SQL 
--  Projet Huile d'Olive — MSc2 INSEEC 2026
-- ============================================================

USE olive_oil_db;

-- ============================================================
-- REQUÊTE 1 — WHERE + ORDER BY + LIMIT
-- Top 10 des produits Extra Vierge les moins acides (qualité max)
-- ============================================================
SELECT
    p.nom_produit,
    pr.nom_domaine          AS producteur,
    pp.nom_pays             AS pays_origine,
    p.acidite               AS taux_acidite,
    p.prix_litre            AS prix_euro_litre,
    p.appellation
FROM produits p
INNER JOIN producteurs pr ON p.id_producteur = pr.id_producteur
INNER JOIN pays_producteurs pp ON pr.id_pays = pp.id_pays
WHERE p.type_huile = 'Extra Vierge'
  AND p.acidite < 0.30
  AND p.annee_recolte = 2024
ORDER BY p.acidite ASC
LIMIT 10;

-- ============================================================
-- REQUÊTE 2 — GROUP BY + ORDER BY + LIMIT
-- Chiffre d'affaires total par pays client (top 10)
-- ============================================================
SELECT
    c.pays_client,
    COUNT(DISTINCT c.id_client)   AS nb_clients,
    COUNT(o.id_commande)          AS nb_commandes,
    SUM(o.montant_total)          AS ca_total,
    AVG(o.montant_total)          AS panier_moyen,
    MAX(o.date_commande)          AS derniere_commande
FROM clients c
INNER JOIN commandes o ON c.id_client = o.id_client
WHERE o.statut != 'Annulée'
GROUP BY c.pays_client
ORDER BY ca_total DESC
LIMIT 10;

-- ============================================================
-- REQUÊTE 3 — GROUP BY + HAVING
-- Clients avec au moins 3 commandes ET CA > 5000€
-- (clients fidèles et à forte valeur)
-- ============================================================
SELECT
    c.nom_societe,
    c.pays_client,
    c.type_client,
    COUNT(o.id_commande)   AS nb_commandes,
    SUM(o.montant_total)   AS ca_total,
    AVG(o.montant_total)   AS panier_moyen
FROM clients c
INNER JOIN commandes o ON c.id_client = o.id_client
WHERE o.statut IN ('Livrée', 'Expédiée', 'En cours')
GROUP BY c.id_client, c.nom_societe, c.pays_client, c.type_client
HAVING COUNT(o.id_commande) >= 3
   AND SUM(o.montant_total) > 5000
ORDER BY ca_total DESC;

-- ============================================================
-- REQUÊTE 4 — WHERE avec BETWEEN + filtre date
-- Commandes passées au 1er semestre 2024 entre 1000€ et 10000€
-- ============================================================
SELECT
    o.id_commande,
    c.nom_societe,
    c.pays_client,
    o.date_commande,
    o.montant_total,
    o.statut
FROM commandes o
INNER JOIN clients c ON o.id_client = c.id_client
WHERE o.montant_total BETWEEN 1000 AND 10000
  AND o.date_commande BETWEEN '2024-01-01' AND '2024-06-30'
ORDER BY o.date_commande ASC;

-- ============================================================
-- REQUÊTE 5 — GROUP BY + HAVING + ORDER BY
-- Analyse des ventes par type d'huile
-- ============================================================
SELECT
    p.type_huile,
    COUNT(DISTINCT p.id_produit)      AS nb_produits,
    SUM(cp.quantite_litres)           AS litres_vendus,
    ROUND(AVG(p.prix_litre), 2)       AS prix_moyen_litre,
    ROUND(SUM(cp.quantite_litres * cp.prix_unitaire), 2) AS ca_type
FROM produits p
INNER JOIN commande_produit cp ON p.id_produit = cp.id_produit
GROUP BY p.type_huile
HAVING SUM(cp.quantite_litres) > 100
ORDER BY ca_type DESC;

-- ============================================================
-- REQUÊTE 6 — JOINTURE SUR 3 TABLES (obligatoire)
-- Détail complet : client + commande + produit + producteur
-- ============================================================
SELECT
    c.nom_societe                              AS client,
    c.pays_client,
    o.date_commande,
    p.nom_produit,
    pp.nom_domaine                             AS producteur,
    pays.nom_pays                              AS pays_origine,
    cp.quantite_litres,
    cp.prix_unitaire,
    ROUND(cp.quantite_litres * cp.prix_unitaire, 2) AS total_ligne
FROM commandes o
INNER JOIN clients c             ON o.id_client      = c.id_client
INNER JOIN commande_produit cp   ON o.id_commande    = cp.id_commande
INNER JOIN produits p            ON cp.id_produit    = p.id_produit
INNER JOIN producteurs pp        ON p.id_producteur  = pp.id_producteur
INNER JOIN pays_producteurs pays ON pp.id_pays       = pays.id_pays
WHERE o.statut = 'Livrée'
  AND p.type_huile = 'Extra Vierge'
ORDER BY o.date_commande DESC
LIMIT 50;

-- ============================================================
-- REQUÊTE 7 — CTE (WITH) : Analyse RFM complète (obligatoire)
-- Récence / Fréquence / Montant par client
-- ============================================================
WITH rfm_base AS (
    -- Étape 1 : calcul des 3 métriques RFM brutes
    SELECT
        c.id_client,
        c.nom_societe,
        c.pays_client,
        c.type_client,
        DATEDIFF('2024-12-31', MAX(o.date_commande))  AS recence_jours,
        COUNT(o.id_commande)                          AS frequence,
        SUM(o.montant_total)                          AS valeur_totale,
        AVG(o.montant_total)                          AS panier_moyen
    FROM clients c
    INNER JOIN commandes o ON c.id_client = o.id_client
    WHERE o.statut != 'Annulée'
    GROUP BY c.id_client, c.nom_societe, c.pays_client, c.type_client
),
rfm_scores AS (
    -- Étape 2 : attribution des scores R, F, M (1 à 3)
    SELECT *,
        CASE
            WHEN recence_jours <= 30  THEN 3
            WHEN recence_jours <= 90  THEN 2
            ELSE 1
        END AS score_r,
        CASE
            WHEN frequence >= 4 THEN 3
            WHEN frequence >= 2 THEN 2
            ELSE 1
        END AS score_f,
        CASE
            WHEN valeur_totale >= 10000 THEN 3
            WHEN valeur_totale >= 3000  THEN 2
            ELSE 1
        END AS score_m
    FROM rfm_base
)
-- Étape 3 : score total et segment final
SELECT
    id_client,
    nom_societe,
    pays_client,
    type_client,
    recence_jours,
    frequence,
    ROUND(valeur_totale, 2)       AS valeur_totale,
    ROUND(panier_moyen, 2)        AS panier_moyen,
    score_r,
    score_f,
    score_m,
    (score_r + score_f + score_m) AS score_rfm_total,
    CASE
        WHEN (score_r + score_f + score_m) >= 8 THEN 'Gold'
        WHEN (score_r + score_f + score_m) >= 5 THEN 'Silver'
        ELSE 'Bronze'
    END AS segment_rfm
FROM rfm_scores
ORDER BY score_rfm_total DESC;

-- ============================================================
-- REQUÊTE 8 — SOUS-REQUÊTE (obligatoire)
-- Produits dont le prix est supérieur à la moyenne du catalogue
-- ============================================================
SELECT
    p.nom_produit,
    p.type_huile,
    p.prix_litre,
    pr.nom_domaine    AS producteur,
    pp.nom_pays       AS pays
FROM produits p
INNER JOIN producteurs pr ON p.id_producteur = pr.id_producteur
INNER JOIN pays_producteurs pp ON pr.id_pays = pp.id_pays
WHERE p.prix_litre > (
    SELECT AVG(prix_litre) FROM produits
)
ORDER BY p.prix_litre DESC;

-- ============================================================
-- CREATE VIEW — vue_rfm (obligatoire)
-- Vue réutilisable par Python pour le dashboard
-- ============================================================
DROP VIEW IF EXISTS vue_rfm;

CREATE VIEW vue_rfm AS
SELECT
    c.id_client,
    c.nom_societe,
    c.pays_client,
    c.type_client,
    c.segment                                         AS segment_actuel,
    COUNT(o.id_commande)                              AS frequence,
    ROUND(SUM(o.montant_total), 2)                    AS valeur_totale,
    ROUND(AVG(o.montant_total), 2)                    AS panier_moyen,
    MAX(o.date_commande)                              AS derniere_commande,
    DATEDIFF('2024-12-31', MAX(o.date_commande))      AS recence_jours,
    CASE
        WHEN DATEDIFF('2024-12-31', MAX(o.date_commande)) <= 30  THEN 3
        WHEN DATEDIFF('2024-12-31', MAX(o.date_commande)) <= 90  THEN 2
        ELSE 1
    END AS score_r,
    CASE
        WHEN COUNT(o.id_commande) >= 4 THEN 3
        WHEN COUNT(o.id_commande) >= 2 THEN 2
        ELSE 1
    END AS score_f,
    CASE
        WHEN SUM(o.montant_total) >= 10000 THEN 3
        WHEN SUM(o.montant_total) >= 3000  THEN 2
        ELSE 1
    END AS score_m
FROM clients c
LEFT JOIN commandes o ON c.id_client = o.id_client
    AND o.statut != 'Annulée'
GROUP BY c.id_client, c.nom_societe, c.pays_client, c.type_client, c.segment;

-- Test de la vue :
SELECT * FROM vue_rfm ORDER BY valeur_totale DESC;

-- ============================================================
-- PROCÉDURE STOCKÉE (obligatoire)
-- Met à jour le segment RFM de tous les clients automatiquement
-- ============================================================
DROP PROCEDURE IF EXISTS maj_segments_rfm;

DELIMITER $$

CREATE PROCEDURE maj_segments_rfm()
BEGIN
    -- Déclare un compteur pour afficher le résultat
    DECLARE nb_gold   INT DEFAULT 0;
    DECLARE nb_silver INT DEFAULT 0;
    DECLARE nb_bronze INT DEFAULT 0;

    -- Met à jour les segments Gold
    UPDATE clients c
    INNER JOIN vue_rfm v ON c.id_client = v.id_client
    SET c.segment = 'Gold'
    WHERE (v.score_r + v.score_f + v.score_m) >= 8;

    SET nb_gold = ROW_COUNT();

    -- Met à jour les segments Silver
    UPDATE clients c
    INNER JOIN vue_rfm v ON c.id_client = v.id_client
    SET c.segment = 'Silver'
    WHERE (v.score_r + v.score_f + v.score_m) BETWEEN 5 AND 7;

    SET nb_silver = ROW_COUNT();

    -- Met à jour les segments Bronze
    UPDATE clients c
    INNER JOIN vue_rfm v ON c.id_client = v.id_client
    SET c.segment = 'Bronze'
    WHERE (v.score_r + v.score_f + v.score_m) < 5;

    SET nb_bronze = ROW_COUNT();

    -- Affiche un résumé
    SELECT
        nb_gold   AS clients_gold,
        nb_silver AS clients_silver,
        nb_bronze AS clients_bronze,
        (nb_gold + nb_silver + nb_bronze) AS total_mis_a_jour;
END$$

DELIMITER ;

-- Appel de la procédure :
CALL maj_segments_rfm();

-- Vérifie les segments mis à jour :
SELECT segment, COUNT(*) AS nb_clients
FROM clients
GROUP BY segment
ORDER BY nb_clients DESC;