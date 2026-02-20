import streamlit as st
import json
import re

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Grimorio Mastro Luke", layout="centered")

# --- CSS PERSONALIZZATO (Colori Fissi e Griglia) ---
st.markdown("""
    <style>
    /* Sfondo pergamena e testi scuri */
    .stApp { background-color: #fdf5e6; }
    h1, h2, h3, p, span, label { color: #1a1a1a !important; }
    
    /* Titolo Grande Bordeaux */
    .main-title { 
        color: #8b0000 !important; 
        text-align: center; 
        font-weight: bold; 
        font-size: 2.5em;
        margin-bottom: 0px;
    }
    .sub-title { 
        text-align: center; 
        font-size: 1.1em; 
        margin-bottom: 20px;
        color: #555 !important;
    }

    /* Griglia Bottoni Classi */
    .stButton > button {
        width: 100%;
        height: 70px;
        border-radius: 12px;
        border: 2px solid #8b0000;
        font-size: 18px !important;
        font-weight: bold !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }

    /* Box Dettaglio Incantesimo */
    .spell-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #8b0000;
        color: #1a1a1a !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI PULIZIA ---
def pulisci_descrizione(desc, durata):
    if not desc: return ""
    testo = desc.strip()
    durata_clean = durata.lower().replace("concentrazione,", "").strip()
    
    # Rimuove residui della durata all'inizio
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

# --- GESTIONE STATO ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'sel_classe' not in st.session_state: st.session_state.sel_classe = None

# --- NAVIGAZIONE ---
def vai_a(pagina): st.session_state.page = pagina

# --- HEADER FISSO ---
st.markdown("<h1 class='main-title'>GRIMORIO INCANTESIMI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>5E D&D 2024 ITA</p>", unsafe_allow_html=True)

# --- PAGINA 1: HOME ---
if st.session_state.page == 'home':
    # Barra di ricerca
    search = st.text_input("🔍 Cerca...", placeholder="Nome incantesimo...").lower()
    if search:
        risultati = [s for s in spells if search in s['name_it'].lower()][:5]
        for r in risultati:
            if st.button(f"📖 {r['name_it']}", key=r['name_it']):
                st.session_state.spell = r
                vai_a('dettaglio')
                st.rerun()

    st.markdown("<p style='text-align:center;'>Benvenuto, Viandante. Cerca un incantesimo o seleziona una classe</p>", unsafe_allow_html=True)

    # Griglia 2x4 ordinata
    classi = [
        ("Bardo", "🎵"), ("Chierico", "🛡️"), 
        ("Druido", "🌿"), ("Paladino", "⚔️"),
        ("Ranger", "🏹"), ("Stregone", "🔥"), 
        ("Warlock", "👁️"), ("Mago", "📖")
    ]
    
    col1, col2 = st.columns(2)
    for i, (nome, icona) in enumerate(classi):
        target_col = col1 if i % 2 == 0 else col2
        if target_col.button(f"{icona} {nome.upper()}", key=nome):
            st.session_state.sel_classe = nome
            vai_a('livelli')
            st.rerun()

# --- PAGINA 2: LIVELLI ---
elif st.session_state.page == 'livelli':
    st.subheader(f"Classe: {st.session_state.sel_classe}")
    if st.button("⬅️ TORNA ALLE CLASSI"): vai_a('home'); st.rerun()
    
    col1, col2 = st.columns(2)
    livelli = ["Trucchetti"] + [f"Livello {i}" for i in range(1, 10)]
    for i, liv in enumerate(livelli):
        target_col = col1 if i % 2 == 0 else col2
        if target_col.button(liv):
            st.session_state.sel_livello = i
            vai_a('lista')
            st.rerun()

# --- PAGINA 3: LISTA ---
elif st.session_state.page == 'lista':
    st.subheader(f"{st.session_state.sel_classe} - Lvl {st.session_state.sel_livello}")
    if st.button("⬅️ CAMBIA LIVELLO"): vai_a('livelli'); st.rerun()
    
    mappa = {"Bardo":"bard","Chierico":"cleric","Druido":"druid","Paladino":"paladin","Ranger":"ranger","Stregone":"sorcerer","Warlock":"warlock","Mago":"wizard"}
    c_code = mappa[st.session_state.sel_classe]
    
    f_spells = [s for s in spells if c_code in s.get('classes', []) and int(s.get('level', 0)) == st.session_state.sel_livello]
    
    for s in sorted(f_spells, key=lambda x: x['name_it']):
        if st.button(s['name_it']):
            st.session_state.spell = s
            vai_a('dettaglio')
            st.rerun()

# --- PAGINA 4: DETTAGLIO ---
elif st.session_state.page == 'dettaglio':
    s = st.session_state.spell
    if st.button("⬅️ TORNA INDIETRO"): vai_a('lista') if st.session_state.sel_classe else vai_a('home'); st.rerun()
    
    st.markdown(f"<h2 style='color:#8b0000;'>{s['name_it'].upper()}</h2>", unsafe_allow_html=True)
    
    info = f"""
    <div style='background:#eee; padding:10px; border-radius:10px; color:#1a1a1a;'>
    <b>Livello:</b> {s['level']} | <b>Tempo:</b> {s['action_type']}<br>
    <b>Gittata:</b> {s.get('range')} | <b>Durata:</b> {s.get('duration')}
    </div>
    """
    st.markdown(info, unsafe_allow_html=True)
    
    desc = pulisci_descrizione(s['description_it'], s.get('duration', ''))
    st.markdown(f"<div style='margin-top:20px; color:#1a1a1a; font-size:1.1em;'>{desc}</div>", unsafe_allow_html=True)