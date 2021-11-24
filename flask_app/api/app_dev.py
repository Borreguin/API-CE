""" Setting the production environment variable """
import os, sys
os.environ['production_env'] = 'False'

# añadiendo a sys el path del proyecto:
# permitiendo el uso de librerías propias:
api_path = os.path.dirname(os.path.abspath(__file__))
flask_path = os.path.dirname(api_path)
project_path = os.path.dirname(flask_path)
sys.path.append(api_path)
sys.path.append(project_path)

# import project modules
import flask_app.settings.initial_settings as init
from flask_app.api.app import build_app
from flask_app.api import log


def main():
    # build the flask app (web application)
    app = build_app()
    init.DEBUG = True
    # serve the application in development mode
    log.info(f'>>>>> Starting development server <<<<<')
    app.run(debug=init.DEBUG, port=5000)
    log.info(f'>>>>> host: localhost port: {init.API_PORT}<<<<<')
    log.info(f">>>>> API running over: {init.API_PREFIX}")


if __name__ == "__main__":
    main()
