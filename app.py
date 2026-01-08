import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="mentraIQ", layout="centered")

CONTENT_FILE = Path("content.json")
ADMIN_PASSWORD = "mentraqueen"

# ---------- Helpers ----------
def load_content():
    if CONTENT_FILE.exists():
        return json.loads(CONTENT_FILE.read_text())
    return {}

def save_content(data):
    CONTENT_FILE.write_text(json.dumps(data, indent=2))

content = load_content()

# ---------- Session Defaults ----------
if "page" not in st.session_state:
    st.session_state.page = "Tutor"

if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

# ---------- Header ----------
st.markdown(f"## {content.get('title', 'mentraIQ')}")
st.markdown(content.get("subtitle", ""))

# ---------- Top Right Buttons ----------
top_right = st.columns([6, 1, 1])

with top_right[1]:
    st.link_button("GitHub", "https://github.com", use_container_width=True)

with top_right[2]:
    if st.button("Admin"):
        st.session_state.page = "Admin"

st.divider()

# ---------- Pages ----------
if st.session_state.page == "Tutor":
    st.subheader("Tutor")

    st.text_input(
        "Study prompt",
        placeholder=content.get("tutor_placeholder", "")
    )

    st.info(content.get("coming_soon", "Coming soon"))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Study Mode"):
            st.session_state.page = "Study"
    with col2:
        if st.button("Account"):
            st.session_state.page = "Account"


elif st.session_state.page == "Study":
    st.subheader("Study Mode")
    st.write(content.get("study_mode_text", ""))

    if st.button("⬅ Back"):
        st.session_state.page = "Tutor"


elif st.session_state.page == "Account":
    st.subheader("Account")
    st.write("Accounts coming soon")

    if st.button("⬅ Back"):
        st.session_state.page = "Tutor"


elif st.session_state.page == "Admin":
    st.subheader("Admin Panel")

    if not st.session_state.admin_auth:
        password = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.success("Access granted")
                st.rerun()
            else:
                st.error("Wrong password")

        if st.button("⬅ Back"):
            st.session_state.page = "Tutor"

    else:
        st.markdown("### Edit Site Content")

        new_title = st.text_input("Title", content.get("title", ""))
        new_subtitle = st.text_input("Subtitle", content.get("subtitle", ""))
        new_study = st.text_input("Study Mode Text", content.get("study_mode_text", ""))
        new_tutor = st.text_input("Tutor Placeholder", content.get("tutor_placeholder", ""))
        new_soon = st.text_input("Coming Soon Text", content.get("coming_soon", ""))

        if st.button("💾 Save Changes"):
            save_content({
                "title": new_title,
                "subtitle": new_subtitle,
                "study_mode_text": new_study,
                "tutor_placeholder": new_tutor,
                "coming_soon": new_soon
            })
            st.success("Saved!")
            st.rerun()

        if st.button("Logout"):
            st.session_state.admin_auth = False
            st.session_state.page = "Tutor"
            st.rerun()

