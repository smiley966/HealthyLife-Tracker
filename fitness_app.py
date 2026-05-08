import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
import hashlib
import re
import random
import os
import base64
import calendar
from datetime import date, datetime, timedelta

# GLOSSARY OF ABBREVIATIONS & TERMS
#
# This section explains the short codes and variable names used in this code.
#
# LIBRARIES & EXTENSIONS 
# st   : Streamlit (The web app framework used to build the interface)
# pd   : Pandas (Library for data manipulation, acts like Excel in code)
# plt  : Pyplot (Part of Matplotlib, used for drawing graphs/charts)
# py   : Python (The file extension .py or the programming language itself)
#
# VARIABLES 
# c    : Cursor (A pointer used to execute SQL queries in the database)
# conn : Connection (The active link to the MySQL database)
# df   : DataFrame (A table of data in Pandas, similar to a spreadsheet sheet)
#
# MEDICAL/FITNESS TERMS 
# BMI  : Body Mass Index (Measure of body fat based on height and weight)
# MET  : Metabolic Equivalent of Task (Energy cost of physical activities)
# BPM  : Beats Per Minute (Heart rate unit)
# Kcal : Kilocalories (Calories burned)
#
# TECHNICAL TERMS 
# unsafe_allow_html=True : 
#    - By default, Streamlit treats text as plain text for security.
#    - This setting tells Streamlit "Trust me, let me write actual HTML code".
#    - We use this to center images and create custom styled boxes.

# 1. CONFIGURATION & STYLE

# Try to use the local logo file, otherwise fallback to a running emoji
logo_path = "lowgoow.png"
icon = logo_path if os.path.exists(logo_path) else "🏃"

# Initialize the Streamlit app with a title and wide layout
st.set_page_config(page_title="HealthyLife Tracker", page_icon=icon, layout="wide")

# Set Matplotlib (charting library) to use a dark background to match the app theme
plt.style.use('dark_background')

# Inject Custom CSS for specific UI elements
# NOTE: We use unsafe_allow_html=True here to inject raw CSS <style> tags
st.markdown(""" 
    <style>
    /* ----------------------------------------------------
       THEME OVERRIDES: 
       Green (#2ECC71) for BRANDING (Buttons, Headers)
       Blue (#3498DB) for INTERACTION (Focus, Tabs, Selection)
       ---------------------------------------------------- */
    
    /* Force buttons to be Green */
    .stButton > button {
        background-color: #2ECC71 !important;
        color: #121212 !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #27AE60 !important;
        box-shadow: 0 4px 10px rgba(46, 204, 113, 0.4);
        color: white !important;
    }

    /* Force Headers to be Green */
    h1, h2, h3 {
        color: #2ECC71 !important;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Styling for Tabs (Blue highlight when selected) */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #3498DB !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #3498DB !important;
    }

    /* Input Fields Styling (Focus state) */
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within {
        #border: 1px solid #3498DB !important;
    }
    
    /* General App Background */
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }

    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
        border-right: 1px solid #333;
    }

    /* Input Fields (Text, Number, Date) Default Dark Style */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div, 
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #2D2D2D !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
    }

    /* Hide standard Streamlit header/menu for a cleaner look */
    [data-testid="stHeaderAction"] { display: none !important; }
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a { display: none !important; }
    
    /* Custom Box for displaying Tips/Results */
    .result-box {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #3498DB; /* Blue Accent */
        font-size: 18px;
        font-weight: 500;
        color: #FAFAFA;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Metric Cards (used in Dashboard) */
    .metric-card {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        border: 1px solid #333;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: white;
    }
    .metric-label {
        font-size: 13px;
        color: #888;
        text-transform: uppercase;
    }
    
    /* Calendar Day Styling */
    .cal-day {
        height: 45px;
        width: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        font-weight: bold;
        margin: 0 auto 8px auto;
        color: #666;
        cursor: default;
        transition: transform 0.2s;
    }
    .cal-day.active {
        background-color: #3498DB; /* BLUE for active workout days */
        color: white;
        box-shadow: 0 0 10px rgba(52, 152, 219, 0.5);
    }
    .cal-day.today {
        border: 2px solid #2ECC71; /* Green border for Today */
        color: #2ECC71;
    }
    .cal-header {
        text-align: center;
        font-weight: bold;
        color: #888;
        font-size: 14px;
        padding-bottom: 10px;
        text-transform: uppercase;
    }
    
    /* Dashboard Weekly Goal Circles */
    .day-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #2D2D2D;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 5px auto;
        font-weight: bold;
        font-size: 14px;
        color: #888;
        border: 1px solid #444;
    }
    .day-active {
        background-color: #3498DB;
        color: white;
        border-color: #3498DB;
        box-shadow: 0 0 8px rgba(52, 152, 219, 0.4);
    }

    /* Expander Header styling */
    .streamlit-expanderHeader {
        background-color: #1E1E1E;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True) # Enables us to write raw HTML/CSS above

# 2. DATABASE CONFIGURATION
# Configuration for connecting to the XAMPP MySQL Database.
# NOTE: 'port' is often 3306 by default, but set to 3307 here based on user setup.
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'port': 3307
}
DB_NAME = "fitness_app_web"

def get_connection():
    """Establishes and returns a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)

