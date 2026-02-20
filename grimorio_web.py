import streamlit as st
import json
import re
import os

# Configurazione per Mobile
st.set_page_config(page_title="Grimorio", page_icon="📜", layout="centered")

# --- TRADUZIONI ---
TRAD_COMP = {"V": "Verbale", "S": "Somatica", "M": "Materiale"}
TRAD_SCUOLE = {
    "abjuration": "Abiurazione", "conjuration": "Evocazione", "divination": "Divinazione",
    "enchantment": "Ammaliamento", "evocation": "Invocazione", "illusion": "Illusione",
    "necromancy": "Negromanzia", "transmutation": "Trasmutazione"
}

# --- CSS MOBILE-FIRST ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;700&display=swap');
    
    .stApp { background-color: #fdf5e6; }
    
    /* Forza il testo nero e leggibile */
    p, span, label, .stSelectbox { 
        color: #1a1a1a !important; 
        font-family: 'Crimson Pro', serif;
    }

    /* Titolo enorme stile D&D */
    .spell-title {
        color: #8b0000;
        font-size: 2.2rem;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        margin-bottom: 0px;
    }

    /* Card per la descrizione */
    .spell-card {
        background-color: #fffaf0;
        border: 1px solid #d4c4a8;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        line-height: 1.6;
        text-align: justify;
    }

    /* Numeri dadi rossi */
    .dice { color: #8b0000; font-weight: bold; }

    /* Nascondi header streamlit inutile su mobile */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DI PULIZIA ---
def pulizia_live(desc, durata):
    if not desc or not durata: return desc
    # Rimuove frammenti della durata dall'inizio della descrizione
    parti = re.findall(r'\w+', durata.lower()) + ["fino", "a", "ora", "minuto", "round"]
    desc = desc.lstrip(' \t\n\r\f\v.,:;-')
    for _ in range(5):
        for p in sorted(parti, key=len, reverse=True):
            if len(p) < 2 and p != "a": continue
            pattern = re.compile(r'^' + re.escape(p) + r'\b', re.IGNORECASE)
            if pattern.search(desc):
                desc = pattern.sub('', desc, count=1).lstrip(' \t\n\r\f\v.,:;-')
    return desc[0].upper() + desc[1:] if desc else ""

@st.cache_data
def load_data():
    files = ["incantesimi_puliti.json", "incantesimi.json"]
    for f_name in files:
        if os.path.exists(f_name):
            with open(f_name, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

spells = load_data()

# --- INTERFACCIA CENTRALE (NIENTE SIDEBAR) ---
st.markdown("<h2 style='text-align: center; color: #8b0000;'>📜 GRIMORIO</h2>", unsafe_allow_html=True)

# 1. Ricerca Globale
nomi_tutti = sorted([s['name_it'] for s in spells])
scelta_search = st.selectbox("🔍 Cerca per nome:", [""] + nomi_tutti, help="Scrivi il nome dell'incantesimo")

st.markdown("<div style='margin: 10px 0; border-top: 1px solid #d4c4a8;'></div>", unsafe_allow_html=True)

# 2. Filtri rapidi (in colonne per occupare meno spazio verticale)
col_a, col_b = st.columns(2)
with col_a:
    classe_sel = st.selectbox("Classe:", ["Bardo", "Chierico", "Druido", "Paladino", "Ranger", "Stregone", "Warlock", "Mago"])
with col_b:
    cod_cls = {"Bardo":"bard","Chierico":"cleric","Druido":"druid","Paladino":"paladin","Ranger":"ranger","Stregone":"sorcerer","Warlock":"warlock","Mago":"wizard"}[classe_sel]
    sp_cls = [s for s in spells if cod_cls in s.get('classes', [])]
    livelli = sorted(list(set([int(str(s['level']).replace('o','0')) for s in sp_cls])))
    liv_sel = st.selectbox("Livello:", livelli)

nomi_filtro = sorted([s['name_it'] for s in sp_cls if int(str(s['level']).replace('o','0')) == liv_sel])
scelta_lista = st.selectbox("Seleziona dalla lista:", nomi_filtro)

# --- LOGICA VISUALIZZAZIONE ---
nome_final = scelta_search if scelta_search != "" else scelta_lista
spell = next((s for s in spells if s['name_it'] == nome_final), None)

if spell:
    st.markdown(f'<p class="spell-title">{spell["name_it"]}</p>', unsafe_allow_html=True)
    liv = str(spell.get('level', '0')).replace('o', '0')
    st.markdown(f"<p style='text-align:center; margin-top:-10px;'><i>{'TRUCCHETTO' if liv=='0' else f'LIVELLO {liv}'} • {TRAD_SCUOLE.get(spell.get('school','').lower(), 'Variante')}</i></p>", unsafe_allow_html=True)
    
    # Info compatte per mobile
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Tempo:** {spell.get('action_type', '-')}")
        st.markdown(f"**Gittata:** {spell.get('range', '-')}")
    with c2:
        st.markdown(f"**Durata:** {spell.get('duration', '-')}")
        comps = [TRAD_COMP.get(c, c) for c in spell.get('components', [])]
        st.markdown(f"**Componenti:** {', '.join(comps)}")

    st.markdown("<hr style='border: 1px solid #8b0000;'>", unsafe_allow_html=True)
    
    # Descrizione pulita e formattata
    desc_pulita = pulizia_live(spell.get('description_it', ''), spell.get('duration', ''))
    desc_html = re.sub(r'(\d+d\d+|\b\d+\b)', r'<span class="dice">\1</span>', desc_pulita)
    
    st.markdown(f'<div class="spell-card">{desc_html.replace("\n", "<br>")}</div>', unsafe_allow_html=True)