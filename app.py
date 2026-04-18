import streamlit as st
import json
import os

# --- डेटा फ़ाइल सेटअप ---
DATA_FILE = "app_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        initial = {"courses": {}, "users": {"admin": "admin123"}}
        with open(DATA_FILE, "w") as f:
            json.dump(initial, f)
        return initial
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"courses": {}, "users": {"admin": "admin123"}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = ""

st.set_page_config(page_title="Learning App", layout="wide")

# --- लॉगिन स्क्रीन ---
if not st.session_state.logged_in:
    st.title("🎓 Learning Portal - Welcome")
    t1, t2 = st.tabs(["Login", "Register"])
    
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            data = load_data()
            if u == "admin" and p == "admin123": # Fixed Admin Credentials
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.session_state.user = "Admin"
                st.rerun()
            elif u in data["users"] and data["users"][u] == p:
                st.session_state.logged_in = True
                st.session_state.role = "student"
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register Account"):
            if nu and np:
                data = load_data()
                data["users"][nu] = np
                save_data(data)
                st.success("Registration Successful! Please Login.")

else:
    # Sidebar - Logout
    st.sidebar.title(f"👤 {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ADMIN DASHBOARD (Visible only to Admin) ---
    if st.session_state.role == "admin":
        st.title("🛡️ Admin Dashboard")
        
        # Admin के लिए दो मुख्य टैब
        admin_tab, student_tab = st.tabs(["⚙️ Manage Content (Upload/Delete)", "👀 View as Student (Preview)"])
        
        with admin_tab:
            data = load_data()
            action = st.radio("Select Action:", ["Add Content", "Delete Content"], horizontal=True)
            courses = ["IIOT", "IR&DMT", "PLUMBER"]

            if action == "Add Content":
                c1, c2 = st.columns(2)
                with c1:
                    c_sel = st.selectbox("Select Course", courses)
                    cat_sel = st.selectbox("Category", ["Theory Video", "Practical Video", "Software Video", "Notes PDF", "PYQ", "MCQ"])
                with c2:
                    title = st.text_input("Title")
                    link = st.text_input("Link URL")
                
                if st.button("Publish"):
                    if title and link:
                        if c_sel not in data["courses"]: data["courses"][c_sel] = {}
                        if cat_sel not in data["courses"][c_sel]: data["courses"][c_sel][cat_sel] = []
                        data["courses"][c_sel][cat_sel].append({"title": title, "link": link})
                        save_data(data)
                        st.success("Uploaded!")
                        st.rerun()

            else: # Delete Content
                for cn, cats in data["courses"].items():
                    with st.expander(f"Manage {cn}"):
                        for ctn, items in cats.items():
                            st.write(f"**{ctn}**")
                            for i, item in enumerate(items):
                                col_a, col_b = st.columns([5,1])
                                col_a.write(item['title'])
                                if col_b.button("🗑️", key=f"del_{cn}_{ctn}_{i}"):
                                    data["courses"][cn][ctn].pop(i)
                                    save_data(data)
                                    st.rerun()
        
        with student_tab:
            st.info("यह प्रिव्यू है कि स्टूडेंट्स को कंटेंट कैसा दिखेगा।")
            # यहाँ नीचे स्टूडेंट वाला व्यू फंक्शन कॉल होगा (ताकि एडमिन भी देख सके)
            show_student_view()

    # --- STUDENT VIEW (Visible only to Students) ---
    else:
        show_student_view()

# --- स्टूडेंट व्यू फंक्शन (Shared by Student and Admin Preview) ---
def show_student_view():
    if st.session_state.role != "admin": # Admin के लिए टाइटल पहले से है
        st.title(f"📖 Welcome, {st.session_state.user}")
    
    data = load_data()
    courses = ["IIOT", "IR&DMT", "PLUMBER"]
    sel_course = st.selectbox("Choose Your Course", courses, key="std_course_sel")
    
    t_tabs = st.tabs(["Theory", "Practical", "Software", "Notes", "PYQ", "MCQ"])
    cat_map = {
        "Theory Video": t_tabs[0], "Practical Video": t_tabs[1], "Software Video": t_tabs[2],
        "Notes PDF": t_tabs[3], "PYQ": t_tabs[4], "MCQ": t_tabs[5]
    }

    for cat_name, tab_ui in cat_map.items():
        with tab_ui:
            if sel_course in data["courses"] and cat_name in data["courses"][sel_course]:
                for item in data["courses"][sel_course][cat_name]:
                    with st.container(border=True):
                        st.write(f"📁 **{item['title']}**")
                        if "Video" in cat_name:
                            st.video(item['link'])
                        else:
                            st.link_button("Open Content", item['link'])
            else:
                st.info("No content available here.")
