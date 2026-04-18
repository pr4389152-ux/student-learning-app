import streamlit as st
import json
import os

# --- डेटा फाइल मैनेजमेंट ---
DATA_FILE = "app_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {"courses": {}, "users": {"admin": "admin123"}}
        with open(DATA_FILE, "w") as f:
            json.dump(initial_data, f)
        return initial_data
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Session State (लॉगिन याद रखने के लिए) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""

# UI Setup
st.set_page_config(page_title="Learning Portal", layout="wide")
data = load_data()
courses_list = ["IIOT", "IR&DMT", "PLUMBER"]

# --- APP LOGIC ---

# 1. अगर लॉगिन नहीं है
if not st.session_state.logged_in:
    st.title("🎓 Student Learning Portal")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login Now"):
            # एडमिन चेक
            if u == "admin" and p == "admin123":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.session_state.username = "Admin"
                st.rerun()
            # स्टूडेंट चेक
            elif u in data["users"] and data["users"][u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = "student"
                st.session_state.username = u
                st.rerun()
            else:
                st.error("❌ गलत यूजरनेम या पासवर्ड!")

    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if new_u and new_p:
                data["users"][new_u] = new_p
                save_data(data)
                st.success("✅ अकाउंट बन गया! अब लॉगिन करें।")

# 2. अगर लॉगिन है
else:
    # Sidebar Logout
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- एडमिन व्यू (Admin View) ---
    if st.session_state.user_role == "admin":
        st.header("🛡️ Admin Panel - Manage Content")
        menu = ["Add Content", "Manage/Delete"]
        choice = st.selectbox("Action", menu)

        if choice == "Add Content":
            col1, col2 = st.columns(2)
            with col1:
                course = st.selectbox("Course", courses_list)
                cat = st.selectbox("Category", ["Theory Video", "Practical Video", "Software Video", "Notes PDF", "PYQ", "MCQ"])
            with col2:
                title = st.text_input("Content Title")
                link = st.text_input("Link (YouTube or Direct Link)")

            if st.button("Upload"):
                if title and link:
                    if course not in data["courses"]: data["courses"][course] = {}
                    if cat not in data["courses"][course]: data["courses"][course][cat] = []
                    data["courses"][course][cat].append({"title": title, "link": link})
                    save_data(data)
                    st.success("✅ सफलतापूर्वक अपलोड हुआ!")
                else:
                    st.error("Title और Link दोनों भरें")

        elif choice == "Manage/Delete":
            for c_name, c_data in data["courses"].items():
                with st.expander(f"Course: {c_name}"):
                    for cat_name, items in c_data.items():
                        st.write(f"**{cat_name}**")
                        for i, item in enumerate(items):
                            col_t, col_b = st.columns([4, 1])
                            col_t.write(item['title'])
                            if col_b.button("Delete", key=f"del_{c_name}_{cat_name}_{i}"):
                                data["courses"][c_name][cat_name].pop(i)
                                save_data(data)
                                st.rerun()

    # --- स्टूडेंट व्यू (Student View) ---
    else:
        st.header(f"📚 {st.session_state.username}'s Learning Area")
        selected_course = st.selectbox("कोर्स चुनें", courses_list)
        
        tab_t, tab_p, tab_s, tab_n, tab_py, tab_m = st.tabs(["Theory", "Practical", "Software", "Notes", "PYQ", "MCQ"])
        
        mapping = {
            "Theory Video": tab_t, "Practical Video": tab_p, "Software Video": tab_s,
            "Notes PDF": tab_n, "PYQ": tab_py, "MCQ": tab_m
        }

        for cat_name, tab_obj in mapping.items():
            with tab_obj:
                if selected_course in data["courses"] and cat_name in data["courses"][selected_course]:
                    for item in data["courses"][selected_course][cat_name]:
                        st.subheader(item['title'])
                        if "Video" in cat_name:
                            # YouTube लिंक के लिए बेस्ट तरीका
                            try:
                                st.video(item['link'])
                            except:
                                st.error("वीडियो लोड नहीं हो सका। लिंक चेक करें।")
                        else:
                            st.link_button("View Content", item['link'])
                else:
                    st.info("No content yet.")
