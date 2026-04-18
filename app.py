import streamlit as st
import json
import os

# --- डेटा फ़ाइल सेटअप ---
DATA_FILE = "app_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"courses": {}, "users": {}}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"courses": {}, "users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Session State (लॉगिन स्थिति) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = ""

st.set_page_config(page_title="Learning App", layout="wide")

# --- लॉगिन चेक ---
if not st.session_state.logged_in:
    st.title("🎓 Student Learning Portal")
    
    tab1, tab2 = st.tabs(["Login", "Student Register"])
    
    with tab1:
        u = st.text_input("Username / ईमेल")
        p = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # 1. एडमिन के लिए स्पेशल चेक (यह हमेशा काम करेगा)
            if u == "admin" and p == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.session_state.user = "Admin"
                st.rerun()
            
            # 2. स्टूडेंट के लिए चेक
            else:
                data = load_data()
                if u in data["users"] and data["users"][u] == p:
                    st.session_state.logged_in = True
                    st.session_state.role = "student"
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("❌ यूजरनेम या पासवर्ड गलत है!")

    with tab2:
        new_u = st.text_input("Choose Username")
        new_p = st.text_input("Choose Password", type="password")
        if st.button("Register Now"):
            if new_u and new_p:
                data = load_data()
                data["users"][new_u] = new_p
                save_data(data)
                st.success("✅ रजिस्ट्रेशन सफल! अब लॉगिन करें।")

# --- लॉगिन होने के बाद का हिस्सा ---
else:
    st.sidebar.title(f"Welcome, {st.session_state.user}")
    if st.sidebar.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    # ==========================
    # 🛡️ ADMIN PANEL (केवल एडमिन को दिखेगा)
    # ==========================
    if st.session_state.role == "admin":
        st.title("🛡️ Admin Dashboard")
        st.subheader("Manage Courses & Content")
        
        menu = st.radio("Action:", ["Add New Content", "View/Delete Content"], horizontal=True)
        data = load_data()
        courses = ["IIOT", "IR&DMT", "PLUMBER"]

        if menu == "Add New Content":
            col1, col2 = st.columns(2)
            with col1:
                course_sel = st.selectbox("Select Course", courses)
                cat_sel = st.selectbox("Category", ["Theory Video", "Practical Video", "Software Video", "Notes PDF", "PYQ", "MCQ"])
            with col2:
                title = st.text_input("Title (e.g. Lesson 1)")
                link = st.text_input("Link (YouTube/Drive/PDF)")

            if st.button("Upload Content"):
                if title and link:
                    if course_sel not in data["courses"]: data["courses"][course_sel] = {}
                    if cat_sel not in data["courses"][course_sel]: data["courses"][course_sel][cat_sel] = []
                    
                    data["courses"][course_sel][cat_sel].append({"title": title, "link": link})
                    save_data(data)
                    st.success(f"✅ {title} added to {course_sel}")
                else:
                    st.error("सभी जानकारी भरें!")

        elif menu == "View/Delete Content":
            for c_name, c_cats in data["courses"].items():
                with st.expander(f"📚 {c_name}"):
                    for cat_name, items in c_cats.items():
                        st.write(f"--- {cat_name} ---")
                        for idx, item in enumerate(items):
                            c1, c2 = st.columns([4, 1])
                            c1.write(f"{idx+1}. {item['title']}")
                            if c2.button("🗑️", key=f"del_{c_name}_{cat_name}_{idx}"):
                                data["courses"][c_name][cat_name].pop(idx)
                                save_data(data)
                                st.rerun()

    # ==========================
    # 🎓 STUDENT VIEW (स्टूडेंट्स को दिखेगा)
    # ==========================
    else:
        st.title(f"👋 Hello, {st.session_state.user}")
        data = load_data()
        courses = ["IIOT", "IR&DMT", "PLUMBER"]
        
        sel_course = st.selectbox("Select Your Course", courses)
        
        t1, t2, t3, t4, t5, t6 = st.tabs(["Theory", "Practical", "Software", "Notes", "PYQ", "MCQ"])
        map_tabs = {
            "Theory Video": t1, "Practical Video": t2, "Software Video": t3,
            "Notes PDF": t4, "PYQ": t5, "MCQ": t6
        }

        for cat_name, tab_ui in map_tabs.items():
            with tab_ui:
                if sel_course in data["courses"] and cat_name in data["courses"][sel_course]:
                    for item in data["courses"][sel_course][cat_name]:
                        with st.container(border=True):
                            st.write(f"📁 **{item['title']}**")
                            if "Video" in cat_name:
                                try:
                                    st.video(item['link'])
                                except:
                                    st.write(f"🔗 [Watch Video Here]({item['link']})")
                            else:
                                st.link_button("Open File / Link", item['link'])
                else:
                    st.info("No data uploaded yet.")
