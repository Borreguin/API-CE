# Created by Roberto Sanchez at 4/16/2019
# -*- coding: utf-8 -*-
""""
    Servicio Web de Sistema Remoto:
        - Permite la administración de Nodos, Entidades y Tags
        - Serializar e ingresar datos

    If you need more information. Please contact the email above: rg.sanchez.arg_from@gmail.com
    "My work is well done to honor God at any time" R Sanchez A.
    Mateo 6:33
"""

from flask_restplus import Resource
from flask import request
import re, os
# importando configuraciones iniciales
from api.settings import initial_settings as init
from api.services.restplus_config import api
from api.services.restplus_config import default_error_handler
from api.services.sRemoto import serializers as srl
from api.services.sRemoto import parsers
# importando clases para leer desde MongoDB
from api.my_lib.mongo_engine_handler.sRNode import *


# configurando logger y el servicio web
log = init.LogDefaultConfig("ws_sRemoto.log").logger
ns = api.namespace('admin-sRemoto', description='Relativas a la administración de nodos de Sistema Remoto')

ser_from = srl.sRemotoSerializers(api)
api = ser_from.add_serializers()


@ns.route('/nodo/<string:nombre>')
class SRNodeAPI(Resource):

    def get(self, nombre:str="Nombre del nodo a buscar"):
        """ Busca si un nodo tipo SRNode existe en base de datos """
        try:
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return nodo, 404
            return nodo.to_dict(), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.name_update)
    def put(self, nombre: str="Nombre de la entity_list a cambiar"):
        """
        Actualiza el nombre de un nodo
        """
        new_name = request.json["nuevo_nombre"]
        try:
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return nodo, 404
            nodo.nombre = new_name
            nodo.actualizado = dt.datetime.now()
            nodo.save()
            return nodo.to_dict(), 200
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.name_delete)
    def delete(self, nombre):
        """ Elimina el nodo con documentos de consignación asociados """
        name_delete = request.json["eliminar_elemento"]
        if name_delete != nombre:
            return None, 400
        try:
            nodo = SRNode.objects(nombre=name_delete).first()
            if nodo is None:
                return nodo, 404
            nodo.delete_all()
            return nodo.to_dict(), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/nodo')
class PostSRNodeAPI(Resource):
    @api.expect(ser_from.node)
    @api.response(400, 'No es posible crear este nodo')
    def post(self):
        """ Crear un SRNode """
        try:
            request_data = dict(request.json)
            nodo = SRNode(**request_data)
            nodo.save()
            return nodo.to_dict(), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/nodo/<string:nombre>/entity_list')
class SREntidadAPI(Resource):
    @api.expect(ser_from.entidad)
    @api.response(404, 'No se puede añadir. El nodo especificado en "nombre" no existe')
    def put(self, nombre):
        """ Añadir/substituir una entity_list en el nodo "nombre"
            Si el nodo no existe entonces error 404
            La entity_list es añadida a un nodo ya existente
            Si la entity_list ya existe entonces es reemplazada
        """
        try:
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return nodo, 404
            request_data = dict(request.json)
            entidad = SREntity(**request_data)
            nodo.add_or_replace_entities(entidad)
            nodo.save()
            return nodo.to_dict(), 200
        except Exception as e:
            return default_error_handler(e)

    @api.response(404, 'No se encuentran resultados')
    @api.expect(ser_from.name_delete)
    def delete(self, nombre):
        """ Eliminar una entity_list en el nodo "nombre"
            Si el nodo no existe entonces error 404
            Si la entity_list no existe entonces error 404
        """
        try:
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return nodo, 404
            name_delete = dict(request.json)["eliminar_elemento"]
            success, msg = nodo.delete_entity(name_delete)
            if success:
                nodo.save()
                return nodo.to_dict(), 200
            else:
                return dict(success=success, errors=msg), 404
        except Exception as e:
            return default_error_handler(e)


@ns.route('/nodo/<string:nombre>/<string:entity_list>')
class SREntidadesAPI(Resource):
    @api.response(404, 'No se encuentran resultados')
    def get(self, nombre, entidad):
        """ Muestra la entity_list
            Si el nodo no existe entonces error 404
            Si la entity_list no existe entonces error 404
        """
        try:
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return nodo, 404
            success, result = nodo.search_entity(entidad)
            return (result.to_dict(), 200) if success else (dict(success=success, errors=result), 404)
        except Exception as e:
            return default_error_handler(e)


@ns.route('/nodo/<string:nombre>/entidades')
class SREntidadesAPI(Resource):
    @api.response(404, 'No se encuentran resultados')
    def get(self, nombre):
        """ Muestra las entidades de un nodo
            Si nodo no existe entonces error 404
        """
        try:
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return nodo, 404
            return [e.to_dict() for e in nodo.entidades], 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/nodo/<string:nombre>/<string:entity_list>/tags')
