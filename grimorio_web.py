import streamlit as st
import json
import re
import os

st.set_page_config(
    page_title="Grimorio Mastro Luke",
    page_icon="📜",
    layout="centered"
)

# ---------------- CSS MOBILE FIRST ----------------
st.markdown("""
<style>

.stApp {
    background-color: #121212;
    color: #eaeaea;
    font-family: 'Crimson Pro', serif;
}

h1,h2,h3,h4,h5,h6,p,span,label {
    color:#eaeaea !important;
}

.section-title {
    font-size:1.1rem;
    font-weight:bold;
    margin-top:20px;
    margin-bottom:10px;
    color:#ffcc66;
}

.spell-card {
    background:#1e1e1e;
    padding:16px;
    border-radius:12px;
    line-height:1.6;
    margin-bottom:12px;
}

.spell-title {
    text-align:center;
    font-size:1.8rem;
    font-weight:bold;
    color:#ffcc66;
}

.spell-sub {
    text-align:center;
    font-style:italic;
    margin-bottom:12px;
    color:#bbbbbb;
}

.dice {
    color:#ff4d4d;
    font-weight:bold;
}

/* Pulsanti colorati */
button[kind="secondary"] {
    border-radius:10px !important;
}

/* Riduce spazio verticale mobile */
@media (max-width:600px){
    div[data-testid="column"] {
        padding:2px !important;
    }
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
    "Bardo":"bard",
    "Chierico":"cleric",
    "Druido":"druid",
    "Paladino":"paladin",
    "Ranger":"ranger",
    "Stregone":"sorcerer",
    "Warlock":"warlock",
    "Mago":"wizard"
}

# ---------------- SESSION STATE ----------------
for key in ["selected_spell","selected_class","selected_level"]:
    if key not in st.session_state:
        st.session_state[key] = None

def reset_all():
    for key in ["selected_spell","selected_class","selected_level"]:
        st.session_state[key] = None

# ---------------- RICERCA LIVE CON PREVIEW ----------------
st.markdown("<div class='section-title'>🔎 Cerca</div>", unsafe_allow_html=True)

search = st.text_input("", placeholder="Scrivi nome incantesimo...")

if search:
    risultati = sorted(
        [s for s in spells if search.lower() in s["name_it"].lower()],
        key=lambda x: x["name_it"]
    )

    for s in risultati[:8]:
        preview = s.get("description_it","")[:80] + "..."
        if st.button(s["name_it"], use_container_width=True):
            st.session_state.selected_spell = s["name_it"]
            st.rerun()

        st.markdown(f"<div style='font-size:0.8rem;color:#aaa;margin-bottom:10px;'>{preview}</div>", unsafe_allow_html=True)

# ---------------- CLASSI ----------------
if not search and not st.session_state.selected_spell:

    st.markdown("<div class='section-title'>🎭 Classi</div>", unsafe_allow_html=True)

    cols = st.columns(2)  # 2 colonne mobile-friendly
    for i, cls in enumerate(map_cls.keys()):
        if cols[i % 2].button(cls, use_container_width=True):
            st.session_state.selected_class = cls
            st.session_state.selected_level = None
            st.rerun()

# ---------------- LIVELLI ----------------
if st.session_state.selected_class and not st.session_state.selected_spell:

    st.markdown(f"<div class='section-title'>🎚 Livelli — {st.session_state.selected_class}</div>", unsafe_allow_html=True)

    cod = map_cls[st.session_state.selected_class]

    spells_class = [s for s in spells if cod in s.get("classes",[])]

    livelli = sorted(
        set(int(str(s["level"]).replace("o","0")) for s in spells_class)
    )

    cols = st.columns(len(livelli))
    for i, lvl in enumerate(livelli):
        label = "Trucc." if lvl == 0 else str(lvl)
        if cols[i].button(label, use_container_width=True):
            st.session_state.selected_level = lvl
            st.rerun()

# ---------------- LISTA INCANTESIMI ----------------
if st.session_state.selected_level is not None and not st.session_state.selected_spell:

    cod = map_cls[st.session_state.selected_class]

    spells_filtered = sorted(
        [
            s for s in spells
            if cod in s.get("classes",[])
            and int(str(s["level"]).replace("o","0")) == st.session_state.selected_level
        ],
        key=lambda x: x["name_it"]
    )

    st.markdown("<div class='section-title'>📜 Incantesimi</div>", unsafe_allow_html=True)

    for s in spells_filtered:
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

        liv = int(str(spell["level"]).replace("o","0"))
        testo_liv = "TRUCCHETTO" if liv==0 else f"LIVELLO {liv}"
        scuola = spell.get("school","").lower()

        st.markdown(
            f"<div class='spell-sub'>{testo_liv} • {TRAD_SCUOLE.get(scuola,'')}</div>",
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
                f"<div style='margin-top:12px;'><b>Ai Livelli Superiori:</b> {spell['higher_levels_it']}</div>",
                unsafe_allow_html=True
            )