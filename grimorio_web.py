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

# ---------------- CSS DARK APP STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-color: #121212;
    color: #e6e6e6;
    font-family: 'Crimson Pro', serif;
}

h1,h2,h3,h4,h5,h6,p,span,label {
    color:#e6e6e6 !important;
}

.spell-card {
    background:#1e1e1e;
    padding:20px;
    border-radius:14px;
    line-height:1.7;
    box-shadow:0 4px 15px rgba(0,0,0,0.4);
}

.spell-title {
    text-align:center;
    font-size:2rem;
    font-weight:bold;
    color:#ffcc66;
}

.spell-sub {
    text-align:center;
    font-style:italic;
    margin-bottom:12px;
    color:#bbbbbb;
}

.dice { color:#ff4d4d; font-weight:bold; }

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

@media (max-width:600px){
    .spell-title{font-size:1.5rem;}
    .spell-card{padding:14px;font-size:0.95rem;}
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
for key in ["selected_spell","selected_class","selected_level"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ---------------- RESET FUNCTION ----------------
def reset_all():
    st.session_state.selected_spell = None
    st.session_state.selected_class = None
    st.session_state.selected_level = None

# ---------------- RICERCA LIVE ----------------
st.markdown("### 🔎 Cerca")

search = st.text_input("")

if search:
    risultati = [
        s for s in spells
        if search.lower() in s["name_it"].lower()
    ]

    for s in risultati[:10]:
        if st.button(s["name_it"], key=f"search_{s['name_it']}"):
            st.session_state.selected_spell = s["name_it"]
            st.rerun()

# ---------------- CLASSI ----------------
if not search and not st.session_state.selected_spell:

    st.markdown("### 🎭 Classi")

    cols = st.columns(4)
    for i, cls in enumerate(map_cls.keys()):
        if cols[i % 4].button(cls):
            st.session_state.selected_class = cls
            st.session_state.selected_level = None
            st.session_state.selected_spell = None
            st.rerun()

# ---------------- LIVELLI ----------------
if st.session_state.selected_class and not st.session_state.selected_spell:

    st.markdown(f"### 🎚 Livelli — {st.session_state.selected_class}")

    cod = map_cls[st.session_state.selected_class]

    spells_class = [s for s in spells if cod in s.get("classes",[])]

    livelli = sorted(set(int(str(s["level"]).replace("o","0")) for s in spells_class))

    cols = st.columns(5)
    for i, lvl in enumerate(livelli):
        label = "Trucc." if lvl == 0 else str(lvl)
        if cols[i % 5].button(label):
            st.session_state.selected_level = lvl
            st.rerun()

# ---------------- LISTA INCANTESIMI ----------------
if st.session_state.selected_level is not None and not st.session_state.selected_spell:

    cod = map_cls[st.session_state.selected_class]

    spells_filtered = [
        s for s in spells
        if cod in s.get("classes",[])
        and int(str(s["level"]).replace("o","0")) == st.session_state.selected_level
    ]

    st.markdown("### 📜 Incantesimi")

    for s in sorted(spells_filtered, key=lambda x: x["name_it"]):
        if st.button(s["name_it"], use_container_width=True):
            st.session_state.selected_spell = s["name_it"]
            st.rerun()

# ---------------- SCHEDA ----------------
if st.session_state.selected_spell:

    spell = next((s for s in spells if s["name_it"] == st.session_state.selected_spell), None)

    if spell:
        if st.button("⬅ Torna"):
            reset_all()
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
        desc = re.sub(r'(\d+d\d+|\b\d+\b)', r'<span class="dice">\\1</span>', desc)

        st.markdown(
            f"<div class='spell-card'>{desc.replace(chr(10),'<br>')}</div>",
            unsafe_allow_html=True
        )

        if spell.get("higher_levels_it"):
            st.markdown(
                f"<div style='margin-top:15px;'><b>Ai Livelli Superiori:</b> {spell['higher_levels_it']}</div>",
                unsafe_allow_html=True
            )