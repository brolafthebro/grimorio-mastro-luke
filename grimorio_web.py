import streamlit as st
import json
import re
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Grimorio Mastro Luke", page_icon="📜", layout="centered")

# --- CSS DEFINITIVO (FIX MENU, COLORI E MOBILE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;700&display=swap');
    
    .stApp { background-color: #fdf5e6 !important; }
    
    /* Forza testo nero ovunque */
    .stApp, .stMarkdown, p, span, label, li, h1, h2, h3, h4, [data-testid="stWidgetLabel"] p { 
        color: #1a1a1a !important; 
        font-family: 'Crimson Pro', serif !important;
    }

    /* FIX MENU A TENDINA (Per leggere i nomi mentre scrivi) */
    div[data-baseweb="popover"], div[data-baseweb="listbox"] {
        background-color: white !important;
    }
    div[data-baseweb="popover"] li, div[data-baseweb="listbox"] li {
        color: black !important;
        background-color: white !important;
    }
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }

    /* Stile Scheda Incantesimo */
    .spell-title {
        color: #8b0000 !important;
        font-size: 2.2rem !important;
        font-weight: bold !important;
        text-align: center !important;
        text-transform: uppercase !important;
        margin-top: 10px !important;
        margin-bottom: 0px !important;
    }

    .spell-sub {
        text-align: center !important;
        margin-top: -5px !important;
        font-style: italic !important;
        font-size: 1rem !important;
        color: #444 !important;
    }

    .spell-card {
        background-color: #fffaf0 !important;
        border: 1px solid #d4c4a8 !important;
        border-radius: 8px !important;
        padding: 18px !important;
        color: #1a1a1a !important;
        line-height: 1.6 !important;
        text-align: justify !important;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05) !important;
    }

    .dice { color: #b30000 !important; font-weight: bold !important; }
    header, footer {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DI SUPPORTO ---
TRAD_COMP = {"V": "Verbale", "S": "Somatica", "M": "Materiale"}
TRAD_SCUOLE = {
    "abjuration": "Abiurazione", "conjuration": "Evocazione", "divination": "Divinazione",
    "enchantment": "Ammaliamento", "evocation": "Invocazione", "illusion": "Illusione",
    "necromancy": "Negromanzia", "transmutation": "Trasmutazione"
}

def pulizia_live(desc, durata):
    if not desc or not durata: return desc
    desc = desc.lstrip(' \t\n\r\f\v.,:;-')
    parti = re.findall(r'\w+', durata.lower()) + ["fino", "a", "ad", "ora", "ore", "minuto", "minuti", "round"]
    for _ in range(6):
        for p in sorted(list(set(parti)), key=len, reverse=True):
            if len(p) < 2 and p != "a": continue
            pattern = re.compile(r'^' + re.escape(p) + r'\b', re.IGNORECASE)
            if pattern.search(desc):
                desc = pattern.sub('', desc, count=1).lstrip(' \t\n\r\f\v.,:;-')
    return desc[0].upper() + desc[1:] if desc else ""

@st.cache_data
def load_data():
    for f_name in ["incantesimi_puliti.json", "incantesimi.json"]:
        if os.path.exists(f_name):
            with open(f_name, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

spells = load_data()

# --- INTERFACCIA ---
st.markdown("<h2 style='text-align: center; color: #8b0000; margin-top: -30px;'>📜 GRIMORIO</h2>", unsafe_allow_html=True)

# 1. BARRA DI RICERCA
nomi_tutti = sorted([s['name_it'] for s in spells])
scelta_search = st.selectbox("🔍 Cerca Incantesimo:", [""] + nomi_tutti)

st.markdown("<div style='margin: 15px 0; border-top: 1px solid #8b0000; opacity: 0.2;'></div>", unsafe_allow_html=True)

# 2. FILTRI CLASSE/LIVELLO
col_a, col_b = st.columns(2)
with col_a:
    classe_sel = st.selectbox("Classe:", ["Bardo", "Chierico", "Druido", "Paladino", "Ranger", "Stregone", "Warlock", "Mago"])
with col_b:
    map_cls = {"Bardo":"bard","Chierico":"cleric","Druido":"druid","Paladino":"paladin","Ranger":"ranger","Stregone":"sorcerer","Warlock":"warlock","Mago":"wizard"}
    cod_cls = map_cls[classe_sel]
    sp_cls = [s for s in spells if cod_cls in s.get('classes', [])]
    livelli = sorted(list(set([int(str(s['level']).replace('o','0')) for s in sp_cls])))
    liv_sel = st.selectbox("Livello:", livelli)

nomi_filtro = sorted([s['name_it'] for s in sp_cls if int(str(s['level']).replace('o','0')) == liv_sel])
scelta_lista = st.selectbox("Oppure scegli dalla lista:", nomi_filtro)

# --- LOGICA DI SELEZIONE ---
# Se la barra di ricerca non è vuota, vince lei.
if scelta_search != "":
    nome_final = scelta_search
else:
    nome_final = scelta_lista

spell = next((s for s in spells if s['name_it'] == nome_final), None)

# --- VISUALIZZAZIONE SCHEDA ---
if spell:
    # Titolo
    st.markdown(f'<p class="spell-title">{spell["name_it"]}</p>', unsafe_allow_html=True)
    
    # Sottotitolo
    liv = str(spell.get('level', '0')).replace('o', '0')
    testo_liv = "TRUCCHETTO" if liv == '0' else f"LIVELLO {liv}"
    scuola = TRAD_SCUOLE.get(spell.get('school','').lower(), 'Variante')
    st.markdown(f'<p class="spell-sub">{testo_liv} • {scuola.upper()}</p>', unsafe_allow_html=True)
    
    # Info Tecniche
    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Tempo:** {spell.get('action_type', '-')}")
        st.markdown(f"**Gittata:** {spell.get('range', '-')}")
    with c2:
        st.markdown(f"**Durata:** {spell.get('duration', '-')}")
        raw_comp = spell.get('components', [])
        comp_ita = [TRAD_COMP.get(c, c) for c in (raw_comp if isinstance(raw_comp, list) else [])]
        st.markdown(f"**Componenti:** {', '.join(comp_ita)}")

    st.markdown("<hr style='border: 1px solid #8b0000; opacity: 0.6;'>", unsafe_allow_html=True)
    
    # Descrizione con dadi rossi e pulizia
    desc_base = spell.get('description_it', '')
    desc_pulita = pulizia_live(desc_base, spell.get('duration', ''))
    
    # Regex dadi rossi
    desc_html = re.sub(r'(\d+d\d+|\b\d+\b)', r'<span class="dice">\1</span>', desc_pulita)
    
    st.markdown(f'<div class="spell-card">{desc_html.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    
    # Livelli Superiori
    if spell.get('higher_levels_it'):
        st.markdown(f"<div style='margin-top:15px;'><b>Ai Livelli Superiori:</b> {spell['higher_levels_it']}</div>", unsafe_allow_html=True)

else:
    st.info("Seleziona un incantesimo per visualizzarlo.")