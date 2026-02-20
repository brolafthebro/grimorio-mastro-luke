import streamlit as st
import json
import re

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Grimorio Mastro Luke", page_icon="📖", layout="centered")

# --- CSS PER COLORI D&D E MOBILE ---
st.markdown("""
    <style>
    .stApp { background-color: #fdf5e6; }
    .main-title { color: #8b0000; font-family: 'serif'; font-weight: bold; text-align: center; margin-bottom: 0px; }
    .sub-title { color: #1a1a1a; font-family: 'serif'; text-align: center; margin-bottom: 30px; font-size: 1.2em; }
    .welcome-msg { text-align: center; color: #1a1a1a; font-style: italic; margin: 20px 0; }
    
    /* Testo descrizione (Nero su Pergamena) */
    .spell-desc { color: #1a1a1a !important; font-size: 1.1em; line-height: 1.6; }
    .technical-box { border-top: 2px solid #8b0000; border-bottom: 2px solid #8b0000; padding: 10px 0; margin: 10px 0; color: #1a1a1a; }
    
    /* Pulsanti Classi 2x4 */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 60px;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI PULIZIA (Dal tuo script originale) ---
def pulisci_descrizione(desc, durata):
    if not desc: return "Descrizione non disponibile."
    testo = desc.strip()
    # Rimuove residui della durata all'inizio del testo
    durata_clean = durata.lower().replace("concentrazione,", "").strip()
    patterns = [durata_clean, f"fino a {durata_clean}", "ora", "minuto", "round", "istantanea", "a 1 ora"]
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

# --- STATO DELL'APP ---
if 'view' not in st.session_state: st.session_state.view = 'home'
if 'classe' not in st.session_state: st.session_state.classe = None
if 'livello' not in st.session_state: st.session_state.livello = None

# --- HEADER ---
st.markdown("<h1 class='main-title'>GRIMORIO INCANTESIMI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>5E D&D 2024 ITA</p>", unsafe_allow_html=True)

# --- FUNZIONI DI NAVIGAZIONE ---
def vai_a_home(): st.session_state.view = 'home'

# --- 1. LANDING PAGE / HOME ---
if st.session_state.view == 'home':
    # Barra di ricerca con preview (simula il tuo Listbox)
    search_query = st.text_input("🔍 Cerca incantesimo...", placeholder="Scrivi il nome...").strip().lower()
    
    if search_query:
        suggerimenti = [s for s in spells if search_query in s['name_it'].lower()][:5]
        for s in suggerimenti:
            if st.button(f"📖 {s['name_it']}", key=f"search_{s['name_it']}"):
                st.session_state.spell_selezionata = s
                st.session_state.view = 'dettaglio'
                st.rerun()

    st.markdown("<p class='welcome-msg'>Benvenuto, Viandante. Cerca un incantesimo o seleziona una classe</p>", unsafe_allow_html=True)
    
    # Griglia Classi 2x4
    classi = [
        ("Bardo", "🎵", "#E6CCFF"), ("Chierico", "🛡️", "#FFFFFF"), 
        ("Druido", "🌿", "#D5F5E3"), ("Paladino", "⚔️", "#F9E79F"),
        ("Ranger", "🏹", "#ABEBC6"), ("Stregone", "🔥", "#FAD7A0"), 
        ("Warlock", "👁️", "#EBDEF0"), ("Mago", "📖", "#D6EAF8")
    ]
    
    cols = st.columns(2)
    for i, (nome, icona, colore) in enumerate(classi):
        with cols[i % 2]:
            if st.button(f"{icona} {nome}"):
                st.session_state.classe = nome
                st.session_state.view = 'livelli'
                st.rerun()

# --- 2. SELEZIONE LIVELLO ---
elif st.session_state.view == 'livelli':
    st.subheader(f"Classe: {st.session_state.classe}")
    if st.button("⬅️ Torna alle Classi"): vai_a_home(); st.rerun()
    
    livelli = ["Trucchetti"] + [f"Livello {i}" for i in range(1, 10)]
    cols_liv = st.columns(2)
    for i, liv in enumerate(livelli):
        with cols_liv[i % 2]:
            if st.button(liv):
                st.session_state.livello = i
                st.session_state.view = 'lista_spells'
                st.rerun()

# --- 3. LISTA INCANTESIMI ---
elif st.session_state.view == 'lista_spells':
    st.subheader(f"{st.session_state.classe} - Lvl {st.session_state.livello}")
    if st.button("⬅️ Cambia Livello"): st.session_state.view = 'livelli'; st.rerun()
    
    codice_classe = {"Bardo": "bard", "Chierico": "cleric", "Druido": "druid", "Paladino": "paladin", "Ranger": "ranger", "Stregone": "sorcerer", "Warlock": "warlock", "Mago": "wizard"}[st.session_state.classe]
    
    lista = [s for s in spells if codice_classe in s.get('classes', []) and int(s.get('level', 0)) == st.session_state.livello]
    
    for s in sorted(lista, key=lambda x: x['name_it']):
        if st.button(s['name_it'], key=s['name_it']):
            st.session_state.spell_selezionata = s
            st.session_state.view = 'dettaglio'
            st.rerun()

# --- 4. DETTAGLIO INCANTESIMO ---
elif st.session_state.view == 'dettaglio':
    s = st.session_state.spell_selezionata
    if st.button("⬅️ Torna alla lista"): st.session_state.view = 'lista_spells'; st.rerun()
    
    st.markdown(f"<h2 style='color: #8b0000; text-align:center;'>{s['name_it'].upper()}</h2>", unsafe_allow_html=True)
    
    # Info tecniche (Nero su pergamena)
    info = f"""
    <div class='technical-box'>
    <b>Livello:</b> {s['level']} | <b>Tempo:</b> {s['action_type']}<br>
    <b>Gittata:</b> {s.get('range', 'Varia')} | <b>Durata:</b> {s.get('duration', 'Istantanea')}<br>
    <b>Componenti:</b> {', '.join(s.get('components', []))}
    </div>
    """
    st.markdown(info, unsafe_allow_html=True)
    
    # Descrizione pulita
    testo_pulito = pulisci_descrizione(s['description_it'], s['duration'])
    st.markdown(f"<div class='spell-desc'>{testo_pulito}</div>", unsafe_allow_html=True)