# 3. HELPER FUNCTIONS
# Utility functions used throughout the application for logic, math, and validation.

def make_hash(password):
    """Hashes a password using SHA256 for basic security storage."""
    return hashlib.sha256(str.encode(password)).hexdigest()

def is_valid_email(email):
    """Validates email format using Regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_img_as_base64(file):
    """Converts a local image file to base64 string for HTML embedding."""
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def estimate_calories(activity, intensity, duration):
    """
    Estimates calories burned based on activity type, intensity, and duration.
    Uses standard MET (Metabolic Equivalent of Task) values.
    
    MET = A ratio of your working metabolic rate relative to your resting metabolic rate.
    1 MET = The energy you use sitting quietly.
    """
    met_values = {
        "Running": 9.8, "Cycling": 7.5, "Gym/Weights": 5.0,
        "Yoga": 3.0, "Swimming": 8.0, "Walking": 3.5,
        "HIIT": 11.0, "Pilates": 3.5
    }
    base_met = met_values.get(activity, 5.0)
    
    # Adjust MET based on intensity selection
    multiplier = 1.0
    if intensity == "Low": multiplier = 0.8
    elif intensity == "High": multiplier = 1.2
    elif intensity == "Extreme": multiplier = 1.4
    
    avg_weight = 70 # Default weight in KG
    # Formula: Kcal (Kilocalories) = MET * Weight * Hours
    kcal = (base_met * multiplier * avg_weight) * (duration / 60)
    return int(kcal)

# 4. DATA GENERATION & INITIALIZATION
# Functions to setup the database tables and populate dummy data for demo accounts.

def generate_sample_data_for_user(user_id, gender):
    """
    Generates 30 days of realistic dummy data (workouts, pulse, BMI) 
    ending TODAY for a specific user ID.
    Used for 'Juan' and 'Maria' demo accounts.
    """
    conn = get_connection()
    c = conn.cursor() # 'c' stands for Cursor - it executes SQL commands
    c.execute(f"USE {DB_NAME}")
    
    # Clear old data to prevent duplication
    c.execute("DELETE FROM records WHERE user_id = %s", (user_id,))
    c.execute("DELETE FROM exercises WHERE user_id = %s", (user_id,))
    
    today = datetime.now()
    activities_high = ["Running", "Gym/Weights", "HIIT", "Swimming", "Cycling"]
    activities_low = ["Walking", "Yoga", "Pilates", "Stretching"]
    
    # Loop back 30 days
    for i in range(30):
        day = today - timedelta(days=30-i)
        date_ts = day.strftime('%Y-%m-%d %H:%M:%S')
        date_dt = day.strftime('%Y-%m-%d')
        
        # Gender-based variations for realism
        if gender == "Male":
            pulse_base = random.randint(60, 75)
            bmi_base = 22.5
        else:
            pulse_base = random.randint(65, 80)
            bmi_base = 20.0
            
        # Insert Pulse Record (Heart Rate)
        pulse = pulse_base + random.randint(-5, 5)
        c.execute("INSERT INTO records (user_id, type, value, note, date) VALUES (%s, %s, %s, %s, %s)", 
                 (user_id, "Pulse", pulse, f"{pulse} bpm - Normal", date_ts))
        
        # Insert BMI Record (Body Mass Index) every 5 days
        if i % 5 == 0:
            bmi = bmi_base + random.uniform(-0.2, 0.2)
            c.execute("INSERT INTO records (user_id, type, value, note, date) VALUES (%s, %s, %s, %s, %s)", 
                     (user_id, "BMI", bmi, f"{bmi:.2f} - Normal", date_ts))

        # Insert Exercise (Alternating days roughly)
        if i % 2 == 0:
            dur = random.randint(30, 60)
            act = random.choice(activities_high)
            c.execute("INSERT INTO exercises (user_id, activity, intensity, duration, date) VALUES (%s, %s, %s, %s, %s)", 
                     (user_id, act, "High", dur, date_dt))
        elif i % 3 == 0:
             dur = random.randint(20, 45)
             act = random.choice(activities_low)
             c.execute("INSERT INTO exercises (user_id, activity, intensity, duration, date) VALUES (%s, %s, %s, %s, %s)", 
                     (user_id, act, "Low", dur, date_dt))
    
    conn.commit()
    conn.close()
    return True

def init_db():
    """
    Initializes the database.
    1. Creates the DB if not exists.
    2. Creates Users, Records, Exercises tables.
    3. Injects the default Admin and Sample Users (Juan/Maria).
    """
    try:
        conn = get_connection()
        c = conn.cursor(buffered=True) # 'c' is the database cursor
        # Create DB
        c.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        c.execute(f"USE {DB_NAME}")
        
        # Create Users Table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(255) UNIQUE,
                        email VARCHAR(255),
                        password VARCHAR(255),
                        gender VARCHAR(50),
                        birthdate DATE)''')

        # Run minimal migrations (add columns if missing in old versions)
        try:
            c.execute("SELECT password FROM users LIMIT 1")
        except:
            c.execute("ALTER TABLE users ADD COLUMN password VARCHAR(255) DEFAULT '12345'")
            conn.commit()
        try:
            c.execute("SELECT email FROM users LIMIT 1")
        except:
            c.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255) DEFAULT 'user@example.com'")
            conn.commit()
        
        # Create Records Table (Health Metrics like BMI, Pulse)
        c.execute('''CREATE TABLE IF NOT EXISTS records (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        type VARCHAR(50),
                        value FLOAT,
                        note VARCHAR(255),
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Create Exercises Table (Workouts)
        c.execute('''CREATE TABLE IF NOT EXISTS exercises (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        activity VARCHAR(255),
                        intensity VARCHAR(50),
                        duration INT,
                        date DATE)''')
        
        conn.commit()

        # ENSURE ADMIN EXISTS 
        c.execute("SELECT * FROM users WHERE username = 'Admin'")
        if not c.fetchone():
            admin_hash = make_hash("admin123")
            c.execute("INSERT INTO users (username, email, password, gender, birthdate) VALUES (%s, %s, %s, %s, %s)", 
                      ("Admin", "admin@fitness.com", admin_hash, "Male", "2000-01-01"))
            conn.commit()

        # ENSURE SAMPLE USERS EXIST 
        default_pass_hash = make_hash("12345")
        
        # Check/Create Juan
        c.execute("SELECT * FROM users WHERE username = 'Juan Dela Cruz'")
        if not c.fetchone():
            c.execute("INSERT INTO users (username, email, password, gender, birthdate) VALUES (%s, %s, %s, %s, %s)", 
                      ("Juan Dela Cruz", "juan@gmail.com", default_pass_hash, "Male", "1999-01-01"))
            juan_id = c.lastrowid
            generate_sample_data_for_user(juan_id, "Male")
            
        # Check/Create Maria
        c.execute("SELECT * FROM users WHERE username = 'Maria Clara'")
        if not c.fetchone():
            c.execute("INSERT INTO users (username, email, password, gender, birthdate) VALUES (%s, %s, %s, %s, %s)", 
                      ("Maria Clara", "maria@gmail.com", default_pass_hash, "Female", "2003-05-15"))
            maria_id = c.lastrowid
            generate_sample_data_for_user(maria_id, "Female")

        conn.commit()
        c.close()
        conn.close()
    except Exception as e:
        st.error(f"Database Error: {e}")

def reset_database():
    """Drops the entire database (Admin Functionality)."""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error resetting database: {e}")
        return False

def delete_user_account(user_id):
    """Deletes a user and all their associated records/exercises."""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(f"USE {DB_NAME}")
        
        # 1. Delete Records
        c.execute("DELETE FROM records WHERE user_id = %s", (user_id,))
        # 2. Delete Exercises
        c.execute("DELETE FROM exercises WHERE user_id = %s", (user_id,))
        # 3. Delete User
        c.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Delete Error: {e}")
        return False

# 5. DATABASE ACTION FUNCTIONS

def login_user(login_id, password):
    """
    Authenticates a user.
    Also handles the 'Smart Refresh' logic: if a demo user logs in 
    and their data is old, it regenerates fresh data for today.
    """
    conn = get_connection()
    c = conn.cursor(dictionary=True, buffered=True)
    c.execute(f"USE {DB_NAME}")
    hashed_pw = make_hash(password)
    c.execute("SELECT * FROM users WHERE (username = %s OR email = %s) AND password = %s", 
              (login_id, login_id, hashed_pw))
    user = c.fetchone()
    
    #  AUTO REFRESH DEMO DATA LOGIC 
    if user and user['username'] in ['Juan Dela Cruz', 'Maria Clara']:
        c.execute("SELECT date FROM exercises WHERE user_id=%s ORDER BY date DESC LIMIT 1", (user['id'],))
        last_entry = c.fetchone()
        
        # Check if data is stale (older than yesterday)
        is_stale = False
        if not last_entry:
            is_stale = True
        else:
            last_date = last_entry['date']
            if isinstance(last_date, datetime):
                last_date = last_date.date()
                
            if last_date < (date.today() - timedelta(days=1)):
                is_stale = True
        
        # Regenerate if stale
        if is_stale:
            c.close()
            conn.close()
            generate_sample_data_for_user(user['id'], user['gender'])
            return user 

    c.close()
    conn.close()
    return user

def register_user(username, email, password, gender, birthdate):
    """Registers a new user in the database."""
    try:
        conn = get_connection()
        c = conn.cursor(buffered=True)
        c.execute(f"USE {DB_NAME}")
        hashed_pw = make_hash(password)
        c.execute("INSERT INTO users (username, email, password, gender, birthdate) VALUES (%s, %s, %s, %s, %s)", 
                  (username, email, hashed_pw, gender, birthdate))
        conn.commit()
        c.close()
        conn.close()
        return True
    except:
        return False

def add_record(user_id, r_type, value, note):
    """Adds a health metric record (Pulse, BMI)."""
    conn = get_connection()
    c = conn.cursor(buffered=True)
    c.execute(f"USE {DB_NAME}")
    c.execute("INSERT INTO records (user_id, type, value, note) VALUES (%s, %s, %s, %s)", 
              (user_id, r_type, value, note))
    conn.commit()
    c.close()
    conn.close()

def add_exercise(user_id, activity, intensity, duration, date_str):
    """Adds an exercise workout entry."""
    conn = get_connection()
    c = conn.cursor(buffered=True)
    c.execute(f"USE {DB_NAME}")
    c.execute("INSERT INTO exercises (user_id, activity, intensity, duration, date) VALUES (%s, %s, %s, %s, %s)", 
              (user_id, activity, intensity, duration, date_str))
    conn.commit()
    c.close()
    conn.close()

# 6. MAIN APP INTERFACE

# Initialize database on app start
init_db()

# Initialize Session State for User Auth
if 'user' not in st.session_state:
    st.session_state.user = None

# SIDEBAR & NAVIGATION 
if st.session_state.user:
    # Sidebar: Logo & User Info
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=150)
        
    st.sidebar.title(f"User: {st.session_state.user['username']}")
    
    # DYNAMIC MENU 
    # Standard menu options
    menu_options = ["Dashboard", "Health Tools", "Exercise Log", "History & Graphs"]
    
    # Conditional: Add 'Admin Panel' ONLY if user is 'Admin'
    if st.session_state.user['username'] == "Admin":
        menu_options.append("Admin Panel")
        
    menu = st.sidebar.radio("Menu", menu_options)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

else:
    menu = "Login"

# SCREEN 1: LOGIN & REGISTER
if menu == "Login":
    # Display Logo
    if os.path.exists(logo_path):
        img_b64 = get_img_as_base64(logo_path)
        # Using unsafe_allow_html=True here to inject raw HTML for layout centering
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <img src="data:image/png;base64,{img_b64}" width="200">
            </div>
        """, unsafe_allow_html=True)
    
    # Welcome Text
    st.markdown("<h1 style='text-align: center; color: #2ECC71;'>HealthyLife Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #E0E0E0;'>Your journey starts here.</h3>", unsafe_allow_html=True)
    st.write("")
    
    # Info Box showing Demo Credentials
    # HTML allows us to create a styled 'card' look not easily possible with standard Streamlit
    st.markdown("""
        <div style="background-color: #1E3A5F; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #3498DB; margin-bottom: 20px;">
            <strong style="color: #3498DB; font-size: 16px;">Demo Accounts:</strong><br>
            <span style="color: #DDD; font-size: 14px;">
                Juan Dela Cruz | <code style="color: #2ECC71;">juan@gmail.com</code> | Pass: <code style="color: #E74C3C;">12345</code>
            </span><br>
            <span style="color: #DDD; font-size: 14px;">
                Maria Clara | <code style="color: #2ECC71;">maria@gmail.com</code> | Pass: <code style="color: #E74C3C;">12345</code>
            </span><br>
            <hr style="border-color: #444;">
            <span style="color: #AAA; font-size: 13px;">
                Administrator | <code style="color: #F1C40F;">admin@fitness.com</code> | Pass: <code style="color: #E74C3C;">admin123</code>
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs for Sign In vs Register
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login_id = st.text_input("Username or Email", key="login_id")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Sign In"):
            user = login_user(login_id, password)
            if user:
                st.session_state.user = user
                st.success("Welcome back!")
                st.rerun()
            else:
                st.error("Invalid credentials.")
    with tab2:
        new_name = st.text_input("Username", key="reg_name")
        new_email = st.text_input("Email", key="reg_email")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        gender = st.selectbox("Gender", ["Male", "Female"])
        bdate = st.date_input("Birthdate", min_value=date(1950, 1, 1))
        if st.button("Create Account"):
            if new_name and new_pass and new_email:
                if is_valid_email(new_email):
                    if register_user(new_name, new_email, new_pass, gender, bdate):
                        st.success("Created! Login now.")
                    else:
                        st.error("Username taken.")
                else:
                    st.error("Invalid email.")
            else:
                st.warning("Fill all fields.")

# SCREEN 2: DASHBOARD (Overview)
elif menu == "Dashboard":
    st.title(f"Hi, {st.session_state.user['username']}! 👋")
    conn = get_connection()
    c = conn.cursor(dictionary=True, buffered=True) # 'c' is the database cursor
    c.execute(f"USE {DB_NAME}")
    
    # 1. FETCH METRICS (Latest BMI, Avg Pulse, Workout Count)
    c.execute("SELECT value FROM records WHERE user_id=%s AND type='BMI' ORDER BY date DESC LIMIT 1", (st.session_state.user['id'],))
    last_bmi = c.fetchone()
    bmi_val = f"{last_bmi['value']:.1f}" if last_bmi else "--"
    
    c.execute("SELECT AVG(value) as avg_pulse FROM records WHERE user_id=%s AND type='Pulse' AND date >= DATE_SUB(NOW(), INTERVAL 7 DAY)", (st.session_state.user['id'],))
    avg_pulse = c.fetchone()
    pulse_val = f"{int(avg_pulse['avg_pulse'])} bpm" if avg_pulse and avg_pulse['avg_pulse'] else "--"
    
    c.execute("SELECT COUNT(*) as count FROM exercises WHERE user_id=%s AND date >= DATE_SUB(NOW(), INTERVAL 7 DAY)", (st.session_state.user['id'],))
    workout_res = c.fetchone()
    workout_count = workout_res['count'] if workout_res else 0
    
    # 2. FETCH RECENT ACTIVITIES (Last 3)
    c.execute("SELECT activity, duration, date FROM exercises WHERE user_id=%s ORDER BY date DESC LIMIT 3", (st.session_state.user['id'],))
    recent_activities = c.fetchall()
    
    # 3. FETCH DATA FOR WEEKLY GOAL CIRCLES
    today = date.today()
    week_dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    c.execute("SELECT date FROM exercises WHERE user_id=%s AND date >= DATE_SUB(NOW(), INTERVAL 7 DAY)", (st.session_state.user['id'],))
    workout_dates = {row['date'].strftime('%Y-%m-%d') for row in c.fetchall()}
    conn.close()
    
    # Display Metrics in Columns using unsafe_allow_html for custom card styling
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"""<div class="metric-card"><div class="metric-label">BMI</div><div class="metric-value">{bmi_val}</div></div>""", unsafe_allow_html=True)
    with col2: st.markdown(f"""<div class="metric-card"><div class="metric-label">Pulse (Avg)</div><div class="metric-value" style="color: #E74C3C;">{pulse_val}</div></div>""", unsafe_allow_html=True)
    with col3: st.markdown(f"""<div class="metric-card"><div class="metric-label">Workouts (7d)</div><div class="metric-value" style="color: #3498DB;">{workout_count}</div></div>""", unsafe_allow_html=True)

    # Weekly Goal Visualizer (7 Circles)
    st.write("")
    st.markdown("### 📅 Weekly Goal")
    cols = st.columns(7)
    for i, day_date in enumerate(week_dates):
        day_str = day_date.strftime('%Y-%m-%d')
        day_num = day_date.day
        is_active = day_str in workout_dates
        active_class = "day-active" if is_active else ""
        with cols[i]: st.markdown(f"""<div class="day-circle {active_class}">{day_num}</div>""", unsafe_allow_html=True)

    # Recent Activity List & Daily Tip
    st.write("")
    col_act, col_mot = st.columns([3, 2])
    with col_act:
        st.markdown("### 🕒 Recent Activity")
        if recent_activities:
            for act in recent_activities:
                st.markdown(f"""<div style="background-color: #1E1E1E; padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #333; display: flex; justify-content: space-between; align-items: center;"><div style="font-weight: bold; color: white;">{act['activity']}</div><div style="color: #888; font-size: 14px;">{act['duration']} mins <span style="margin-left:10px; font-size:12px; color:#555;">{act['date']}</span></div></div>""", unsafe_allow_html=True)
        else: 
            st.info("No recent activities. Start logging today!")
            
    with col_mot:
        st.markdown("### 💡 Daily Tip")
        st.markdown("""<div class="result-box" style="padding: 15px; font-size: 14px; border-left-color: #3498DB;">Stay consistent! Even 20 minutes a day makes a huge difference.</div>""", unsafe_allow_html=True)

# SCREEN 3: HEALTH TOOLS (Calculator & Pulse)
elif menu == "Health Tools":
    st.title("Health Tools")
    st.write("Track your essential health metrics.")
    col_bmi, col_pulse = st.columns(2)
    
    # BMI Calculator Section
    with col_bmi:
        with st.container(border=True):
            st.subheader("⚖️ BMI Calculator")
            with st.expander("❓ How to use"):
                st.write("1. Select Weight/Height.\n2. Click Calculate.\n3. Result shows category.")
            weight = st.slider("Weight (kg)", 30.0, 200.0, 60.0, format="%.1f kg")
            height = st.slider("Height (cm)", 100, 250, 170, format="%d cm")
            if st.button("Calculate BMI"):
                h_m = height / 100
                bmi = weight / (h_m ** 2)
                # Categorize BMI
                if bmi < 18.5: cat, color = "Underweight", "#3498DB"
                elif bmi < 25: cat, color = "Normal", "#2ECC71"
                elif bmi < 30: cat, color = "Overweight", "#3498DB" 
                else: cat, color = "Obese", "#E74C3C"
                # Display Result
                st.markdown(f'<div style="background:#121212; padding:10px; border-radius:8px; text-align:center; border: 1px solid {color}; margin-top:10px;"><h2 style="color:{color} !important; margin:0;">{bmi:.2f}</h2><span style="color:#aaa;">{cat}</span></div>', unsafe_allow_html=True)
                add_record(st.session_state.user['id'], "BMI", bmi, f"{bmi:.2f} - {cat}")
                st.toast("BMI Saved!")

    # Pulse Tracker Section
    with col_pulse:
        with st.container(border=True):
            st.subheader("❤️ Pulse Tracker")
            with st.expander("❓ How to use"):
                st.write("1. Start Timer.\n2. Count beats for 10s.\n3. Enter count & Save.")
            st.write("Count beats for **10 seconds**.")
            
            # Interactive Timer
            if st.button("Start Timer"):
                countdown_placeholder = st.empty()
                progress_bar = st.progress(0)
                for i in range(10, -1, -1):
                    countdown_placeholder.markdown(f"<h1 style='text-align: center; color: #3498DB; font-size: 48px; margin: 0;'>{i}</h1>", unsafe_allow_html=True)
                    progress_bar.progress((10-i)*10)
                    time.sleep(1)
                countdown_placeholder.markdown("<h1 style='text-align: center; color: #2ECC71; font-size: 48px; margin: 0;'>DONE!</h1>", unsafe_allow_html=True)
            
            # Record Input
            count = st.number_input("Beats counted:", min_value=0, max_value=50)
            if st.button("Save Heart Rate"):
                if count > 0:
                    bpm = count * 6 # Convert 10s count to 60s BPM (Beats Per Minute)
                    status = "Normal" if 60 <= bpm <= 100 else "High" if bpm > 100 else "Low"
                    color = "#2ECC71" if status == "Normal" else "#E74C3C"
                    st.markdown(f'<div style="background:#121212; padding:10px; border-radius:8px; text-align:center; border: 1px solid {color}; margin-top:10px;"><h2 style="color:{color} !important; margin:0;">{bpm} <span style="font-size:16px;">bpm</span></h2><span style="color:#aaa;">{status}</span></div>', unsafe_allow_html=True)
                    add_record(st.session_state.user['id'], "Pulse", bpm, f"{bpm} bpm - {status}")
                    st.toast("Pulse Saved!")
                else: st.warning("Enter count first.")

# SCREEN 4: EXERCISE LOG (Tabbed)
elif menu == "Exercise Log":
    st.title("Exercise Progress")
    tab_log, tab_cal = st.tabs(["📋 Log & List", "📅 Calendar View"])
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"USE {DB_NAME}")
    cursor.close()
    
    # TAB 1: LIST VIEW 
    with tab_log:
        # Logging Form
        with st.expander("➕ Log New Workout", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                ex_date = st.date_input("Date")
                ex_type = st.selectbox("Activity", ["Running", "Cycling", "Gym/Weights", "Yoga", "Swimming", "Walking", "HIIT", "Pilates"])
            with col2:
                ex_int = st.select_slider("Intensity", options=["Low", "Medium", "High", "Extreme"])
                ex_dur = st.number_input("Duration (minutes)", min_value=1, value=30)
            if st.button("Log Workout"):
                add_exercise(st.session_state.user['id'], ex_type, ex_int, ex_dur, ex_date)
                st.success("Logged!")
                st.rerun()

        # Data Fetching & Filtering
        query = "SELECT date, activity, intensity, duration FROM exercises WHERE user_id=%s ORDER BY date DESC"
        df = pd.read_sql_query(query, conn, params=(st.session_state.user['id'],)) # df = DataFrame
        
        c1, c2 = st.columns(2)
        with c1: time_filter = st.selectbox("Filter Time", ["All Time", "Last 7 Days", "Last 30 Days"])
        with c2: act_filter = st.selectbox("Filter Activity", ["All"] + sorted(df['activity'].unique().tolist()) if not df.empty else ["All"])
        
        # Apply Filters
        df_filtered = df.copy()
        if not df.empty:
            df_filtered['date'] = pd.to_datetime(df_filtered['date'])
            today_ts = pd.Timestamp.today()
            if time_filter == "Last 7 Days": 
                df_filtered = df_filtered[df_filtered['date'] >= (today_ts - pd.Timedelta(days=7))]
            elif time_filter == "Last 30 Days": 
                df_filtered = df_filtered[df_filtered['date'] >= (today_ts - pd.Timedelta(days=30))]
            if act_filter != "All": 
                df_filtered = df_filtered[df_filtered['activity'] == act_filter]

        # Stacked Bar Chart (Activity by Date)
        st.subheader("Weekly Trends")
        if not df_filtered.empty:
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#121212')
            ax.set_facecolor('#1E1E1E')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('#444')
            ax.spines['left'].set_color('#444')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            df_grouped = df_filtered.groupby(['date', 'activity'])['duration'].sum().unstack(fill_value=0)
            df_grouped.plot(kind='bar', stacked=True, ax=ax, edgecolor='#121212')
            ax.set_ylabel("Mins", color="white")
            legend = ax.legend(facecolor='#1E1E1E', edgecolor='#444')
            plt.setp(legend.get_texts(), color='white')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.markdown("<div style='text-align:center; color:#555; padding:20px;'>No data to plot. Log your first workout!</div>", unsafe_allow_html=True)
        
        # Data Table
        st.subheader("Activity Analysis")
        if not df_filtered.empty:
            df_display = df_filtered.copy()
            df_display['date'] = df_display['date'].dt.strftime('%b %d, %Y')
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No data for current selection.")

    # TAB 2: CALENDAR VIEW 
    with tab_cal:
        st.subheader("Workout History")
        # Month/Year Selectors
        col_cal1, col_cal2 = st.columns(2)
        with col_cal1: sel_year = st.selectbox("Year", [2024, 2025, 2026], index=1)
        with col_cal2: sel_month = st.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
        
        month_idx = list(calendar.month_name).index(sel_month)
        query_cal = """SELECT date, activity, duration, intensity 
                       FROM exercises 
                       WHERE user_id=%s AND MONTH(date)=%s AND YEAR(date)=%s 
                       ORDER BY date"""
        df_cal = pd.read_sql_query(query_cal, conn, params=(st.session_state.user['id'], month_idx, sel_year))
        
        # Identify which days have workouts
        workout_days = set()
        if not df_cal.empty:
            df_cal['date'] = pd.to_datetime(df_cal['date'])
            workout_days = set(df_cal['date'].dt.day.tolist())

        # Generate Calendar Grid HTML
        cal_matrix = calendar.monthcalendar(sel_year, month_idx)
        cols = st.columns(7)
        days_header = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days_header):
            cols[i].markdown(f"<div class='cal-header'>{day}</div>", unsafe_allow_html=True)
            
        today_date = datetime.now()
        for week in cal_matrix:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write("")
                else:
                    is_active = "active" if day in workout_days else ""
                    is_today = "today" if (day == today_date.day and month_idx == today_date.month and sel_year == today_date.year) else ""
                    cols[i].markdown(f"<div class='cal-day {is_active} {is_today}'>{day}</div>", unsafe_allow_html=True)
                    
        # Summary & Detailed Cards below calendar
        st.divider()
        st.markdown(f"### {sel_month} Summary")
        if not df_cal.empty:
            total_workouts = len(df_cal)
            total_duration = df_cal['duration'].sum()
            total_cals = sum(estimate_calories(row['activity'], row['intensity'], row['duration']) for _, row in df_cal.iterrows())
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Workouts", total_workouts)
            m2.metric("Duration", f"{total_duration} min")
            m3.metric("Est. Calories", f"{total_cals} Kcal")
            
            st.write("")
            st.write("**Detailed History**")
            for _, row in df_cal.iterrows():
                d_str = row['date'].strftime('%b %d')
                cal_est = estimate_calories(row['activity'], row['intensity'], row['duration'])
                st.markdown(f"""
                <div style="background-color: #1E1E1E; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #3498DB;">
                    <div style="font-weight: bold; font-size: 16px;">{d_str} - {row['activity']}</div>
                    <div style="display: flex; gap: 15px; font-size: 14px; color: #aaa; margin-top: 5px;">
                        <span>⏱️ {row['duration']} min</span>
                        <span>🔥 {cal_est} Kcal</span>
                        <span>⚡ {row['intensity']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"No workouts found for {sel_month} {sel_year}.")

    conn.close()

# SCREEN 5: HISTORY & GRAPHS
elif menu == "History & Graphs":
    st.title("Medical Trends")
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"USE {DB_NAME}")
    c.close()
    
    # Fetch Data
    df_bmi = pd.read_sql_query("SELECT date, value FROM records WHERE user_id=%s AND type='BMI' ORDER BY date DESC", conn, params=(st.session_state.user['id'],))
    df_pulse = pd.read_sql_query("SELECT date, value FROM records WHERE user_id=%s AND type='Pulse' ORDER BY date DESC", conn, params=(st.session_state.user['id'],))
    conn.close()
    
    # Filter Controls
    col_filter, _ = st.columns([1, 3])
    with col_filter:
        time_filter = st.selectbox("Filter Time", ["All Time", "Last 7 Days", "Last 30 Days"], key="history_filter")

    df_bmi['date'] = pd.to_datetime(df_bmi['date'])
    df_pulse['date'] = pd.to_datetime(df_pulse['date'])
    today_ts = pd.Timestamp.today()
    
    # Apply Time Filter
    if time_filter == "Last 7 Days":
        cutoff = today_ts - pd.Timedelta(days=7)
        df_bmi = df_bmi[df_bmi['date'] >= cutoff]
        df_pulse = df_pulse[df_pulse['date'] >= cutoff]
    elif time_filter == "Last 30 Days":
        cutoff = today_ts - pd.Timedelta(days=30)
        df_bmi = df_bmi[df_bmi['date'] >= cutoff]
        df_pulse = df_pulse[df_pulse['date'] >= cutoff]

    # Classification Helpers
    def classify_bmi(bmi):
        if bmi < 18.5: return "Underweight"
        elif bmi < 25: return "Normal"
        elif bmi < 30: return "Overweight"
        else: return "Obese"

    def classify_pulse(bpm):
        if bpm < 60: return "Low"
        elif bpm <= 100: return "Normal"
        else: return "High"
    
    tab1, tab2 = st.tabs(["BMI History", "Pulse History"])
    
    # TAB 1: BMI
    with tab1:
        if not df_bmi.empty:
            df_bmi['classification'] = df_bmi['value'].apply(classify_bmi)
            df_chart = df_bmi.sort_values('date')
            
            # Matplotlib Chart
            fig, ax = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor('#121212')
            ax.set_facecolor('#1E1E1E')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.spines['bottom'].set_color('#444')
            ax.spines['left'].set_color('#444')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            ax.plot(df_chart['date'], df_chart['value'], marker='o', color='#2ECC71', linewidth=2)
            ax.set_ylabel("BMI Score", fontsize=12)
            ax.set_xlabel("Date", fontsize=12)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            plt.xticks(rotation=45)
            ax.grid(True, linestyle='--', alpha=0.3, color='#444')
            ax.axhline(y=25, color='#3498DB', linestyle='--', label='Overweight Threshold')
            legend = ax.legend(facecolor='#1E1E1E', edgecolor='#444')
            plt.setp(legend.get_texts(), color='white')
            st.pyplot(fig)
            
            st.write("### 📊 Detailed History")
            df_display = df_bmi.sort_values('date', ascending=False).copy()
            df_display['date'] = df_display['date'].dt.strftime('%b %d, %Y %I:%M %p')
            st.dataframe(df_display, use_container_width=True, column_config={"date": "Date Recorded", "value": st.column_config.NumberColumn("BMI Score", format="%.2f"), "classification": "Category"})
        else: 
            st.info("No BMI records found. Use Health Tools to calculate one!")
            
    # TAB 2: PULSE
    with tab2:
        if not df_pulse.empty:
            df_pulse['classification'] = df_pulse['value'].apply(classify_pulse)
            df_chart = df_pulse.sort_values('date')
            
            fig, ax = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor('#121212')
            ax.set_facecolor('#1E1E1E')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.spines['bottom'].set_color('#444')
            ax.spines['left'].set_color('#444')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            ax.plot(df_chart['date'], df_chart['value'], marker='o', color='#E74C3C', linewidth=2)
            ax.set_ylabel("BPM", fontsize=12)
            ax.set_xlabel("Date", fontsize=12)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            plt.xticks(rotation=45)
            ax.grid(True, linestyle='--', alpha=0.3, color='#444')
            ax.axhline(y=60, color='#3498DB', linestyle=':', label='Low (60)')
            ax.axhline(y=100, color='#3498DB', linestyle=':', label='High (100)')
            legend = ax.legend(facecolor='#1E1E1E', edgecolor='#444')
            plt.setp(legend.get_texts(), color='white')
            st.pyplot(fig)
            
            st.write("### 📊 Detailed History")
            df_display = df_pulse.sort_values('date', ascending=False).copy()
            df_display['date'] = df_display['date'].dt.strftime('%b %d, %Y %I:%M %p')
            st.dataframe(df_display, use_container_width=True, column_config={"date": "Date Recorded", "value": st.column_config.NumberColumn("Heart Rate", format="%d bpm"), "classification": "Status"})
        else: 
            st.info("No Pulse records found. Use Health Tools to measure it!")

