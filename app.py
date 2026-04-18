import streamlit as st
import json
import os

# --- डेटा हैंडलिंग ---
DATA_FILE = "app_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"courses": {}, "users": {"admin": "admin123"}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- ऐप स्टेट मैनेजमेंट (Session State) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None  # 'admin' or 'student'
    st.session_state.username = ""

# UI Setup
st.set_page_config(page_title="Learning Portal", layout="wide")
data = load_data()
courses_list = ["IIOT", "IR&DMT", "PLUMBER"]

# --- SIDEBAR LOGOUT ---
if st.session_state.logged_in:
    st.sidebar.write(f"👤 यूजर: **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()

# --- मुख्य लॉजिक ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        user_input = st.text_input("Username", key="login_user")
        pass_input = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            if user_input == "admin" and pass_input == "admin123":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.session_state.username = "Admin"
                st.rerun()
            elif user_input in data["users"] and data["users"][user_input] == pass_input:
                st.session_state.logged_in = True
                st.session_state.user_role = "student"
                st.session_state.username = user_input
                st.rerun()
            else:
                st.error("गलत यूजरनेम या पासवर्ड")

    with tab2:
        st.subheader("New Student Registration")
        reg_user = st.text_input("Choose Username", key="reg_user")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register"):
            if reg_user in data["users"]:
                st.warning("यह यूजरनेम पहले से मौजूद है")
            elif reg_user and reg_pass:
                data["users"][reg_user] = reg_pass
                save_data(data)
                st.success("रजिस्ट्रेशन सफल! अब लॉगिन करें।")
            else:
                st.error("दोनों फील्ड भरना जरूरी है")

# --- एडमिन पैनल (ADMIN VIEW) ---
elif st.session_state.user_role == "admin":
    st.title("🛡️ Admin Dashboard")
    action = st.radio("चुनें:", ["Content Upload", "Delete Content", "User List"])
    
    if action == "Content Upload":
        course = st.selectbox("Course", courses_list)
        cat = st.selectbox("Category", ["Theory Video", "Practical Video", "Software Video", "Notes PDF", "PYQ", "MCQ"])
        title = st.text_input("Title")
        link = st.text_input("Link (YouTube/Google Drive)")
        
        if st.button("Publish Content"):
            if course not in data["courses"]: data["courses"][course] = {}
            if cat not in data["courses"][course]: data["courses"][course][cat] = []
            data["courses"][course][cat].append({"title": title, "link": link})
            save_data(data)
            st.success(f"✅ {title} अपलोड हो गया!")

    elif action == "Delete Content":
        st.info("यहाँ से आप कंटेंट हटा सकते हैं।")
        course_del = st.selectbox("Course to manage", list(data["courses"].keys()))
        if course_del:
            cat_del = st.selectbox("Category to manage", list(data["courses"][course_del].keys()))
            items = data["courses"][course_del][cat_del]
            for idx, item in enumerate(items):
                col1, col2 = st.columns([4, 1])
                col1.write(item['title'])
                if col2.button("Delete", key=f"del_{idx}"):
                    data["courses"][course_del][cat_del].pop(idx)
                    save_data(data)
                    st.rerun()

# --- स्टूडेंट पोर्टल (STUDENT VIEW) ---
elif st.session_state.user_role == "student":
    st.title(f"👋 Welcome, {st.session_state.username}")
    selected_course = st.selectbox("अपना कोर्स चुनें", courses_list)
    
    tab_theory, tab_pract, tab_soft, tab_notes, tab_pyq, tab_mcq = st.tabs(["Theory", "Practical", "Software", "Notes", "PYQ", "MCQ"])
    
    tabs = {
        "Theory Video": tab_theory, "Practical Video": tab_pract, 
        "Software Video": tab_soft, "Notes PDF": tab_notes, 
        "PYQ": tab_pyq, "MCQ": tab_mcq
    }

    for cat_name, tab_obj in tabs.items():
        with tab_obj:
            if selected_course in data["courses"] and cat_name in data["courses"][selected_course]:
                items = data["courses"][selected_course][cat_name]
                for item in items:
                    with st.expander(item['title']):
                        if "Video" in cat_name:
                            st.video(item['link'])
                        else:
                            st.link_button("View / Download", item['link'])
            else:
                st.info("फिलहाल यहाँ कोई कंटेंट नहीं है।")

