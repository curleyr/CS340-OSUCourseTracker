from flask import Flask, request, jsonify, render_template, redirect
from database.DatabaseManager import DatabaseManager, DatabaseError
from database.QueryManager import QueryManager, QueryError
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
dm = DatabaseManager()
qm = QueryManager(dm)

# ////////////// #
# ERROR HANDLING #
# ////////////// #
app.errorhandler(QueryError)
def handleQueryError(error):
  return jsonify({"error": "QueryError occurred", "message": str(error)}), 400 

app.errorhandler(DatabaseError)
def handleDatabaseError(error):
  return jsonify({"error": "DatabaseError occurred", "message": str(error)}), 500 

@app.errorhandler(HTTPException)
def handleHTTPException(error):
  return render_template("exception.j2", error_name = error.name, error_description = error.description), error.code

@app.errorhandler(Exception)
def handleGenericException(error):
  return jsonify({"error": "Unexpected error occurred", "message": str(error)}), 500

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
  # Close db connection to avoid caching of data
  dm.close_connection()

  # Retrieve all courses and prerequisitesfrom 'Courses' table
  courses = qm.get_courses_and_prerequisites()
  return render_template("courses.j2", courses=courses)
  
@app.route("/add-course", methods=["POST"])
def addCourse():
  # Get posted form data
  request_data = request.get_json()
  course_code = request_data.get("course_code")
  course_credit = request_data.get("course_credit")
  course_name = request_data.get("course_name")
  prerequisite_course_ids = request_data.get("prerequisite_course_ids", [])

  if any(parameter is None for parameter in [course_code, course_credit, course_name]):
    return jsonify(message = "Not all required attributes were provided in the request"), 400

  # Check if course already exists
  if qm.get_courseid_by_code(course_code):
    return jsonify(message = f"A class with code {course_code} already exists"), 400

  # Add course
  qm.add_course(course_code, course_name, course_credit)

  # Iterate through prerequisite course ids and insert into Courses_has_Prerequisites
  for prerequisite_course_id in prerequisite_course_ids:
    qm.add_course_prerequisite(course_code, prerequisite_course_id)
  
  return jsonify(message = "The course and prerequisite(s) if any have been added."), 200

# ///// #
# TERMS #
# //////#
@app.route("/terms", methods=["GET"])
def viewTerms():
  # Close db connection to avoid caching of data
  dm.close_connection()

  # Retrieve all terms from 'Terms' table
  terms = qm.get_terms()
  
  # Retrieve all courses from 'Courses' table
  courses = qm.get_courses()

  return render_template("terms.j2", terms=terms, courses=courses)
    
@app.route("/add-term", methods=["POST"])
def addTerm():
  # Get posted form data
  request_data = request.get_json()
  term_season = request_data.get("term_season")
  term_year = request_data.get("term_year")
  term_start_date = request_data.get("term_start_date")
  term_end_date = request_data.get("term_end_date")
  term_course_ids = request_data.get("term_course_ids", [])

  if any(parameter is None for parameter in [term_season, term_year, term_start_date, term_end_date]):
    return jsonify(message = "Not all required attributes were provided in the request"), 400

  term_name = f"{term_season} {term_year}"

  # Check if term already exists
  if qm.get_termid_by_name(term_name):
    return jsonify(message = f"A term with the name of {term_name} already exists"), 400

  # Add term
  qm.add_term(term_name, term_start_date, term_end_date)

  # Iterate through term course ids and insert into Terms_has_Courses
  for term_course_id in term_course_ids:
    qm.add_term_course(term_name=term_name, term_course_id=term_course_id)

  return jsonify(message = "The term and courses if any have been added."), 200

@app.route("/add-term-course", methods=["PATCH"])
def addTermCourse():
  # Get posted form data
  request_data = request.get_json()
  term_id = request_data.get("term_id")
  new_course_id = request_data.get("new_course_id")

  # Add course
  qm.add_term_course(term_id=term_id, term_course_id=new_course_id)

  return jsonify(message = f"The course has been added."), 200
  
# ////////////////// #
# STUDENT TERM PLANS #
# ///////////////////#
@app.route("/student-term-plans", methods=["GET"])
def viewStudentTermPlans():
  # Close db connection to avoid caching of data
  dm.close_connection()
  
  student_term_plans = qm.get_student_term_plans()    # Retrieve all term plans from 'StudentTermPlans' table
  students = qm.get_students_formatted()              # Retrieve all students from 'Students' table
  terms = qm.get_terms()                              # Retrieve all terms from 'Terms' table
  courses = qm.get_courses()                          # Retrieve all courses from 'Courses' table

  return render_template("student-term-plans.j2", student_term_plans=student_term_plans, students=students, terms=terms, courses=courses)
        
