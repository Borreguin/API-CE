import argparse, os
import datetime as dt
# import pandas as pd
import pickle as pkl

from flask_app.dto.mongo_class.FormTemporal import FormularioTemporal
import flask_app.settings.initial_settings as init

script_path = os.path.dirname(os.path.abspath(__file__))


def valid_date(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "El parámetro: '{0}' no es una fecha válida, (formato YYYY-MM-DD).".format(s)
        raise argparse.ArgumentTypeError(msg)


def get_dates_for_last_month():
    d_n = dt.datetime.now()
    date_ini = dt.datetime(year=d_n.year, month=d_n.month - 1, day=1)
    date_end = dt.datetime(year=d_n.year, month=d_n.month, day=d_n.day) - dt.timedelta(days=d_n.day)
    return date_ini, date_end


def check_date_yyyy_mm_dd(s):
    try:
        return True, dt.datetime.strptime(s, "%Y-%m-%d")
    except Exception as e:
        return False, str(e)


def fill_basic_information(html_str: str, form, files=None):
    html_str = html_str.replace("#codigo_tramite", form.id_forma, files)
    html_str = html_str.replace("#tipo_tramite", form.data["tipo_tramite"])
    html_str = html_str.replace("#nombres", form.data["nombre_apellidos"])
    html_str = html_str.replace("#c_ciudadania", form.data["ci"])
    html_str = html_str.replace("#cargo", form.data["cargo"])
    html_str = html_str.replace("#telefono", form.data["telefono"])
    html_str = html_str.replace("#detalle", form.data["detalle_tramite"])
    if files is None or len(files) == 0:
        html_str = html_str.replace("#archivos", "Sin archivos adjuntos")
    else:
        html_str = html_str.replace("#archivos", "; ".join(files))
    return html_str


def fill_information_usuario(html_str: str, form: FormularioTemporal, files=None):
    html_str = fill_basic_information(html_str, form, files)
    enlace_modifiacion = f"{init.HOSTNAME_URL}/formulario?ifmd={form.id_forma}"
    html_str = html_str.replace("#enlace_modificacion", enlace_modifiacion)
    enlace_aceptar = f"{init.HOSTNAME_URL}/confirmacion?ifmd={form.id_forma}"
    html_str = html_str.replace("#enlace_aceptar", enlace_aceptar)
    return html_str


def fill_information_comite(html_str: str, form: FormularioTemporal, files=None):
    html_str = fill_basic_information(html_str, form, files)
    return html_str


def fill_timeline_notification(html_str: str, form, files=None):
    html_str = fill_basic_information(html_str, form, files)
    # The last state of the timeline
    state = form.timeline[-1].state if len(form.timeline) > 1 else None
    html_str = html_str.replace("#estado", state)
    # link to see the current state:
    enlace_consulta = f"{init.HOSTNAME_URL}/consulta?ifmd={form.id_forma}"
    html_str = html_str.replace("#enlace_consulta", enlace_consulta)
    return html_str


def get_files_for(id_forma: str):
    file_form_path = os.path.join(init.FILE_REPO, id_forma)
    if not os.path.exists(file_form_path):
        return []
    dirs = os.listdir(file_form_path)
    return [f for f in dirs if os.path.isfile(os.path.join(file_form_path, f))]


def set_max_age_to_response(response, seconds):
    response.expires = dt.datetime.utcnow() + dt.timedelta(seconds=seconds)
    response.cache_control.max_age = seconds
    return response
