from database.DatabaseManager import DatabaseManager
from blueprints.errorHandlers import QueryError
from typing import List, TypedDict, Any, Union

class Student(TypedDict):
  id: int
  firstName: str
  lastName: str

class StudentFormatted(TypedDict):
  student: str
  studentID: str

class StudentManager:
  """
  Manages all database queries related to Students and interacts with the DatabaseManager to execute the queries.
  """

  def __init__(self, database_manager: DatabaseManager):
    """
    Initializes the TermManager instance and stores the provided DatabaseManager instance.

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

  def all(self, is_formatted: bool = False) -> Union[List[Student], List[StudentFormatted]]:
    """
    Retrieves all students

    Arguments:
      - is_formatted (bool, optional): Whether the Student attributes should be combined and formatted for form dropdown, defaults to False.

    Returns:
      - If is_formatted is True, list of dictionaries representing the students. Each dictionary contains:
        - "student" (str): The student lastname, firstname, and id
        - "studentID" (str): The student's id

      - If is_formatted is False, list of dictionaries representing the students. Each dictionary contains:
        - "id" (int): The student ID
        - "firstName" (str): The student's first name
        - "lastName" (str): The student's last name

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
    
    if is_formatted:
      query = """
        SELECT 
          CONCAT(lastName, ', ', firstName, ' - ', studentID) AS student,
          studentID
        FROM Students
        ORDER BY lastName ASC
      """

      return [
        {
          "student": row[0],
          "studentID": row[1]
        }
        for row in self.perform_query(query=query, method="fetchall")
      ]
    
    else:
      query = """
        SELECT *
        FROM Students 
        ORDER BY lastName ASC
      """

      return [
        {
          "id": row[0],
          "firstName": row[1],
          "lastName": row[2],
        }
        for row in self.perform_query(query=query, method="fetchall")
      ]
        
  def get(self, student_id: int) -> Student:
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

    result = self.perform_query(query=query, parameters=(student_id,), method="fetchone")

    if result is None:
      return None
    
    return {
      "id": result[0],
      "firstName": result[1],
      "lastName": result[2],
    }

  def create(self, student_id: str, first_name: str, last_name: str) -> None:
    """
    Creates a new student

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

    self.perform_query(query=query, parameters=(student_id, first_name, last_name), method="commit")

  def update(self, first_name: str, last_name: str, student_id: str) -> None:
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

    self.perform_query(query=query, parameters=(first_name, last_name, student_id), method="commit")

  def delete(self, student_id: str) -> None:
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

    self.perform_query(query=query, parameters=(student_id,), method="commit")