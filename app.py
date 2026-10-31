
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import init_db, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)

# Secret Key
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-only-change-this-secret-before-deployment"
)

# Initialize Database
init_db()


# HOME PAGE - Show All Published Blogs
@app.route("/")
def home():

    conn = get_db_connection()

    try:
        blogs = conn.execute(
            """
            SELECT blogs.*, users.username
            FROM blogs
            JOIN users ON blogs.user_id = users.id
            ORDER BY blogs.created_at DESC
            """
        ).fetchall()

    finally:
        conn.close()

    return render_template("index.html", blogs=blogs)

@app.route("/blog/<int:blog_id>")
def blog_detail(blog_id):
    conn = get_db_connection()

    try:
        blog = conn.execute("""
            SELECT blogs.*, users.username
            FROM blogs
            JOIN users ON blogs.user_id = users.id
            WHERE blogs.id = ?
        """, (blog_id,)).fetchone()
    finally:
        conn.close()

    if blog is None:
        return "Blog not found", 404

    return render_template("blog_detail.html", blog=blog)

# USER REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required!", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters!", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        try:
            conn.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username, email, hashed_password)
            )

            conn.commit()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("This email is already registered!", "error")
            return redirect(url_for("register"))

        finally:
            conn.close()

    return render_template("register.html")


# USER LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter email and password!", "error")
            return redirect(url_for("login"))

        conn = get_db_connection()

        try:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        finally:
            conn.close()

        if user and check_password_hash(user["password_hash"], password):

            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash("Login successful! Welcome back.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password!", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# DASHBOARD - Show User's Blogs
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()

    try:
        blogs = conn.execute(
            """
            SELECT * FROM blogs
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (session["user_id"],)
        ).fetchall()

    finally:
        conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        blogs=blogs
    )


# USER LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


# CREATE BLOG
@app.route("/create-blog", methods=["GET", "POST"])
def create_blog():

    if "user_id" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            flash("Title and content are required!", "error")
            return redirect(url_for("create_blog"))

        conn = get_db_connection()

        try:
            conn.execute(
                """
                INSERT INTO blogs (user_id, title, category, content)
                VALUES (?, ?, ?, ?)
                """,
                (session["user_id"], title, category, content)
            )

            conn.commit()

            flash("Blog created successfully!", "success")
            return redirect(url_for("dashboard"))

        finally:
            conn.close()

    return render_template("create_blog.html")


# EDIT BLOG
@app.route("/edit-blog/<int:blog_id>", methods=["GET", "POST"])
def edit_blog(blog_id):

    if "user_id" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()

    try:
        blog = conn.execute(
            """
            SELECT * FROM blogs
            WHERE id = ? AND user_id = ?
            """,
            (blog_id, session["user_id"])
        ).fetchone()

        if blog is None:
            flash("Blog not found!", "error")
            return redirect(url_for("dashboard"))

        if request.method == "POST":

            title = request.form.get("title", "").strip()
            category = request.form.get("category", "").strip()
            content = request.form.get("content", "").strip()

            if not title or not content:
                flash("Title and content are required!", "error")
                return redirect(url_for("edit_blog", blog_id=blog_id))

            conn.execute(
                """
                UPDATE blogs
                SET title = ?, category = ?, content = ?
                WHERE id = ? AND user_id = ?
                """,
                (title, category, content, blog_id, session["user_id"])
            )

            conn.commit()

            flash("Blog updated successfully!", "success")
            return redirect(url_for("dashboard"))

    finally:
        conn.close()

    return render_template("edit_blog.html", blog=blog)


# DELETE BLOG
@app.route("/delete-blog/<int:blog_id>", methods=["POST"])
def delete_blog(blog_id):

    if "user_id" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()

    try:
        result = conn.execute(
            """
            DELETE FROM blogs
            WHERE id = ? AND user_id = ?
            """,
            (blog_id, session["user_id"])
        )

        conn.commit()

        if result.rowcount > 0:
            flash("Blog deleted successfully!", "success")
        else:
            flash("Blog not found!", "error")

    finally:
        conn.close()

    return redirect(url_for("dashboard"))


# RUN APPLICATION
if __name__ == "__main__":
    app.run(debug=True)
