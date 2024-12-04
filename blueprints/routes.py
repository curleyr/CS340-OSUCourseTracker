from flask import Blueprint, request, jsonify, render_template, redirect
from database.DatabaseManager import DatabaseManager
from database.QueryManager import QueryManager

# Define blueprint
routes_blueprint = Blueprint('routes', __name__)

# Instantiate Database and Query Manager classes
dm = DatabaseManager()
qm = QueryManager(dm)

# Routes
@routes_blueprint.route("/", methods=["GET"])
@routes_blueprint.route("/index", methods=["GET"])
def index():
  return render_template("index.j2")

@routes_blueprint.route("/courses", methods=["GET"])
def viewCourses():
  # Close db connection to avoid caching of data
  dm.close_connection()

  courses = qm._courses.all(with_prerequisites = True)
  return render_template("courses.j2", courses=courses)
  
@routes_blueprint.route("/add-course", methods=["POST"])
def addCourse():
  request_data = request.get_json()
  course_code = request_data.get("course_code")
  course_credit = request_data.get("course_credit")
  course_name = request_data.get("course_name")
  prerequisite_course_ids = request_data.get("prerequisite_course_ids", [])

  if any(parameter is None for parameter in [course_code, course_credit, course_name]):
    return jsonify(message = "Not all required attributes were provided in the request"), 400

  if qm._courses.get(course_code):
    return jsonify(message = f"A class with code {course_code} already exists"), 400

  qm._courses.create(course_code, course_name, course_credit)

  for prerequisite_course_id in prerequisite_course_ids:
    qm._courses.add_prerequisite(course_code, prerequisite_course_id)
  
  return jsonify(message = "The course and prerequisite(s) if any have been added."), 200

@routes_blueprint.route("/terms", methods=["GET"])
def viewTerms():
  # Close db connection to avoid caching of data
  dm.close_connection()

  # Retrieve all terms from 'Terms' table
  terms = qm._terms.all()
  
  # Retrieve all courses from 'Courses' table
  courses = qm._courses.all()

  return render_template("terms.j2", terms=terms, courses=courses)
    
@routes_blueprint.route("/add-term", methods=["POST"])
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

  # Check if term already exists
  if qm._terms.get(term_season, term_year):
    return jsonify(message = f"A term with the name of {term_season} {term_year} already exists"), 400

  # Add term
  qm._terms.create(term_season, term_year, term_start_date, term_end_date)

  # Iterate through term course ids and insert into Terms_has_Courses
  for term_course_id in term_course_ids:
    qm._terms.add_course(term_season=term_season, term_year=term_year, term_course_id=term_course_id)

  return jsonify(message = "The term and courses if any have been added."), 200

@routes_blueprint.route("/add-term-course", methods=["PATCH"])
def addTermCourse():
  # Get posted form data
  request_data = request.get_json()
  term_id = request_data.get("term_id")
  new_course_id = request_data.get("new_course_id")

  # Add course
  qm._terms.add_course(term_id=term_id, term_course_id=new_course_id)

  return jsonify(message = f"The course has been added."), 200
  
@routes_blueprint.route("/student-term-plans", methods=["GET"])
def viewStudentTermPlans():
  # Close db connection to avoid caching of data
  dm.close_connection()
  
  student_term_plans = qm._studentTermPlans.all()    # Retrieve all term plans from 'StudentTermPlans' table
  students = qm._students.all(is_formatted=True)     # Retrieve all students from 'Students' table
  terms = qm._terms.all()                            # Retrieve all terms from 'Terms' table
  courses = qm._courses.all()                        # Retrieve all courses from 'Courses' table

  return render_template("student-term-plans.j2", student_term_plans=student_term_plans, students=students, terms=terms, courses=courses)
        
