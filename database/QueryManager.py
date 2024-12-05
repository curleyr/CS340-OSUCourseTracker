from database.DatabaseManager import DatabaseManager
from database.CourseManager import CourseManager
from database.TermManager import TermManager
from database.StudentManager import StudentManager
from database.StudentTermPlanManager import StudentTermPlanManager

class QueryManager:
  """
  Manages all database queries and interacts with the DatabaseManager to execute the queries.
  """

  def __init__(self, database_manager: DatabaseManager):
    """
    Initializes the QueryManager instance and stores the provided CourseManager, TermManager, StudentManager, and StudentTermPlanManager instances.

    Arguments:
      - database_manager (DatabaseManager): An instance of the DatabaseManager class that manages database connections and executing queries.
    """
    self._database_manager = database_manager
    self._courses = CourseManager(self._database_manager)
    self._terms = TermManager(self._database_manager)
    self._students = StudentManager(self._database_manager)
    self._studentTermPlans = StudentTermPlanManager(self._database_manager)