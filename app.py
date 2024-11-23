from flask import Flask, request, jsonify, render_template, session, redirect, abort
from database.db_config import connectToDB
import MySQLdb

app = Flask(__name__)
mysql_connection = connectToDB()

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
  global mysql_connection
  try:
    # Close db connection then reopen to avoid caching of data
    mysql_connection.close()
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
        GROUP_CONCAT(CONCAT(pc.code, ' ', pc.name) ORDER BY pc.code SEPARATOR ', ') AS prerequisites 
      FROM Courses c
      LEFT JOIN Courses_has_Prerequisites p   
        ON c.courseID = p.courseID 
      LEFT JOIN Courses pc  
        ON p.prerequisiteID = pc.courseID 
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

  except MySQLdb.DatabaseError as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

  finally:
    cursor.close()

@app.route("/add-course", methods=["POST"])
def addCourse():
  global mysql_connection
  try:
    # Get posted form data
    request_data = request.get_json()

    course_code = request_data.get("course_code")
    course_credit = request_data.get("course_credit")
    course_name = request_data.get("course_name")
    prerequisite_course_ids = request_data.get("prerequisite_course_ids")

    if any(parameter is None for parameter in [course_code, course_credit, course_name]):
      return jsonify(message = "Not all required attributes were provided in the request"), 400

    # Check DB connection and reconnect if needed
    mysql_connection = connectToDB()

    try:
      # Check if course already exists
      query = """
        SELECT courseID
        FROM Courses
        WHERE code = %s
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (course_code,))
      course_id = cursor.fetchone() 

      if course_id:
        return jsonify(message = f"A class with code {course_code} already exists"), 400

      # Add course
      query = """
        INSERT INTO Courses (code, name, credit)
        VALUES (%s, %s, %s)
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (course_code, course_name, course_credit))
      mysql_connection.commit()

      if cursor.rowcount == 0:
        return f"Failed to add course with name {course_code} {course_name}.", 400

      # Iterate through prerequisite course ids and insert into Courses_has_Prerequisites
      if prerequisite_course_ids:
        for prerequisite_course_id in prerequisite_course_ids:
          query = """
            INSERT INTO Courses_has_Prerequisites (courseID, prerequisiteID)
            VALUES ((SELECT courseID FROM Courses WHERE code = %s), %s)
          """

          # Execute query
          cursor = mysql_connection.cursor()
          cursor.execute(query, (course_code, prerequisite_course_id))
          mysql_connection.commit()
          
          if cursor.rowcount == 0:
            return f"Failed to add prerequisite with ID {prerequisite_course_id} for course with ID {course_id}.", 400

      return jsonify(message = "The course and prerequisite(s) if any have been added."), 200

    except MySQLdb.DatabaseError as error:
      return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
    finally:
      cursor.close()

  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

# ///// #
# TERMS #
# //////#
@app.route("/terms", methods=["GET"])
def viewTerms():
  global mysql_connection
  try:
    # Close db connection then reopen to avoid caching of data
    mysql_connection.close()
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
      LEFT JOIN Terms_has_Courses thc ON t.termID = thc.termID
      LEFT JOIN Courses c ON thc.courseID = c.courseID
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

  except MySQLdb.DatabaseError as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

  finally:
    cursor.close()

