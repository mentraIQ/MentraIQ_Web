import streamlit as st
import json, os, datetime
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MentraIQ", page_icon="🧠", layout="centered")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
USERS_FILE = "users.json"

# ---------------- HELPERS ----------------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

users = load_users()

# ---------------- SESSION STATE ----------------
st.session_state.setdefault("page", "home")
st.session_state.setdefault("user", None)
st.session_state.setdefault("flip", {})

# ---------------- STYLING ----------------
st.markdown("""
<style>
.stApp { background:#0d1b2a; color:#f5f5f5; }
.stButton>button {
  background:#f5f5f5; color:#0d1b2a; border-radius:12px;
  height:3em; width:100%; font-size:16px; border:none;
}
.stTextInput input, .stSelectbox select {
  background:#f5f5f5; color:#0d1b2a; border-radius:8px;
}
.card-wrap { perspective:1000px; max-width:500px; height:260px; margin:auto; margin-top:20px; }
.card {
  width:100%; height:100%; position:relative;
  transform-style:preserve-3d; transition:0.8s;
  border-radius:18px; box-shadow:0 8px 16px rgba(0,0,0,.3);
}
.card.flip { transform:rotateY(180deg); }
.side {
  position:absolute; width:100%; height:100%;
  backface-visibility:hidden; border-radius:18px;
  display:flex; align-items:center; justify-content:center;
  text-align:center; padding:25px; font-size:18px;
}
.front { background:#f5f5f5; color:#0d1b2a; }
.back { background:#f5f5f5; color:#0d1b2a; transform:rotateY(180deg); }
</style>
""", unsafe_allow_html=True)

# ---------------- NAV ----------------
def nav(page): st.session_state.page = page

# ---------------- SIDEBAR LOGIN ----------------
st.sidebar.title("MentraIQ Login")
u = st.sidebar.text_input("Username")
p = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Create Account"):
    if u in users:
        st.sidebar.error("Username exists")
    else:
        users[u] = {
            "password": p,
            "streak": 0,
            "last": "",
            "flashcards": {"tutor": [], "custom": []}
        }
        save_users(users)
        st.sidebar.success("Account created!")

if st.sidebar.button("Log In"):
    if u in users and users[u]["password"] == p:
        st.session_state.user = u
        st.sidebar.success(f"Logged in as {u}")
    else:
        st.sidebar.error("Invalid login")

logged = st.session_state.user is not None

# ---------------- HOME ----------------
if st.session_state.page == "home":
    st.title("MentraIQ 🧠")
    st.subheader("Quizlet ✕ Gauth vibes")
    st.button("📘 Tutor", on_click=nav, args=("tutor",))
    st.button("🃏 Flashcards", on_click=nav, args=("cards",))

# ---------------- TUTOR ----------------
elif st.session_state.page == "tutor":
    st.title("AI Tutor")

    subject = st.selectbox("Subject", ["Math", "Science", "English"])
    q = st.text_input("Ask your question")

    if q:
        prompt = {
            "Math":"Explain step by step clearly.",
            "Science":"Explain simply with examples.",
            "English":"Help with grammar and understanding."
        }

        try:
            r = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role":"system","content":prompt[subject]},
                    {"role":"user","content":q}
                ],
                max_tokens=300
            )
            ans = r.choices[0].message.content

            st.markdown(f"""
            <div class="card-wrap">
              <div class="card">
                <div class="side front">{q}</div>
                <div class="side back">{ans}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if logged:
                cat = st.text_input("Category (optional)", value="General")
                if st.button("Save as Flashcard"):
                    users[st.session_state.user]["flashcards"]["tutor"].append({
                        "question": q,
                        "answer": ans,
                        "category": cat or "General",
                        "favorite": False
                    })
                    save_users(users)
                    st.success("Saved!")

        except:
            st.error("AI unavailable")

    st.button("⬅ Home", on_click=nav, args=("home",))

# ---------------- FLASHCARDS ----------------
elif st.session_state.page == "cards":
    st.title("My Flashcards")

    if not logged:
        st.warning("Log in to see flashcards")
        st.button("⬅ Home", on_click=nav, args=("home",))
    else:
        user = st.session_state.user

        cards = (
            users[user]["flashcards"].get("tutor", []) +
            users[user]["flashcards"].get("custom", [])
        )

        categories = ["All"] + sorted(set(c.get("category","General") for c in cards))
        filt = st.selectbox("Category", categories)

        for i, c in enumerate(cards):
            if filt != "All" and c.get("category","General") != filt:
                continue

            key = f"flip{i}"
            st.session_state.flip.setdefault(key, False)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Flip", key=f"b{key}"):
                    st.session_state.flip[key] = not st.session_state.flip[key]
            with col2:
                if st.button("⭐", key=f"f{key}"):
                    c["favorite"] = not c.get("favorite", False)
                    save_users(users)

            cls = "flip" if st.session_state.flip[key] else ""
            front = c.get("question") or c.get("term")
            back = c.get("answer") or c.get("definition")

            st.markdown(f"""
            <div class="card-wrap">
              <div class="card {cls}">
                <div class="side front">{front}</div>
                <div class="side back">{back}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.button("⬅ Home", on_click=nav, args=("home",))


