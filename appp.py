# Advanced Gemini Murder Mystery Streamlit App
# Save as app.py if downloading separately

import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="AI Murder Mystery", page_icon="🕵️", layout="wide")

st.markdown("""
<style>
.stApp {background:#121212;color:white;}
.card {background:#1e1e1e;padding:15px;border-radius:12px;border:1px solid #444;}
.clue {background:#252525;padding:10px;border-left:4px solid crimson;margin:8px 0;border-radius:6px;}
.rank {padding:10px;border-radius:8px;background:#202020;}
</style>
""", unsafe_allow_html=True)

with open("gemini_api_key.txt","r") as f:
    API_KEY = f.read().strip()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def clean_json(text):
    text = text.strip()
    text = text.replace("```json","").replace("```","")
    return json.loads(text)

def generate_mystery(difficulty):
    prompt = f"""
Create a {difficulty} murder mystery.
Return ONLY JSON.

{{
"victim":"",
"crime_scene":"",
"suspects":[{{"name":"","occupation":"","alibi":""}}],
"clues":["","","","",""]
}}

Rules:
- exactly 3 suspects
- exactly 5 clues
- one suspect must be guilty
- clues must allow logical deduction
- do not reveal the murderer
"""
    return clean_json(model.generate_content(prompt).text)

def solve_case(mystery):
    prompt = f"""
Analyze this mystery and identify the guilty suspect.

{json.dumps(mystery)}

Return ONLY the suspect's name.
"""
    return model.generate_content(prompt).text.strip()

if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Medium"

if "game" not in st.session_state:
    st.session_state.game = generate_mystery(st.session_state.difficulty)
    st.session_state.clues_found = []
    st.session_state.solution = solve_case(st.session_state.game)

st.title("🕵️ AI Murder Mystery Detective")

with st.sidebar:
    st.header("Detective Dashboard")

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy","Medium","Hard"],
        index=["Easy","Medium","Hard"].index(st.session_state.difficulty)
    )

    if st.button("🔄 New Case"):
        st.session_state.difficulty = difficulty
        st.session_state.game = generate_mystery(difficulty)
        st.session_state.clues_found = []
        st.session_state.solution = solve_case(st.session_state.game)
        st.rerun()

game = st.session_state.game

score = max(20, 100 - len(st.session_state.clues_found)*10)

if score >= 90:
    rank = "Master Detective"
elif score >= 70:
    rank = "Senior Detective"
elif score >= 50:
    rank = "Detective"
else:
    rank = "Rookie Detective"

st.sidebar.metric("Score", score)
st.sidebar.write(f"Rank: **{rank}**")
st.sidebar.info(f"Victim: {game['victim']}")

st.subheader("Crime Scene")
st.markdown(f"<div class='card'>{game['crime_scene']}</div>", unsafe_allow_html=True)

st.subheader("Evidence Board")

if st.button("🔍 Find New Clue"):
    if len(st.session_state.clues_found) < len(game["clues"]):
        st.session_state.clues_found.append(
            game["clues"][len(st.session_state.clues_found)]
        )

for clue in st.session_state.clues_found:
    st.markdown(f"<div class='clue'>{clue}</div>", unsafe_allow_html=True)

st.subheader("Suspects")

cols = st.columns(3)

for col, suspect in zip(cols, game["suspects"]):
    with col:
        st.markdown(
            f"""
<div class='card'>
<h3>{suspect['name']}</h3>
<b>Occupation:</b> {suspect['occupation']}<br><br>
<b>Alibi:</b><br>{suspect['alibi']}
</div>
""",
            unsafe_allow_html=True
        )

st.subheader("Detective Notebook")

notes = st.text_area(
    "Write down your deductions",
    height=150
)

suspect_names = [s["name"] for s in game["suspects"]]

guess = st.selectbox(
    "Who is the murderer?",
    suspect_names
)

if st.button("🚨 Accuse"):

    if guess.lower() == st.session_state.solution.lower():
        st.balloons()
        st.success(
            f"Case Solved! {guess} is guilty.\n\nScore: {score}\nRank: {rank}"
        )
    else:
        st.error(
            f"Wrong accusation.\n\nThe guilty suspect was {st.session_state.solution}."
        )