@app.route("/add-term", methods=["POST"])
def addTerm():
  global mysql_connection
  try:
    # Get posted form data
    request_data = request.get_json()

    term_season = request_data.get("term_season")
    term_year = request_data.get("term_year")
    term_start_date = request_data.get("term_start_date")
    term_end_date = request_data.get("term_end_date")
    term_course_ids = request_data.get("term_course_ids")

    if any(parameter is None for parameter in [term_season, term_year, term_start_date, term_end_date]):
      return jsonify(message = "Not all required attributes were provided in the request"), 400

    term_name = f"{term_season} {term_year}"

    # Check DB connection and reconnect if needed
    mysql_connection = connectToDB()

    try:
      # Check if term already exists
      query = """
        SELECT termID
        FROM Terms
        WHERE name = %s
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (term_name,))
      term_id = cursor.fetchone()

      if term_id:
        return jsonify(message = f"A term with the name of {term_name} already exists"), 400

      # Add term
      query = """
        INSERT INTO Terms (name, startDate, endDate)
        VALUES (%s, %s, %s);
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (term_name, term_start_date, term_end_date))
      mysql_connection.commit()

      if cursor.rowcount == 0:
        return f"Failed to add term with name of {term_name}.", 400

      # Iterate through term course ids and insert into Terms_has_Courses
      if term_course_ids:
        for term_course_id in term_course_ids:
          query = """
            INSERT INTO Terms_has_Courses (termID, courseID)
            VALUES ((SELECT termID FROM Terms WHERE name = %s), %s);
          """

          # Execute query
          cursor = mysql_connection.cursor()
          cursor.execute(query, (term_name, term_course_id))
          mysql_connection.commit()
          
          if cursor.rowcount == 0:
            return f"Failed to add course with ID {term_course_id} for {term_name} term.", 400

      return jsonify(message = "The term and courses if any have been added."), 200

    except MySQLdb.DatabaseError as error:
      return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
    finally:
      cursor.close()

  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

@app.route("/add-term-course", methods=["PATCH"])
def addTermCourse():
  global mysql_connection
  try:
    # Get posted form data
    request_data = request.get_json()

    term_id = request_data.get("term_id")
    new_course_id = request_data.get("new_course_id")

    # Check DB connection and reconnect if needed
    mysql_connection = connectToDB()

    query = """
      INSERT INTO Terms_has_Courses (termID, courseID)
      VALUES (%s, %s)
    """
        
    # Execute query
    cursor = mysql_connection.cursor()
    cursor.execute(query, (term_id, new_course_id))
    mysql_connection.commit()

    if cursor.rowcount == 0:
      return jsonify(message = "No term found with the provided ID."), 404

    return jsonify(message = f"The course has been added."), 200

  except MySQLdb.DatabaseError as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500
  
  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

  finally:
    cursor.close()

# ////////////////// #
# STUDENT TERM PLANS #
# ///////////////////#
@app.route("/student-term-plans", methods=["GET"])
def viewStudentTermPlans():
  global mysql_connection
  try:
    # Close db connection then reopen to avoid caching of data
    mysql_connection.close()
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
    
  except MySQLdb.DatabaseError as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

  finally:
    cursor.close()

@app.route("/add-student-term-plan", methods=["POST"])
def addStudentTermPlan():
  global mysql_connection
  try:
    # Get posted form data
    request_data = request.get_json()

    student_id = request_data.get("student_id")
    term_id = request_data.get("term_id")
    advisor_approved = request_data.get("advisor_approved")
    courses = request_data.get("courses")

    if any(parameter is None for parameter in [student_id, term_id, advisor_approved, courses]):
      return jsonify(message = "Not all required attributes were provided in the request"), 400
    
    # Check DB connection and reconnect if needed
    mysql_connection = connectToDB()

    try:
      # Check if student term plan already exists for provided student/term
      query = """
        SELECT studentTermPlanID
        FROM StudentTermPlans
        WHERE studentID = %s AND termID = %s
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (student_id, term_id))
      student_term_plan_id = cursor.fetchone()

      if student_term_plan_id:
        return jsonify(message = "A student term plan already exists for the provided student and term."), 400

      # Add student term plan
      query = """
        INSERT INTO StudentTermPlans (studentID, termID, advisorApproved)
        VALUES (%s, %s, %s);
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (student_id, term_id, advisor_approved))
      mysql_connection.commit()

      # Add courses 
      status, code = addStudentTermPlanCourses(student_id, term_id, courses)
      if code == 200:
        return jsonify(message = "The student term plan and courses have been successfully added."), 200
      else:
        return jsonify(message = f"The student term plan has been successfully added but the courses failed to add due to the following error: {status}."), 500
    
    except MySQLdb.DatabaseError as error:
      return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
    finally:
      cursor.close()

  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

