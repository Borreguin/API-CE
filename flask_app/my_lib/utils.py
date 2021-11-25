import argparse, os
import datetime as dt
import pandas as pd
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


def read_excel(file_name):
    """
    Lee un archivo excel y devuelve un diccionario de DataFrames
    :param file_name: path del archivo a leer
    :return: diccionario de DataFrames
    """
    # variables generales usadas en el script:
    name = file_name.split('\\')
    name = name[-1]
    file_time = None
    last_time = -1
    df_update = pd.DataFrame(columns=["time"])

    # configurando rutas:
    db_path = script_path.replace("my_lib", "_db")
    pkl_file = os.path.join(db_path, name.replace("xlsx", "pkl"))
    json_file = os.path.join(db_path, "update_time.json")

    # verificando si los archivos existen:
    json_exists = os.path.exists(json_file)
    file_exists = os.path.exists(file_name)
    pkl_exists = os.path.exists(pkl_file)

    if file_exists:
        # obtener la hora de última modificación
        file_time = os.path.getmtime(file_name)
    else:
        msg = "El archivo {0} no existe".format(file_name)
        print(msg)
        return None, msg

    # si el archivo json existe, obtener last_time
    if json_exists:
        df_update = pd.read_json(json_file)
        if name in df_update.index:
            last_time = df_update["time"][name]

    # grabar file_time in df_update:
    df_update.loc[name] = [file_time]
    df_update.to_json(json_file)

    # si hay una modificación en el archivo Excel, leer el archivo
    # y transformarlo en formato pkl
    if last_time != file_time or not pkl_exists:
        try:
            xls = pd.ExcelFile(file_name)
            dt_excel = dict()
            for s in xls.sheet_names:
                dt_excel[s] = pd.read_excel(xls, s)
            with open(pkl_file, 'wb') as handle:
                pkl.dump(dt_excel, handle, protocol=pkl.HIGHEST_PROTOCOL)
            return dt_excel, "[{0}] Leído correctamente".format(file_name)
        except Exception as e:
            return None, str(e)
    elif pkl_exists and last_time == file_time:
        with open(pkl_file, 'rb') as handle:
            dt_excel = pkl.load(handle)
        return dt_excel, "[{0}] Leído correctamente".format(file_name)


def fill_information_usuario(html_str: str, form: FormularioTemporal, files=None):
    html_str = html_str.replace("#codigo_tramite", form.id_forma)
    html_str = html_str.replace("#tipo_tramite", form.data["tipo_tramite"])
    html_str = html_str.replace("#nombres", form.data["nombre_apellidos"])
    html_str = html_str.replace("#c_ciudadania", form.data["ci"])
    html_str = html_str.replace("#cargo", form.data["cargo"])
    html_str = html_str.replace("#telefono", form.data["telefono"])
    html_str = html_str.replace("#detalle", form.data["detalle_tramite"])
    enlace_modifiacion = f"{init.HOSTNAME_URL}/formulario?ifmd={form.id_forma}"
    html_str = html_str.replace("#enlace_modificacion", enlace_modifiacion)
    enlace_aceptar = f"{init.HOSTNAME_URL}/confirmacion?ifmd={form.id_forma}"
    html_str = html_str.replace("#enlace_aceptar", enlace_aceptar)
    if files is None or len(files) == 0:
        html_str = html_str.replace("#archivos","Sin archivos adjuntos")
    else:
        html_str = html_str.replace("#archivos", "; ".join(files))
    return html_str


def fill_information_comite(html_str: str, form: FormularioTemporal, files=None):
    html_str = html_str.replace("#codigo_tramite", form.id_forma)
    html_str = html_str.replace("#tipo_tramite", form.data["tipo_tramite"])
    html_str = html_str.replace("#nombres", form.data["nombre_apellidos"])
    html_str = html_str.replace("#c_ciudadania", form.data["ci"])
    html_str = html_str.replace("#cargo", form.data["cargo"])
    html_str = html_str.replace("#telefono", form.data["telefono"])
    html_str = html_str.replace("#detalle", form.data["detalle_tramite"])
    if files is None or len(files) == 0:
        html_str = html_str.replace("#archivos","Sin archivos adjuntos")
    else:
        html_str = html_str.replace("#archivos", "; ".join(files))
    return html_str


def get_files_for(id_forma:str):
    file_form_path = os.path.join(init.FILE_REPO, id_forma)
    if not os.path.exists(file_form_path):
        return []
    dirs = os.listdir(file_form_path)
    return [f for f in dirs if os.path.isfile(os.path.join(file_form_path, f))]


def set_max_age_to_response(response, seconds):
    response.expires = dt.datetime.utcnow() + dt.timedelta(seconds=seconds)
    response.cache_control.max_age = seconds
    return response