class SRTagsAPI(Resource):
    @api.expect(ser_from.list_tagname)
    def put(self, nombre, entidad):
        """ Actualiza la configuración de tags en una entity_list
            Si el nodo no existe entoces error 404
            Si entity_list no existe entonces error 404
        """
        try:
            tags = dict(request.json)["tags"]
            tag_list = [SRTag(**t) for t in tags]
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return dict(success=False, errors=f"No existe nodo [{nombre}]"), 404
            success, msg = nodo.add_or_replace_tags_in_entity(tag_list, entidad)
            if success:
                nodo.save()
                correct, r = nodo.search_entity(entidad)
                return (r.to_dict(), 200) if correct else (r, 400)
            return dict(success=False, errors=msg), 400
        except Exception as e:
            return default_error_handler(e)

    def get(self, nombre, entidad):
        """ Muestra las tags dentro de una entity_list """
        try:
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return dict(success=False, errors=f"No existe nodo [{nombre}]"), 404
            check = [i for i, e in enumerate(nodo.entidades) if entidad == e.nombre]
            if len(check) > 0:
                ix = check[0]
                tags = nodo.entidades[ix].tags
                return [t.to_dict() for t in tags], 200
            return dict(success=False, errors=f"No existe entity_list [{entidad}] en nodo [{nombre}]"), 404
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.tags)
    def delete(self, nombre, entidad):
        """ Elimina una lista de tags de una entity_list en un nodo """
        try:
            tags = dict(request.json)["tags"]
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return dict(success=False, errors=f"No existe nodo [{nombre}]"), 404
            success, msg = nodo.remove_tags_in_entity(tag_list=tags, nombre_entidad=entidad)
            if success:
                nodo.save()
                correct, r = nodo.search_entity(entidad)
                return (r.to_dict(), 200) if correct else (r, 400)
            return dict(success=False, errors=msg), 400
        except Exception as e:
            return default_error_handler(e)


@ns.route('/nodo/<string:nombre>/<string:entity_list>/tag')
class SRTagAPI(Resource):
    @api.expect(ser_from.tagname)
    def put(self, nombre, entidad):
        """ Modifica la configuración de una tag
            Si la entity_list no existe en el nodo entonces habrá un error 404
            Si la tag no existe en la entity_list entonces se crea una nueva
        """
        try:
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return dict(success=False, errors=f"No existe nodo [{nombre}]"), 404
            # from body content convert to SRTag object
            tag = SRTag(**request.json)
            success, msg = nodo.add_or_replace_tags_in_entity([tag], entidad)
            if success:
                nodo.save()
                correct, r = nodo.search_entity(entidad)
                return (r.to_dict(), 200) if correct else (r, 400)
            return dict(success=False, errors=msg), 400
        except Exception as e:
            return default_error_handler(e)

    @api.expect(ser_from.name_delete)
    def delete(self, nombre, entidad):
        """ Elimina la configuración de una tag
            Si la entity_list no existe en el nodo entonces habrá un error 404
            Si la tag no existe en la entity_list entonces habrá un error 404
        """
        try:
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is None:
                return dict(success=False, errors=f"No existe nodo [{nombre}]"), 404
            # nombre a eliminar
            name_delete = dict(request.json)["eliminar_elemento"]
            # check if entity exists:
            check_entity = [i for i, e in enumerate(nodo.entidades) if entidad == e.nombre]
            if len(check_entity) == 0:
                return dict(success=False, errors=f"No existe la entity_list [{entidad}] en nodo [{nombre}]")
            id_e = check_entity[0]
            # if entity exists then use tags from that entity (id_e)
            new_tags = list()
            for t in nodo.entidades[id_e].tags:
                if t.tag_name != name_delete:
                    new_tags.append(t)

            nodo.entidades[id_e].tags = new_tags
            nodo.save()
            return nodo.entidades[id_e].to_dict(), 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/nodos/')
@ns.route('/nodos/<string:filter>')
class SRNodoAPI(Resource):
    def get(self, filter=None):
        """
        Muestra todos los nombres de los nodos existentes si el filtro está vacio
        Los caracteres * son comodines de busqueda
        Ejemplo: ['pala', 'alambre', 'pétalo'] ,
                *ala* => 'pala', 'alambre'
                ala* => 'alambre'
        """
        try:
            nodes = SRNode.objects
            if len(nodes) == 0:
                return dict(success=False, errors=f"No hay nodos en la base de datos"), 404
            if filter is None or len(filter) == 0:
                to_show = [n.to_summary() for n in nodes]
                return to_show, 200
            filter = str(filter).replace("*", ".*")
            regex = re.compile(filter, re.IGNORECASE)
            nodes = SRNode.objects(nombre=regex)
            to_show = [n.to_summary() for n in nodes]
            return to_show, 200
        except Exception as e:
            return default_error_handler(e)


