from database.DatabaseManager import DatabaseManager
from blueprints.errorHandlers import QueryError
from typing import List, TypedDict, Any 

class Term(TypedDict):
  id: int
  name: str
  startDate: str
  endDate: str
  courses: str

class TermManager:
  """
  Manages all database queries related to Terms and interacts with the DatabaseManager to execute the queries.
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
  
  def all(self) -> List[Term]:
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

    return [
      {
        "id": row[0],
        "name": row[1],
        "startDate": row[2],
        "endDate": row[3],
        "courses": row[4]
      }
      for row in self.perform_query(query=query, method="fetchall")
    ]
    
  def get(self, term_season: str, term_year: int, fields: list = ["termID"]) -> Term:
    """
    Retrieves the requested term fields given term season and year

    Arguments:
      - term_season (str): The name of the season for which the ID is requested.
      - term_year (int): The year of the term for which the ID is requested.
      - fields (list, optional): The term fields to return. Defaults to "id". 
      
    Returns:
      - Term (dict): The term with the fields included if found, otherwise None.

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()

    query = """
      SELECT {}
      FROM Terms
      WHERE name = %s
    """.format(", ".join(fields))

    return self.perform_query(query=query, parameters=(f"{term_season} {term_year}",), method="fetchone")

  def create(self, term_season: str, term_year: int, term_start_date: str, term_end_date: str) -> None:
    """
    Creates a new term

    Arguments:
      - term_season (str): The season of the term
      - term_year (int): The year of the term
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

    self.perform_query(query=query, parameters=(f"{term_season} {term_year}", term_start_date, term_end_date), method="commit")

  def add_course(self, term_course_id: int, term_season: str = None, term_year: int = None, term_id: int = None) -> None:
    """
    Adds a course to a term

    Arguments:
      - term_course_id (int): The id of the course being added to the term
      - term_season (str, optional): the season of the term
      - term_year (int, optional): the yar of the term
      - term_name (str, optional): The name of the term
      - term_id (int, optional): The id of the term

    Returns:
      - None

    Raises:
      QueryError: If an error occurs during the query execution.
    """
    self._database_manager.check_connection()
    
    if not any([term_season, term_year, term_id]):
      raise QueryError(f"An error occurred while executing the query: neither a term season/year or id was provided.")

    if term_season and term_year:
      query = """
        INSERT INTO Terms_has_Courses (termID, courseID)
        VALUES ((SELECT termID FROM Terms WHERE name = %s), %s);
      """
      parameters = (f"{term_season} {term_year}", term_course_id)

    else:
      query = """
        INSERT INTO Terms_has_Courses (termID, courseID)
        VALUES (%s, %s)
      """
      parameters = (term_id, term_course_id)

    self.perform_query(query=query, parameters=parameters, method="commit")