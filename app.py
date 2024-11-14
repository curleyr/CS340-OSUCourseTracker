from flask import Flask, request, jsonify, render_template, session, redirect
from database.db_config import connectToDB
import MySQLdb

app = Flask(__name__)

# ///// #
# INDEX #
# ///// #
@app.route("/", methods=["GET"])
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

  # ---------------------------------
  # COURSES & PREREQUISITES RETRIEVAL
  # ---------------------------------
  # Retrieve all courses and prerequisitesfrom 'Courses' table
  query = """
    SELECT
      c.courseID,
      CONCAT(c.code, ' ', c.name) AS course,
      c.credit,  
      GROUP_CONCAT((SELECT CONCAT(code, ' ', name) FROM Courses WHERE courseID = pc.courseID) ORDER BY pc.courseID SEPARATOR ', ') AS prerequisites 
      FROM Courses c 
    LEFT JOIN Prerequisites p   
      ON c.courseID = p.courseID 
    LEFT JOIN Courses pc  
      ON p.prerequisiteCourseID = pc.courseID 
    GROUP BY c.courseID 
    ORDER BY c.code ASC
  """

  # Execute query
  cursor = mysql_connection.cursor()
  cursor.execute(query)
  courses = cursor.fetchall()

  # Format courses to pass to template
  courses = [
    {
      "id": row[0],
      "course": row[1],
      "credit": row[2],
      "prerequisites": row[3]
    }
    for row in courses
  ]

  return render_template("courses.j2", courses=courses)

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
    SELECT 
      t.*, 
      GROUP_CONCAT(CONCAT(c.code, ' ', c.name) ORDER BY c.courseID ASC SEPARATOR ', ') AS courses
    FROM Terms t
    INNER JOIN Terms_has_Courses thc ON t.termID = thc.termID
    INNER JOIN Courses c ON thc.courseID = c.courseID
    GROUP BY t.termID
    ORDER BY t.startDate ASC;
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
      "endDate": row[3],
      "courses": row[4]
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
  
  # ----------------------------
  # STUDENT TERM PLANS RETRIEVAL
  # ----------------------------
  # Retrieve all term plans from 'StudentTermPlans' table
  query = """
    SELECT
      stp.studentTermPlanID,
      stp.studentID, 
      CONCAT(s.firstName, ' ', s.lastName) as studentName,
      t.name as termName, 
      GROUP_CONCAT((SELECT CONCAT(code, ' ', name) FROM Courses WHERE courseID = stpc.courseID) ORDER BY stpc.courseID ASC SEPARATOR ', ') AS courses,
      CASE WHEN stp.advisorApproved = 1 THEN 'Yes' ELSE 'No' End AS advisorApproved
    FROM StudentTermPlans stp
    INNER JOIN Terms t ON stp.termID = t.termID
	  INNER JOIN Students s ON s.studentID = stp.studentID
    INNER JOIN StudentTermPlans_has_Courses stpc ON stp.studentTermPlanID = stpc.studentTermPlanID
    GROUP BY stp.studentTermPlanID
    ORDER BY stp.studentTermPlanID ASC
  """

  # Execute query
  cursor = mysql_connection.cursor()
  cursor.execute(query)
  student_term_plans = cursor.fetchall()

  # Format student term plans to pass to template
  student_term_plans = [
    {
      "studentTermPlanID": row[0],
      "studentID": row[1],
      "studentName": row[2],
      "termName": row[3],
      "courses": row[4],
      "advisorApproved": row[5]
    }
    for row in student_term_plans
  ]

  # ------------------
  # STUDENTS RETRIEVAL
  # ------------------
  # Retrieve all students from 'Students' table
  query = """
    SELECT 
      CONCAT(lastName, ', ', firstName, ' - ', studentID) AS student,
      studentID
    FROM Students
    ORDER BY lastName ASC
  """

  # Execute query
  cursor = mysql_connection.cursor()
  cursor.execute(query)
  students = cursor.fetchall()

  # Format student term plans to pass to template
  students = [
    {
      "student": row[0],
      "studentID": row[1]
    }
    for row in students
  ]

  # ---------------
  # TERMS RETRIEVAL
  # ---------------
  # Retrieve all terms from 'Terms' table
  query = """
    SELECT 
      name, 
      termID
    FROM Terms
    ORDER BY startDate ASC
  """

  # Execute query
  cursor = mysql_connection.cursor()
  cursor.execute(query)
  terms = cursor.fetchall()

  # Format student term plans to pass to template
  terms = [
    {
      "name": row[0],
      "termID": row[1]
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

  # Format student term plans to pass to template
  courses = [
    {
      "course": row[0],
      "courseID": row[1]
    }
    for row in courses
  ]

  return render_template("student-term-plans.j2", student_term_plans=student_term_plans, students=students, terms=terms, courses=courses)
  

def addStudentTermPlan():
  pass

# //////// #
# STUDENTS #
# /////////#
@app.route("/students", methods=["GET"])
def viewStudents():
  # Check DB connection and reconnect if needed
  mysql_connection = connectToDB()

  # --------------
  # STUDENTS RETRIEVAL
  # --------------
  # Retrieve all students from 'Students' table
  query = """
    SELECT *
    FROM Students 
    ORDER BY lastName ASC
  """

  # Execute query
  cursor = mysql_connection.cursor()
  cursor.execute(query)
  students = cursor.fetchall()

  # Format terms to pass to template
  students = [
    {
      "id": row[0],
      "firstName": row[1],
      "lastName": row[2],
    }
    for row in students
  ]

  return render_template("students.j2", students=students)

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
    gunicorn --name OSUCourseTracker -b 0.0.0.0:7124 -D app:app (Bobby)
    gunicorn --name OSUCourseTracker -b 0.0.0.0:23071 -D app:app (April)
  stop:
    pkill -f 'gunicorn --name OSUCourseTracker'
  """
  app.run()