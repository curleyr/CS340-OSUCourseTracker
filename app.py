from flask import Flask
from blueprints.errorHandlers import error_handlers_blueprint
from blueprints.routes import routes_blueprint

app = Flask(__name__)

# Register the error handlers blueprint
app.register_blueprint(error_handlers_blueprint)

# Register the routes blueprint
app.register_blueprint(routes_blueprint)
    
# Listener
if __name__ == "__main__":
  """
  * Terminal Commands *
  run: 
    gunicorn --name OSUCourseTracker_BC -b 0.0.0.0:7124 -D app:app (Bobby)
    gunicorn --name OSUCourseTracker -b 0.0.0.0:23071 -D app:app (April)
  stop:
    pkill -f 'gunicorn --name OSUCourseTracker_BC'
    pkill -f 'gunicorn --name OSUCourseTracker'
  """
  #app.run()
  app.run(port=8007, debug=True)