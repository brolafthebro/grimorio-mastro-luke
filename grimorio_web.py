import streamlit as st
import json
import re
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Grimorio Mastro Luke", page_icon="📜", layout="centered")

# --- CSS PERSONALIZZATO (Colori e Numeri Rossi) ---
st.markdown("""
    <style>
    /* Sfondo e Font */
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;700&display=swap');

    .stApp {
        background-color: #fdf5e6;
    }
    
    /* Testo Generale */
    .stApp, p, span, label {
        color: #1a1a1a !important;
        font-family: 'Crimson Pro', serif;
        font-size: 1.1rem;
    }

    /* Sidebar scura */
    [data-testid="stSidebar"] {
        background-color: #2b2b2b;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Titolo Incantesimo */
    .spell-title {
        color: #8b0000;
        font-family: 'Crimson Pro', serif;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }

    /* Numeri e Dadi in Rosso */
    .dice-num {
        color: #8b0000;
        font-weight: bold;
    }

    /* Separatore Bordeaux */
    .bordeaux-line {
        border-top: 3px solid #8b0000;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARICAMENTO DATI ---
@st.cache_data
def load_spells():
    if os.path.exists("incantesimi_puliti.json"):
        with open("incantesimi_puliti.json", "r", encoding="utf-8") as f:
            return json.load(f)
    elif os.path.exists("incantesimi.json"):
        with open("incantesimi.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

spells = load_spells()

DIZ_CLASSI = {
    "Bardo": "bard", "Chierico": "cleric", "Druido": "druid", 
    "Paladino": "paladin", "Ranger": "ranger", "Stregone": "sorcerer", 
    "Warlock": "warlock", "Mago": "wizard"
}

# --- LOGICA DI RICERCA NELLA SIDEBAR ---
st.sidebar.title("📜 GRIMORIO")

# 1. BARRA DI RICERCA (Sostituisce l'anteprima di tkinter con una lista filtrabile)
nomi_tutti = sorted([s['name_it'] for s in spells])
scelta_ricerca = st.sidebar.selectbox("Cerca Incantesimo (scrivi il nome):", [""] + nomi_tutti)

st.sidebar.markdown("---")

# 2. FILTRI TRADIZIONALI
classe_sel = st.sidebar.selectbox("Classe", list(DIZ_CLASSI.keys()))
codice_classe = DIZ_CLASSI[classe_sel]
spells_classe = [s for s in spells if codice_classe in s.get('classes', [])]

livelli = sorted(list(set([int(str(s['level']).replace('o','0')) for s in spells_classe])))
liv_sel = st.sidebar.selectbox("Livello", livelli)

nomi_filtrati = sorted([s['name_it'] for s in spells_classe if int(str(s['level']).replace('o','0')) == liv_sel])
scelta_menu = st.sidebar.selectbox("Seleziona dalla lista:", nomi_filtrati)

# --- DETERMINAZIONE SPELL DA MOSTRARE ---
# Se l'utente ha usato la barra di ricerca, vince quella. Altrimenti il menu.
nome_finale = scelta_ricerca if scelta_ricerca != "" else scelta_menu
spell = next((s for s in spells if s['name_it'] == nome_finale), None)

# --- VISUALIZZAZIONE ---
if spell:
    # Titolo
    st.markdown(f'<p class="spell-title">{spell["name_it"]}</p>', unsafe_allow_html=True)
    
    # Sottotitolo livello
    liv = str(spell.get('level', '0')).replace('o', '0')
    testo_liv = "TRUCCHETTO" if liv == "0" else f"INCANTESIMO DI LIVELLO {liv}"
    st.markdown(f"*{testo_liv}*")
    
    st.markdown('<div class="bordeaux-line"></div>', unsafe_allow_html=True)
    
    # Dati Tecnici
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Tempo di Lancio:** {spell.get('action_type', '-')}")
        st.write(f"**Gittata:** {spell.get('range', '-')}")
    with col2:
        st.write(f"**Durata:** {spell.get('duration', '-')}")
        st.write(f"**Componenti:** {', '.join(spell.get('components', []))}")

    st.markdown('<div class="bordeaux-line"></div>', unsafe_allow_html=True)
    
    # Descrizione con Numeri Rossi
    desc = spell.get('description_it', '')
    
    # Regex per evidenziare numeri e dadi in rosso bordeaux
    # Trova dadi (1d8) e numeri singoli (\d+)
    desc_evidenziata = re.sub(r'(\d+d\d+|\b\d+\b)', r'<span class="dice-num">\1</span>', desc)
    
    st.markdown(f"""
        <div style="text-align: justify; line-height: 1.6;">
            {desc_evidenziata.replace('\n', '<br>')}
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Seleziona un incantesimo dalla ricerca o dai filtri per visualizzarlo.")