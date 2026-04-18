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
    st.session_state.username = ""

st.set_page_config(page_title="Learning Portal", layout="wide")

# --- LOGIN / REGISTER SECTION ---
if not st.session_state.logged_in:
    st.title("🎓 Student Learning Portal")
    t1, t2 = st.tabs(["Login", "Student Registration"])
    
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login Now"):
            data = load_data()
            if u == "admin" and p == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.session_state.username = "Admin"
                st.rerun()
            elif u in data["users"] and data["users"][u] == p:
                st.session_state.logged_in = True
                st.session_state.role = "student"
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if nu and np:
                data = load_data()
                data["users"][nu] = np
                save_data(data)
                st.success("Registration Successful! Now Login.")

# --- LOGGED IN AREA ---
else:
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # ==============================
    # 🛡️ ADMIN PANEL (यहाँ से Edit/Delete होगा)
    # ==============================
    if st.session_state.role == "admin":
        st.title("🛡️ Admin Dashboard")
        st.info("यहाँ से आप कंटेंट को मैनेज (Add/Edit/Delete) कर सकते हैं।")
        
        tab_add, tab_manage = st.tabs(["➕ Add New Content", "⚙️ Manage & Delete Content"])
        
        data = load_data()
        courses_list = ["IIOT", "IR&DMT", "PLUMBER"]

        with tab_add:
            st.subheader("नया वीडियो या पीडीएफ डालें")
            c1, c2 = st.columns(2)
            with c1:
                c_sel = st.selectbox("Course Select", courses_list)
                cat_sel = st.selectbox("Category", ["Theory Video", "Practical Video", "Software Video", "Notes PDF", "PYQ", "MCQ"])
            with c2:
                title = st.text_input("Title")
                link = st.text_input("Link (YouTube/PDF Link)")

            if st.button("Publish Now"):
                if title and link:
                    if c_sel not in data["courses"]: data["courses"][c_sel] = {}
                    if cat_sel not in data["courses"][c_sel]: data["courses"][c_sel][cat_sel] = []
                    data["courses"][c_sel][cat_sel].append({"title": title, "link": link})
                    save_data(data)
                    st.success("✅ कंटेंट सफलतापूर्वक जुड़ गया!")
                    st.rerun()
                else:
                    st.error("कृपया सभी जानकारी भरें।")

        with tab_manage:
            st.subheader("कंटेंट डिलीट करें")
            for c_name, c_data in data["courses"].items():
                with st.expander(f"📚 Course: {c_name}"):
                    for cat_name, items in c_data.items():
                        st.markdown(f"**{cat_name}**")
                        for idx, item in enumerate(items):
                            col_t, col_b = st.columns([4, 1])
                            col_t.write(f"📝 {item['title']}")
                            if col_b.button("Delete", key=f"del_{c_name}_{cat_name}_{idx}"):
                                data["courses"][c_name][cat_name].pop(idx)
                                save_data(data)
                                st.rerun()

    # ==============================
    # 🎓 STUDENT VIEW (स्टूडेंट्स के लिए)
    # ==============================
    else:
        st.title(f"📖 Hello, {st.session_state.username}")
        data = load_data()
        sel_course = st.selectbox("अपना कोर्स चुनें", ["IIOT", "IR&DMT", "PLUMBER"])
        
        t1, t2, t3, t4, t5, t6 = st.tabs(["Theory", "Practical", "Software", "Notes", "PYQ", "MCQ"])
        map_cat = {
            "Theory Video": t1, "Practical Video": t2, "Software Video": t3,
            "Notes PDF": t4, "PYQ": t5, "MCQ": t6
        }

        for cat_name, tab_ui in map_cat.items():
            with tab_ui:
                if sel_course in data["courses"] and cat_name in data["courses"][sel_course]:
                    for item in data["courses"][sel_course][cat_name]:
                        with st.container(border=True):
                            st.subheader(item['title'])
                            if "Video" in cat_name:
                                st.video(item['link'])
                            else:
                                st.link_button("View / Download", item['link'])
                else:
                    st.info("No content uploaded yet.")
