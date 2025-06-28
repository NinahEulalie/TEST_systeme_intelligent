import psycopg2
from psycopg2 import sql
import datetime

DB_CONFIG = {
    "host": "localhost",
    "database": "systeme_intelligent",
    "user": "postgres",
    "password": "Bora16hae",
    "port": 5432
}

# Connexion à la base
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Connexion réussie")
        return conn
        conn.close()
    except Exception as e:
        print(f"Erreur : {e}")

# Création de la table (une fois)
def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resultat (
            id SERIAL PRIMARY KEY,
            matching_score FLOAT,
            label_section TEXT,
            recommendation TEXT,
            timestamp TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Sauvegarde d’un résultat
def save_result(result):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resultat (matching_score, label_section, recommendation, timestamp)
        VALUES (%s, %s, %s, %s)
    """, (
        result["matching_score"],
        result["label_section"],
        result["recommendation"],
        datetime.datetime.now()
    ))

    conn.commit()
    cur.close()
    conn.close()