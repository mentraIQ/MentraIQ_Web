import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta

# --------------------
# CONFIG
# --------------------
st.set_page_config(page_title="MentraIQ V7", layout="wide")
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
    "card_idx": 0
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# --------------------
# CSS STYLING
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
    padding: 40px;
    border-radius: 20px;
    text-align: center;
    font-size: 22px;
    perspective: 1000px;
}}
.flash-inner {{
    transition: transform 0.6s;
    transform-style: preserve-3d;
    padding: 30px;
    border-radius: 20px;
}}
</style>
""", unsafe_allow_html=True)

# --------------------
# NAVIGATION FUNCTIONS
# --------------------
def go_admin():
    st.session_state.page = "Admin"

def go_tutor():
    st.session_state.page = "Tutor"

def go_study():
    st.session_state.page = "Study"

def go_account():
    st.session_state.page = "Account"

# --------------------
# NAV BAR
# --------------------
c1, c2, c3 = st.columns([1,1,1])
with c1:
    st.button("Tutor", key="nav_tutor", on_click=go_tutor)
with c2:
    st.button("Study Mode", key="nav_study", on_click=go_study)
with c3:
    st.button("Account", key="nav_account", on_click=go_account)

st.markdown(
    "<div class='admin' onclick=\"document.getElementById('admin').click()\">⚙️</div>",
    unsafe_allow_html=True
)
st.button("admin", key="admin", on_click=go_admin)

# --------------------
# TUTOR PAGE
# --------------------
if st.session_state.page == "Tutor":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown(f"## {st.session_state.tutor_title}")
    st.markdown(st.session_state.tutor_desc)

    question = st.text_area("", placeholder="Type your question here…", height=150)

    if st.button(st.session_state.btn_answer):
        if not question.strip():
            st.warning("Ask something first.")
        else:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": question}]
                )
                answer = response.choices[0].message.content
                st.markdown("### Answer")
                st.write(answer)

                if st.session_state.user:
                    if st.button(st.session_state.btn_save):
                        st.session_state.users[st.session_state.user]["cards"].append({
                            "front": question,
                            "back": answer
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
            idx = st.session_state.card_idx
            card = cards[idx]
            flipped = st.checkbox("Flip card")

            st.markdown(f"""
            <div class='flash'>
                <div class='flash-inner' style="transform: rotateY({'180deg' if flipped else '0deg'})">
                    {card['back'] if flipped else card['front']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Prev"):
                    st.session_state.card_idx = (idx - 1) % len(cards)
            with c2:
                if st.button("Next ➡️"):
                    st.session_state.card_idx = (idx + 1) % len(cards)

            # --------------------
            # STREAK / PROGRESS
            # --------------------
            user = st.session_state.user
            st.session_state.users[user].setdefault("streak", 0)
            st.session_state.users[user].setdefault("last_login", "")
            today = datetime.today().date()
            last = st.session_state.users[user]["last_login"]

            if str(today) != last:
                if last:
                    yesterday = today - timedelta(days=1)
                    if str(yesterday) == last:
                        st.session_state.users[user]["streak"] += 1
                    else:
                        st.session_state.users[user]["streak"] = 1
                else:
                    st.session_state.users[user]["streak"] = 1
                st.session_state.users[user]["last_login"] = str(today)

            st.markdown(f"**🔥 Current streak:** {st.session_state.users[user]['streak']} day(s)")
            st.markdown(f"**📚 Cards saved:** {len(st.session_state.users[user]['cards'])}")

# --------------------
# ACCOUNT PAGE
# --------------------
if st.session_state.page == "Account":
    if not st.session_state.user:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Sign In / Sign Up"):
            if username not in st.session_state.users:
                st.session_state.users[username] = {"password": password, "cards": []}
            if st.session_state.users[username]["password"] == password:
                st.session_state.user = username
                st.success("Logged in!")
            else:
                st.error("Wrong password.")
    else:
        st.success(f"Logged in as {st.session_state.user}")
        if st.button("Log out"):
            st.session_state.user = None
            st.session_state.page = "Tutor"

# --------------------
# ADMIN PAGE
# --------------------
if st.session_state.page == "Admin":
    if not st.session_state.admin:
        pw = st.text_input("Admin password", type="password")
        if st.button("Enter Admin"):
            if pw == "mentraqueen":
                st.session_state.admin = True
            else:
                st.error("Wrong password.")
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

