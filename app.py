from flask import Flask, request, jsonify, render_template, session, redirect
from database.db_config import connectToDB
import MySQLdb

app = Flask(__name__)

# ///// #
# INDEX #
# ///// #
@app.route("/index", methods=["GET"])
def index():
  return render_template("index.j2")

# /////// #
# COURSES #
# /////// #
@app.route("/courses", methods=["GET"])
def viewCourses():
  # Check DB connection and reconnect if needed
  mysql_connection = connectToDB()
  
  return render_template("courses.j2")

def addCourse():
  pass

# ///// #
# TERMS #
# //////#
@app.route("/terms", methods=["GET"])
def viewTerms():
  # Check DB connection and reconnect if needed
  mysql_connection = connectToDB()

  # --------------
  # TERM RETRIEVAL
  # --------------
  # Retrieve all terms from 'Terms' table
  query = """
    SELECT *
    FROM Terms 
    ORDER BY startDate ASC
  """

  # Execute query
  cursor = mysql_connection.cursor()
  cursor.execute(query)
  terms = cursor.fetchall()

  # Format terms to pass to template
  terms = [
    {
      "id": row[0],
      "name": row[1],
      "startDate": row[2],
      "endDate": row[3]
    }
    for row in terms
  ]

  # -----------------
  # COURSES RETRIEVAL
  # -----------------
  # Retrieve all courses from 'Courses' table
  query = """
    SELECT 
      CONCAT(code, ' ', name) AS course,
      courseID
    FROM Courses
    ORDER BY code ASC
  """

  # Execute query
  cursor = mysql_connection.cursor()
  cursor.execute(query)
  courses = cursor.fetchall()

  # Format courses to pass to template
  courses = [
    {
      "course": row[0],
      "id": row[1]
    }
    for row in courses
  ]

  return render_template("terms.j2", terms=terms, courses=courses)

@app.route("/add-term", methods=["POST"])
def addTerm():
  pass

# ////////////////// #
# STUDENT TERM PLANS #
# ///////////////////#
@app.route("/student-term-plans", methods=["GET"])
def viewStudentTermPlans():
  # Check DB connection and reconnect if needed
  mysql_connection = connectToDB()
  
  return render_template("student-term-plans.j2")

def addStudentTermPlan():
  pass

# //////// #
# STUDENTS #
# /////////#
@app.route("/students", methods=["GET"])
def viewStudents():
  # Check DB connection and reconnect if needed
  mysql_connection = connectToDB()
  
  return render_template("students.j2")

def addStudent():
  pass

def removeStudent():
  pass

def updateStudent():
  pass
  
# Listener
if __name__ == "__main__":
  """
  * Terminal Commands *
  run: 
    gunicorn --name OSUCourseTracker -b 0.0.0.0:7124 -D app:app
  stop:
    pkill -f 'gunicorn --name OSUCourseTracker'
  """
  app.run()