# SCREEN 6: ADMIN PANEL (Protected)
elif menu == "Admin Panel":
    st.title("Admin Dashboard 🛡️")
    st.markdown("Authorized access only. Manage users and system data.")
    
    # 1. System Actions (Reset DB)
    with st.container(border=True):
        st.subheader("⚠️ Global System Actions")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Reset All Data", type="primary", help="Deletes ALL users and generates fresh demo data."):
                if reset_database():
                    st.session_state.user = None
                    st.success("Database Reset! Please refresh.")
                    time.sleep(1)
                    st.rerun()
        with col2:
            st.warning("This action cannot be undone. It will wipe all registered users and history.")

    # 2. User Management (List & Delete)
    st.divider()
    st.subheader("👥 User Management")
    
    conn = get_connection()
    c = conn.cursor(dictionary=True)
    c.execute(f"USE {DB_NAME}")
    
    # Get all non-admin users
    c.execute("SELECT id, username, email, gender FROM users WHERE username != 'Admin'")
    all_users = c.fetchall()
    
    if all_users:
        # Prepare Data for Table
        monitoring_data = []
        user_map = {} # Map ID to Name for selector
        
        for u in all_users:
            # Store for selector dropdown
            user_map[f"{u['username']} ({u['email']})"] = u['id']
            
            # Get Last Active Date
            c.execute("SELECT date FROM exercises WHERE user_id=%s ORDER BY date DESC LIMIT 1", (u['id'],))
            last_ex = c.fetchone()
            last_active = last_ex['date'].strftime('%Y-%m-%d') if last_ex else "Inactive"
            
            # Get Total Workouts
            c.execute("SELECT COUNT(*) as cnt FROM exercises WHERE user_id=%s", (u['id'],))
            ex_count = c.fetchone()['cnt']
            
            monitoring_data.append({
                "ID": u['id'],
                "User": u['username'],
                "Email": u['email'],
                "Gender": u['gender'],
                "Last Active": last_active,
                "Total Logs": ex_count
            })
        
        df_monitor = pd.DataFrame(monitoring_data)
        
        # Display Monitoring Table
        st.dataframe(
            df_monitor, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "User": st.column_config.TextColumn("Username", width="medium"),
                "Total Logs": st.column_config.ProgressColumn("Engagement", format="%d", min_value=0, max_value=50)
            }
        )
        
        # Delete User Section
        st.write("")
        st.markdown("### 🗑️ Delete User")
        
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            selected_user_str = st.selectbox("Select User to Delete", list(user_map.keys()))
        
        with col_btn:
            st.write("") # Spacer alignment
            if st.button("Delete User", type="primary"):
                user_id_to_del = user_map[selected_user_str]
                if delete_user_account(user_id_to_del):
                    st.success(f"User {selected_user_str.split('(')[0]} deleted.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to delete user.")
    else:
        st.info("No users registered yet.")
        
    conn.close()