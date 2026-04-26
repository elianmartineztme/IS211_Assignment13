import sqlite3
from flask import Flask, render_template, request, redirect, session, g

app = Flask(__name__)
app.secret_key = "secret_key_for_class_assignment"
DATABASE = "hw13.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_required():
    return session.get("logged_in") is True


@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "password":
            session["logged_in"] = True
            return redirect("/dashboard")
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect("/login")

    db = get_db()
    students = db.execute("SELECT * FROM students").fetchall()
    quizzes = db.execute("SELECT * FROM quizzes").fetchall()

    return render_template("dashboard.html", students=students, quizzes=quizzes)


@app.route("/student/add", methods=["GET", "POST"])
def add_student():
    if not login_required():
        return redirect("/login")

    error = None

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()

        if not first_name or not last_name:
            error = "First name and last name are required."
        else:
            db = get_db()
            db.execute(
                "INSERT INTO students (first_name, last_name) VALUES (?, ?)",
                (first_name, last_name)
            )
            db.commit()
            return redirect("/dashboard")

    return render_template("student_add.html", error=error)


@app.route("/quiz/add", methods=["GET", "POST"])
def add_quiz():
    if not login_required():
        return redirect("/login")

    error = None

    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        questions = request.form.get("questions", "").strip()
        quiz_date = request.form.get("quiz_date", "").strip()

        if not subject or not questions or not quiz_date:
            error = "All fields are required."
        else:
            try:
                questions = int(questions)
                db = get_db()
                db.execute(
                    "INSERT INTO quizzes (subject, questions, quiz_date) VALUES (?, ?, ?)",
                    (subject, questions, quiz_date)
                )
                db.commit()
                return redirect("/dashboard")
            except ValueError:
                error = "Questions must be a number."

    return render_template("quiz_add.html", error=error)


@app.route("/student/<int:student_id>")
def student_results(student_id):
    if not login_required():
        return redirect("/login")

    db = get_db()

    student = db.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if student is None:
        return "Student not found"

    results = db.execute("""
        SELECT results.score, quizzes.id AS quiz_id, quizzes.subject, quizzes.quiz_date
        FROM results
        JOIN quizzes ON results.quiz_id = quizzes.id
        WHERE results.student_id = ?
    """, (student_id,)).fetchall()

    return render_template("student_results.html", student=student, results=results)


@app.route("/results/add", methods=["GET", "POST"])
def add_result():
    if not login_required():
        return redirect("/login")

    db = get_db()
    students = db.execute("SELECT * FROM students").fetchall()
    quizzes = db.execute("SELECT * FROM quizzes").fetchall()
    error = None

    if request.method == "POST":
        student_id = request.form.get("student_id")
        quiz_id = request.form.get("quiz_id")
        score = request.form.get("score", "").strip()

        try:
            score = int(score)
            if score < 0 or score > 100:
                error = "Score must be between 0 and 100."
            else:
                db.execute(
                    "INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)",
                    (student_id, quiz_id, score)
                )
                db.commit()
                return redirect("/dashboard")
        except ValueError:
            error = "Score must be a number."

    return render_template("result_add.html", students=students, quizzes=quizzes, error=error)


if __name__ == "__main__":
    app.run(debug=True)