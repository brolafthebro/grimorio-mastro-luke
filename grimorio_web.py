import streamlit as st
import json
import re

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Grimorio Mastro Luke", layout="centered")

# --- NUOVA PALETTE COLORI (Elegante e Desaturata) ---
DIZ_CLASSI_WEB = {
    "Bardo": {"icon": "🎵", "color": "#8E44AD"},   # Viola scuro
    "Chierico": {"icon": "🛡️", "color": "#5D6D7E"}, # Grigio fumo
    "Druido": {"icon": "🌿", "color": "#1E8449"},   # Verde foresta
    "Paladino": {"icon": "⚔️", "color": "#B7950B"}, # Oro antico
    "Ranger": {"icon": "🏹", "color": "#527E5E"},   # Salvia scuro
    "Stregone": {"icon": "🔥", "color": "#922B21"}, # Sangue di bue
    "Warlock": {"icon": "👁️", "color": "#4A235A"}, # Prugna
    "Mago": {"icon": "📖", "color": "#2E86C1"}      # Blu notte
}

# --- CSS DEFINITIVO PER IPHONE ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #fdf5e6; }}
    
    .main-title {{ 
        color: #8b0000 !important; 
        text-align: center; 
        font-weight: bold; 
        font-size: 2.2em;
        margin-bottom: 0px;
    }}
    .sub-title {{ text-align: center; color: #1a1a1a !important; font-size: 1em; margin-bottom: 20px; }}

    /* FORZA GRIGLIA 2 COLONNE SU MOBILE */
    [data-testid="column"] {{
        width: 48% !important;
        flex: unset !important;
        min-width: 48% !important;
    }}
    
    div.stButton > button {{
        width: 100% !important;
        height: 60px !important;
        border-radius: 8px !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        margin-bottom: 10px !important;
        display: block;
    }}

    /* Testi */
    .spell-name {{ color: #8b0000 !important; font-size: 1.8em; font-weight: bold; }}
    .spell-info {{ background-color: #f2e9d9; padding: 15px; border-radius: 10px; color: #1a1a1a !important; border: 1px solid #d4c4a8; }}
    .spell-desc {{ color: #1a1a1a !important; font-size: 1.1em; margin-top: 15px; line-height: 1.5; }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI PULIZIA ---
def pulisci_descrizione(desc, durata):
    if not desc: return ""
    testo = desc.strip()
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
    except: return []

spells = load_data()

# --- NAVIGAZIONE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'classe' not in st.session_state: st.session_state.classe = None

st.markdown("<h1 class='main-title'>GRIMORIO INCANTESIMI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>5E D&D 2024 ITA</p>", unsafe_allow_html=True)

# --- HOME ---
if st.session_state.page == 'home':
    # Ricerca
    search = st.text_input("🔍 Cerca...", placeholder="Nome incantesimo...").lower()
    if search:
        res = [s for s in spells if search in s['name_it'].lower()][:3]
        for s in res:
            if st.button(f"📖 {s['name_it'].upper()}", key=f"s_{s['name_it']}"):
                st.session_state.spell = s
                st.session_state.page = 'dettaglio'
                st.rerun()

    st.markdown("<p style='text-align:center; margin-top:10px;'>Seleziona una classe:</p>", unsafe_allow_html=True)

    # Griglia 2x4
    col1, col2 = st.columns(2)
    for i, (nome, info) in enumerate(DIZ_CLASSI_WEB.items()):
        target = col1 if i % 2 == 0 else col2
        st.markdown(f"<style>div.stButton > button[key='{nome}'] {{ background-color: {info['color']} !important; }}</style>", unsafe_allow_html=True)
        if target.button(f"{info['icon']} {nome.upper()}", key=nome):
            st.session_state.classe = nome
            st.session_state.page = 'livelli'
            st.rerun()

# --- LIVELLI ---
elif st.session_state.page == 'livelli':
    st.subheader(f"Classe: {st.session_state.classe}")
    if st.button("⬅️ CLASSI", key="b_h"): st.session_state.page = 'home'; st.rerun()
    
    col1, col2 = st.columns(2)
    livs = ["Trucchetti"] + [f"Lvl {i}" for i in range(1, 10)]
    for i, l in enumerate(livs):
        t = col1 if i % 2 == 0 else col2
        if t.button(l.upper(), key=f"l_{i}"):
            st.session_state.liv = i
            st.session_state.page = 'lista'
            st.rerun()

# --- LISTA ---
elif st.session_state.page == 'lista':
    st.subheader(f"{st.session_state.classe} - Lvl {st.session_state.liv}")
    if st.button("⬅️ LIVELLI", key="b_l"): st.session_state.page = 'livelli'; st.rerun()
    
    m = {"Bardo":"bard","Chierico":"cleric","Druido":"druid","Paladino":"paladin","Ranger":"ranger","Stregone":"sorcerer","Warlock":"warlock","Mago":"wizard"}
    lista = [s for s in spells if m[st.session_state.classe] in s.get('classes', []) and int(s.get('level', 0)) == st.session_state.liv]
    
    for s in sorted(lista, key=lambda x: x['name_it']):
        if st.button(s['name_it'].upper(), key=f"sp_{s['name_it']}"):
            st.session_state.spell = s
            st.session_state.page = 'dettaglio'
            st.rerun()

# --- DETTAGLIO ---
elif st.session_state.page == 'dettaglio':
    s = st.session_state.spell
    if st.button("⬅️ INDIETRO"): st.session_state.page = 'lista' if st.session_state.classe else 'home'; st.rerun()
    
    st.markdown(f"<div class='spell-name'>{s['name_it'].upper()}</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='spell-info'>
    <b>Livello {s['level']}</b> | {s['school'].upper()}<br>
    <b>Lancio:</b> {s['action_type']} | <b>Gittata:</b> {s.get('range')}<br>
    <b>Durata:</b> {s.get('duration')}
    </div>
    """, unsafe_allow_html=True)
    
    d = pulisci_descrizione(s['description_it'], s.get('duration', ''))
    st.markdown(f"<div class='spell-desc'>{d}</div>", unsafe_allow_html=True)