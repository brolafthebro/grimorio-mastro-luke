import streamlit as st
import json
import re
import os

st.set_page_config(page_title="Grimorio Mastro Luke", page_icon="📜", layout="centered")

# --- CSS DEFINITIVO (FIX MENU A TENDINA & RESET) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;700&display=swap');
    
    .stApp { background-color: #fdf5e6 !important; }
    
    /* Forza testo nero ovunque */
    .stApp, .stMarkdown, p, span, label, li, h1, h2, h3, h4 { 
        color: #1a1a1a !important; 
        font-family: 'Crimson Pro', serif !important;
    }

    /* FIX MENU A TENDINA (Suggerimenti del cerca) */
    div[data-baseweb="popover"], div[data-baseweb="listbox"] {
        background-color: white !important;
    }
    div[data-baseweb="popover"] li {
        color: black !important;
        background-color: white !important;
    }
    /* Colore testo nelle caselle di selezione */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }

    .spell-title {
        color: #8b0000 !important;
        font-size: 2.2rem !important;
        font-weight: bold !important;
        text-align: center !important;
        text-transform: uppercase !important;
        margin-top: 10px !important;
    }

    .spell-card {
        background-color: #fffaf0 !important;
        border: 1px solid #d4c4a8 !important;
        border-radius: 8px !important;
        padding: 18px !important;
        color: #1a1a1a !important;
        line-height: 1.6 !important;
        text-align: justify !important;
    }

    .dice { color: #b30000 !important; font-weight: bold !important; }
    header, footer {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DATI ---
@st.cache_data
def load_data():
    for f_name in ["incantesimi_puliti.json", "incantesimi.json"]:
        if os.path.exists(f_name):
            with open(f_name, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

spells = load_data()

# --- LOGICA DI NAVIGAZIONE CON RESET ---
# Inizializziamo lo stato della ricerca se non esiste
if 'search_idx' not in st.session_state:
    st.session_state.search_idx = 0

def reset_search():
    # Questa funzione viene chiamata quando usi i filtri per classe
    st.session_state.search_idx = 0

# --- INTERFACCIA ---
st.markdown("<h2 style='text-align: center; color: #8b0000; margin-top: -30px;'>📜 GRIMORIO</h2>", unsafe_allow_html=True)

# 1. BARRA DI RICERCA
nomi_tutti = sorted([s['name_it'] for s in spells])
options_search = [""] + nomi_tutti

# Se l'utente scrive qui, l'app si aggiorna
scelta_search = st.selectbox("🔍 Cerca Incantesimo:", options_search, key="search_bar")

st.markdown("<div style='margin: 15px 0; border-top: 1px solid #8b0000; opacity: 0.3;'></div>", unsafe_allow_html=True)

# 2. FILTRI CLASSE/LIVELLO
col_a, col_b = st.columns(2)
with col_a:
    # Se cambi classe, chiamiamo reset_search per "pulire" la barra di ricerca
    classe_sel = st.selectbox("Classe:", ["Bardo", "Chierico", "Druido", "Paladino", "Ranger", "Stregone", "Warlock", "Mago"], on_change=reset_search)
with col_b:
    map_cls = {"Bardo":"bard","Chierico":"cleric","Druido":"druid","Paladino":"paladin","Ranger":"ranger","Stregone":"sorcerer","Warlock":"warlock","Mago":"wizard"}
    sp_cls = [s for s in spells if map_cls[classe_sel] in s.get('classes', [])]
    livelli = sorted(list(set([int(str(s['level']).replace('o','0')) for s in sp_cls])))
    liv_sel = st.selectbox("Livello:", livelli, on_change=reset_search)

nomi_filtro = sorted([s['name_it'] for s in sp_cls if int(str(s['level']).replace('o','0')) == liv_sel])
scelta_lista = st.selectbox("Oppure scegli dalla lista:", nomi_filtro, on_change=reset_search)

# --- DETERMINAZIONE INCANTESIMO ---
# Logica: Se l'utente ha appena interagito con la ricerca (non è vuota), mostra quella.
# Se però l'utente tocca i filtri, il sistema dovrebbe dare priorità alla lista.
# Per rendere l'app fluida: se 'search_bar' ha un valore, mostriamo quello, 
# a meno che l'utente non voglia usare i filtri (in quel caso deve svuotare il cerca).

if scelta_search != "":
    nome_final = scelta_search
else:
    nome_final = scelta_lista

spell = next((s for s in spells if s['name_it'] == nome_final), None)

# --- VISUALIZZAZIONE --- (Il resto rimane uguale alla versione precedente)
if spell:
    st.markdown(f'<p class="spell-title">{spell["name_it"]}</p>', unsafe_allow_html=True)
    # ... (Codice di visualizzazione: Scuola, Tempo, Gittata, Durata, Descrizione con pulizia_live)
    # Per brevità non incollo di nuovo tutto il blocco visualizzazione, 
    # ma assicurati di includere la funzione pulizia_live e il blocco 'if spell' precedente.