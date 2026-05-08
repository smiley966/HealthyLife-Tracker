This is a project made for Event Driven Subject of Sir. Joseph Darwin Co.

Brought to you by the Group DATS of BSIT 3-1

Members:
Antonio, Paul Zabdiel
Dizon, Bryan
Sañoza, Rafael
Toledana, Jan Louis

HealthyLife Tracker - Setup Instructions

To run this application on a new device, follow these steps.

1. Prerequisites

You need two main things installed on the new computer:

Python (Version 3.8 or higher)

Download from: https://www.python.org/downloads/

IMPORTANT: During installation, check the box that says "Add Python to PATH".

XAMPP (for the MySQL Database)

Download from: https://www.apachefriends.org/index.html

Install it and open the XAMPP Control Panel.

2. Setting up the Database

Open XAMPP Control Panel.

Click Start next to MySQL.

Check your Port: - Look at the "Port" column next to MySQL.

The app is currently set to use port 3307.

IF your XAMPP uses port 3306 (the default):

Open fitness_app.py in a text editor.

Find the line: 'port': 3307

Change it to: 'port': 3306

Note: You do not need to manually create the database. The app will automatically create the "fitness_app_web" database and all tables the first time you run it.

3. Installing Libraries

Open the folder where you saved fitness_app.py.

Right-click inside the folder > Open Terminal (or Command Prompt).

Run the following command to install the necessary libraries:

pip install streamlit mysql-connector-python pandas matplotlib

4. Running the App

In the terminal/command prompt, type:

streamlit run fitness_app.py

The app should automatically open in your default web browser.

Login using the demo accounts (displayed on the login screen) or create a new one.

Troubleshooting

Database Connection Error: Ensure XAMPP MySQL is running and that the port number in the python file matches the port shown in XAMPP.

Module Not Found: Run the pip install command again to ensure all libraries downloaded correctly.