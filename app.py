import streamlit as st
import json
import os

# --- डेटा फाइल मैनेजमेंट ---
DATA_FILE = "app_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"courses": {}, "users": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Session State (लॉगिन स्थिति) ---
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.role = ""

# --- UI Setup ---
st.set_page_config(page_title="Learning Portal", layout="wide")

# --- LOGIN SCREEN ---
if not st.session_state.auth:
    st.title("🎓 Welcome to Learning Portal")
    choice = st.radio("Choose Option", ["Login", "Student Registration"])
    
    if choice == "Login":
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Submit"):
            if u == "admin" and p == "admin123":
                st.session_state.auth = True
                st.session_state.role = "admin"
                st.rerun()
            else:
                data = load_data()
                if u in data["users"] and data["users"][u] == p:
                    st.session_state.auth = True
                    st.session_state.role = "student"
                    st.rerun()
                else:
                    st.error("गलत आईडी या पासवर्ड!")
                    
    else:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Register"):
            data = load_data()
            data["users"][new_u] = new_p
            save_data(data)
            st.success("Registration Successful! Now Login.")

# --- AFTER LOGIN ---
else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
    
    # 🛡️ ADMIN PANEL (केवल एडमिन को दिखेगा)
    if st.session_state.role == "admin":
        st.title("🛡️ Admin Panel (Control Room)")
        st.write("यहाँ से आप वीडियो और नोट्स अपलोड या डिलीट कर सकते हैं।")
        
        tab_add, tab_del = st.tabs(["➕ Upload Content", "🗑️ Delete Content"])
        
        data = load_data()
        courses = ["IIOT", "IR&DMT", "PLUMBER"]

        with tab_add:
            c_sel = st.selectbox("Course Select", courses)
            cat_sel = st.selectbox("Category", ["Theory Video", "Practical Video", "Software Video", "Notes PDF", "PYQ", "MCQ"])
            title = st.text_input("Title")
            link = st.text_input("URL Link")
            
            if st.button("Add to Website"):
                if title and link:
                    if c_sel not in data["courses"]: data["courses"][c_sel] = {}
                    if cat_sel not in data["courses"][c_sel]: data["courses"][c_sel][cat_sel] = []
                    data["courses"][c_sel][cat_sel].append({"title": title, "link": link})
                    save_data(data)
                    st.success("Content Added!")
                else: st.error("Please fill all fields")

        with tab_del:
            for c_name, cats in data["courses"].items():
                with st.expander(f"Manage: {c_name}"):
                    for cat_name, items in cats.items():
                        st.markdown(f"**{cat_name}**")
                        for idx, item in enumerate(items):
                            col1, col2 = st.columns([4, 1])
                            col1.write(item['title'])
                            if col2.button("Delete", key=f"del_{c_name}_{cat_name}_{idx}"):
                                data["courses"][c_name][cat_name].pop(idx)
                                save_data(data)
                                st.rerun()

    # 🎓 STUDENT VIEW (स्टूडेंट्स को दिखेगा)
    else:
        st.title("📖 Student Learning Area")
        data = load_data()
        sel_course = st.selectbox("Choose Your Course", ["IIOT", "IR&DMT", "PLUMBER"])
        
        t1, t2, t3, t4, t5, t6 = st.tabs(["Theory", "Practical", "Software", "Notes", "PYQ", "MCQ"])
        mapping = {"Theory Video": t1, "Practical Video": t2, "Software Video": t3, "Notes PDF": t4, "PYQ": t5, "MCQ": t6}

        for cat_name, tab_obj in mapping.items():
            with tab_obj:
                if sel_course in data["courses"] and cat_name in data["courses"][sel_course]:
                    for item in data["courses"][sel_course][cat_name]:
                        st.subheader(item['title'])
                        if "Video" in cat_name:
                            st.video(item['link'])
                        else:
                            st.link_button("View/Download", item['link'])
                else:
                    st.info("Coming Soon!")
