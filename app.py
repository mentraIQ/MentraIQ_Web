import streamlit as st
import json
import datetime

# --------------------------
# SESSION STATE INIT
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
if "show_account_panel" not in st.session_state:
    st.session_state.show_account_panel = False
if "show_settings_panel" not in st.session_state:
    st.session_state.show_settings_panel = False

# --------------------------
# LOAD CONTENT
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
    }

# --------------------------
# HELPER FUNCTIONS
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

def update_streak():
    today = datetime.date.today()
    if st.session_state.last_study_date != today:
        if st.session_state.last_study_date == today - datetime.timedelta(days=1):
            st.session_state.streak += 1
        else:
            st.session_state.streak = 1
        st.session_state.last_study_date = today

# --------------------------
# FLASHCARD CLASS
# --------------------------
class FlashCard:
    def __init__(self, front, back, category="General"):
        self.front = front
        self.back = back
        self.category = category
        self.show_back = False

    def render(self, key):
        card_html = f"""
        <div onclick="this.querySelector('.front').style.display = (this.querySelector('.front').style.display=='none')?'block':'none';
                    this.querySelector('.back').style.display = (this.querySelector('.back').style.display=='none')?'block':'none';"
             style="border:1px solid #ccc; padding:20px; width:400px; height:200px; margin-bottom:20px; border-radius:10px; cursor:pointer; background-color:#fff; color:#000;">
            <div class="front">{self.front}</div>
            <div class="back" style="display:none;">{self.back}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

# --------------------------
# PAGE DISPLAYS
# --------------------------
def show_home():
    st.markdown(f"<h1 style='font-size:50px'>{content['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3>{content['subtitle']}</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Tutor"):
            st.session_state.page = "Tutor"
    with col2:
        if st.button("Study Mode"):
            st.session_state.page = "StudyMode"

def show_tutor():
    st.markdown("## Tutor")
    st.text_input("Ask a question:", placeholder=content["tutor_placeholder"], key="tutor_input")
    if st.button("Back"):
        st.session_state.page = "Home"

def show_study_mode():
    st.markdown("## Study Mode")
    if not st.session_state.user:
        st.info(content["study_mode_text"])
        return

    # Example flashcards
    cards = [
        FlashCard("What is 2+2?", "4", "Math"),
        FlashCard("Capital of France?", "Paris", "Geography")
    ]

    update_streak()
    st.markdown(f"**Current Streak:** {st.session_state.streak} days")

    for card in cards:
        card.render(card.front)

    if st.button("Back"):
        st.session_state.page = "Home"

def show_account_panel():
    st.markdown("## Account Login")
    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")
    if st.button("Sign In"):
        st.session_state.user = username
        st.success(f"Signed in as {username}")
        st.session_state.show_account_panel = False

def show_settings_panel():
    st.markdown("## Settings")
    if st.button("Toggle Dark/Light Mode"):
        toggle_dark_mode()

def show_admin_panel():
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

# --------------------------
# PAGE ROUTING
# --------------------------
if st.session_state.page == "Home":
    show_home()
elif st.session_state.page == "Tutor":
    show_tutor()
elif st.session_state.page == "StudyMode":
    show_study_mode()

# --------------------------
# TOP-RIGHT PANEL ICONS
# --------------------------
top_right_style = """
<style>
.top-right-icon {
    position: fixed;
    top: 20px;
    right: 20px;
    font-size: 25px;
    cursor: pointer;
    margin-left:10px;
}
</style>
"""
st.markdown(top_right_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.1,0.1,0.1])
st.markdown(f"<div class='top-right-icon' onclick='window.location.href=\"#\"'>👤</div>", unsafe_allow_html=True)
st.markdown(f"<div class='top-right-icon' onclick='window.location.href=\"#\"'>⚙️</div>", unsafe_allow_html=True)

# --------------------------
# BOTTOM-RIGHT ADMIN BUTTON
# --------------------------
admin_style = """
<style>
#admin_button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    font-weight: bold;
    font-size: 25px;
    cursor: pointer;
}
</style>
"""
st.markdown(admin_style, unsafe_allow_html=True)
st.markdown('<button id="admin_button" onclick="window.location.href=\'#\'">A</button>', unsafe_allow_html=True)
if st.session_state.admin_mode:
    show_admin_panel()

# --------------------------
# DARK / LIGHT MODE
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
</style>
""", unsafe_allow_html=True)