@routes_blueprint.route("/add-student-term-plan", methods=["POST"])
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
  if qm._studentTermPlans.get(student_id, term_id):
    return jsonify(message = "A student term plan already exists for the provided student and term."), 400

  qm._studentTermPlans.create(student_id, term_id, advisor_approved)                                # Add student term plan
  qm._studentTermPlans.add_courses(student_id=student_id, term_id=term_id, courses=courses)      # Add courses 

  return jsonify(message = f"The student term plan and associated course(s) has been added."), 200

# Define constants for actions
ACTION_UPDATE = "update"
ACTION_ADD = "add"

# Define constant for None string
STRING_NONE = "None"

@routes_blueprint.route("/edit-student-term-plan", methods=["PATCH"])
def editStudentTermPlan():
  # Get posted form data
  request_data = request.get_json()
  student_term_plan_id = request_data.get("student_term_plan_id")
  course_id = request_data.get("course_id")
  new_course_id = request_data.get("new_course_id")
  action = request_data.get("action")

  if new_course_id == STRING_NONE:
    new_course_id = None

  # Updating existing course 
  if action == ACTION_UPDATE:
    qm._studentTermPlans.update_course(new_course_id, student_term_plan_id, course_id)

  # Adding new course
  elif action == ACTION_ADD:
    qm._studentTermPlans.add_courses(student_term_plan_id=student_term_plan_id, courses=[new_course_id])

  return jsonify(message = f"The course has been {'updated' if action == ACTION_UPDATE else 'added'}."), 200

@routes_blueprint.route("/delete-student-term-plan/<int:student_term_plan_id>", methods=["DELETE"])
def deleteStudentTermPlan(student_term_plan_id):
  # Delete student term plan
  qm._studentTermPlans.delete(student_term_plan_id)
  
  return jsonify(message = "The student term plan has been deleted."), 200

@routes_blueprint.route("/delete-student-term-plan-course", methods=["DELETE"])
def deleteStudentTermPlanCourse():
  # Get posted form data
  request_data = request.get_json()
  student_term_plan_id = request_data.get("student_term_plan_id")
  course_id = request_data.get("course_id")

  # Delete student term plan course
  qm._studentTermPlans.remove_course(student_term_plan_id, course_id)
  
  return jsonify(message = "The student course plan course has been deleted."), 200

@routes_blueprint.route("/students", methods=["GET"])
def viewStudents():
  # Close db connection to avoid caching of data
  dm.close_connection()

  # Retrieve all students from 'Students' table
  students = qm._students.all()
  print(students)
  
  return render_template("students.j2", students=students)
  
@routes_blueprint.route("/add-student", methods=["POST"])
def addStudent():
  # Get posted form data
  request_data = request.get_json()
  student_id = request_data.get("student_id")
  first_name = request_data.get("first_name")
  last_name = request_data.get("last_name")

  if any(parameter is None for parameter in [student_id, first_name, last_name]):
    return jsonify(message = "Not all required attributes were provided in the request"), 400
  
  # Check if student ID already exists in database
  if qm._students.get(student_id):
    return jsonify(message = "A student already exists for the provided student id."), 400

  # Add student
  qm._students.create(student_id, first_name, last_name)

  return jsonify(message = "This student has been added."), 200

@routes_blueprint.route("/delete-student", methods=["DELETE"])
def removeStudent():
  # Get posted form data
  request_data = request.get_json()
  student_id = request_data.get("student_id")

  # Delete student
  qm._students.delete(student_id)

  return jsonify(message = "The student has been deleted."), 200

@routes_blueprint.route("/edit-student/<id>", methods=["POST", "GET"])
def updateStudent(id):
  if request.method == "GET":
    student = qm._students.get(id)

    return render_template("edit_student.j2", student=student)
  
  # If user submits form
  if request.method == "POST":
    if request.form.get("edit_student"):
      student_id = request.form["studentID"]
      first_name = request.form["first_name"]
      last_name = request.form["last_name"]

      # Update student
      qm._students.update(first_name, last_name, student_id)
    
      return redirect("/students")