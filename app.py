# ======================
# MENTRAIQ v5 – FULL PRO / ERROR-PROOF
# ======================

import streamlit as st
import json
import os
import datetime
from openai import OpenAI

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="MentraIQ", page_icon="🧠")
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

USERS_FILE = "users.json"

# ======================
# HELPER FUNCTIONS
# ======================
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

users = load_users()

# ======================
# SESSION STATE
# ======================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user" not in st.session_state:
    st.session_state.user = None
if "flip_state" not in st.session_state:
    st.session_state.flip_state = {}

# ======================
# NAVIGATION
# ======================
def go_home(): st.session_state.page = "home"
def go_tutor(): st.session_state.page = "tutor"
def go_flashcards(): st.session_state.page = "flashcards"

# ======================
# STYLING
# ======================
st.markdown("""
<style>
.stApp { background-color: #0d1b2a; color: #f5f5f5; }
.stButton>button { background-color: #f5f5f5; color: #0d1b2a; border-radius: 12px; height: 3em; width: 90%; border: none; font-size: 16px; margin-top: 10px;}
.stTextInput>div>div>input, .stSelectbox>div>div>div>select { background-color: #f5f5f5; color: #0d1b2a; border-radius: 8px; }
.card-container { perspective: 1000px; max-width:500px; height:250px; margin:auto; margin-top:20px; }
.card { width:100%; height:100%; position:relative; transform-style: preserve-3d; transition: transform 0.8s; box-shadow:0 4px 8px rgba(0,0,0,0.2); border-radius:16px; }
.card.flipped { transform: rotateY(180deg); }
.card .front, .card .back { position:absolute; width:100%; height:100%; backface-visibility:hidden; display:flex; justify-content:center; align-items:center; text-align:center; padding:24px; font-size:18px; line-height:1.6; border-radius:16px; }
.card .front { background:#f5f5f5; color:#0d1b2a; }
.card .back { background:#f5f5f5; color:#0d1b2a; transform: rotateY(180deg);}
</style>
""", unsafe_allow_html=True)

# ======================
# SIDEBAR LOGIN / SIGNUP
# ======================
st.sidebar.title("MentraIQ Account")
input_user = st.sidebar.text_input("Username")
input_pass = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Create Account"):
    if input_user in users:
        st.sidebar.error("Username already exists")
    else:
        users[input_user] = {"password": input_pass, "streak":0, "last_visit":"", "flashcards":{"tutor":[],"custom":[]}}
        save_users(users)
        st.sidebar.success("Account created! You can now Log In.")

if st.sidebar.button("Log In"):
    if input_user in users and users[input_user]["password"] == input_pass:
        st.session_state.user = input_user
        st.sidebar.success(f"Logged in as {input_user}")
    else:
        st.sidebar.error("Invalid login")

logged_in = st.session_state.user is not None

# ======================
# HOME PAGE
# ======================
if st.session_state.page == "home":
    st.markdown('<div style="max-width:800px;margin:auto;text-align:center;"><h1>MentraIQ 🧠</h1><h3>Understand it. Retain it.</h3></div>', unsafe_allow_html=True)
    st.button("🔍 Ask a Question", on_click=go_tutor)
    st.button("📚 View Flashcards", on_click=go_flashcards)

