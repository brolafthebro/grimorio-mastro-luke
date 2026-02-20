import streamlit as st
import json
import re
import os

# Configurazione pagina
st.set_page_config(page_title="Grimorio Mastro Luke", page_icon="📜", layout="centered")

# --- TRADUZIONI ---
TRAD_COMP = {"V": "Verbale", "S": "Somatica", "M": "Materiale"}
TRAD_SCUOLE = {
    "abjuration": "Abiurazione", "conjuration": "Evocazione", "divination": "Divinazione",
    "enchantment": "Ammaliamento", "evocation": "Invocazione", "illusion": "Illusione",
    "necromancy": "Negromanzia", "transmutation": "Trasmutazione"
}
TRAD_TEMPI = {"action": "1 Azione", "1 action": "1 Azione", "bonus action": "1 Azione Bonus", "reaction": "1 Reazione"}

# --- CSS DEFINITIVO (Fix testo bianco e mobile) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;700&display=swap');
    
    /* Forza sfondo pergamena */
    .stApp { background-color: #fdf5e6 !important; }

    /* Forza testo nero ovunque (evita il bug del testo bianco su iPhone) */
    .stApp, p, span, label, div, .stSelectbox p, .stMarkdown { 
        color: #1a1a1a !important; 
        font-family: 'Crimson Pro', serif !important;
    }

    /* Stile Titolo */
    .spell-title { 
        color: #8b0000 !important; 
        font-size: 2.2rem !important; 
        font-weight: bold !important; 
        text-align: center; 
        text-transform: uppercase; 
        margin-top: 10px;
    }

    /* Card Descrizione */
    .spell-card { 
        background-color: #fffaf0 !important; 
        border: 1px solid #d4c4a8 !important; 
        border-radius: 8px; 
        padding: 15px; 
        line-height: 1.6; 
        text-align: justify;
        color: #1a1a1a !important;
    }

    /* Dadi Rossi */
    .dice { color: #8b0000 !important; font-weight: bold !important; }

    /* Nascondi elementi inutili */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    for f_name in ["incantesimi_puliti.json", "incantesimi.json"]:
        if os.path.exists(f_name):
            with open(f_name, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

spells = load_data()

# --- LOGICA DI NAVIGAZIONE ---
st.markdown("<h1 style='text-align: center; color: #8b0000;'>📜 GRIMORIO</h1>", unsafe_allow_html=True)

# 1. BARRA DI RICERCA (Sempre scrivibile)
nomi_tutti = sorted([s['name_it'] for s in spells])
scelta_search = st.selectbox("🔍 Cerca Incantesimo:", [""] + nomi_tutti)

st.markdown("<hr style='border: 0.5px solid #d4c4a8; margin: 10px 0;'>", unsafe_allow_html=True)

# 2. FILTRI CLASSE/LIVELLO (Se non si usa la ricerca)
col1, col2 = st.columns(2)
with col1:
    classe_sel = st.selectbox("Filtra Classe:", ["Bardo", "Chierico", "Druido", "Paladino", "Ranger", "Stregone", "Warlock", "Mago"])
with col2:
    liv_sel = st.selectbox("Livello:", range(10))

# Filtriamo la lista in base ai menu
cod_cls = {"Bardo":"bard","Chierico":"cleric","Druido":"druid","Paladino":"paladin","Ranger":"ranger","Stregone":"sorcerer","Warlock":"warlock","Mago":"wizard"}[classe_sel]
sp_filtrati = [s for s in spells if cod_cls in s.get('classes', []) and int(str(s.get('level', 0)).replace('o','0')) == liv_sel]
nomi_filtrati = sorted([s['name_it'] for s in sp_filtrati])

scelta_lista = st.selectbox("Oppure seleziona dalla lista:", [""] + nomi_filtrati)

# --- SCELTA FINALE ---
# Se l'utente ha usato la barra di ricerca, mostriamo quello. Altrimenti la lista filtrata.
nome_finale = scelta_search if scelta_search != "" else scelta_lista

# --- VISUALIZZAZIONE ---
if nome_finale:
    spell = next((s for s in spells if s['name_it'] == nome_finale), None)
    if spell:
        st.markdown(f'<p class="spell-title">{spell["name_it"]}</p>', unsafe_allow_html=True)
        liv = str(spell.get('level', '0')).replace('o', '0')
        scuola = TRAD_SCUOLE.get(spell.get('school','').lower(), 'Variante')
        st.markdown(f"<p style='text-align:center; margin-top:-10px;'><i>{'TRUCCHETTO' if liv=='0' else f'LIVELLO {liv}'} • {scuola}</i></p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border: 1.5px solid #8b0000; margin: 10px 0;'>", unsafe_allow_html=True)
        
        # Dati Tecnici
        c1, c2 = st.columns(2)
        with c1:
            tempo_raw = spell.get('action_type', '').lower()
            st.markdown(f"**Tempo:** {TRAD_TEMPI.get(tempo_raw, tempo_raw)}")
            st.markdown(f"**Gittata:** {spell.get('range', '-')}")
        with c2:
            st.markdown(f"**Durata:** {spell.get('duration', '-')}")
            comps = [TRAD_COMP.get(c, c) for c in spell.get('components', [])]
            st.markdown(f"**Componenti:** {', '.join(comps)}")

        st.markdown("<hr style='border: 1.5px solid #8b0000; margin: 10px 0;'>", unsafe_allow_html=True)
        
        # Descrizione
        desc = spell.get('description_it', '')
        # Evidenzia i numeri in rosso
        desc_html = re.sub(r'(\d+d\d+|\b\d+\b)', r'<span class="dice">\1</span>', desc)
        
        st.markdown(f'<div class="spell-card">{desc_html.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
else:
    st.info("Utilizza la barra di ricerca o i filtri per visualizzare un incantesimo.")