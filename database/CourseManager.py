from database.DatabaseManager import DatabaseManager
from blueprints.errorHandlers import QueryError
from typing import List, TypedDict, Any, Union

class CourseWithPrerequisites(TypedDict):  
  id: int  
  course: str  
  credit: int  
  prerequisites: str

class Course(TypedDict):  
  course: str  
  id: int 

class CourseManager:
  """
  Manages all database queries related to Courses and interacts with the DatabaseManager to execute the queries.
  """

  def __init__(self, database_manager: DatabaseManager):
    """
    Initializes the CourseManager instance and stores the provided DatabaseManager instance.

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
  
  def all(self, with_prerequisites: bool = False) -> Union[List[CourseWithPrerequisites], List[Course]]:
    """
    Retrieves all courses and optionally prerequisites

    Arguments: 
      - with_prerequisites (bool, optional): Whether course prerequisites should be retrieved with the courses, defaults to False.

    Returns:
      - If with_prerequisites is True, list of dictionaries representing the courses. Each dictionary contains:
        - "id" (int): The course ID.
        - "course" (str): The course name and code.
        - "credit" (int): The number of credits.
        - "prerequisites" (str): A comma-separated list of prerequisite courses.
      
      - If with_prerequisites is False: list of dictionaries representing the courses. Each dictionary contains:
        - "course" (str): The course name and code.
        - "id" (int): The course ID.

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    if with_prerequisites:
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
    
      return [
        {
          "id": row[0],
          "course": row[1],
          "credit": row[2],
          "prerequisites": row[3]
        }
        for row in self.perform_query(query=query, method="fetchall")
      ]
  
    else:
      query = """
        SELECT 
          CONCAT(code, ' ', name) AS course,
          courseID
        FROM Courses
        ORDER BY code ASC
      """

      return [
        {
          "course": row[0],
          "id": row[1]
        }
        for row in self.perform_query(query=query, method="fetchall")
      ]

  def get(self, course_code: int, fields: list = ["courseID"]) -> Course:
    """
    Retrieves the requested course fields from a given course code

    Arguments:
      - course_code (int): The code of the course for which the ID is requested.
      - fields (list, optional): The course fields to return. Defaults to "id". 

    Returns:
      - Course(dict): The course with the fields included if found, otherwise None.

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    query = """
      SELECT {}
      FROM Courses
      WHERE code = %s
    """.format(", ".join(fields))

    return self.perform_query(query=query, parameters=(course_code,), method="fetchone")

  def create(self, course_code: str, course_name: str, course_credit: int) -> None:
    """
    Creates a new course

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

    self.perform_query(query=query, parameters=(course_code, course_name, course_credit), method="commit")

  def add_prerequisite(self, course_code: str, prerequisite_course_id: int) -> None:
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

    self.perform_query(query=query, parameters=(course_code, prerequisite_course_id), method="commit")