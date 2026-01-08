import streamlit as st
from openai import OpenAI

# --------------------
# CONFIG
# --------------------
st.set_page_config(page_title="MentraIQ", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --------------------
# SESSION STATE INIT
# --------------------
defaults = {
    "page": "Tutor",
    "user": None,
    "admin": False,
    "users": {},
    "bg": "#0b0f19",
    "card": "#111827",
    "text": "#e5e7eb",
    "accent": "#3b82f6",
    "tutor_title": "AI Tutor",
    "tutor_desc": "Ask anything. Get clear, step‑by‑step help.",
    "btn_answer": "Get Answer",
    "btn_save": "Save to Study Mode",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# --------------------
# STYLES
# --------------------
st.markdown(f"""
<style>
html, body, [data-testid="stApp"] {{
    background-color: {st.session_state.bg};
    color: {st.session_state.text};
}}
.main-card {{
    background: {st.session_state.card};
    max-width: 720px;
    margin: 60px auto;
    padding: 40px;
    border-radius: 22px;
    box-shadow: 0 30px 60px rgba(0,0,0,.5);
}}
button {{
    background-color: {st.session_state.accent} !important;
    color: white !important;
    border-radius: 12px !important;
}}
.nav-btn {{
    background: none !important;
    color: {st.session_state.text} !important;
    font-weight: 600;
}}
.admin {{
    position: fixed;
    top: 14px;
    right: 20px;
    font-size: 20px;
    cursor: pointer;
}}
.flash {{
    background: {st.session_state.card};
    padding: 35px;
    border-radius: 20px;
    text-align: center;
    font-size: 22px;
}}
</style>
""", unsafe_allow_html=True)

# --------------------
# NAV BAR
# --------------------
c1, c2, c3 = st.columns([1,1,1])
with c1:
    if st.button("Tutor", key="nav_tutor"):
        st.session_state.page = "Tutor"
with c2:
    if st.button("Study Mode", key="nav_study"):
        st.session_state.page = "Study"
with c3:
    if st.button("Account", key="nav_account"):
        st.session_state.page = "Account"

st.markdown(
    "<div class='admin' onclick=\"document.getElementById('admin').click()\">⚙️</div>",
    unsafe_allow_html=True
)
st.button("admin", key="admin", on_click=lambda: setattr(st.session_state, "page", "Admin"))

# --------------------
# TUTOR PAGE
# --------------------
if st.session_state.page == "Tutor":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown(f"## {st.session_state.tutor_title}")
    st.markdown(st.session_state.tutor_desc)

    q = st.text_area("", placeholder="Type your question here…", height=150)

    if st.button(st.session_state.btn_answer):
        if not q.strip():
            st.warning("Ask something first.")
        else:
            try:
                r = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":q}]
                )
                a = r.choices[0].message.content
                st.markdown("### Answer")
                st.write(a)

                if st.session_state.user:
                    if st.button(st.session_state.btn_save):
                        st.session_state.users[st.session_state.user]["cards"].append({
                            "front": q,
                            "back": a
                        })
                        st.success("Saved!")
                else:
                    st.info("Sign in to save to Study Mode.")
            except:
                st.error("Tutor is busy. Try again later.")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------
# STUDY MODE
# --------------------
if st.session_state.page == "Study":
    if not st.session_state.user:
        st.warning("Sign in for Study Mode.")
    else:
        cards = st.session_state.users[st.session_state.user]["cards"]
        if not cards:
            st.info("No cards yet.")
        else:
            idx = st.session_state.setdefault("card_idx", 0)
            flip = st.checkbox("Flip card")

            card = cards[idx]
            st.markdown("<div class='flash'>", unsafe_allow_html=True)
            st.write(card["back"] if flip else card["front"])
            st.markdown("</div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Prev"):
                    st.session_state.card_idx = (idx - 1) % len(cards)
            with c2:
                if st.button("Next ➡️"):
                    st.session_state.card_idx = (idx + 1) % len(cards)

# --------------------
# ACCOUNT
# --------------------
if st.session_state.page == "Account":
    if not st.session_state.user:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Sign In / Sign Up"):
            if u not in st.session_state.users:
                st.session_state.users[u] = {"password": p, "cards": []}
            if st.session_state.users[u]["password"] == p:
                st.session_state.user = u
                st.success("Logged in!")
            else:
                st.error("Wrong password.")
    else:
        st.success(f"Logged in as {st.session_state.user}")
        if st.button("Log out"):
            st.session_state.user = None
            st.session_state.page = "Tutor"

# --------------------
# ADMIN
# --------------------
if st.session_state.page == "Admin":
    if not st.session_state.admin:
        pw = st.text_input("Admin password", type="password")
        if st.button("Enter Admin"):
            if pw == "mentraqueen":
                st.session_state.admin = True
            else:
                st.error("Nope.")
    else:
        st.subheader("Admin Panel (Live Edit)")
        st.session_state.bg = st.color_picker("Background", st.session_state.bg)
        st.session_state.card = st.color_picker("Card", st.session_state.card)
        st.session_state.accent = st.color_picker("Accent", st.session_state.accent)

        st.session_state.tutor_title = st.text_input("Tutor Title", st.session_state.tutor_title)
        st.session_state.tutor_desc = st.text_input("Tutor Description", st.session_state.tutor_desc)
        st.session_state.btn_answer = st.text_input("Answer Button Text", st.session_state.btn_answer)
        st.session_state.btn_save = st.text_input("Save Button Text", st.session_state.btn_save)

        if st.button("Exit Admin"):
            st.session_state.admin = False
            st.session_state.page = "Tutor"