@app.route("/add-student-term-plan", methods=["POST"])
def addStudentTermPlan():
  # Get posted form data
  request_data = request.get_json()
  student_id = request_data.get("student_id")
  term_id = request_data.get("term_id")
  advisor_approved = request_data.get("advisor_approved")
  courses = request_data.get("courses")

  if any(parameter is None for parameter in [student_id, term_id, advisor_approved, courses]):
    return jsonify(message = "Not all required attributes were provided in the request"), 400
  
  # Check if student term plan already exists for provided student/term
  if qm.get_student_term_planid_by_studentid_and_termid(student_id, term_id):
    return jsonify(message = "A student term plan already exists for the provided student and term."), 400

  qm.add_student_term_plan(student_id, term_id, advisor_approved)                                # Add student term plan
  qm.add_student_term_plan_courses(student_id=student_id, term_id=term_id, courses=courses)      # Add courses 

  return jsonify(message = f"The student term plan and associated course(s) has been added."), 200

@app.route("/edit-student-term-plan", methods=["PATCH"])
def editStudentTermPlan():
  # Get posted form data
  request_data = request.get_json()
  student_term_plan_id = request_data.get("student_term_plan_id")
  course_id = request_data.get("course_id")
  new_course_id = request_data.get("new_course_id")
  action = request_data.get("action")

  if new_course_id == "None":
    new_course_id = None

  # Updating existing course 
  if action == "update":
    qm.update_student_term_plan_course(new_course_id, student_term_plan_id, course_id)

  # Adding new course
  else:
    qm.add_student_term_plan_courses(student_term_plan_id=student_term_plan_id, courses=[new_course_id])

  return jsonify(message = f"The course has been {'updated' if action == 'update' else 'added'}."), 200

@app.route("/delete-student-term-plan/<int:student_term_plan_id>", methods=["DELETE"])
def deleteStudentTermPlan(student_term_plan_id):
  # Delete student term plan
  qm.delete_student_term_plan(student_term_plan_id)
  
  return jsonify(message = "The student term plan has been deleted."), 200

@app.route("/delete-student-term-plan-course", methods=["DELETE"])
def deleteStudentTermPlanCourse():
  # Get posted form data
  request_data = request.get_json()
  student_term_plan_id = request_data.get("student_term_plan_id")
  course_id = request_data.get("course_id")

  # Delete student term plan course
  qm.delete_student_term_plan_course(student_term_plan_id, course_id)
  
  return jsonify(message = "The student course plan course has been deleted."), 200

# //////// #
# STUDENTS #
# /////////#
@app.route("/students", methods=["GET"])
def viewStudents():
  # Close db connection to avoid caching of data
  dm.close_connection()

  # Retrieve all students from 'Students' table
  students = qm.get_students()
  
  return render_template("students.j2", students=students)
  
@app.route("/add-student", methods=["POST"])
def addStudent():
  # Get posted form data
  request_data = request.get_json()
  student_id = request_data.get("student_id")
  first_name = request_data.get("first_name")
  last_name = request_data.get("last_name")

  if any(parameter is None for parameter in [student_id, first_name, last_name]):
    return jsonify(message = "Not all required attributes were provided in the request"), 400
  
  # Check if student ID already exists in database
  if qm.get_student_by_id(student_id):
    return jsonify(message = "A student already exists for the provided student id."), 400

  # Add student
  qm.add_student(student_id, first_name, last_name)

  return jsonify(message = "This student has been added."), 200

@app.route("/delete-student", methods=["DELETE"])
def removeStudent():
  # Get posted form data
  request_data = request.get_json()
  student_id = request_data.get("student_id")

  # Delete student
  qm.delete_student(student_id)

  return jsonify(message = "The student has been deleted."), 200

@app.route("/edit-student/<id>", methods=["POST", "GET"])
def updateStudent(id):
  if request.method == "GET":
    student = qm.get_student_by_id(id)

    return render_template("edit_student.j2", student=student)
  
  # If user submits form
  if request.method == "POST":
    if request.form.get("edit_student"):
      student_id = request.form["studentID"]
      first_name = request.form["first_name"]
      last_name = request.form["last_name"]

      # Update student
      qm.update_student(first_name, last_name, student_id)
    
      return redirect("/students")
    
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
  #app.run(port=8007, debug=True)