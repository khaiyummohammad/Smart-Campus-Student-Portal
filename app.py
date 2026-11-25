
from flask import Flask, render_template, request, redirect, url_for, session
from database import (
    create_tables,
    add_demo_student,
    add_demo_attendance,
    add_demo_assignments,
    add_demo_timetable,
    add_demo_announcements,
    add_demo_materials
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, timedelta
import sqlite3

app = Flask(__name__)
app.secret_key = "smart_campus_secret_key"


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# LOGIN
@app.route("/login", methods=["POST"])
def login():
    enrollment = request.form.get("enrollment")
    password = request.form.get("password")

    connection = sqlite3.connect("smart_campus.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE enrollment_number = ?",
        (enrollment,)
    )
    student = cursor.fetchone()
    connection.close()

    if student and check_password_hash(student["password"], password):
        session["student_name"] = student["student_name"]
        session["enrollment"] = student["enrollment_number"]
        return redirect(url_for("dashboard"))

    return render_template(
        "index.html",
        error="Invalid Enrollment Number or Password!"
    )


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "student_name" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("smart_campus.db")
    cursor = connection.cursor()

    enrollment = session["enrollment"]

    # Attendance calculation
    cursor.execute("""
        SELECT SUM(total_classes), SUM(attended_classes)
        FROM attendance
        WHERE enrollment_number = ?
    """, (enrollment,))

    attendance_result = cursor.fetchone()

    total_classes = attendance_result[0] or 0
    attended_classes = attendance_result[1] or 0

    attendance_percentage = (
        round((attended_classes / total_classes) * 100, 2)
        if total_classes > 0 else 0
    )

    # Total assignments
    cursor.execute("""
        SELECT COUNT(*)
        FROM assignments
        WHERE enrollment_number = ?
    """, (enrollment,))

    total_assignments = cursor.fetchone()[0]

    # Completed assignments
    cursor.execute("""
        SELECT COUNT(*)
        FROM assignments
        WHERE enrollment_number = ?
        AND status = 'Completed'
    """, (enrollment,))

    completed_assignments = cursor.fetchone()[0]

    # Pending assignments
    pending_assignments = total_assignments - completed_assignments

    # Assignment completion percentage
    completion_percentage = (
        round((completed_assignments / total_assignments) * 100, 2)
        if total_assignments > 0 else 0
    )

    # Total timetable classes
    cursor.execute("""
        SELECT COUNT(*)
        FROM timetable
        WHERE enrollment_number = ?
    """, (enrollment,))

    total_timetable = cursor.fetchone()[0]

    # Total announcements
    cursor.execute("SELECT COUNT(*) FROM announcements")
    total_announcements = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        student_name=session["student_name"],
        enrollment=enrollment,
        attendance_percentage=attendance_percentage,
        total_assignments=total_assignments,
        completed_assignments=completed_assignments,
        pending_assignments=pending_assignments,
        completion_percentage=completion_percentage,
        total_timetable=total_timetable,
        total_announcements=total_announcements
    )


# ATTENDANCE
@app.route("/attendance")
def attendance():
    if "enrollment" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("smart_campus.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM attendance
        WHERE enrollment_number = ?
    """, (session["enrollment"],))

    attendance_data = cursor.fetchall()
    connection.close()

    total_classes = sum(
        row["total_classes"] for row in attendance_data
    )

    attended_classes = sum(
        row["attended_classes"] for row in attendance_data
    )

    missed_classes = total_classes - attended_classes

    percentage = (
        round((attended_classes / total_classes) * 100, 2)
        if total_classes > 0 else 0
    )

    return render_template(
        "attendance.html",
        attendance_data=attendance_data,
        total_classes=total_classes,
        attended_classes=attended_classes,
        missed_classes=missed_classes,
        percentage=percentage
    )


# ASSIGNMENTS
@app.route("/assignments")
def assignments():
    if "enrollment" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("smart_campus.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM assignments
        WHERE enrollment_number = ?
    """, (session["enrollment"],))

    assignments_data = cursor.fetchall()
    connection.close()

    today = date.today().isoformat()
    due_soon = (date.today() + timedelta(days=2)).isoformat()

    return render_template(
        "assignments.html",
        assignments=assignments_data,
        today=today,
        due_soon=due_soon
    )


# MARK ASSIGNMENT AS COMPLETED
@app.route("/complete_assignment/<int:assignment_id>", methods=["POST"])
def complete_assignment(assignment_id):
    if "enrollment" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("smart_campus.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE assignments
        SET status = 'Completed'
        WHERE id = ? AND enrollment_number = ?
    """, (assignment_id, session["enrollment"]))

    connection.commit()
    connection.close()

    return redirect(url_for("assignments"))


# TIMETABLE
@app.route("/timetable")
def timetable():
    if "student_name" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("smart_campus.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM timetable
        WHERE enrollment_number = ?
        ORDER BY id
    """, (session["enrollment"],))

    timetable_data = cursor.fetchall()
    connection.close()

    return render_template(
        "timetable.html",
        timetable_data=timetable_data
    )


# ANNOUNCEMENTS
@app.route("/announcements")
def announcements():
    if "student_name" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("smart_campus.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM announcements
        ORDER BY date DESC
    """)

    announcements_data = cursor.fetchall()
    connection.close()

    return render_template(
        "announcements.html",
        announcements_data=announcements_data
    )


# STUDENT REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        student_name = request.form.get("student_name")
        enrollment = request.form.get("enrollment")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            return render_template(
                "register.html",
                error="Passwords do not match!"
            )

        if len(password) < 6:
            return render_template(
                "register.html",
                error="Password must contain at least 6 characters!"
            )

        connection = sqlite3.connect("smart_campus.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM students
            WHERE enrollment_number = ?
        """, (enrollment,))

        existing_student = cursor.fetchone()

        if existing_student:
            connection.close()
            return render_template(
                "register.html",
                error="Enrollment Number already registered!"
            )

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO students
            (student_name, enrollment_number, password)
            VALUES (?, ?, ?)
        """, (student_name, enrollment, hashed_password))

        connection.commit()
        connection.close()

        return render_template(
            "register.html",
            success="Registration successful! You can login now."
        )

    return render_template("register.html")


# STUDY MATERIALS
@app.route("/materials")
def materials():
    if "student_name" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("smart_campus.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM materials
        ORDER BY subject
    """)

    materials_data = cursor.fetchall()
    connection.close()

    return render_template(
        "materials.html",
        materials_data=materials_data
    )


# STUDENT PROFILE
@app.route("/profile")
def profile():
    if "enrollment" not in session:
        return redirect(url_for("home"))

    connection = sqlite3.connect("smart_campus.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE enrollment_number = ?
    """, (session["enrollment"],))

    student = cursor.fetchone()
    connection.close()

    return render_template(
        "profile.html",
        student=student
    )


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# START APPLICATION
if __name__ == "__main__":
    create_tables()
    add_demo_student()
    add_demo_attendance()
    add_demo_assignments()
    add_demo_timetable()
    add_demo_announcements()
    add_demo_materials()

    app.run(debug=True)