def addStudentTermPlanCourses(student_id, term_id, courses):
  global mysql_connection
  try:
    # Check DB connection and reconnect if needed
    mysql_connection = connectToDB()

    try:
      # Iterate through course ids and insert into StudentTermPlans_has_Courses
      for course_id in courses:
        query = """
          INSERT INTO StudentTermPlans_has_Courses (studentTermPlanID, courseID)
          VALUES ((SELECT studentTermPlanID FROM StudentTermPlans WHERE studentID = %s AND termID = %s), %s);
        """

        # Execute query
        cursor = mysql_connection.cursor()
        cursor.execute(query, (student_id, term_id, course_id))
        mysql_connection.commit()
        
        if cursor.rowcount == 0:
          return f"Failed to add course with ID {course_id} for student term plan.", 400

      return "All courses have been added for the provided student term plan.", 200
        
    except MySQLdb.DatabaseError as error:
      return f"The following error has occurred: {str(error)}", 500
    
    finally:
      cursor.close()

  except Exception as error:
    return f"The following error has occurred: {str(error)}", 500

@app.route("/edit-student-term-plan", methods=["PATCH"])
def editStudentTermPlan():
  global mysql_connection
  try:
     # Get posted form data
    request_data = request.get_json()

    student_term_plan_id = request_data.get("student_term_plan_id")
    course_id = request_data.get("course_id")
    new_course_id = request_data.get("new_course_id")
    action = request_data.get("action")

    if new_course_id == "None":
      new_course_id = None

    # Check DB connection and reconnect if needed
    mysql_connection = connectToDB()

    try:
      # Updating existing course 
      if action == "update":
        query = """
          UPDATE StudentTermPlans_has_Courses
          SET courseID = %s
          WHERE studentTermPlanCourseID = (SELECT studentTermPlanCourseID FROM StudentTermPlans_has_Courses WHERE studentTermPlanID = %s AND courseID = %s)
        """
        parameters = (new_course_id, student_term_plan_id, course_id)

      # Adding new course
      else:
        query = """
          INSERT INTO StudentTermPlans_has_Courses (studentTermPlanID, courseID)
          VALUES (%s, %s)
        """
        parameters = (student_term_plan_id, new_course_id)
        
      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, parameters)
      mysql_connection.commit()

      if cursor.rowcount == 0:
        return jsonify(message = "No student term plan course found with the provided ID."), 404

      return jsonify(message = f"The course has been {'updated' if action == 'update' else 'added'}."), 200

    except MySQLdb.DatabaseError as error:
      return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
    finally:
      cursor.close()

  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

