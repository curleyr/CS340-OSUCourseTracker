from database.DatabaseManager import DatabaseManager

class QueryError(Exception):
  """
  Custom exception class for query errors
  """
  pass

class QueryManager:
  """
  Manages all database queries and interacts with the DatabaseManager to execute the queries.
  """

  def __init__(self, database_manager: DatabaseManager):
    """
    Initializes the QueryManager instance and stores the provided DatabaseManager instance.

    Arguments:
      - database_manager (DatabaseManager): An instance of the DatabaseManager class that manages database connections and executing queries.
    """
    self._database_manager = database_manager

  # ///////////////// #
  #  COURSES QUERIES  #
  # ///////////////// # 
  def get_courses_and_prerequisites(self) -> list:
    """
    Retrieves all courses and prerequisites

    Returns:
      - List: A list of dictionaries representing the courses. Each dictionary contains:
        - "id" (int): The course ID.
        - "course" (str): The course name and code.
        - "credit" (int): The number of credits.
        - "prerequisites" (str): A comma-separated list of prerequisite courses.

    Arguments: 
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
  
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

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, method="fetchall")

    if status == 200:
      # Format courses to pass to template
      return [
        {
          "id": row[0],
          "course": row[1],
          "credit": row[2],
          "prerequisites": row[3]
        }
        for row in result
      ]
    
    raise QueryError(f"An error occurred while executing the query: {result}")
  
  def get_courses(self) -> list:
    """
    Retrieves all courses

    Arguments:
      - None

    Returns:
      - List: A list of dictionaries representing the courses. Each dictionary contains:
        - "course" (str): The course name and code.
        - "id" (int): The course ID.

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
  
    query = """
      SELECT 
        CONCAT(code, ' ', name) AS course,
        courseID
      FROM Courses
      ORDER BY code ASC
    """

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, method="fetchall")

    if status == 200:
      # Format courses to pass to template
      return [
        {
          "course": row[0],
          "id": row[1]
        }
        for row in result
      ]
    
    raise QueryError(f"An error occurred while executing the query: {result}")

  def get_courseid_by_code(self, course_code: int) -> int:
    """
    Retrieves a course ID of a course from a given course code

    Arguments:
      - course_code (int): The code of the course for which the ID is requested.

    Returns:
      - int: The course ID if found, otherwise None.

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    query = """
      SELECT courseID
      FROM Courses
      WHERE code = %s
    """

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, parameters=(course_code,), method="fetchone")

    if status == 200:
      return result
    
    raise QueryError(f"An error occurred while executing the query: {result}")

  def add_course(self, course_code: str, course_name: str, course_credit: int) -> None:
    """
    Adds a new course

    Arguments:
      - course_code (str): The code of the course (e.g. "CS161")
      - course_name (str): The name of the course (e.g. "INTRODUCTION TO COMPUTER SCIENCE I")
      - course_credit (int): The number of credits the course is worth

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
    
    query = """
      INSERT INTO Courses (code, name, credit)
      VALUES (%s, %s, %s)
    """

    status, result = self._database_manager.execute_query(query=query, parameters=(course_code, course_name, course_credit), method="commit")

    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  def add_course_prerequisite(self, course_code: str, prerequisite_course_id: int) -> None:
    """
    Adds prerequisites to a course

    Arguments:
      - course_code (str): The code of the course (e.g. "CS161")
      - prerequisite_course_id (int): The id of the prerequisite course

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
    
    query = """
      INSERT INTO Courses_has_Prerequisites (courseID, prerequisiteID)
      VALUES ((SELECT courseID FROM Courses WHERE code = %s), %s)
    """

    status, result = self._database_manager.execute_query(query=query, parameters=(course_code, prerequisite_course_id), method="commit")

    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  # /////////////// #
  #  TERMS QUERIES  #
  # /////////////// # 
  def get_terms(self) -> list:
    """
    Retrieves all terms

    Arguments:
      - None

    Returns:
      - List: A list of dictionaries representing the terms. Each dictionary contains:
        - "id" (int): The term ID
        - "name" (str): The term name
        - "startDate" (str): The date the term starts
        - "endDate" (str): The date the term ends
        - courses (str): A comma-separated list of courses

    Raises:
      QueryError: If an error occurs during the query execution.
    """

    self._database_manager.check_connection()
  
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

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, method="fetchall")

    if status == 200:
      # Format terms to pass to template
      return [
        {
          "id": row[0],
          "name": row[1],
          "startDate": row[2],
          "endDate": row[3],
          "courses": row[4]
        }
        for row in result
      ]
    
    raise QueryError(f"An error occurred while executing the query: {result}")

  def get_termid_by_name(self, term_name: str) -> int:
    """
    Retrieves a term ID of a term from a given term name

    Arguments:
      - term_name (int): The name of the term for which the ID is requested.

    Returns:
      - int: The term ID if found, otherwise None.

    Raises:
      QueryError: If an error occurs during the query execution.
    """

    self._database_manager.check_connection()

    query = """
      SELECT termID
      FROM Terms
      WHERE name = %s
    """

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, parameters=(term_name,), method="fetchone")

    if status == 200:
      return result
    
    raise QueryError(f"An error occurred while executing the query: {result}")

  def add_term(self, term_name: str, term_start_date: str, term_end_date: str) -> None:
    """
    Adds a new term

    Arguments:
      - term_name (str): The name of the term
      - term_start_date (str): The date the term starts
      - term_end_date (int): The date the term ends

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """

    self._database_manager.check_connection()
    
    query = """
      INSERT INTO Terms (name, startDate, endDate)
      VALUES (%s, %s, %s);
    """

    status, result = self._database_manager.execute_query(query=query, parameters=(term_name, term_start_date, term_end_date), method="commit")

    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  def add_term_course(self, term_course_id: int, term_name: str = None, term_id: int = None) -> None:
    """
    Adds a course to a term

    Arguments:
      - term_course_id (int): The id of the course being added to the term
      - term_name (str, optional): The name of the term
      - term_id (int, optional): The id of the term

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
    
    if not any([term_name, term_id]):
      raise QueryError(f"An error occurred while executing the query: neither a term name or id was provided.")

    if term_name:
      query = """
        INSERT INTO Terms_has_Courses (termID, courseID)
        VALUES ((SELECT termID FROM Terms WHERE name = %s), %s);
      """
      parameters = (term_name, term_course_id)

    else:
      query = """
        INSERT INTO Terms_has_Courses (termID, courseID)
        VALUES (%s, %s)
      """
      parameters = (term_id, term_course_id)

    status, result = self._database_manager.execute_query(query=query, parameters=parameters, method="commit")

    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  # ////////////////// #
  #  STUDENTS QUERIES  #
  # ////////////////// #
  def get_students(self) -> list:
    """
    Retrieves all students

    Arguments:
      - None

    Returns:
      - List: A list of dictionaries representing the students. Each dictionary contains:
        - "id" (int): The student ID
        - "firstName" (str): The student's first name
        - "lastName" (str): The student's last name

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
  
    query = """
      SELECT *
      FROM Students 
      ORDER BY lastName ASC
    """

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, method="fetchall")

    if status == 200:
      # Format students to pass to template
      return [
        {
          "id": row[0],
          "firstName": row[1],
          "lastName": row[2],
        }
        for row in result
      ]
      
    raise QueryError(f"An error occurred while executing the query: {result}")

  def get_students_formatted(self) -> list:
    """
    Retrieves all students and formats for dropdown select

    Arguments:
      - None

    Returns:
      - List: A list of dictionaries representing the students. Each dictionary contains:
        - "student" (str): The student lastname, firstname, and id
        - "studentID" (str): The student's id

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
  
    query = """
      SELECT 
        CONCAT(lastName, ', ', firstName, ' - ', studentID) AS student,
        studentID
      FROM Students
      ORDER BY lastName ASC
    """

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, method="fetchall")

    if status == 200:
      # Format courses to pass to template
      return [
        {
          "student": row[0],
          "studentID": row[1]
        }
        for row in result
      ]
      
    raise QueryError(f"An error occurred while executing the query: {result}")

  def get_student_by_id(self, student_id: int) -> dict:
    """
    Retrieves a student from a given student id

    Arguments:
      - student_id (int): The ID of the student being retrieved

    Returns:
      - Dictionary: A dictionary representing the student. It contains:
        - "id" (int): The student ID
        - "firstName" (str): The student first name
        - "lastName" (str): The student last name

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    query = """
      SELECT *
      FROM Students
      WHERE studentID = %s
    """

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, parameters=(student_id,), method="fetchone")

    if result == None:
      return None
    
    if status == 200:      
      # Format student to pass to template
      return {
        "id": result[0],
        "firstName": result[1],
        "lastName": result[2],
      }

    raise QueryError(f"An error occurred while executing the query: {result}")

  def add_student(self, student_id: str, first_name: str, last_name: str) -> None:
    """
    Adds a new student

    Arguments:
      - student_id (str): The ID of the student
      - first_name (str): The first name of the student
      - last_name (int): The last name of the student

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """

    self._database_manager.check_connection()
    
    query = """
      INSERT INTO Students (studentID, firstName, lastName)
      VALUES (%s, %s, %s)
    """

    status, result = self._database_manager.execute_query(query=query, parameters=(student_id, first_name, last_name), method="commit")

    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  def update_student(self, first_name: str, last_name: str, student_id: str) -> None:
    """
    Updates a student first and last name

    Arguments:
      - first_name (str): The first name of the student
      - last_name (int): The last name of the student
      - student_id (str): The ID of the student

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    query = """
      UPDATE Students 
      SET firstName = %s, lastName = %s
      WHERE studentID = %s
    """

    status, result = self._database_manager.execute_query(query=query, parameters=(first_name, last_name, student_id), method="commit")
    
    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  def delete_student(self, student_id: str) -> None:
    """
    Deletes a student

    Arguments:
      - student_id (str): The ID of the student being deleted

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    query = """
      DELETE FROM Students
      WHERE studentID = %s;
    """

    status, result = self._database_manager.execute_query(query=query, parameters=(student_id,), method="commit")
    
    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  # //////////////////////////// #
  #  STUDENT TERM PLANS QUERIES  #
  # //////////////////////////// #
  def get_student_term_plans(self) -> list:
    """
    Retrieves all student term plans

    Arguments:
      - None

    Returns:
      - List: A list of dictionaries representing the student term plans. Each dictionary contains:
        - "studentTermPlanID" (int): The student term plan ID
        - "studentID" (int): The student ID
        - "studentName" (str): The student first and last name
        - "termName" (str): The term name
        - "courses" (str): A comma-separated list of courses
        - "advisorApproved" (bool): 1 if advisor has approved, otherwise 0
    
    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
  
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

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, method="fetchall")

    if status == 200:
      # Format courses to pass to template
      return [
        {
          "studentTermPlanID": row[0],
          "studentID": row[1],
          "studentName": row[2],
          "termName": row[3],
          "courses": row[4],
          "advisorApproved": row[5]
        }
        for row in result
      ]
    
    raise QueryError(f"An error occurred while executing the query: {result}")

  def get_student_term_planid_by_studentid_and_termid(self, student_id: str, term_id: int) -> int:
    """
    Retrieves a student term plan ID of a student term from a given student ID and term ID

    Arguments:
      - student_id (str): The student ID for which the student term plan ID being retrieved
      - term_id (int): The term ID for which the student term plan ID being retrieved

    Returns:
      - int: The student term plan ID if found, otherwise None.

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    query = """
      SELECT studentTermPlanID
      FROM StudentTermPlans
      WHERE studentID = %s AND termID = %s
    """

    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, parameters=(student_id, term_id), method="fetchone")

    if status == 200:
      return result
    
    raise QueryError(f"An error occurred while executing the query: {result}")

  def add_student_term_plan(self, student_id: str, term_id: int, advisor_approved: bool) -> None:
    """
    Adds a new student term plan

    Arguments:
      - student_id (str): The student ID
      - term_id (int): The term ID
      - advisor_approved (bool): 1 if approved, otherwise 0

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
    
    query = """
      INSERT INTO StudentTermPlans (studentID, termID, advisorApproved)
      VALUES (%s, %s, %s);
    """

    status, result = self._database_manager.execute_query(query=query, parameters=(student_id, term_id, advisor_approved), method="commit")

    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  def add_student_term_plan_courses(self, courses: list, student_term_plan_id: int = None, student_id: str = None, term_id: int = None) -> None:
    """
    Adds courses to a student term plan

    Arguments:
      - courses (list): An array of course IDs
      - student_term_plan_id (int, optional): The student term plan ID
      - student_id (int, optional): The student ID
      - term_id (int, optional): The term ID

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    if not any([student_term_plan_id, student_id, term_id]):
      raise QueryError(f"An error occurred while executing the query: neither a student term plan id or studend id/term id was provided.")

    if student_term_plan_id:
      query = """
        INSERT INTO StudentTermPlans_has_Courses (studentTermPlanID, courseID)
        VALUES (%s, %s)
      """
      parameters = (student_term_plan_id,)
    
    else:
      query = """
        INSERT INTO StudentTermPlans_has_Courses (studentTermPlanID, courseID)
        VALUES ((SELECT studentTermPlanID FROM StudentTermPlans WHERE studentID = %s AND termID = %s), %s)
      """
      parameters = (student_id, term_id)

    # Iterate through course ids and insert into StudentTermPlans_has_Courses
    for course_id in courses:
      self._database_manager.check_connection()
      status, result = self._database_manager.execute_query(query=query, parameters=parameters+(course_id,), method="commit")

      if status != 200:
        raise QueryError(f"An error occurred while executing the query: {result}")

  def update_student_term_plan_course(self, new_course_id: int, student_term_plan_id: int, course_id: int) -> None:
    """
    Updates a student term plan course

    Arguments:
      - new_course_id (int): The course ID
      - student_term_plan_id (int): Student term plan ID
      - course_id (str): The course ID

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """

    self._database_manager.check_connection()

    query = """
      UPDATE StudentTermPlans_has_Courses
      SET courseID = %s
      WHERE studentTermPlanCourseID = (SELECT studentTermPlanCourseID FROM StudentTermPlans_has_Courses WHERE studentTermPlanID = %s AND courseID = %s)
    """
    
    status, result = self._database_manager.execute_query(query=query, parameters=(new_course_id, student_term_plan_id, course_id), method="commit")

    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  def delete_student_term_plan(self, student_term_plan_id: int) -> None:
    """
    Deletes a student term plan

    Arguments:
      - student_term_plan_id (int): The ID of the student term plan being deleted

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    query = """
      DELETE FROM StudentTermPlans
      WHERE studentTermPlanID = %s
    """
    
    status, result = self._database_manager.execute_query(query=query, parameters=(student_term_plan_id,), method="commit")

    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")

  def delete_student_term_plan_course(self, student_term_plan_id: int, course_id: int) -> None:
    """
    Deletes a course from a student term plan

    Arguments:
      - student_term_plan_id (int): The ID of the student term plan
      - course_id (int): The ID of the course being deleted

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    query = """
      DELETE FROM StudentTermPlans_has_Courses
      WHERE studentTermPlanCourseID = (SELECT studentTermPlanCourseID FROM StudentTermPlans_has_Courses WHERE studentTermPlanID = %s AND courseID = %s)
    """
    
    status, result = self._database_manager.execute_query(query=query, parameters=(student_term_plan_id, course_id), method="commit")

    if status != 200:
      raise QueryError(f"An error occurred while executing the query: {result}")