import streamlit as st
from datetime import date
from openai import OpenAI  # Latest SDK, no error module

# ---------------- APP TITLE ----------------
st.markdown(
    """
    <h1 style='text-align:center; color:#60a5fa; font-size:48px; margin-bottom:20px;'>
        MentraIQ V6 🧠
    </h1>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="MentraIQ V6", layout="wide", page_icon="🧠")

# ---------------- OPENAI CLIENT ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- SESSION STATE ----------------
if "users" not in st.session_state:
    st.session_state.users = {}
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Tutor"
if "flip" not in st.session_state:
    st.session_state.flip = {}
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# ---------------- CSS ----------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0b1220;
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}
input, textarea {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 10px !important;
}
button {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 600;
}
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

# ---------------- NAVIGATION ----------------
st.sidebar.title("MentraIQ")
pages = ["Tutor", "Flashcards", "Account"]
# 3-dot menu for admin mode
if st.sidebar.button("⋮ Admin Mode"):
    st.session_state.admin_mode = not st.session_state.admin_mode

st.session_state.page = st.sidebar.radio("Navigate", pages)

# ---------------- USER AUTH ----------------
def login(username):
    if username not in st.session_state.users:
        st.session_state.users[username] = {
            "streak": 1,
            "last_login": str(date.today()),
            "flashcards": []
        }
    st.session_state.user = username

# ---------------- TUTOR ----------------
if st.session_state.page == "Tutor":
    st.title("AI Tutor ✨")
    question = st.text_area(
        "Ask anything",
        placeholder="Explain photosynthesis, solve x² + 4x = 0, summarize Hamlet..."
    )

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
                    st.markdown(f'<div class="flashcard">{ans}</div>', unsafe_allow_html=True)

                    if st.session_state.user:
                        category = st.text_input("Category (optional)", value="General")
                        if st.button("Save as Flashcard"):
                            st.session_state.users[st.session_state.user]["flashcards"].append({
                                "front": question,
                                "back": ans,
                                "category": category or "General"
                            })
                            st.success("Saved to flashcards!")

                except Exception as e:
                    if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                        st.error("You’ve run out of tokens! Please try again later.")
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
            st.markdown(f'<div class="flashcard">{content}</div>', unsafe_allow_html=True)
        else:
            st.info("No flashcards yet")

# ---------------- ACCOUNT ----------------
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

# ---------------- ADMIN MODE ----------------
if st.session_state.admin_mode:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Admin Panel")
    st.sidebar.write("👀 View all users and flashcards:")
    for u, info in st.session_state.users.items():
        st.sidebar.write(f"**{u}** - {len(info['flashcards'])} flashcards, streak: {info['streak']} days")