@app.route("/delete-student-term-plan/<int:student_term_plan_id>", methods=["DELETE"])
def deleteStudentTermPlan(student_term_plan_id):
  global mysql_connection
  try:    
    # Check DB connection and reconnect if needed
    mysql_connection = connectToDB()

    try:
      query = """
        DELETE FROM StudentTermPlans
        WHERE studentTermPlanID = %s
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (student_term_plan_id,))
      mysql_connection.commit()

      if cursor.rowcount == 0:
        return jsonify(message = "No student term plan found with the provided ID."), 404

      return jsonify(message = "The student term plan has been deleted."), 200

    except MySQLdb.DatabaseError as error:
      return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
    finally:
      cursor.close()

  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

@app.route("/delete-student-term-plan-course", methods=["DELETE"])
def deleteStudentTermPlanCourse():
  global mysql_connection
  try:   
    # Get posted form data
    request_data = request.get_json()

    student_term_plan_id = request_data.get("student_term_plan_id")
    course_id = request_data.get("course_id")

    # Check DB connection and reconnect if needed
    mysql_connection = connectToDB()

    try:
      # Get student term plan course id
      query = """
        SELECT studentTermPlanCourseID
        FROM StudentTermPlans_has_Courses
        WHERE studentTermPlanID = %s AND courseID = %s           
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (student_term_plan_id, course_id))
      student_term_plan_course_id = cursor.fetchone()

      if not student_term_plan_course_id:
        return jsonify(message = "No student term plan course id was found using the provided student term plan id and course id."), 400

      query = """
        DELETE FROM StudentTermPlans_has_Courses
        WHERE studentTermPlanCourseID = %s
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (student_term_plan_course_id,))
      mysql_connection.commit()

      if cursor.rowcount == 0:
        return jsonify(message = "No course found with the provided ID."), 404

      return jsonify(message = "The student course plan course has been deleted."), 200

    except MySQLdb.DatabaseError as error:
      return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
    finally:
      cursor.close()

  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

# //////// #
# STUDENTS #
# /////////#
@app.route("/students", methods=["GET"])
def viewStudents():
  global mysql_connection
  try:
    # Close db connection then reopen to avoid caching of data
    mysql_connection.close()
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

  except MySQLdb.DatabaseError as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

  finally:
    cursor.close()

@app.route("/add-student", methods=["POST"])
def addStudent():
  global mysql_connection
  try:
    # Get form data
    request_data = request.get_json()

    student_id = request_data.get("student_id")
    first_name = request_data.get("first_name")
    last_name = request_data.get("last_name")

    if any(parameter is None for parameter in [student_id, first_name, last_name]):
      return jsonify(message = "Not all required attributes were provided in the request"), 400

    # Close db connection then reopen to avoid caching of data
    mysql_connection.close()
    mysql_connection = connectToDB()
  
    try:
      # Check if student ID already exists in database
      query = """
        SELECT studentID
        FROM Students
        WHERE studentID = %s
      """

      # Execute query
      cursor = mysql_connection.cursor()
      cursor.execute(query, (student_id,))
      existing_student_id = cursor.fetchall()

      if existing_student_id:
        return jsonify(message = "A student already exists for the provided student id."), 400
      
      # Add student
      query = """
      INSERT INTO Students (studentID, firstName, lastName)
      VALUES (%s, %s, %s)
      """

      cursor = mysql_connection.cursor()
      cursor.execute(query, (student_id, first_name, last_name))
      mysql_connection.commit()

      return jsonify(message = "This student has been added."), 200
    
    except MySQLdb.DatabaseError as error:
      return jsonify(message = f"Database: The following error has occurred: {str(error)}"), 500
    
    finally:
      cursor.close()

  except Exception as error:
    return jsonify(message = f"Exception: The following error has occurred: {str(error)}"), 500

@app.route("/delete-student", methods=["DELETE"])
def removeStudent():
  global mysql_connection
  try:   
    # Get posted form data
    request_data = request.get_json()

    student_id = request_data.get("student_id")

    # Check DB connection and reconnect if needed
    mysql_connection = connectToDB()
    
    try:
      query = """
      DELETE FROM Students
      WHERE studentID = %s;
      """

      cursor = mysql_connection.cursor()
      cursor.execute(query, (student_id,))
      mysql_connection.commit()

      if cursor.rowcount == 0:
        return jsonify(message = "No student found with the provided ID."), 404

      return jsonify(message = "The student has been deleted."), 200

    except MySQLdb.DatabaseError as error:
      return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
    finally:
      cursor.close()

  except Exception as error:
    return jsonify(message = f"The following error has occurred: {str(error)}"), 500

@app.route("/edit-student/<id>", methods=["POST", "GET"])
def updateStudent(id):
  global mysql_connection
  if request.method == "GET":
    try:
      # Close db connection then reopen to avoid caching of data
      mysql_connection.close()
      mysql_connection = connectToDB()

      query = "SELECT * FROM Students WHERE studentId = %s" % (id)
      cur = mysql_connection.cursor()
      cur.execute(query)
      student = cur.fetchall()

      student = [
        {
          "id": row[0],
          "firstName": row[1],
          "lastName": row[2],
        }
        for row in student
      ]

    except MySQLdb.DatabaseError as error:
      return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
    except Exception as error:
      return jsonify(message = f"The following error has occurred: {str(error)}"), 500
  
    finally:
      cur.close()

    return render_template("edit_student.j2", student=student)
    
  
  # If user submits form
  if request.method == "POST":
    if request.form.get("edit_student"):
      student_id = request.form["studentID"]
      first_name = request.form["first_name"]
      last_name = request.form["last_name"]

      try:
        # Close db connection then reopen to avoid caching of data
        mysql_connection.close()
        mysql_connection = connectToDB()

        query = "UPDATE Students SET firstName = %s, lastName = %s WHERE studentID = %s"
        cur = mysql_connection.cursor()
        cur.execute(query, (first_name, last_name, student_id))
        mysql_connection.commit()
    
      except MySQLdb.DatabaseError as error:
        return jsonify(message = f"The following error has occurred: {str(error)}"), 500
      
      except Exception as error:
        return jsonify(message = f"The following error has occurred: {str(error)}"), 500
    
      finally:
        cur.close()
  
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