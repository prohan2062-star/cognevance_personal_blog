# Personal Blog Website

A dynamic and responsive Personal Blog Website developed using Python Flask, HTML, CSS, JavaScript and SQLite.

## Features

- User Registration and Login
- Secure Password Hashing
- User Dashboard
- Create New Blog Posts
- View All Published Blogs
- Read Full Blog Details
- Edit Existing Blog Posts
- Delete Blog Posts
- User Session Management
- Protected Dashboard Routes
- Responsive Design for Mobile and Desktop

## Technologies Used

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite
- **Authentication:** Werkzeug Password Hashing

## Project Structure

text
personal_blog/
│
├── app.py
├── database.py
├── blog.db
├── requirements.txt
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── create_blog.html
│   ├── edit_blog.html
│   └── blog_detail.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
└── README.md


## Installation and Setup

1. Clone or download this repository.
2. Open the project folder in VS Code.
3. Create a virtual environment:

bash
python -m venv venv


4. Activate the virtual environment (Windows PowerShell):

powershell
.\venv\Scripts\Activate.ps1


5. Install dependencies:

bash
pip install -r requirements.txt


6. Run the application:

bash
python app.py


7. Open your browser:

text
http://127.0.0.1:5000


## Database

SQLite is used to store user accounts and blog posts. Passwords are stored as secure hashes.

## Project Purpose

This project was developed as part of the Cognevance Internship Program – Level 1.

## Developer

**Rohan Pawar**

