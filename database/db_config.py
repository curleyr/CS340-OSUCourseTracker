import MySQLdb
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
mysql_host = os.environ.get("mysql_host")
mysql_user = os.environ.get("mysql_user")
mysql_password = os.environ.get("mysql_password") 
mysql_database = os.environ.get("mysql_database")

mysql_connection = MySQLdb.connect(mysql_host, mysql_user, mysql_password, mysql_database)

def connectToDB():
  """
  Checks connection to DB and reconnects if connection has been lost
  """
  # Set global variable to be used outside of function scope
  global mysql_connection
  try:
    # Check MySQL connection and attempt reconnect
    mysql_connection.ping()
  except MySQLdb.Error:
    # If recconect failed, restart connection
    mysql_connection = MySQLdb.connect(mysql_host, mysql_user, mysql_password, mysql_database)
  return mysql_connection