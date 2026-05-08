# 🏃 HealthyLife Tracker

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://healthylife-tracker.streamlit.app/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**HealthyLife Tracker** is a comprehensive, web-based fitness and health monitoring system built with Streamlit and MySQL. It allows users to track their Body Mass Index (BMI), heart rate, and workout logs with real-time analytics and visualizations.

---

## ✨ Features

- **📊 Dashboard Overview**: Get a quick glance at your BMI, average pulse, and weekly workout engagement.
- **⚖️ BMI Calculator**: Calculate and track your Body Mass Index with historical logging.
- **❤️ Pulse Tracker**: Monitor your heart rate with an integrated 10-second timer.
- **📅 Exercise Log**: Log various activities (Running, Cycling, HIIT, etc.) and view them in a list or calendar format.
- **📈 Medical Trends**: Visualize your health progress over time with dynamic charts (Matplotlib & Pandas).
- **🛡️ Admin Panel**: System-level management for user accounts and database maintenance.

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python (3.8 or higher)**: [Download Python](https://www.python.org/downloads/)
  * *Important: Ensure "Add Python to PATH" is checked during installation.*
- **XAMPP (MySQL Database)**: [Download XAMPP](https://www.apachefriends.org/index.html)

### 2. Database Setup

1. Open **XAMPP Control Panel**.
2. Start the **MySQL** module.
3. **Note on Ports**: The app defaults to port `3307`. If your XAMPP uses `3306`, update the `DB_CONFIG` in `fitness_app.py`:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '',
       'port': 3306  # Change from 3307 if needed
   }
   ```
4. The database (`fitness_app_web`) and tables will be **automatically created** upon the first run.

### 3. Installation

Clone the repository and install the required libraries:

```bash
pip install -r requirements.txt
```

### 4. Running the App

```bash
streamlit run fitness_app.py
```

---

## 👥 Contributors (Group DATS - BSIT 3-1)

This project was developed for the **Event Driven Programming** subject.

- **Antonio, Paul Zabdiel**
- **Dizon, Bryan**
- **Sañoza, Rafael**
- **Toledana, Jan Louis**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📁 Project Structure

- `fitness_app.py`: Main application logic and UI.
- `requirements.txt`: Python dependencies.
- `lowgoow.png`: Application logo.
- `profile.png`: Profile placeholder asset.
- `HealthyLife Tracker_...pdf`: Full project documentation.
