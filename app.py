import streamlit as st
from datetime import datetime, timedelta
from openai import OpenAI

# --------------------
# PAGE CONFIG
# --------------------
st.set_page_config(page_title="MentraIQ V12", layout="wide")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --------------------
# SESSION STATE INIT
# --------------------
defaults = {
    "page": "Tutor",
    "user": None,
    "admin": False,
    "users": {},
    "card_idx": 0
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# --------------------
# CSS STYLING
# --------------------
st.markdown("""
<style>
/* Background and text */
[data-testid="stAppViewContainer"] {background-color: #0b0f19; color: #e5e7eb;}
/* Nav buttons horizontal */
.nav-btn {
    margin-right: 20px;
    font-weight: 600;
    color: #e5e7eb;
    background: none;
    border: none;
    font-size: 18px;
}
/* Admin button top-right */
.admin-btn {
    position: fixed;
    top: 15px;
    right: 20px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    color: #e5e7eb;
    background: none;
    border: none;
}
/* Flashcard styling */
.flash {
    background: #111827;
    padding: 40px;
    border-radius: 20px;
    text-align: center;
    font-size: 22px;
    perspective: 1000px;
    margin-bottom: 20px;
}
.flash-inner {
    transition: transform 0.6s;
    transform-style: preserve-3d;
    padding: 30px;
    border-radius: 20px;
    color: #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# --------------------
# NAVIGATION FUNCTIONS
# --------------------
def go_tutor(): st.session_state.page = "Tutor"
def go_study(): st.session_state.page = "Study"
def go_account(): st.session_state.page = "Account"
def go_admin(): st.session_state.page = "Admin"

# --------------------
# TOP TITLE
# --------------------
st.markdown("# MentraIQ", unsafe_allow_html=True)

# --------------------
# NAV BAR
# --------------------
c1, c2, c3 = st.columns([1,1,1])
with c1: st.button("Tutor", on_click=go_tutor, key="nav_tutor", help="Go to Tutor")
with c2: st.button("Study Mode", on_click=go_study, key="nav_study", help="Go to Study Mode")
with c3: st.button("Account", on_click=go_account, key="nav_account", help="Go to Account")

# --------------------
# ADMIN BUTTON TOP-RIGHT
# --------------------
if st.button("Admin", key="admin_btn", on_click=go_admin):
    pass

# --------------------
# TUTOR PAGE
# --------------------
if st.session_state.page == "Tutor":
    st.markdown("## AI Tutor")
    st.markdown("Ask anything. Get step-by-step help.")

    question = st.text_area("Your question…", height=150)

    if st.button("Get Answer"):
        if not question.strip():
            st.warning("Type a question first!")
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
                    if st.button("Save to Study Mode"):
                        st.session_state.users[st.session_state.user].setdefault("cards", [])
                        st.session_state.users[st.session_state.user]["cards"].append({
                            "front": question,
                            "back": answer
                        })
                        st.success("Saved to Study Mode!")
                else:
                    st.info("Sign in to save to Study Mode.")

            except:
                st.error("Tutor is busy. Try again later.")

# --------------------
# STUDY MODE
# --------------------
if st.session_state.page == "Study":
    if not st.session_state.user:
        st.warning("Sign in for Study Mode.")
    else:
        user_cards = st.session_state.users[st.session_state.user].get("cards", [])
        st.markdown("### Create a new study card")
        with st.form("new_card"):
            front = st.text_input("Front (Question)")
            back = st.text_input("Back (Answer)")
            if st.form_submit_button("Add Card"):
                if front and back:
                    user_cards.append({"front": front, "back": back})
                    st.session_state.users[st.session_state.user]["cards"] = user_cards
                    st.success("Card added!")
                else:
                    st.error("Both front and back are required.")

        if user_cards:
            idx = st.session_state.card_idx
            card = user_cards[idx]
            flip = st.checkbox("Flip card")
            st.markdown(f"""
            <div class='flash'>
                <div class='flash-inner' style="transform: rotateY({'180deg' if flip else '0deg'})">
                    {card['back'] if flip else card['front']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Prev"):
                    st.session_state.card_idx = (idx - 1) % len(user_cards)
            with c2:
                if st.button("Next ➡️"):
                    st.session_state.card_idx = (idx + 1) % len(user_cards)

            # STREAK TRACKING
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
            st.markdown(f"**📚 Cards saved:** {len(user_cards)}")

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
        st.color_picker("Background", "#0b0f19")
        st.color_picker("Card", "#111827")
        st.color_picker("Accent", "#3b82f6")
        st.text_input("Tutor Title", "AI Tutor")
        st.text_input("Tutor Description", "Ask anything. Get step‑by‑step help.")
        st.button("Exit Admin", on_click=lambda: st.session_state.update({"admin": False, "page":"Tutor"}))
