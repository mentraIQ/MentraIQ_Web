import streamlit as st
from datetime import date
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MentraIQ V7", layout="wide", page_icon="🧠")

# ---------------- OPENAI CLIENT ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- SESSION STATE ----------------
if "users" not in st.session_state:
    st.session_state.users = {}
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "theme" not in st.session_state:
    st.session_state.theme = {
        "background": "#0b1220",
        "text": "#e5e7eb",
        "button": "#1e293b",
        "flashcard_bg": "#111827",
        "flashcard_text": "#e5e7eb"
    }

# ---------------- CSS ----------------
st.markdown(f"""
<style>
html, body, [class*="css"] {{
    background-color: {st.session_state.theme['background']};
    color: {st.session_state.theme['text']};
    font-family: 'Inter', sans-serif;
}}
input, textarea {{
    background-color: {st.session_state.theme['flashcard_bg']} !important;
    color: white !important;
    border-radius: 10px !important;
}}
button {{
    background-color: {st.session_state.theme['button']} !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 600;
}}
.flashcard {{
    background-color: {st.session_state.theme['flashcard_bg']};
    color: {st.session_state.theme['flashcard_text']};
    border-radius: 20px;
    padding: 40px;
    min-height: 220px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    cursor: pointer;
    transition: transform 0.6s;
    transform-style: preserve-3d;
}}
.flashcard.flipped {{
    transform: rotateY(180deg);
}}
</style>
""", unsafe_allow_html=True)

# ---------------- USER AUTH ----------------
def create_account(username, password):
    if username in st.session_state.users:
        st.warning("Username already exists!")
    else:
        st.session_state.users[username] = {
            "password": password,
            "streak": 1,
            "last_login": str(date.today()),
            "flashcards": []
        }
        st.success("Account created! You can log in now.")

def login(username, password):
    if username in st.session_state.users:
        if st.session_state.users[username]["password"] == password:
            st.session_state.user = username
            st.success("Logged in!")
        else:
            st.error("Incorrect password!")
    else:
        st.error("Username not found!")

# ---------------- NAVIGATION ----------------
if st.session_state.page == "Home":
    st.markdown("<h1 style='text-align:center; color:#60a5fa;'>MentraIQ V7 🧠</h1>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Tutor"):
            st.session_state.page = "Tutor"
    with col2:
        if st.button("Flashcards"):
            st.session_state.page = "Flashcards"
    with col3:
        if st.button("Account"):
            st.session_state.page = "Account"
    with col4:
        if st.button("Admin"):
            pwd = st.text_input("Admin Password", type="password")
            if pwd == "mentraqueen":  # admin password
                st.session_state.admin_mode = True
                st.session_state.page = "Admin"
            elif pwd:
                st.error("Incorrect admin password!")

# ---------------- TUTOR ----------------
elif st.session_state.page == "Tutor":
    st.title("AI Tutor ✨")
    question = st.text_area("Ask anything", placeholder="Explain photosynthesis, solve x² + 4x = 0...")
    if st.button("Get Answer"):
        if question.strip():
            with st.spinner("Thinking... 🤖"):
                try:
                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role":"system","content":"Explain step by step clearly like a tutor."},
                            {"role":"user","content": question}
                        ],
                        max_tokens=500
                    )
                    ans = response.choices[0].message.content
                    st.markdown(f'<div class="flashcard" id="tutor_card">{ans}</div>', unsafe_allow_html=True)
                    # Save flashcard
                    if st.session_state.user:
                        cat = st.text_input("Category (optional)", value="General")
                        if st.button("Save Flashcard"):
                            st.session_state.users[st.session_state.user]["flashcards"].append({
                                "front": question,
                                "back": ans,
                                "category": cat or "General"
                            })
                            st.success("Saved!")
                except Exception as e:
                    if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                        st.error("Out of tokens, try later.")
                    else:
                        st.error(f"AI error: {e}")
        else:
            st.warning("Type a question first")

# ---------------- FLASHCARDS ----------------
elif st.session_state.page == "Flashcards":
    st.title("My Flashcards 📚")
    if not st.session_state.user:
        st.info("Sign in to see flashcards")
    else:
        user = st.session_state.user
        cards = st.session_state.users[user]["flashcards"]

        st.subheader("Create Flashcard")
        col1, col2 = st.columns(2)
        with col1:
            front = st.text_input("Front")
        with col2:
            back = st.text_input("Back")
        category = st.text_input("Category", placeholder="English Final")
        if st.button("Add Flashcard"):
            if front and back:
                cards.append({"front": front, "back": back, "category": category or "General"})
                st.success("Flashcard added ✨")
            else:
                st.warning("Both sides required")

        st.subheader("Study")
        if cards:
            for idx, card in enumerate(cards):
                st.markdown(f'<div class="flashcard" id="card_{idx}">{card["front"]}</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <script>
                const card{idx} = document.getElementById("card_{idx}");
                card{idx}.addEventListener("click", () => {{
                    if(card{idx}.innerHTML === `{card["front"]}`) {{
                        card{idx}.innerHTML = `{card["back"]}`;
                    }} else {{
                        card{idx}.innerHTML = `{card["front"]}`;
                    }}
                }});
                </script>
                """, unsafe_allow_html=True)
        else:
            st.info("No flashcards yet")

# ---------------- ACCOUNT ----------------
elif st.session_state.page == "Account":
    st.title("Account 👤")
    if not st.session_state.user:
        st.subheader("Sign Up")
        u1 = st.text_input("Username")
        p1 = st.text_input("Password", type="password")
        if st.button("Create Account"):
            if u1 and p1:
                create_account(u1, p1)
        st.subheader("Login")
        u2 = st.text_input("Username Login")
        p2 = st.text_input("Password Login", type="password")
        if st.button("Login"):
            if u2 and p2:
                login(u2, p2)
    else:
        user = st.session_state.user
        data = st.session_state.users[user]
        st.write(f"**Username:** {user}")
        st.write(f"🔥 **Streak:** {data['streak']} days")
        st.write(f"📚 **Flashcards:** {len(data['flashcards'])}")
        if st.button("Log out"):
            st.session_state.user = None

# ---------------- ADMIN ----------------
elif st.session_state.page == "Admin":
    st.title("Admin Panel 🔧")
    st.subheader("Theme Customization")
    st.session_state.theme["background"] = st.color_picker("Background", st.session_state.theme["background"])
    st.session_state.theme["text"] = st.color_picker("Text", st.session_state.theme["text"])
    st.session_state.theme["button"] = st.color_picker("Buttons", st.session_state.theme["button"])
    st.session_state.theme["flashcard_bg"] = st.color_picker("Flashcards BG", st.session_state.theme["flashcard_bg"])
    st.session_state.theme["flashcard_text"] = st.color_picker("Flashcards Text", st.session_state.theme["flashcard_text"])
    st.info("Changes apply immediately!")

