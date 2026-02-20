import streamlit as st
import json
import re
import os

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Grimorio Mastro Luke",
    page_icon="📜",
    layout="centered"
)

# ---------------- CSS DARK ----------------
st.markdown("""
<style>
.stApp {
    background-color: #121212;
    color: #e6e6e6;
    font-family: 'Crimson Pro', serif;
}

.spell-card {
    background-color: #1e1e1e;
    padding: 20px;
    border-radius: 14px;
    line-height: 1.7;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}

.spell-title {
    text-align: center;
    font-size: 2rem;
    font-weight: bold;
    color: #ffcc66;
}

.spell-sub {
    text-align: center;
    font-style: italic;
    margin-bottom: 12px;
    color: #bbbbbb;
}

.dice {
    color: #ff4d4d;
    font-weight: bold;
}

.badge {
    display:inline-block;
    padding:5px 10px;
    border-radius:10px;
    font-size:0.75rem;
    font-weight:bold;
    margin-right:6px;
}

.badge-evocation { background:#ff7043; }
.badge-necromancy { background:#8e24aa; }
.badge-abjuration { background:#039be5; }
.badge-conjuration { background:#43a047; }
.badge-divination { background:#00897b; }
.badge-enchantment { background:#d81b60; }
.badge-illusion { background:#5e35b1; }
.badge-transmutation { background:#fbc02d; color:black; }

@media (max-width:600px) {
    .spell-title { font-size:1.5rem; }
    .spell-card { padding:14px; font-size:0.95rem; }
}

header, footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'>📜 GRIMORIO</h2>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    for f_name in ["incantesimi_puliti.json", "incantesimi.json"]:
        if os.path.exists(f_name):
            with open(f_name, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

spells = load_data()

if not spells:
    st.error("Nessun file incantesimi trovato.")
    st.stop()

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

# ---------------- SESSION STATE ----------------
if "selected_spell" not in st.session_state:
    st.session_state.selected_spell = None

# ---------------- RICERCA ----------------
nomi = sorted([s["name_it"] for s in spells])

search_choice = st.selectbox(
    "🔎 Cerca incantesimo",
    [""] + nomi
)

# Se selezioni dal cerca → apre subito
if search_choice:
    st.session_state.selected_spell = search_choice

# ---------------- FILTRI SEMPRE VISIBILI ----------------
col1, col2 = st.columns(2)

with col1:
    classe_sel = st.selectbox("Classe", ["Tutte"] + list(map_cls.keys()))

with col2:
    livelli = sorted(set(int(str(s["level"]).replace("o","0")) for s in spells))
    liv_sel = st.selectbox("Livello", ["Tutti"] + livelli)

# ---------------- FILTRAGGIO ----------------
filtered = spells.copy()

if classe_sel != "Tutte":
    cod = map_cls[classe_sel]
    filtered = [s for s in filtered if cod in s.get("classes",[])]

if liv_sel != "Tutti":
    filtered = [s for s in filtered if int(str(s["level"]).replace("o","0")) == liv_sel]

# ---------------- LISTA ----------------
if not st.session_state.selected_spell:

    if not filtered:
        st.info("Nessun incantesimo trovato con questi filtri.")
    else:
        for s in sorted(filtered, key=lambda x: (int(str(x["level"]).replace("o","0")), x["name_it"])):

            scuola = s.get("school","").lower()
            badge = f"<span class='badge badge-{scuola}'>{TRAD_SCUOLE.get(scuola,'')}</span>"

            livello = str(s["level"]).replace("o","0")
            livello_txt = "Trucchetto" if livello=="0" else f"Liv {livello}"

            if st.button(f"{s['name_it']}  •  {livello_txt}", use_container_width=True):
                st.session_state.selected_spell = s["name_it"]
                st.rerun()

            st.markdown(badge, unsafe_allow_html=True)

# ---------------- SCHEDA ----------------
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

        st.markdown(
            f"<div class='spell-sub'>{testo_liv} • {badge_html}</div>",
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