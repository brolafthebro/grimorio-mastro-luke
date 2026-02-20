import streamlit as st
import json
import re
import os

# ---------------- CONFIG PAGINA ----------------
st.set_page_config(
    page_title="Grimorio Mastro Luke",
    page_icon="📜",
    layout="centered"
)

# ---------------- DARK MODE TOGGLE ----------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

col_dark, col_title = st.columns([1,4])
with col_dark:
    st.session_state.dark_mode = st.toggle("🌙 Dark", value=st.session_state.dark_mode)

with col_title:
    st.markdown("<h2 style='text-align:center;'>📜 GRIMORIO</h2>", unsafe_allow_html=True)

# ---------------- CSS DINAMICO ----------------
if st.session_state.dark_mode:
    bg = "#1b1b1b"
    text = "#f5f5f5"
    card = "#262626"
else:
    bg = "#fdf5e6"
    text = "#1a1a1a"
    card = "#fffaf0"

st.markdown(f"""
<style>

.stApp {{
    background-color: {bg};
    color: {text};
    font-family: 'Crimson Pro', serif;
}}

.spell-card {{
    background-color: {card};
    padding: 18px;
    border-radius: 12px;
    line-height: 1.6;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    animation: fadeIn 0.4s ease-in-out;
}}

.spell-title {{
    text-align: center;
    font-size: 2rem;
    font-weight: bold;
    color: #b22222;
}}

.spell-sub {{
    text-align: center;
    font-style: italic;
    margin-bottom: 10px;
}}

.dice {{
    color: #d00000;
    font-weight: bold;
}}

.badge {{
    display:inline-block;
    padding:4px 8px;
    border-radius:8px;
    font-size:0.8rem;
    font-weight:bold;
    margin-right:4px;
}}

.badge-evocation {{ background:#ff7043; color:white; }}
.badge-necromancy {{ background:#6a1b9a; color:white; }}
.badge-abjuration {{ background:#0277bd; color:white; }}
.badge-conjuration {{ background:#2e7d32; color:white; }}
.badge-divination {{ background:#00897b; color:white; }}
.badge-enchantment {{ background:#c2185b; color:white; }}
.badge-illusion {{ background:#512da8; color:white; }}
.badge-transmutation {{ background:#f9a825; color:black; }}

@keyframes fadeIn {{
    from {{opacity:0; transform:translateY(10px);}}
    to {{opacity:1; transform:translateY(0);}}
}}

@media (max-width:600px) {{
    .spell-title {{ font-size:1.5rem; }}
    .spell-card {{ padding:12px; font-size:0.95rem; }}
}}

header, footer {{visibility:hidden;}}

</style>
""", unsafe_allow_html=True)

# ---------------- CARICAMENTO DATI ----------------
@st.cache_data
def load_data():
    for f_name in ["incantesimi_puliti.json", "incantesimi.json"]:
        if os.path.exists(f_name):
            with open(f_name, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

spells = load_data()

# ---------------- TRADUZIONI ----------------
TRAD_SCUOLE = {
    "abjuration":"Abiurazione",
    "conjuration":"Evocazione",
    "divination":"Divinazione",
    "enchantment":"Ammaliamento",
    "evocation":"Invocazione",
    "illusion":"Illusione",
    "necromancy":"Negromanzia",
    "transmutation":"Trasmutazione"
}

map_cls = {
    "Bardo":"bard","Chierico":"cleric","Druido":"druid",
    "Paladino":"paladin","Ranger":"ranger",
    "Stregone":"sorcerer","Warlock":"warlock","Mago":"wizard"
}

# ---------------- RICERCA ----------------
st.markdown("### 🔎 Cerca")
search_text = st.text_input("", placeholder="Scrivi il nome dell'incantesimo...")

# ---------------- FILTRI ----------------
with st.expander("🎛️ Filtri"):
    classe_sel = st.selectbox("Classe", ["Tutte"] + list(map_cls.keys()))
    livelli = sorted(set(int(str(s["level"]).replace("o","0")) for s in spells))
    liv_sel = st.selectbox("Livello", ["Tutti"] + livelli)

# ---------------- FILTRAGGIO ----------------
filtered = spells

if search_text:
    filtered = [s for s in filtered if search_text.lower() in s["name_it"].lower()]

if classe_sel != "Tutte":
    cod = map_cls[classe_sel]
    filtered = [s for s in filtered if cod in s.get("classes",[])]

if liv_sel != "Tutti":
    filtered = [s for s in filtered if int(str(s["level"]).replace("o","0")) == liv_sel]

# ---------------- LISTA ----------------
if "selected_spell" not in st.session_state:
    st.session_state.selected_spell = None

if not st.session_state.selected_spell:

    st.markdown("### 📜 Incantesimi")

    if not filtered:
        st.info("Nessun incantesimo trovato.")
    else:
        for s in sorted(filtered, key=lambda x: x["name_it"]):
            scuola = s.get("school","").lower()
            badge = f'<span class="badge badge-{scuola}">{TRAD_SCUOLE.get(scuola,"")}</span>'
            if st.button(s["name_it"], use_container_width=True):
                st.session_state.selected_spell = s["name_it"]
                st.rerun()

# ---------------- SCHEDA INCANTESIMO ----------------
else:
    spell = next((s for s in spells if s["name_it"] == st.session_state.selected_spell), None)

    if spell:
        if st.button("⬅ Torna alla lista"):
            st.session_state.selected_spell = None
            st.rerun()

        st.markdown(f"<div class='spell-title'>{spell['name_it']}</div>", unsafe_allow_html=True)

        liv = str(spell["level"]).replace("o","0")
        testo_liv = "TRUCCHETTO" if liv=="0" else f"LIVELLO {liv}"
        scuola = spell.get("school","").lower()

        badge_html = f"<span class='badge badge-{scuola}'>{TRAD_SCUOLE.get(scuola,'')}</span>"

        concentrazione = ""
        if "concentrazione" in spell.get("duration","").lower():
            concentrazione = "<span class='badge' style='background:#b71c1c;color:white;'>Concentrazione</span>"

        st.markdown(
            f"<div class='spell-sub'>{testo_liv} • {badge_html} {concentrazione}</div>",
            unsafe_allow_html=True
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        desc = spell.get("description_it","")
        desc = re.sub(r'(\d+d\d+|\b\d+\b)', r'<span class="dice">\1</span>', desc)

        st.markdown(f"<div class='spell-card'>{desc.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

        if spell.get("higher_levels_it"):
            st.markdown(
                f"<div style='margin-top:15px;'><b>Ai Livelli Superiori:</b> {spell['higher_levels_it']}</div>",
                unsafe_allow_html=True
            )