import MySQLdb
from blueprints.errorHandlers import DatabaseError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class DatabaseManager:
  """
  Manages the connection to the MySQL database
  Handles the following:
    - Connecting to the database
    - Checking the connection status
    - Executing queries
    - Closing the cursor
    - Closing the db connection
  """

  def __init__(self):
    """
    Initializes the DatabaseManager instance and environment variables to store as attributes
    """
    # Initialize connection variables
    self._mysql_host = os.environ.get("mysql_host")
    self._mysql_user = os.environ.get("mysql_user")
    self._mysql_password = os.environ.get("mysql_password")
    self._mysql_database = os.environ.get("mysql_database")
    self._mysql_connection = None
    self._mysql_cursor = None
    self.make_connection()

  def make_connection(self):
    """
    Makes a connection to the MySQL database using the provided environment variables
    Sets up a cursor for executing queries
    """
    try:
      # Make connection
      self._mysql_connection = MySQLdb.connect(
        self._mysql_host, 
        self._mysql_user, 
        self._mysql_password, 
        self._mysql_database
      )
      # Set cursor
      self._mysql_cursor = self._mysql_connection.cursor()
    
    except MySQLdb.DatabaseError as error:
      raise DatabaseError(f"An error occurred while connecting to the database: {error}")

  def check_connection(self):
    """
    Checks if the current connection to the MySQL database is still active
    If the connection is lost or encounters an error, it attempts to reconnect by calling the make_connection method
    """
    try:
      # Check MySQL connection
      self._mysql_connection.ping()

      # Set cursor
      self._mysql_cursor = self._mysql_connection.cursor()

    except MySQLdb.Error as error:
      # If connection failed, restart connection
      print(f"Error connecting to database: {error}. Attempting to reconnect.")
      self.make_connection()

  def close_cursor(self):
    """
    Closes the MySQL cursor
    This method is called after each query is executed
    """
    try:
      self._mysql_cursor.close()

    except MySQLdb.DatabaseError as error:
      raise DatabaseError(f"An error occurred while closing the database cursor: {error}")

  def close_connection(self):
    """
    Closes the MySQL connection
    This method is called on select pages to reset db cache
    """
    try:
      self._mysql_connection.close()
    
    except MySQLdb.DatabaseError as error:
      raise DatabaseError(f"An error occurred while closing the connection to the database: {error}")

  def execute_query(self, query: str, parameters: tuple = None, method: str = None):
    """
    Executes a MySQL query on the database
    Depending on the method passed, it returns:
      - All results (fetchall)
      - A single result (fetchone)
      - Commit changes (commit) 

    Arguments:
      - query (str): The SQL query to execute
      - parameters (tuple, optional): The parameters for the query. Defaults to an empty tuple if not provided.
      - method (str, optional): The query method, e.g., "fetchall", "fetchone", or "commit". Defaults to "fetchall".

    Returns:
      - Tuple with a status code and either the result or an error message
    """
    if not parameters:
      parameters = ()

    try:
      self._mysql_cursor.execute(query, parameters)
      
      if not method or method == "fetchall":
        return (200, self._mysql_cursor.fetchall())
      
      elif method == "fetchone":
        return (200, self._mysql_cursor.fetchone())
      
      elif method == "commit":
        self._mysql_connection.commit()
        if self._mysql_cursor.rowcount == 0:
          return (400, "Commit unsuccessful")
        return (200, "Commit successful")
      
      else:
        return(500, f"Unsupported query method received: {method}")

    except MySQLdb.DatabaseError as error:
      return (500, error)
    
    finally:
      self._mysql_cursor.close()