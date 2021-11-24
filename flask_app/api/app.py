""""
      Created by Roberto Sánchez A.
      API de gestion de denuncias del Comité de Ética de CENACE
      Servicios:
        - Formularios de denuncias
        - Subir archivos referentes a las denuncias
"""
from flask import send_from_directory
import os, sys
import copy, json
from flask import Blueprint

# añadiendo a sys el path del proyecto:
# permitiendo el uso de librerías propias:
api_path = os.path.dirname(os.path.abspath(__file__))
flask_path = os.path.dirname(api_path)
project_path = os.path.dirname(flask_path)
sys.path.append(api_path)
sys.path.append(project_path)

from flask_app.settings import initial_settings as init
# importando la configuración general de la API
from flask_app.api.services.restplus_config import api as api_p
from flask_app.api import app
from waitress import serve

""" EndPoints """
# namespaces: Todos los servicios de esta API
from flask_app.api.services.Formulario.endpoints.api_form import ns as namespace_api_form
from flask_app.api.services.Formulario.endpoints.api_users import ns as namespace_api_users
from flask_app.api.services.Formulario.endpoints.api_confirmation import ns as namespace_confirmacion
from flask_app.api.services.Formulario.endpoints.api_configurations import ns as namespace_configurations

""" global variables """
from flask_app.api.app_config import log  # Logger

blueprint = Blueprint('api', __name__, url_prefix=init.API_PREFIX)  # Name Space for API


def adding_end_points(blueprint, app):
    """
    Configuración de la API. Añadiendo los servicios a la página inicial
    Aquí añadir todos los servicios que se requieran para la API:
    """
    # adding the blueprint (/API_URL_PREFIX)
    api_p.init_app(blueprint)

    # adding Endpoints to this API
    # añadiendo los servicios de la API (EndPoints)
    api_p.add_namespace(namespace_api_form)
    api_p.add_namespace(namespace_api_users)
    api_p.add_namespace(namespace_confirmacion)
    api_p.add_namespace(namespace_configurations)

    # registrando las rutas:
    app.register_blueprint(blueprint)


def generate_swagger_json_file(app):
    # to generate the local copy of swagger.json
    app_cpy = copy.copy(app)
    app_cpy.config["SERVER_NAME"] = "localhost"
    app_cpy.app_context().__enter__()
    with open('swagger.json', 'w', encoding='utf-8') as outfile:
        json.dump(api_p.__schema__, outfile, indent=2, ensure_ascii=False)


def adding_blueprint_routes(blueprint):
    # this path is only for testing purposes:
    @blueprint.route("/test")
    def b_test():
        """
            To know whether the Blueprint is working or not Ex: http://127.0.0.1:5000/api/test
        """
        return "This is a test. Blueprint is working correctly."


def adding_app_routes(app):
    @app.route("/")
    def main_page():
        """ Adding initial page """
        return f"This is home page for this API, check the prefix to see the UI: {init.API_PREFIX} " \
               f"<br><br>Gerencia Nacional de Desarrollo Técnico - Octubre 2020 - API Cálculo de disponibilidad de " \
               f"Sistema Remoto"

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')


def build_app():
    # Add authentication for this API
    # add_authentication(app)

    # Path configuration:
    blueprint = Blueprint('api', __name__, url_prefix=init.API_PREFIX)  # Name Space for API using Blueprint

    # blueprint for non-auth parts of app
    # from api.authentication.main import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    # from api.authentication.auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)

    adding_blueprint_routes(blueprint)  # adding normal routes to the Blueprint /API_URL_PREFIX/.. (if is needed)
    adding_end_points(blueprint, app)  # Add blueprint (API_URL_PREFIX), routes and EndPoints
    adding_app_routes(app)  # adding normal routes to the app /..
    return app


def main():
    # build the flask app (web application)
    app = build_app()

    # Iniciando la API
    log.info(">>>>> Starting production server <<<<<")
    log.info(f">>>>> API running over: {init.API_PREFIX}")
    # serve the application
    serve(app, host='0.0.0.0', port=init.API_PORT)


if __name__ == "__main__":
    main()