@ns.route('/nodo/<string:nombre>/<string:tipo>/from-excel')
class SRNodeFromExcel(Resource):
    @api.response(200, 'El nodo ha sido ingresado de manera correcta')
    @api.expect(parsers.excel_upload)
    def post(self, nombre, tipo):
        """ Permite añadir un nodo mediante un archivo excel
            Si el nodo ha sido ingresado correctamente, entonces el código es 200
        """
        try:
            args = parsers.excel_upload.parse_args()
            nodo = SRNode.objects(nombre=nombre).first()
            if nodo is not None:
                return dict(success=False, errors=f"El nodo {[nombre]} ya existe"), 400

            if args['excel_file'].mimetype in 'application/xls, application/vnd.ms-excel,  application/xlsx' \
                                              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                excel_file = args['excel_file']
                stream_excel_file = excel_file.stream.read()
                filename = excel_file.filename
                df_main = pd.read_excel(excel_file, sheet_name="main")
                df_tags = pd.read_excel(excel_file, sheet_name="tags")
                # create a virtual node:
                v_node = SRNodeFromDataFrames(nombre, tipo, df_main, df_tags)
                success, msg = v_node.validate()
                if not success:
                    return dict(success=False, errors=msg), 400
                # create a final node to save if is successful
                success, node = v_node.create_node()
                if not success:
                    return dict(success=False, errors=str(node)), 400
                node.actualizado = dt.datetime.now()
                node.save()
                # Guardar como archivo Excel con versionamiento
                destination = os.path.join(init.EXCEL_REPO, filename)
                save_excel_file_from_bytes(destination=destination, stream_excel_file=stream_excel_file)
                return str(node), 200
            else:
                return dict(success=False, errors="El formato del archivo no es aceptado"), 400
        except Exception as e:
            return default_error_handler(e)

    @api.response(200, 'El nodo ha sido actualizado de manera correcta')
    @api.expect(parsers.excel_upload)
    def put(self, nombre, tipo):
        """ Permite actualizar un nodo mediante un archivo excel
            Si el nodo no existe entonces error 404
            Si las entidades internas no existen entonces se añaden a la lista de entidades
            Si las tags ya existen entonces estas son actualizadas, caso contrario se añaden a la lista de tags
        """

        args = parsers.excel_upload.parse_args()
        nodo = SRNode.objects(nombre=nombre).first()
        if nodo is None:
            return dict(success=False, errors=f"El nodo {[nombre]} no existe"), 400

        try:
            if args['excel_file'].mimetype in 'application/xls, application/vnd.ms-excel,  application/xlsx' \
                                              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                excel_file = args['excel_file']
                stream_excel_file = excel_file.stream.read()
                filename = excel_file.filename
                df_main = pd.read_excel(stream_excel_file, sheet_name="main")
                df_tags = pd.read_excel(stream_excel_file, sheet_name="tags")
                # create a virtual node:
                v_node = SRNodeFromDataFrames(nombre, tipo, df_main, df_tags)
                success, msg = v_node.validate()
                if not success:
                    return dict(success=False, errors=msg), 400
                # create a final node to save if is successful
                success, new_node = v_node.create_node()
                if not success:
                    return dict(success=False, errors=str(new_node)), 400
                nodo.actualizado = dt.datetime.now()
                success, msg = nodo.add_or_replace_entities(new_node.entidades)
                if not success:
                    return dict(success=False, errors=str(msg)), 400
                nodo.save()
                # Guardar como archivo Excel con versionamiento
                destination = os.path.join(init.EXCEL_REPO, filename)
                save_excel_file_from_bytes(destination=destination, stream_excel_file=stream_excel_file)
                return str(nodo), 200
            else:
                return dict(success=False, errors="El formato del archivo no es aceptado"), 400
        except Exception as e:
            return default_error_handler(e)


def save_excel_file_from_bytes(destination, stream_excel_file):
    try:
        n = 7
        last_file = destination.replace(".xls", f"_{n}.xls")
        first_file = destination.replace(".xls", "_1.xls")
        for i in range(n, 0, -1):
            file_n = destination.replace(f".xls", f"_{str(i)}.xls")
            file_n_1 = destination.replace(f".xls", f"_{str(i+1)}.xls")
            if os.path.exists(file_n):
                os.rename(file_n, file_n_1)
        if os.path.exists(last_file):
            os.remove(last_file)
        if not os.path.exists(first_file) and os.path.exists(destination):
            os.rename(destination, first_file)

    except Exception as e:
        version = dt.datetime.now().strftime("_%Y-%b-%d_%Hh%M")
        destination = destination.replace(".xls", f"{version}.xls")

    with open(destination, 'wb') as f:
        f.write(stream_excel_file)


@ns.route('/upload')
class UploadFile(Resource):
    @api.response(200, 'Archivo subido correctamente')
    @api.expect(parsers.file_upload)
    def post(self):
        try:
            args = parsers.file_upload.parse_args()
            print(args['file'].mimetype)
            return dict(success=True), 200
        except Exception as e:
            return default_error_handler(e)