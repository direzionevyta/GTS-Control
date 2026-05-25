import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_connection, init_database
import psycopg2

# Configurazione pagina
st.set_page_config(
    page_title="GTS Control - Gestionale",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stile CSS personalizzato
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Inizializza il database
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# Titolo principale
st.title("📊 GTS Control - Gestionale Startup")
st.markdown("---")

# Sidebar - Navigazione
with st.sidebar:
    st.title("🔧 Menu")
    pagina = st.radio(
        "Seleziona una sezione:",
        ["📈 Dashboard", "📋 Servizi", "🚗 Mezzi", "👥 Dipendenti", "📅 Turni", "📍 Fogli Viaggio"]
    )

# Funzione per ottenere statistiche dashboard
def get_dashboard_stats():
    conn = get_connection()
    if not conn:
        return None
    
    cur = conn.cursor()
    stats = {}
    
    try:
        # Numero dipendenti
        cur.execute("SELECT COUNT(*) FROM dipendenti WHERE attivo = TRUE")
        stats['dipendenti'] = cur.fetchone()[0]
        
        # Numero servizi attivi
        cur.execute("SELECT COUNT(*) FROM servizi WHERE attivo = TRUE")
        stats['servizi'] = cur.fetchone()[0]
        
        # Numero mezzi disponibili
        cur.execute("SELECT COUNT(*) FROM mezzi WHERE stato = 'disponibile'")
        stats['mezzi_disponibili'] = cur.fetchone()[0]
        
        # Numero mezzi totali
        cur.execute("SELECT COUNT(*) FROM mezzi")
        stats['mezzi_totali'] = cur.fetchone()[0]
        
        return stats
    except Exception as e:
        st.error(f"Errore nel caricamento dati: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# DASHBOARD
if pagina == "📈 Dashboard":
    st.subheader("Panoramica Generale")
    
    stats = get_dashboard_stats()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Dipendenti Attivi", stats['dipendenti'])
        
        with col2:
            st.metric("📋 Servizi Attivi", stats['servizi'])
        
        with col3:
            st.metric("🚗 Mezzi Disponibili", stats['mezzi_disponibili'])
        
        with col4:
            st.metric("🚗 Mezzi Totali", stats['mezzi_totali'])
    
    st.markdown("---")
    st.info("✅ Accedi alle altre sezioni dal menu a sinistra per gestire i dettagli")

# SERVIZI
elif pagina == "📋 Servizi":
    st.subheader("Gestione Servizi")
    
    tab1, tab2 = st.tabs(["📋 Visualizza", "➕ Aggiungi Nuovo"])
    
    with tab1:
        conn = get_connection()
        if conn:
            try:
                df = pd.read_sql("SELECT id, nome, descrizione, prezzo, durata_ore, categoria FROM servizi ORDER BY id", conn)
                if len(df) > 0:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nessun servizio registrato")
            except Exception as e:
                st.error(f"Errore: {e}")
            finally:
                conn.close()
    
    with tab2:
        st.write("Aggiungi un nuovo servizio")
        nome = st.text_input("Nome servizio")
        descrizione = st.text_area("Descrizione")
        prezzo = st.number_input("Prezzo (€)", min_value=0.0, step=0.01)
        durata = st.number_input("Durata (ore)", min_value=0)
        categoria = st.text_input("Categoria")
        
        if st.button("✅ Aggiungi Servizio"):
            conn = get_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO servizi (nome, descrizione, prezzo, durata_ore, categoria) VALUES (%s, %s, %s, %s, %s)",
                        (nome, descrizione, prezzo, durata, categoria)
                    )
                    conn.commit()
                    st.success("✅ Servizio aggiunto con successo!")
                except Exception as e:
                    st.error(f"Errore: {e}")
                finally:
                    cur.close()
                    conn.close()

# MEZZI
elif pagina == "🚗 Mezzi":
    st.subheader("Gestione Mezzi")
    
    tab1, tab2 = st.tabs(["📋 Visualizza", "➕ Aggiungi Nuovo"])
    
    with tab1:
        conn = get_connection()
        if conn:
            try:
                df = pd.read_sql("SELECT id, nome, tipo, marca, modello, targa, stato, km_attuali FROM mezzi ORDER BY id", conn)
                if len(df) > 0:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nessun mezzo registrato")
            except Exception as e:
                st.error(f"Errore: {e}")
            finally:
                conn.close()
    
    with tab2:
        st.write("Aggiungi un nuovo mezzo")
        nome = st.text_input("Nome mezzo")
        tipo = st.selectbox("Tipo", ["Auto", "Moto", "Furgone", "Camion", "Bicicletta"])
        marca = st.text_input("Marca")
        modello = st.text_input("Modello")
        targa = st.text_input("Targa")
        anno = st.number_input("Anno immatricolazione", min_value=1900, max_value=2099)
        km = st.number_input("KM attuali", min_value=0)
        
        if st.button("✅ Aggiungi Mezzo"):
            conn = get_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO mezzi (nome, tipo, marca, modello, targa, anno_immatricolazione, km_attuali) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (nome, tipo, marca, modello, targa, anno, km)
                    )
                    conn.commit()
                    st.success("✅ Mezzo aggiunto con successo!")
                except Exception as e:
                    st.error(f"Errore: {e}")
                finally:
                    cur.close()
                    conn.close()

