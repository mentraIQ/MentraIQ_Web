import streamlit as st
from datetime import date

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="MentraIQ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- GLOBAL CSS --------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0b1220;
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

/* Remove yellow Streamlit alerts */
div[data-testid="stAlert"] {
    background-color: #111827 !important;
    color: #f9fafb !important;
    border-radius: 14px;
    border: none;
}
div[data-testid="stAlert"] > div:first-child {
    display: none !important;
}

/* Inputs */
input, textarea {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Buttons */
button {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 600;
}

/* Flashcard */
.flashcard {
    background-color: #111827;
    border-radius: 20px;
    padding: 40px;
    min-height: 220px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Tutor"

# -------------------- SIDEBAR --------------------
st.sidebar.title("MentraIQ")

pages = ["Tutor", "Flashcards", "Account"]
st.session_state.page = st.sidebar.radio("Navigate", pages)

# -------------------- USER AUTH --------------------
def login(username):
    if username not in st.session_state.users:
        st.session_state.users[username] = {
            "streak": 1,
            "last_login": str(date.today()),
            "flashcards": []
        }
    st.session_state.user = username

# -------------------- TUTOR (NO LOGIN REQUIRED) --------------------
if st.session_state.page == "Tutor":
    st.title("AI Tutor ✨")

    question = st.text_area(
        "Ask anything",
        placeholder="Explain photosynthesis, solve x² + 4x = 0, summarize Hamlet..."
    )

    if st.button("Get Answer"):
        if question.strip():
            st.success("Answer generated ✨ (AI placeholder)")
            st.write(
                "This is where your AI response goes. "
                "When you're ready, we connect it to the API."
            )
        else:
            st.warning("Type a question first")

# -------------------- FLASHCARDS --------------------
elif st.session_state.page == "Flashcards":
    st.title("Flashcards 📚")

    if not st.session_state.user:
        st.info("Sign in to save and review flashcards")
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
                cards.append({
                    "front": front,
                    "back": back,
                    "category": category or "General"
                })
                st.success("Flashcard added ✨")
            else:
                st.warning("Both sides required")

        st.divider()
        st.subheader("Study")

        if cards:
            idx = st.number_input(
                "Card number",
                min_value=1,
                max_value=len(cards),
                value=1
            ) - 1

            show_back = st.toggle("Flip card")

            content = cards[idx]["back"] if show_back else cards[idx]["front"]

            st.markdown(
                f'<div class="flashcard">{content}</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("No flashcards yet")

# -------------------- ACCOUNT --------------------
elif st.session_state.page == "Account":
    st.title("Account 👤")

    if not st.session_state.user:
        username = st.text_input("Username")
        if st.button("Sign in"):
            if username.strip():
                login(username)
                st.success("Signed in ✨")
    else:
        user = st.session_state.user
        data = st.session_state.users[user]

        st.write(f"**Username:** {user}")
        st.write(f"🔥 **Streak:** {data['streak']} days")
        st.write(f"📚 **Flashcards:** {len(data['flashcards'])}")

        if st.button("Log out"):
            st.session_state.user = None

