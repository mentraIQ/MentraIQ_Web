import streamlit as st
from openai import OpenAI
import hashlib
import datetime

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="MentraIQ", layout="wide")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

body {
    background-color: #0f1117;
    color: white;
}

.stButton>button {
    background-color: #1f2937;
    color: white;
    border-radius: 8px;
    padding: 0.5em 1em;
}

.flashcard {
    background-color: #1f2937;
    padding: 60px;
    border-radius: 16px;
    text-align: center;
    font-size: 24px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ======================
# VERSION
# ======================
st.markdown("## MentraIQ V10")

# ======================
# OPENAI CLIENT
# ======================
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

# ======================
# STATE
# ======================
if "page" not in st.session_state:
    st.session_state.page = "Tutor"

if "users" not in st.session_state:
    st.session_state.users = {}

if "user" not in st.session_state:
    st.session_state.user = None

if "admin" not in st.session_state:
    st.session_state.admin = False

# ======================
# HELPERS
# ======================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def nav_button(name):
    if st.button(name):
        st.session_state.page = name

# ======================
# TOP NAV
# ======================
col1, col2, col3, col4 = st.columns([6,1,1,1])

with col1:
    nav_button("Tutor")
    nav_button("Study Mode")
    nav_button("Account")

with col4:
    if st.button("⚙️"):
        st.session_state.page = "Admin"

# ======================
# TUTOR
# ======================
if st.session_state.page == "Tutor":
    st.subheader("AI Tutor")

    question = st.text_area("Ask anything")

    if st.button("Get Answer"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":question}]
            )
            answer = response.choices[0].message.content
            st.success(answer)

            if st.session_state.user:
                if st.button("Save to Study Mode"):
                    user = st.session_state.user
                    st.session_state.users[user]["cards"].append({
                        "front": question,
                        "back": answer,
                        "category": "General"
                    })
        except Exception:
            st.error("Tutor is busy. Try again later.")

# ======================
# STUDY MODE
# ======================
if st.session_state.page == "Study Mode":
    if not st.session_state.user:
        st.warning("Sign in for Study Mode")
    else:
        st.subheader("Study Mode")

        user = st.session_state.user
        cards = st.session_state.users[user]["cards"]

        if not cards:
            st.info("No cards yet.")
        else:
            idx = st.session_state.get("card_idx", 0)
            flipped = st.session_state.get("flipped", False)

            card = cards[idx]
            content = card["back"] if flipped else card["front"]

            if st.button("← Back"):
                st.session_state.page = "Tutor"

            if st.markdown(f"<div class='flashcard'>{content}</div>", unsafe_allow_html=True):
                st.session_state.flipped = not flipped

            colA, colB = st.columns(2)
            with colA:
                if st.button("Previous") and idx > 0:
                    st.session_state.card_idx = idx - 1
                    st.session_state.flipped = False
            with colB:
                if st.button("Next") and idx < len(cards)-1:
                    st.session_state.card_idx = idx + 1
                    st.session_state.flipped = False

# ======================
# ACCOUNT
# ======================
if st.session_state.page == "Account":
    st.subheader("Account")

    if st.session_state.user:
        st.success(f"Logged in as {st.session_state.user}")
        if st.button("Log out"):
            st.session_state.user = None
            st.session_state.page = "Tutor"
    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Sign In / Register"):
            if username not in st.session_state.users:
                st.session_state.users[username] = {
                    "pw": hash_pw(password),
                    "cards": [],
                    "streak": 1,
                    "last": str(datetime.date.today())
                }
            if st.session_state.users[username]["pw"] == hash_pw(password):
                st.session_state.user = username
                st.session_state.page = "Tutor"
            else:
                st.error("Wrong password")

# ======================
# ADMIN
# ======================
if st.session_state.page == "Admin":
    if not st.session_state.admin:
        pw = st.text_input("Admin password", type="password")
        if st.button("Enter Admin"):
            if pw == "mentraqueen":
                st.session_state.admin = True
            else:
                st.error("Nope.")
    else:
        st.subheader("Admin Panel")
        st.info("Theme + text controls coming here")

        if st.button("Exit Admin"):
            st.session_state.admin = False
            st.session_state.page = "Tutor"

