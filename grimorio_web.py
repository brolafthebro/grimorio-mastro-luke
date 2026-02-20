import streamlit as st
import json
import re

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Grimorio Mastro Luke", layout="centered")

# --- MAPPA COLORI E ICONE (Dal tuo progetto originale) ---
# Ho assegnato colori vivaci per contrastare con il testo bianco dei bottoni
DIZ_CLASSI_WEB = {
    "Bardo": {"icon": "🎵", "color": "#A330C9"},   # Viola
    "Chierico": {"icon": "🛡️", "color": "#B0BCF2"}, # Azzurro/Bianco
    "Druido": {"icon": "🌿", "color": "#33937F"},   # Verde
    "Paladino": {"icon": "⚔️", "color": "#F58CBA"}, # Rosa/Oro
    "Ranger": {"icon": "🏹", "color": "#AAD372"},   # Verde chiaro
    "Stregone": {"icon": "🔥", "color": "#C41E3A"}, # Rosso
    "Warlock": {"icon": "👁️", "color": "#9482C9"}, # Viola scuro
    "Mago": {"icon": "📖", "color": "#3FC7EB"}      # Blu
}

# --- CSS PERSONALIZZATO (Leggibilità Totale) ---
st.markdown(f"""
    <style>
    /* Sfondo Pergamena */
    .stApp {{ background-color: #fdf5e6; }}
    
    /* Titolo Principale FORZATO Bordeaux */
    .main-title {{ 
        color: #8b0000 !important; 
        text-align: center; 
        font-weight: bold; 
        font-size: 2.8em;
        margin-bottom: 0px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }}
    
    /* Sottotitolo Nero */
    .sub-title {{ 
        text-align: center; 
        color: #1a1a1a !important;
        font-size: 1.2em;
        margin-bottom: 30px;
    }}

    /* Testo descrizioni e etichette sempre NERO */
    .stMarkdown, p, span, label, .stSelectbox {{ color: #1a1a1a !important; }}

    /* Pulsanti con TESTO BIANCO per leggibilità */
    div.stButton > button {{
        width: 100%;
        height: 65px;
        border-radius: 10px;
        border: none;
        color: white !important; /* Testo Bianco */
        font-weight: bold !important;
        font-size: 18px !important;
        background-color: #8b0000; /* Default Bordeaux */
        margin-bottom: 10px;
    }}
    
    /* Rende il box ricerca visibile */
    .stTextInput input {{
        color: #1a1a1a !important;
        background-color: white !important;
        border: 2px solid #8b0000 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI PULIZIA INTELLIGENTE ---
def pulisci_descrizione(desc, durata):
    if not desc: return "Descrizione non disponibile."
    testo = desc.strip()
    # Rimuove frammenti di durata dall'inizio della descrizione
    durata_clean = durata.lower().replace("concentrazione,", "").strip()
    patterns = [durata_clean, f"fino a {durata_clean}", "ora", "minuto", "round", "a 1 ora"]
    patterns.sort(key=len, reverse=True)
    
    for p in patterns:
        if testo.lower().startswith(p):
            testo = testo[len(p):].strip()
            break
    
    while testo and testo[0] in ".,:; ": testo = testo[1:].strip()
    return testo[0].upper() + testo[1:] if testo else ""

# --- CARICAMENTO DATI ---
@st.cache_data
def load_data():
    try:
        with open("incantesimi.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

spells = load_data()

# --- STATO NAVIGAZIONE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'classe' not in st.session_state: st.session_state.classe = None

# --- HEADER ---
st.markdown("<h1 class='main-title'>GRIMORIO INCANTESIMI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>5E D&D 2024 ITA</p>", unsafe_allow_html=True)

# --- HOME PAGE ---
if st.session_state.page == 'home':
    # Barra di ricerca
    search = st.text_input("🔍 Cerca un incantesimo...", placeholder="Esempio: Palla di Fuoco").lower()
    if search:
        risultati = [s for s in spells if search in s['name_it'].lower()][:5]
        for r in risultati:
            if st.button(f"📖 {r['name_it'].upper()}", key=f"search_{r['name_it']}"):
                st.session_state.spell = r
                st.session_state.page = 'dettaglio'
                st.rerun()

    st.markdown("<p style='text-align:center; font-weight:bold;'>Benvenuto, Viandante. Seleziona una classe:</p>", unsafe_allow_html=True)

    # Griglia Classi 2x4 con Colori Dinamici
    col1, col2 = st.columns(2)
    for i, (nome, info) in enumerate(DIZ_CLASSI_WEB.items()):
        target_col = col1 if i % 2 == 0 else col2
        # Applichiamo il colore specifico al bottone tramite HTML/CSS iniettato per ogni bottone
        st.markdown(f"<style>div.stButton > button[key='{nome}'] {{ background-color: {info['color']} !important; }}</style>", unsafe_allow_html=True)
        if target_col.button(f"{info['icon']} {nome.upper()}", key=nome):
            st.session_state.classe = nome
            st.session_state.page = 'livelli'
            st.rerun()

# --- PAGINA LIVELLI ---
elif st.session_state.page == 'livelli':
    st.subheader(f"Classi: {st.session_state.classe}")
    if st.button("⬅️ TORNA ALLE CLASSI", key="back_home"): 
        st.session_state.page = 'home'
        st.rerun()
    
    col1, col2 = st.columns(2)
    livelli = ["Trucchetti"] + [f"Livello {i}" for i in range(1, 10)]
    for i, liv in enumerate(livelli):
        target_col = col1 if i % 2 == 0 else col2
        if target_col.button(liv, key=f"liv_{i}"):
            st.session_state.livello = i
            st.session_state.page = 'lista'
            st.rerun()

# --- PAGINA LISTA ---
elif st.session_state.page == 'lista':
    st.subheader(f"{st.session_state.classe} - Lvl {st.session_state.livello}")
    if st.button("⬅️ CAMBIA LIVELLO", key="back_liv"): 
        st.session_state.page = 'livelli'
        st.rerun()
    
    mappa_classi = {"Bardo":"bard","Chierico":"cleric","Druido":"druid","Paladino":"paladin","Ranger":"ranger","Stregone":"sorcerer","Warlock":"warlock","Mago":"wizard"}
    c_code = mappa_classi[st.session_state.classe]
    
    lista_filtrata = [s for s in spells if c_code in s.get('classes', []) and int(s.get('level', 0)) == st.session_state.livello]
    
    for s in sorted(lista_filtrata, key=lambda x: x['name_it']):
        if st.button(s['name_it'], key=f"spell_{s['name_it']}"):
            st.session_state.spell = s
            st.session_state.page = 'dettaglio'
            st.rerun()

# --- PAGINA DETTAGLIO ---
elif st.session_state.page == 'dettaglio':
    s = st.session_state.spell
    if st.button("⬅️ TORNA INDIETRO", key="back_list"): 
        st.session_state.page = 'lista' if st.session_state.classe else 'home'
        st.rerun()
    
    st.markdown(f"<h2 style='color:#8b0000;'>{s['name_it'].upper()}</h2>", unsafe_allow_html=True)
    
    # Box Info Tecniche
    st.markdown(f"""
    <div style='background-color: #eee; padding: 15px; border-radius: 10px; border: 1px solid #8b0000; color: #1a1a1a;'>
        <b>Livello:</b> {s['level']} | <b>Tempo:</b> {s['action_type']}<br>
        <b>Gittata:</b> {s.get('range')} | <b>Durata:</b> {s.get('duration')}
    </div>
    """, unsafe_allow_html=True)
    
    desc = pulisci_descrizione(s['description_it'], s.get('duration', ''))
    st.markdown(f"<div style='margin-top:20px; color:#1a1a1a; font-size:1.2em; line-height:1.5;'>{desc}</div>", unsafe_allow_html=True)