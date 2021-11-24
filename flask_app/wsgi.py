import os, sys

# To register path to search custom libraries
script_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(script_path)
sys.path.append(project_path)
sys.path.append(script_path)

from flask_app.api.app import app

if __name__ == "__main__":
    app.run()