# DIPENDENTI
elif pagina == "👥 Dipendenti":
    st.subheader("Gestione Dipendenti")
    
    tab1, tab2 = st.tabs(["📋 Visualizza", "➕ Aggiungi Nuovo"])
    
    with tab1:
        conn = get_connection()
        if conn:
            try:
                df = pd.read_sql("SELECT id, nome, cognome, email, telefono, ruolo FROM dipendenti WHERE attivo = TRUE ORDER BY id", conn)
                if len(df) > 0:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nessun dipendente registrato")
            except Exception as e:
                st.error(f"Errore: {e}")
            finally:
                conn.close()
    
    with tab2:
        st.write("Aggiungi un nuovo dipendente")
        nome = st.text_input("Nome")
        cognome = st.text_input("Cognome")
        email = st.text_input("Email")
        telefono = st.text_input("Telefono")
        ruolo = st.selectbox("Ruolo", ["Autista", "Tecnico", "Supervisore", "Manager", "Operaio"])
        data_assunzione = st.date_input("Data assunzione")
        
        if st.button("✅ Aggiungi Dipendente"):
            conn = get_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO dipendenti (nome, cognome, email, telefono, ruolo, data_assunzione) VALUES (%s, %s, %s, %s, %s, %s)",
                        (nome, cognome, email, telefono, ruolo, data_assunzione)
                    )
                    conn.commit()
                    st.success("✅ Dipendente aggiunto con successo!")
                except Exception as e:
                    st.error(f"Errore: {e}")
                finally:
                    cur.close()
                    conn.close()

# TURNI
elif pagina == "📅 Turni":
    st.subheader("Gestione Turni")
    
    tab1, tab2 = st.tabs(["📋 Visualizza", "➕ Aggiungi Nuovo"])
    
    with tab1:
        conn = get_connection()
        if conn:
            try:
                df = pd.read_sql("""
                    SELECT t.id, d.nome, d.cognome, t.data_turno, t.ora_inizio, t.ora_fine, t.tipo 
                    FROM turni t 
                    JOIN dipendenti d ON t.dipendente_id = d.id 
                    ORDER BY t.data_turno DESC
                """, conn)
                if len(df) > 0:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nessun turno registrato")
            except Exception as e:
                st.error(f"Errore: {e}")
            finally:
                conn.close()
    
    with tab2:
        st.write("Assegna un nuovo turno")
        
        conn = get_connection()
        if conn:
            try:
                df_dip = pd.read_sql("SELECT id, nome, cognome FROM dipendenti WHERE attivo = TRUE ORDER BY nome", conn)
                dipendenti_dict = {f"{row['nome']} {row['cognome']}": row['id'] for _, row in df_dip.iterrows()}
                
                dipendente_nome = st.selectbox("Seleziona dipendente", list(dipendenti_dict.keys()))
                data_turno = st.date_input("Data turno")
                ora_inizio = st.time_input("Ora inizio")
                ora_fine = st.time_input("Ora fine")
                tipo = st.selectbox("Tipo turno", ["Mattina", "Pomeriggio", "Sera", "Notte", "Intero"])
                note = st.text_area("Note")
                
                if st.button("✅ Assegna Turno"):
                    dipendente_id = dipendenti_dict[dipendente_nome]
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO turni (dipendente_id, data_turno, ora_inizio, ora_fine, tipo, note) VALUES (%s, %s, %s, %s, %s, %s)",
                        (dipendente_id, data_turno, ora_inizio, ora_fine, tipo, note)
                    )
                    conn.commit()
                    st.success("✅ Turno assegnato con successo!")
                    cur.close()
            except Exception as e:
                st.error(f"Errore: {e}")
            finally:
                conn.close()

