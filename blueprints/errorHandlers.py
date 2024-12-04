from flask import Blueprint, jsonify, render_template
from werkzeug.exceptions import HTTPException

# Define custom exceptions
class DatabaseError(Exception):
  """
  Custom exception class for database errors
  """
  pass

class QueryError(Exception):
  """
  Custom exception class for query errors
  """
  pass

# Define blueprint
error_handlers_blueprint = Blueprint('ErrorHandlers', __name__)

# Define error handlers
@error_handlers_blueprint.app_errorhandler(QueryError)
def handleQueryError(error):
  return jsonify({"error": "QueryError occurred", "message": str(error)}), 400 

@error_handlers_blueprint.app_errorhandler(DatabaseError)
def handleDatabaseError(error):
  return jsonify({"error": "DatabaseError occurred", "message": str(error)}), 500 

@error_handlers_blueprint.app_errorhandler(HTTPException)
def handleHTTPException(error):
  return render_template("exception.j2", error_name = error.name, error_description = error.description), error.code

@error_handlers_blueprint.app_errorhandler(KeyError)
def handleKeyError(error):
  return jsonify({"error": "KeyError occurred", "message": f"A key with the name of '{error.args[0]}' was accessed but does not exist."}), 400

@error_handlers_blueprint.app_errorhandler(Exception)
def handleGenericException(error):
  return jsonify({"error": "Unexpected error occurred", "message": str(error)}), 500