import streamlit as st
import json
import datetime

# --------------------------
# Session State Initialization
# --------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "user" not in st.session_state:
    st.session_state.user = ""
if "study_progress" not in st.session_state:
    st.session_state.study_progress = {}
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "last_study_date" not in st.session_state:
    st.session_state.last_study_date = None
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# --------------------------
# Load Content
# --------------------------
try:
    with open("content.json", "r") as f:
        content = json.load(f)
except:
    content = {
        "title": "mentraIQ",
        "subtitle": "Your personal study space",
        "study_mode_text": "Sign in for Study Mode",
        "tutor_placeholder": "AI Tutor coming soon...",
        "coming_soon": "AI Tutor launching soon"
    }

# --------------------------
# Helper Functions
# --------------------------
def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

def go_admin():
    password = st.text_input("Enter admin password:", type="password", key="admin_pass")
    if password == "mentraqueen":
        st.session_state.admin_mode = True
        st.success("Admin mode enabled!")
    elif password:
        st.error("Incorrect password 💙")

def flip_card(card_front, card_back):
    show_back = st.checkbox("Flip Card", key=card_front)
    return card_back if show_back else card_front

def update_streak():
    today = datetime.date.today()
    if st.session_state.last_study_date != today:
        if st.session_state.last_study_date == today - datetime.timedelta(days=1):
            st.session_state.streak += 1
        else:
            st.session_state.streak = 1
        st.session_state.last_study_date = today

# --------------------------
# Page Displays
# --------------------------
def show_home():
    st.markdown(f"# {content['title']}")
    st.markdown(f"### {content['subtitle']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Tutor"):
            st.session_state.page = "Tutor"
    with col2:
        if st.button("Study Mode"):
            st.session_state.page = "StudyMode"
    if st.button("Account"):
        st.session_state.page = "Account"

def show_tutor():
    st.markdown("## Tutor")
    st.text_input("Ask a question:", placeholder=content["tutor_placeholder"])
    if st.button("Back"):
        st.session_state.page = "Home"

def show_study_mode():
    st.markdown("## Study Mode")
    if not st.session_state.user:
        st.info(content["study_mode_text"])
        return

    # Example flashcards
    cards = [
        {"front": "What is 2+2?", "back": "4", "category": "Math"},
        {"front": "Capital of France?", "back": "Paris", "category": "Geography"},
    ]

    update_streak()
    st.markdown(f"**Current Streak:** {st.session_state.streak} days")

    for card in cards:
        st.markdown(f"### Category: {card['category']}")
        answer = flip_card(card["front"], card["back"])
        st.write(answer)
        st.write("---")

    if st.button("Back"):
        st.session_state.page = "Home"

def show_account():
    st.markdown("## Account")
    st.text_input("Username", key="username_input")
    st.text_input("Password", type="password", key="password_input")
    if st.button("Sign In"):
        st.session_state.user = st.session_state.username_input
        st.success(f"Signed in as {st.session_state.user}")
    if st.button("Back"):
        st.session_state.page = "Home"

def show_admin():
    if st.session_state.admin_mode:
        st.markdown("## Admin Panel")
        new_title = st.text_input("App Title:", content["title"])
        new_subtitle = st.text_input("App Subtitle:", content["subtitle"])
        if st.button("Save Changes"):
            content["title"] = new_title
            content["subtitle"] = new_subtitle
            with open("content.json", "w") as f:
                json.dump(content, f)
            st.success("Changes saved!")
    else:
        go_admin()
    if st.button("Back"):
        st.session_state.page = "Home"

# --------------------------
# Page Routing
# --------------------------
if st.session_state.page == "Home":
    show_home()
elif st.session_state.page == "Tutor":
    show_tutor()
elif st.session_state.page == "StudyMode":
    show_study_mode()
elif st.session_state.page == "Account":
    show_account()
elif st.session_state.page == "Admin":
    show_admin()

# --------------------------
# Dark / Light Mode Styling
# --------------------------
if st.session_state.dark_mode:
    background = "#121212"
    text_color = "#FFFFFF"
    button_bg = "#FFFFFF"
    button_text = "#000000"
else:
    background = "#FFFFFF"
    text_color = "#000000"
    button_bg = "#121212"
    button_text = "#FFFFFF"

st.markdown(f"""
<style>
body {{
    background-color: {background};
    color: {text_color};
}}
button, .stButton>button {{
    background-color: {button_bg};
    color: {button_text};
}}
#admin_button {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    font-weight: bold;
    font-size: 20px;
}}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Admin & Settings Buttons
# --------------------------
st.markdown('<button id="admin_button" onclick="window.location.href=\'#\'">A</button>', unsafe_allow_html=True)
if st.button("⚙️ Settings"):
    toggle_dark_mode()


