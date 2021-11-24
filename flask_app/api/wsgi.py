import os, sys

# To register path to search custom libraries
api_path = os.path.dirname(os.path.abspath(__file__))
flask_path = os.path.dirname(api_path)
project_path = os.path.dirname(flask_path)
sys.path.append(api_path)
sys.path.append(project_path)

from flask_app.api.app import app

if __name__ == "__main__":
    app.run()