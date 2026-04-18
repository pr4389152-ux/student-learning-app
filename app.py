import streamlit as st
import pandas as pd
import json
import os

# फाइल सेटअप (डेटा सेव करने के लिए)
DATA_FILE = "app_data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"courses": {}, "users": {}}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# UI Setup
st.set_page_config(page_title="Student Learning Program", layout="wide")
st.title("🎓 Student Learning Portal")

data = load_data()
courses_list = ["IIOT", "IR&DMT", "PLUMBER"]

# Sidebar - Login/Registration
menu = ["Login", "Register", "Admin Panel"]
choice = st.sidebar.selectbox("Menu", menu)

# --- USER REGISTRATION ---
if choice == "Register":
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type='password')
    if st.button("Signup"):
        data["users"][new_user] = new_pass
        save_data(data)
        st.success("Account Created! Please Login.")

# --- ADMIN PANEL (Manage Content) ---
elif choice == "Admin Panel":
    st.subheader("🔒 Admin Access Only")
    admin_pass = st.text_input("Admin Password", type='password')
    
    if admin_pass == "admin123": # आपका सीक्रेट पासवर्ड
        st.success("Welcome, Admin!")
        
        op = st.radio("Action", ["Upload Content", "Delete Content"])
        
        if op == "Upload Content":
            course = st.selectbox("Select Course", courses_list)
            cat = st.selectbox("Category", ["Theory Video", "Practical Video", "Software Video", "Notes PDF", "PYQ", "MCQ"])
            title = st.text_input("Title (e.g. Lesson 1)")
            link = st.text_input("Link / URL")
            
            if st.button("Add to Portal"):
                if course not in data["courses"]: data["courses"][course] = {}
                if cat not in data["courses"][course]: data["courses"][course][cat] = []
                
                data["courses"][course][cat].append({"title": title, "link": link})
                save_data(data)
                st.info(f"Added {title} to {course}")

        elif op == "Delete Content":
            # डिलीट करने का लॉजिक यहाँ आएगा
            st.warning("Select items from data file to remove.")

# --- USER LOGIN & STUDY AREA ---
elif choice == "Login":
    user = st.sidebar.text_input("User Name")
    pwd = st.sidebar.text_input("Password", type='password')
    
    if user in data["users"] and data["users"][user] == pwd:
        st.sidebar.success(f"Logged in as {user}")
        
        selected_course = st.selectbox("Choose Your Course", courses_list)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("### 📚 Study Sections")
            mode = st.radio("Go to:", ["Theory", "Practical", "Software", "Notes", "PYQ", "MCQ"])
        
        with col2:
            st.write(f"### {mode} Content")
            map_cat = {
                "Theory": "Theory Video", "Practical": "Practical Video", 
                "Software": "Software Video", "Notes": "Notes PDF", 
                "PYQ": "PYQ", "MCQ": "MCQ"
            }
            cat_key = map_cat[mode]
            
            if selected_course in data["courses"] and cat_key in data["courses"][selected_course]:
                items = data["courses"][selected_course][cat_key]
                for item in items:
                    st.markdown(f"✅ **{item['title']}**")
                    if "Video" in cat_key:
                        st.video(item['link']) # YouTube या Drive लिंक
                    else:
                        st.link_button(f"Open {cat_key}", item['link'])
            else:
                st.info("No content uploaded yet by Admin.")
    else:
        st.warning("Please enter correct Username and Password.")

