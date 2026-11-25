
import sqlite3

from werkzeug.security import generate_password_hash

def connect_db():
    connection = sqlite3.connect("smart_campus.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():

    connection = connect_db()
    cursor = connection.cursor()

    # Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            enrollment_number TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Attendance Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_number TEXT NOT NULL,
            subject TEXT NOT NULL,
            total_classes INTEGER NOT NULL,
            attended_classes INTEGER NOT NULL
        )
    """)
    # Assignments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_number TEXT NOT NULL,
            subject TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)
    # Timetable Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_number TEXT NOT NULL,
            day TEXT NOT NULL,
            subject TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            room_number TEXT NOT NULL,
            faculty_name TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    print("Database and tables created successfully!")




    
def add_demo_student():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE enrollment_number = ?",
        ("SC2026001",)
    )
def add_demo_attendance():
    connection = connect_db()
    cursor = connection.cursor()

    attendance_data = [
        ("SC2026001", "Python Programming", 30, 26),
        ("SC2026001", "DBMS", 28, 24),
        ("SC2026001", "Data Structures", 32, 27),
        ("SC2026001", "Mathematics", 30, 21),
        ("SC2026001", "Computer Networks", 26, 22)
    ]

    for record in attendance_data:
        cursor.execute(
            "SELECT * FROM attendance WHERE enrollment_number = ? AND subject = ?",
            (record[0], record[1])
        )

        existing = cursor.fetchone()

        if existing is None:
            cursor.execute(
                """INSERT INTO attendance
                (enrollment_number, subject, total_classes, attended_classes)
                VALUES (?, ?, ?, ?)""",
                record
            )

    connection.commit()
    connection.close()

    print("Demo attendance added successfully!")

def add_demo_assignments():
    connection = connect_db()
    cursor = connection.cursor()

    assignments_data = [
        ("SC2026001", "Python Programming", "Python Mini Project",
         "Create a simple Python application.", "2026-11-28", "Pending"),

        ("SC2026001", "DBMS", "SQL Queries Assignment",
         "Write 10 SQL queries using a student database.", "2026-12-02", "Pending"),

        ("SC2026001", "Data Structures", "Linked List Assignment",
         "Implement insertion and deletion in a linked list.", "2026-12-05", "Pending"),

        ("SC2026001", "Mathematics", "Matrix Problems",
         "Solve the given matrix operations problems.", "2026-12-08", "Pending")
    ]

    for record in assignments_data:
        cursor.execute(
            "SELECT * FROM assignments WHERE enrollment_number = ? AND title = ?",
            (record[0], record[2])
        )

        existing = cursor.fetchone()

        if existing is None:
            cursor.execute(
                """INSERT INTO assignments
                (enrollment_number, subject, title, description, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?)""",
                record
            )

    connection.commit()
    connection.close()

    print("Demo assignments added successfully!")

def add_demo_timetable():
    connection = connect_db()
    cursor = connection.cursor()

    timetable_data = [
        ("SC2026001", "Monday", "Python Programming", "09:00 AM", "10:00 AM", "Room 101", "Prof. Patel"),
        ("SC2026001", "Monday", "DBMS", "10:00 AM", "11:00 AM", "Room 102", "Prof. Shah"),
        ("SC2026001", "Monday", "Mathematics", "11:15 AM", "12:15 PM", "Room 103", "Prof. Mehta"),

        ("SC2026001", "Tuesday", "Data Structures", "09:00 AM", "10:00 AM", "Room 104", "Prof. Kumar"),
        ("SC2026001", "Tuesday", "Python Programming", "10:00 AM", "11:00 AM", "Room 101", "Prof. Patel"),
        ("SC2026001", "Tuesday", "Computer Networks", "11:15 AM", "12:15 PM", "Room 105", "Prof. Joshi"),

        ("SC2026001", "Wednesday", "DBMS", "09:00 AM", "10:00 AM", "Room 102", "Prof. Shah"),
        ("SC2026001", "Wednesday", "Mathematics", "10:00 AM", "11:00 AM", "Room 103", "Prof. Mehta"),
        ("SC2026001", "Wednesday", "Data Structures", "11:15 AM", "12:15 PM", "Room 104", "Prof. Kumar"),

        ("SC2026001", "Thursday", "Computer Networks", "09:00 AM", "10:00 AM", "Room 105", "Prof. Joshi"),
        ("SC2026001", "Thursday", "Python Programming", "10:00 AM", "11:00 AM", "Room 101", "Prof. Patel"),
        ("SC2026001", "Thursday", "DBMS", "11:15 AM", "12:15 PM", "Room 102", "Prof. Shah"),

        ("SC2026001", "Friday", "Data Structures", "09:00 AM", "10:00 AM", "Room 104", "Prof. Kumar"),
        ("SC2026001", "Friday", "Computer Networks", "10:00 AM", "11:00 AM", "Room 105", "Prof. Joshi"),
        ("SC2026001", "Friday", "Mathematics", "11:15 AM", "12:15 PM", "Room 103", "Prof. Mehta")
    ]

    for record in timetable_data:
        cursor.execute(
            "SELECT * FROM timetable WHERE enrollment_number = ? AND day = ? AND subject = ?",
            (record[0], record[1], record[2])
        )

        existing = cursor.fetchone()

        if existing is None:
            cursor.execute(
                """INSERT INTO timetable
                (enrollment_number, day, subject, start_time, end_time, room_number, faculty_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                record
            )
               

    connection.commit()
    cursor.execute("SELECT COUNT(*) FROM timetable")
    result = cursor.fetchone()
    print("Actual timetable rows in database:", result)
    connection.close()

    print("Demo timetable added successfully!")

def add_demo_announcements():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM announcements")
    count = cursor.fetchone()[0]

    if count == 0:
        announcements_data = [
            ("Mid Semester Exams", "Mid semester examinations will begin next week. Prepare accordingly.", "2026-11-22"),
            ("Project Submission", "All students must submit their project reports before the deadline.", "2026-11-22"),
            ("Library Notice", "Students are requested to return overdue library books as soon as possible.", "2026-11-22"),
            ("Campus Event", "A technical event will be organized on campus. Stay tuned for further details.", "2026-11-22"),
            ("Attendance Reminder", "Students must maintain minimum required attendance in all subjects.", "2026-11-22")
        ]

        cursor.executemany(
            "INSERT INTO announcements (title, message, date) VALUES (?, ?, ?)",
            announcements_data
        )

        connection.commit()

    connection.close()
    print("Announcements added successfully!")

def add_demo_materials():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            link TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM materials")
    count = cursor.fetchone()[0]

    if count == 0:
        materials_data = [
            ("Python", "Python Official Tutorial", "Python programming basics and documentation.", "https://docs.python.org/3/tutorial/"),
            ("DBMS", "SQL Learning Guide", "Learn database concepts and SQL queries.", "https://www.w3schools.com/sql/"),
            ("Data Structures", "Data Structures Guide", "Learn arrays, linked lists, stacks and queues.", "https://www.geeksforgeeks.org/data-structures/"),
            ("Computer Networks", "Networking Basics", "Introduction to computer networking concepts.", "https://www.geeksforgeeks.org/computer-networks/"),
            ("Mathematics", "Mathematics Learning", "Explore mathematical concepts and practice.", "https://www.khanacademy.org/math")
        ]

        cursor.executemany(
            "INSERT INTO materials (subject, title, description, link) VALUES (?, ?, ?, ?)",
            materials_data
        )

        connection.commit()

    connection.close()
    print("Study materials added successfully!")

