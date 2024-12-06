from database.DatabaseManager import DatabaseManager
from blueprints.errorHandlers import QueryError
from typing import List, TypedDict, Any 

class StudentTermPlan(TypedDict):
  studentTermPlanID: int
  studentID: int
  studentName: str
  termName: str
  courses: str
  advisorApproved: bool

class StudentTermPlanManager:
  """
  Manages all database queries related to Students and interacts with the DatabaseManager to execute the queries.
  """

  def __init__(self, database_manager: DatabaseManager):
    """
    Initializes the StudentTermPlanManager instance and stores the provided DatabaseManager instance.

    Arguments:
      - database_manager (DatabaseManager): An instance of the DatabaseManager class that manages database connections and executing queries.
    """
    self._database_manager = database_manager
    self._HTTP_OK = 200

  def perform_query(self, query: str, parameters: tuple = None, method: str = None) -> Any:
    """
    Helper function that calls the execute_query method of the DatabaseManager class

    Arguments:
      - query (str): The SQL query to execute
      - parameters (tuple, optional): The parameters for the query. Defaults to an empty tuple if not provided.
      - method (str, optional): The query method, e.g., "fetchall", "fetchone", or "commit".

    Returns:
      - Result if method is "fetchall" or "fetchone", else None

    Raises:
      QueryError: If an error occurs during the query execution.
    """  
    # Execute query and catch status code and query result/error response
    status, result = self._database_manager.execute_query(query=query, parameters=parameters, method=method)  

    if status != self._HTTP_OK:  
      raise QueryError(f"An error occurred while executing the query: {result}")  
    return result  

  def all(self) -> List[StudentTermPlan]:
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

    return [
      {
        "studentTermPlanID": row[0],
        "studentID": row[1],
        "studentName": row[2],
        "termName": row[3],
        "courses": row[4],
        "advisorApproved": row[5]
      }
      for row in self.perform_query(query=query, method="fetchall")
    ]
    
  def get(self, student_id: str, term_id: int) -> int:
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

    return self.perform_query(query=query, parameters=(student_id, term_id), method="fetchone")

  def create(self, student_id: str, term_id: int, advisor_approved: bool) -> None:
    """
    Creates a new student term plan

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

    self.perform_query(query=query, parameters=(student_id, term_id, advisor_approved), method="commit")

  def add_courses(self, courses: List[int], student_term_plan_id: int = None, student_id: str = None, term_id: int = None) -> None:
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
      self.perform_query(query=query, parameters=parameters+(course_id,), method="commit")

  def update_course(self, new_course_id: int, student_term_plan_id: int, course_id: int) -> None:
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
    
    self.perform_query(query=query, parameters=(new_course_id, student_term_plan_id, course_id), method="commit")

  def update_approval(self, student_term_plan_id: int, advisor_approved: int) -> None:
    """
    Updates a student term plan advisor approved status

    Arguments:
      - student_term_plan_id (int): Student term plan ID
      - advisor_approved (int): Advisor approval status; 1 if approved else 0

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """

    self._database_manager.check_connection()

    query = """
      UPDATE StudentTermPlans
      SET advisorApproved = %s
      WHERE studentTermPlanID = %s
    """
    
    self.perform_query(query=query, parameters=(advisor_approved, student_term_plan_id), method="commit")

  def remove_course(self, student_term_plan_id: int, course_id: int) -> None:
    """
    Removes a course from a student term plan

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

    self.perform_query(query=query, parameters=(student_term_plan_id, course_id), method="commit")

  def delete(self, student_term_plan_id: int) -> None:
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

    self.perform_query(query=query, parameters=(student_term_plan_id,), method="commit")