# FOGLI VIAGGIO
elif pagina == "📍 Fogli Viaggio":
    st.subheader("Gestione Fogli Viaggio")
    
    tab1, tab2 = st.tabs(["📋 Visualizza", "➕ Aggiungi Nuovo"])
    
    with tab1:
        conn = get_connection()
        if conn:
            try:
                df = pd.read_sql("""
                    SELECT f.id, d.nome, d.cognome, m.nome as mezzo, f.data_viaggio, f.luogo_partenza, f.luogo_arrivo, f.km_percorsi, f.ore_lavoro
                    FROM fogli_viaggio f
                    JOIN dipendenti d ON f.dipendente_id = d.id
                    JOIN mezzi m ON f.mezzo_id = m.id
                    ORDER BY f.data_viaggio DESC
                """, conn)
                if len(df) > 0:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nessun foglio viaggio registrato")
            except Exception as e:
                st.error(f"Errore: {e}")
            finally:
                conn.close()
    
    with tab2:
        st.write("Registra un nuovo foglio viaggio")
        
        conn = get_connection()
        if conn:
            try:
                # Carica dipendenti
                df_dip = pd.read_sql("SELECT id, nome, cognome FROM dipendenti WHERE attivo = TRUE ORDER BY nome", conn)
                dipendenti_dict = {f"{row['nome']} {row['cognome']}": row['id'] for _, row in df_dip.iterrows()}
                
                # Carica mezzi
                df_mezzi = pd.read_sql("SELECT id, nome FROM mezzi ORDER BY nome", conn)
                mezzi_dict = {row['nome']: row['id'] for _, row in df_mezzi.iterrows()}
                
                # Carica servizi
                df_servizi = pd.read_sql("SELECT id, nome FROM servizi WHERE attivo = TRUE ORDER BY nome", conn)
                servizi_dict = {row['nome']: row['id'] for _, row in df_servizi.iterrows()}
                
                dipendente_nome = st.selectbox("Seleziona dipendente", list(dipendenti_dict.keys()), key="dip_viaggio")
                mezzo_nome = st.selectbox("Seleziona mezzo", list(mezzi_dict.keys()), key="mezzo_viaggio")
                servizio_nome = st.selectbox("Seleziona servizio (opzionale)", ["Nessuno"] + list(servizi_dict.keys()), key="serv_viaggio")
                
                data_viaggio = st.date_input("Data viaggio")
                ora_partenza = st.time_input("Ora partenza")
                ora_arrivo = st.time_input("Ora arrivo")
                luogo_partenza = st.text_input("Luogo partenza")
                luogo_arrivo = st.text_input("Luogo arrivo")
                km_percorsi = st.number_input("KM percorsi", min_value=0)
                ore_lavoro = st.number_input("Ore di lavoro", min_value=0.0, step=0.5)
                note = st.text_area("Note")
                
                if st.button("✅ Registra Foglio Viaggio"):
                    dipendente_id = dipendenti_dict[dipendente_nome]
                    mezzo_id = mezzi_dict[mezzo_nome]
                    servizio_id = servizi_dict.get(servizio_nome) if servizio_nome != "Nessuno" else None
                    
                    cur = conn.cursor()
                    cur.execute(
                        """INSERT INTO fogli_viaggio 
                        (dipendente_id, mezzo_id, servizio_id, data_viaggio, ora_partenza, ora_arrivo, luogo_partenza, luogo_arrivo, km_percorsi, ore_lavoro, note) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (dipendente_id, mezzo_id, servizio_id, data_viaggio, ora_partenza, ora_arrivo, luogo_partenza, luogo_arrivo, km_percorsi, ore_lavoro, note)
                    )
                    conn.commit()
                    st.success("✅ Foglio viaggio registrato con successo!")
                    cur.close()
            except Exception as e:
                st.error(f"Errore: {e}")
            finally:
                conn.close()

st.markdown("---")
st.caption("🚀 GTS Control - Gestionale Startup v1.0")
