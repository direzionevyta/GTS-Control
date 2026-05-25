import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'GTS Control')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Admin123')

def get_connection():
    """Connessione al database PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Errore di connessione: {e}")
        return None

def init_database():
    """Crea le tabelle del database se non esistono"""
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    try:
        # Tabella Dipendenti
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dipendenti (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                cognome VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                telefono VARCHAR(20),
                ruolo VARCHAR(50),
                data_assunzione DATE,
                attivo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella Servizi
        cur.execute("""
            CREATE TABLE IF NOT EXISTS servizi (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descrizione TEXT,
                prezzo DECIMAL(10, 2),
                durata_ore INT,
                categoria VARCHAR(50),
                attivo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella Mezzi
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mezzi (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                tipo VARCHAR(50),
                marca VARCHAR(50),
                modello VARCHAR(50),
                targa VARCHAR(20) UNIQUE,
                anno_immatricolazione INT,
                stato VARCHAR(50) DEFAULT 'disponibile',
                km_attuali INT DEFAULT 0,
                data_ultima_manutenzione DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella Turni
        cur.execute("""
            CREATE TABLE IF NOT EXISTS turni (
                id SERIAL PRIMARY KEY,
                dipendente_id INT NOT NULL REFERENCES dipendenti(id),
                data_turno DATE NOT NULL,
                ora_inizio TIME,
                ora_fine TIME,
                tipo VARCHAR(50),
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella Fogli Viaggio
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fogli_viaggio (
                id SERIAL PRIMARY KEY,
                dipendente_id INT NOT NULL REFERENCES dipendenti(id),
                mezzo_id INT NOT NULL REFERENCES mezzi(id),
                servizio_id INT REFERENCES servizi(id),
                data_viaggio DATE NOT NULL,
                ora_partenza TIME,
                ora_arrivo TIME,
                luogo_partenza VARCHAR(255),
                luogo_arrivo VARCHAR(255),
                km_percorsi INT,
                ore_lavoro DECIMAL(5, 2),
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Database inizializzato correttamente")
        return True
        
    except Exception as e:
        print(f"❌ Errore nella creazione delle tabelle: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_database()
