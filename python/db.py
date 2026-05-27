# ============================================================
#  db.py — Module de connexion MySQL sécurisée
#  Projet Huile d'Olive — MSc2 INSEEC 2026
#  Les credentials sont lus depuis le fichier .env
#  
# ============================================================

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import pandas as pd
from typing import Optional

# Charge les variables d'environnement depuis .env
load_dotenv()


def get_connection() -> mysql.connector.MySQLConnection:
    """
    Crée et retourne une connexion MySQL sécurisée.
    Les credentials sont lus depuis le fichier .env

    Returns:
        mysql.connector.MySQLConnection: connexion active

    Raises:
        ConnectionError: si la connexion échoue
    """
    try:
        connection = mysql.connector.connect(
            host     = os.getenv("DB_HOST", "localhost"),
            port     = int(os.getenv("DB_PORT", 3306)),
            user     = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME"),
            charset  = "utf8mb4"
        )
        if connection.is_connected():
            print(f"✅ Connecté à MySQL — base : {os.getenv('DB_NAME')}")
            return connection

    except Error as e:
        raise ConnectionError(f"❌ Échec connexion MySQL : {e}")


def close_connection(connection: mysql.connector.MySQLConnection) -> None:
    """
    Ferme proprement la connexion MySQL si elle est ouverte.

    Args:
        connection: connexion MySQL à fermer
    """
    if connection and connection.is_connected():
        connection.close()
        print("🔒 Connexion MySQL fermée.")


def run_query(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """
    Exécute une requête SELECT et retourne le résultat en DataFrame pandas.
    Gère automatiquement l'ouverture et la fermeture de connexion.

    Args:
        query  : requête SQL SELECT à exécuter
        params : paramètres optionnels pour éviter les injections SQL

    Returns:
        pd.DataFrame : résultat de la requête

    Example:
        df = run_query("SELECT * FROM clients WHERE segment = %s", ('Gold',))
    """
    connection = None
    try:
        connection = get_connection()
        df = pd.read_sql(query, connection, params=params)
        return df

    except Error as e:
        print(f"❌ Erreur lors de la requête : {e}")
        return pd.DataFrame()

    finally:
        close_connection(connection)


def execute_write(query: str, params: Optional[tuple] = None) -> int:
    """
    Exécute une requête INSERT, UPDATE ou DELETE.
    Retourne le nombre de lignes affectées.

    Args:
        query  : requête SQL d'écriture
        params : paramètres de la requête

    Returns:
        int : nombre de lignes affectées
    """
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        return rows_affected

    except Error as e:
        print(f"❌ Erreur écriture MySQL : {e}")
        if connection:
            connection.rollback()
        return 0

    finally:
        close_connection(connection)


def execute_many(query: str, data: list) -> int:
    """
    Insère plusieurs lignes en une seule opération (executemany).
    Beaucoup plus rapide que des INSERT un par un.

    Args:
        query : requête INSERT avec placeholders %s
        data  : liste de tuples, un tuple = une ligne

    Returns:
        int : nombre de lignes insérées

    Example:
        execute_many(
            "INSERT INTO rfm_resultats (id_client, score) VALUES (%s, %s)",
            [(1, 8), (2, 5), (3, 3)]
        )
    """
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.executemany(query, data)
        connection.commit()
        rows = cursor.rowcount
        print(f"✅ {rows} lignes insérées avec succès.")
        cursor.close()
        return rows

    except Error as e:
        print(f"❌ Erreur insertion multiple : {e}")
        if connection:
            connection.rollback()
        return 0

    finally:
        close_connection(connection)


def create_table_if_not_exists(create_sql: str) -> None:
    """
    Crée une table MySQL si elle n'existe pas déjà.

    Args:
        create_sql : requête CREATE TABLE IF NOT EXISTS
    """
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(create_sql)
        connection.commit()
        cursor.close()
        print("✅ Table vérifiée / créée.")

    except Error as e:
        print(f"❌ Erreur création table : {e}")

    finally:
        close_connection(connection)


# ── Test rapide si on exécute ce fichier directement ──────────
if __name__ == "__main__":
    print("=== Test de connexion MySQL ===")
    conn = get_connection()
    close_connection(conn)

    print("\n=== Test run_query ===")
    df = run_query("SELECT nom_societe, pays_client, segment FROM clients LIMIT 5")
    print(df)
