import streamlit as st
import json
import re

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Grimorio di Mastro Luke",
    page_icon="📖",
    layout="centered"
)

# --- CSS PERSONALIZZATO PER LOOK D&D E MOBILE ---
st.markdown("""
    <style>
    .stApp { background-color: #fdf5e6; }
    .title-text { color: #8b0000; font-family: 'serif'; font-weight: bold; text-align: center; }
    .spell-card { 
        background-color: rgba(139, 0, 0, 0.05); 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #8b0000;
        margin-bottom: 20px;
    }
    .technical-info { color: #1a1a1a; font-size: 0.9em; border-bottom: 1px solid #1a1a1a; padding-bottom: 10px; }
    /* Ottimizzazione per iPhone */
    @media (max-width: 640px) {
        .stButton button { width: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI PULIZIA ---
def pulisci_descrizione(desc, durata):
    if not desc: return ""
    testo = desc.strip()
    durata_clean = durata.lower().replace("concentrazione,", "").strip()
    
    # Rimuove frammenti di durata ripetuti all'inizio
    patterns = [durata_clean, "fino a " + durata_clean, "ora", "minuto", "round", "istantanea"]
    patterns.sort(key=len, reverse=True)
    
    testo_lower = testo.lower()
    for p in patterns:
        if testo_lower.startswith(p):
            testo = testo[len(p):].strip()
            break
            
    # Pulizia caratteri residui e maiuscola
    testo = re.sub(r'^[.,\s]+', '', testo)
    return testo[0].upper() + testo[1:] if testo else ""

# --- CARICAMENTO DATI ---
@st.cache_data
def load_data():
    # Prova a caricare il file locale, altrimenti usa l'URL del tuo Gist
    try:
        with open("incantesimi.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        import requests
        url = 'https://gist.githubusercontent.com/vietts/bee17c5aaa7b74f470c8016085864202/raw/dnd-2024-spells-it.json'
        return requests.get(url).json()

spells = load_data()

# --- INTERFACCIA ---
st.markdown("<h1 class='title-text'>📖 GRIMORIO DI MASTRO LUKE</h1>", unsafe_allow_html=True)

# Sidebar per filtri (su mobile finisce nel menu a scomparsa)
with st.sidebar:
    st.header("Filtri Ricerca")
    classe_selezionata = st.selectbox("Classe", ["Tutte", "Bardo", "Chierico", "Druido", "Paladino", "Ranger", "Stregone", "Warlock", "Mago"])
    livello_selezionato = st.select_slider("Livello Incantesimo", options=list(range(10)), value=0)

# Mappatura classi
diz_classi = {"Bardo": "bard", "Chierico": "cleric", "Druido": "druid", "Paladino": "paladin", "Ranger": "ranger", "Stregone": "sorcerer", "Warlock": "warlock", "Mago": "wizard"}

# Filtro logico
filtered_spells = [
    s for s in spells 
    if (classe_selezionata == "Tutte" or diz_classi[classe_selezionata] in s.get('classes', []))
    and int(str(s.get('level', 0)).replace('o','0')) == livello_selezionato
]

# Ricerca testuale rapida
search_query = st.text_input("🔍 Cerca incantesimo per nome...", "").lower()
if search_query:
    filtered_spells = [s for s in filtered_spells if search_query in s['name_it'].lower() or search_query in s['name'].lower()]

# Visualizzazione Risultati
if not filtered_spells:
    st.warning("Nessun incantesimo trovato con questi filtri.")
else:
    nomi_spells = [s['name_it'] for s in filtered_spells]
    scelta = st.selectbox("Seleziona l'incantesimo da leggere:", nomi_spells)
    
    spell = next(s for s in filtered_spells if s['name_it'] == scelta)
    
    # Render Dettagli
    st.markdown(f"<h2 style='color: #8b0000;'>{spell['name_it'].upper()}</h2>", unsafe_allow_html=True)
    
    info_tecniche = f"""
    **Livello:** {spell['level']} | **Scuola:** {spell['school']}  
    **Tempo di lancio:** {spell['action_type']} | **Gittata:** {spell['range']}  
    **Durata:** {spell['duration']} | **Concentrazione:** {'Sì' if spell['concentration'] else 'No'}
    """
    st.markdown(f"<div class='technical-info'>{info_tecniche}</div>", unsafe_allow_html=True)
    
    # Pulizia e visualizzazione descrizione
    desc_pulita = pulisci_descrizione(spell['description_it'], spell['duration'])
    st.write("")
    st.write(desc_pulita)

st.caption("Creato da Mastro Luke - D&D 2024")