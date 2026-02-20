import streamlit as st
import json
import re
import os

st.set_page_config(page_title="Grimorio", page_icon="📜", layout="centered")

# --- TRADUZIONI ---
TRAD_COMP = {"V": "Verbale", "S": "Somatica", "M": "Materiale"}
TRAD_SCUOLE = {
    "abjuration": "Abiurazione", "conjuration": "Evocazione", "divination": "Divinazione",
    "enchantment": "Ammaliamento", "evocation": "Invocazione", "illusion": "Illusione",
    "necromancy": "Negromanzia", "transmutation": "Trasmutazione"
}
TRAD_TEMPI = {"action": "1 Azione", "1 action": "1 Azione", "bonus action": "1 Azione Bonus", "reaction": "1 Reazione"}

# --- CSS OTTIMIZZATO IPHONE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;700&display=swap');
    .stApp { background-color: #fdf5e6; }
    p, span, label, .stSelectbox { color: #1a1a1a !important; font-family: 'Crimson Pro', serif; }
    .spell-title { color: #8b0000; font-size: 2rem; font-weight: bold; text-align: center; text-transform: uppercase; margin-bottom: 0px; }
    .spell-card { 
        background-color: #fffaf0; border: 1px solid #d4c4a8; border-radius: 8px; 
        padding: 15px; line-height: 1.5; text-align: left; /* Corretto allineamento */
        word-wrap: break-word; 
    }
    .dice { color: #8b0000; font-weight: bold; display: inline-block; } /* Fix allineamento dadi */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    for f in ["incantesimi_puliti.json", "incantesimi.json"]:
        if os.path.exists(f):
            with open(f, "r", encoding="utf-8") as file: return json.load(file)
    return []

spells = load_data()

# --- LOGICA DI SINCRONIZZAZIONE ---
if 'selected_spell' not in st.session_state:
    st.session_state.selected_spell = spells[0]['name_it'] if spells else ""

def update_selection():
    st.session_state.selected_spell = st.session_state.search_bar

# --- INTERFACCIA ---
st.markdown("<h2 style='text-align: center; color: #8b0000;'>📜 GRIMORIO</h2>", unsafe_allow_html=True)

# 1. Ricerca
nomi_tutti = sorted([s['name_it'] for s in spells])
scelta_search = st.selectbox("🔍 Cerca Incantesimo:", nomi_tutti, key="search_bar", on_change=update_selection)

# Trova spell attuale per pre-compilare i filtri
spell_attuale = next((s for s in spells if s['name_it'] == st.session_state.selected_spell), None)

# 2. Filtri (che seguono la ricerca)
col_a, col_b = st.columns(2)
with col_a:
    classi_disp = ["Bardo", "Chierico", "Druido", "Paladino", "Ranger", "Stregone", "Warlock", "Mago"]
    # Se lo spell ha classi, proviamo a selezionare la prima disponibile
    default_cls = 0
    if spell_attuale:
        for i, c in enumerate(classi_disp):
            if c.lower() in [cl.lower() for cl in spell_attuale.get('classes', [])]:
                default_cls = i
                break
    classe_sel = st.selectbox("Classe:", classi_disp, index=default_cls)

with col_b:
    liv_default = int(str(spell_attuale.get('level', '0')).replace('o','0')) if spell_attuale else 0
    liv_sel = st.selectbox("Livello:", range(10), index=liv_default)

# --- VISUALIZZAZIONE ---
if spell_attuale:
    st.markdown(f'<p class="spell-title">{spell_attuale["name_it"]}</p>', unsafe_allow_html=True)
    liv = str(spell_attuale.get('level', '0')).replace('o', '0')
    scuola = TRAD_SCUOLE.get(spell_attuale.get('school','').lower(), 'Variante')
    st.markdown(f"<p style='text-align:center;'><i>{'TRUCCHETTO' if liv=='0' else f'LIVELLO {liv}'} • {scuola}</i></p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid #8b0000; margin: 5px 0;'>", unsafe_allow_html=True)
    
    # Dati tecnici tradotti
    c1, c2 = st.columns(2)
    with c1:
        tempo = spell_attuale.get('action_type', '').lower()
        st.markdown(f"**Tempo:** {TRAD_TEMPI.get(tempo, tempo)}")
        st.markdown(f"**Gittata:** {spell_attuale.get('range', '-')}")
    with c2:
        st.markdown(f"**Durata:** {spell_attuale.get('duration', '-')}")
        comps = [TRAD_COMP.get(c, c) for c in spell_attuale.get('components', [])]
        st.markdown(f"**Componenti:** {', '.join(comps)}")

    st.markdown("<hr style='border: 1px solid #8b0000; margin: 5px 0;'>", unsafe_allow_html=True)
    
    desc = spell_attuale.get('description_it', '')
    # Evidenzia dadi senza rompere il layout
    desc_html = re.sub(r'(\d+d\d+|\b\d+\b)', r'<span class="dice">\1</span>', desc)
    
    st.markdown(f'<div class="spell-card">{desc_html.replace("\n", "<br>")}</div>', unsafe_allow_html=True)