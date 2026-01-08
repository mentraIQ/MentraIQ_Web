import streamlit as st
from openai import OpenAI
import hashlib
import datetime

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="MentraIQ V10", layout="wide")

st.markdown("""
<style>
/* Hide Streamlit UI */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Background & text */
body { background-color: #0f1117; color: white; }

/* Main buttons */
.stButton > button {
    background-color: #1f2937;
    color: white;
    border-radius: 12px;
    padding: 0.7em 1.5em;
    font-size: 16px;
    border: none;
}

/* Tutor card */
.tutor-card {
    background-color: #111827;
    padding: 40px;
    border-radius: 20px;
    max-width: 700px;
    margin: 60px auto;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

/* Tutor input */
textarea {
    border-radius: 14px !important;
    background-color: #1f2937 !important;
    color: white !important;
    font-size: 18px !important;
}

/* Admin icon */
.admin-btn button {
    background: transparent !important;
    font-size: 22px !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Flashcards */
.flashcard {
    background-color: #1f2937;
    padding: 60px;
    border-radius: 16px;
    text-align: center;
    font-size: 24px;
    cursor: pointer;
    margin: 20px auto;
    max-width: 700px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.3);
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

if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0
if "flipped" not in st.session_state:
    st.session_state.flipped = False

# ======================
# HELPERS
# ======================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ======================
# TOP NAV
# ======================
nav_left, nav_spacer, nav_right = st.columns([6, 3, 1])

with nav_left:
    st.markdown("### MentraIQ")
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("Tutor"):
            st.session_state.page = "Tutor"
    with colB:
        if st.button("Study Mode"):
            st.session_state.page = "Study Mode"
    with colC:
        if st.button("Account"):
            st.session_state.page = "Account"

with nav_right:
    st.markdown("<div class='admin-btn'>", unsafe_allow_html=True)
    if st.button("🛠️"):
        st.session_state.page = "Admin"
    st.markdown("</div>", unsafe_allow_html=True)

# ======================
# TUTOR PAGE
# ======================
if st.session_state.page == "Tutor":
    st.markdown("<div class='tutor-card'>", unsafe_allow_html=True)
    st.markdown("## AI Tutor")
    st.markdown("Ask a question and get a clear explanation.")

    question = st.text_area(
        "",
        placeholder="Type your question here...",
        height=140
    )

    if st.button("Get Answer"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}]
            )
            answer = response.choices[0].message.content
            st.markdown("### Answer")
            st.write(answer)

            if st.session_state.user:
                if st.button("Save to Study Mode"):
                    st.session_state.users[st.session_state.user]["cards"].append({
                        "front": question,
                        "back": answer,
                        "category": "General"
                    })
        except Exception:
            st.error("Tutor is busy. Try again later.")
    st.markdown("</div>", unsafe_allow_html=True)

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
            idx = st.session_state.card_idx
            flipped = st.session_state.flipped
            card = cards[idx]
            content = card["back"] if flipped else card["front"]

            if st.markdown(f"<div class='flashcard'>{content}</div>", unsafe_allow_html=True):
                st.session_state.flipped = not flipped

            colA, colB, colC = st.columns([1,3,1])
            with colA:
                if st.button("Previous") and idx > 0:
                    st.session_state.card_idx -= 1
                    st.session_state.flipped = False
            with colC:
                if st.button("Next") and idx < len(cards)-1:
                    st.session_state.card_idx += 1
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