# ======================
# TUTOR PAGE
# ======================
elif st.session_state.page == "tutor":
    st.markdown('<div style="max-width:800px;margin:auto;"><h1>AI Tutor</h1></div>', unsafe_allow_html=True)

    # Streak
    if logged_in:
        today = str(datetime.date.today())
        user = st.session_state.user
        if users[user].get("last_visit") != today:
            users[user]["streak"] = users[user].get("streak",0) + 1
            users[user]["last_visit"] = today
            save_users(users)
            st.success(f"🔥 Streak increased! {users[user]['streak']} days in a row")
        st.markdown(f'<div style="max-width:800px;margin:auto;margin-top:10px;">Current Streak: <strong>{users[user].get("streak",0)} days</strong></div>', unsafe_allow_html=True)
    else:
        st.info("Sign in to track streaks and save progress.")

    # Tutor card
    st.markdown('<div style="max-width:800px;margin:auto;background:#f5f5f5;color:#0d1b2a;padding:20px;border-radius:16px;margin-top:20px;"><strong>Ask a question</strong></div>', unsafe_allow_html=True)
    subject = st.selectbox("Subject", ["Math","Science","English"])
    question = st.text_input("Type your question here")

    system_prompts = {
        "Math":"You are a patient math tutor. Explain step by step clearly.",
        "Science":"You are a science tutor. Explain concepts simply with examples.",
        "English":"You are an English tutor. Help with writing, grammar, and understanding."
    }

    if question:
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role":"system","content":system_prompts[subject]},
                    {"role":"user","content":question}
                ],
                max_tokens=300
            )
            answer = response.choices[0].message.content

            # Display tutor answer as big card
            st.markdown(f"""
            <div class="card-container">
                <div class="card">
                    <div class="front">{question}</div>
                    <div class="back">{answer}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if logged_in:
                col1, col2 = st.columns([1,1])
                with col1:
                    if st.button("💾 Save to Tutor Flashcards"):
                        cat = st.text_input("Category (e.g., English Final)", key=f"cat_{question}")
                        if not cat: cat = "General"
                        users[user]["flashcards"].setdefault("tutor",[]).append({"question":question,"answer":answer,"category":cat,"favorite":False})
                        save_users(users)
                        st.success(f"Saved in category '{cat}'!")

        except Exception:
            st.error("AI unavailable right now.")

    st.button("Back to Home", on_click=go_home)

# ======================
# FLASHCARDS PAGE
# ======================
elif st.session_state.page == "flashcards":
    st.markdown('<div style="max-width:800px;margin:auto;"><h1>My Flashcards</h1></div>', unsafe_allow_html=True)

    if not logged_in:
        st.warning("Sign in to view and save flashcards.")
        st.button("Back to Home", on_click=go_home)
    else:
        user = st.session_state.user

        # --- Filter by Category ---
        all_categories = ["All"] + list(set(
            [c.get("category", "General") for c in users[user]["flashcards"].get("tutor",[])] +
            [c.get("category", "General") for c in users[user]["flashcards"].get("custom",[])]
        ))
        filter_cat = st.selectbox("Filter by Category", all_categories)

        tabs = st.tabs(["Tutor Answers","Custom Flashcards","Progress Dashboard"])

        # ---- TUTOR FLASHCARDS ----
        with tabs[0]:
            tutor_cards = [c for c in users[user]["flashcards"].get("tutor",[]) if filter_cat=="All" or c.get("category","General")==filter_cat]
            if not tutor_cards:
                st.info("No tutor flashcards saved yet.")
            for i, card in enumerate(tutor_cards):
                key = f"tutor_flip_{i}"
                if key not in st.session_state.flip_state:
                    st.session_state.flip_state[key] = False

                col1, col2 = st.columns([1,1])
                with col1:
                    if st.button("Flip Card", key=f"button_{key}"):
                        st.session_state.flip_state[key] = not st.session_state.flip_state[key]
                with col2:
                    if st.button("⭐ Favorite", key=f"fav_{key}"):
                        card["favorite"] = not card.get("favorite", False)
                        save_users(users)

                flipped = "flipped" if st.session_state.flip_state[key] else ""
                front_content = card.get("question","")
                back_content = card.get("answer","")
                st.markdown(f"""
                <div class="card-container">
                    <div class="card {flipped}">
                        <div class="front">{front_content}</div>
                        <div class="back">{back_content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ---- CUSTOM FLASHCARDS ----
        with tabs[1]:
            term = st.text_input("Term")
            definition = st.text_input("Definition")
            cat = st.text_input("Category (e.g., Math Final)")
            if st.button("Add Custom Flashcard"):
                if term and definition:
                    if not cat: cat = "General"
                    users[user]["flashcards"].setdefault("custom",[]).append({"term":term,"definition":definition,"category":cat,"favorite":False})
                    save_users(users)
                    st.success(f"Custom flashcard added in category '{cat}'!")

            custom_cards = [c for c in users[user]["flashcards"].get("custom",[]) if filter_cat=="All" or c.get("category","General")==filter_cat]
            if not custom_cards:
                st.info("No custom flashcards yet.")
            for i, card in enumerate(custom_cards):
                key = f"custom_flip_{i}"
                if key not in st.session_state.flip_state:
                    st.session_state.flip_state[key] = False

                col1, col2 = st.columns([1,1])
                with col1:
                    if st.button("Flip Card", key=f"button_{key}"):
                        st.session_state.flip_state[key] = not st.session_state.flip_state[key]
                with col2:
                    if st.button("⭐ Favorite", key=f"fav_{key}"):
                        card["favorite"] = not card.get("favorite", False)
                        save_users(users)

                flipped = "flipped" if st.session_state.flip_state[key] else ""
                front_content = card.get("term","")
                back_content = card.get("definition","")
                st.markdown(f"""
                <div class="card-container">
                    <div class="card {flipped}">
                        <div class="front">{front_content}</div>
                        <div class="back">{back_content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ---- PROGRESS DASHBOARD ----
        with tabs[2]:
            total_tutor = len(users[user]["flashcards"].get("tutor",[]))
            total_custom = len(users[user]["flashcards"].get("custom",[]))
            total_cards = total_tutor + total_custom
            fav_tutor = len([c for c in users[user]["flashcards"].get("tutor",[]) if c.get("favorite", False)])
            fav_custom = len([c for c in users[user]["flashcards"].get("custom",[]) if c.get("favorite", False)])
            st.markdown(f"**Total Flashcards:** {total_cards}")
            st.markdown(f"**Total Tutor Flashcards:** {total_tutor}")
            st.markdown(f"**Total Custom Flashcards:** {total_custom}")
            st.markdown(f"**Favorites:** {fav_tutor+fav_custom}")
            st.markdown(f"**Current Streak:** {users[user].get('streak',0)} days")

        st.button("Back to Home", on_click=go_home)
