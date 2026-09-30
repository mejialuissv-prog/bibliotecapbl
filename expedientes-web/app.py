from flask import Flask, render_template, request

app = Flask(__name__)

VERSION_VIGENTE = 3
ROLES_VALIDOS = ['lectura', 'edicion']

DOCUMENTOS_POR_PERFIL = {
    'administrativo': 5,
    'enfermeria': 7,
    'medico': 9,
}


def a_entero(texto):
    """Convierte el texto de la URL a entero. Si no es un número, regresa None."""
    texto = str(texto).strip()

    if texto.isdigit():
        return int(texto)

    return None


def limpiar_rol(texto):
    """pasa a minúsculas y quita la tilde para aceptar 'edición' o 'edicion'."""
    return str(texto).strip().lower().replace('ó', 'o')


@app.route('/instruccion')
@app.route('/instruccion/<version>/<rol>')
def evaluar_instruccion(version=None, rol=None):
    if version is None:
        version = request.args.get('version', '')

    if rol is None:
        rol = request.args.get('rol', '')

    v = a_entero(version)
    rol = limpiar_rol(rol)

    if v is not None and 1 <= v < VERSION_VIGENTE and rol in ROLES_VALIDOS:
        estado = 'versión obsoleta'
        clase = 'obsoleta'
        detalle = (
            f'la versión {v} fue reemplazada por la versión {VERSION_VIGENTE}. '
            'Solo se muestra como historial; no debe usarse en planta.'
        )

    elif v == VERSION_VIGENTE and rol == 'lectura':
        estado = 'Vigente – solo lectura'
        clase = 'lectura'
        detalle = (
            'el operario puede consultar la instrucción, '
            'pero no modificarla.'
        )

    elif v == VERSION_VIGENTE and rol == 'edicion':
        estado = 'Vigente – lectura y edición'
        clase = 'edicion'
        detalle = (
            'El usuario puede consultar y editar pasos. '
            f'Al guardar cambios se genera la versión {VERSION_VIGENTE + 1}.'
        )

    elif v is not None and v > VERSION_VIGENTE and rol == 'edicion':
        estado = 'Borrador sin publicar'
        clase = 'borrador'
        detalle = (
            'la versión existe como borrador. El editor puede revisarla '
            'y publicarla para que pase a ser la vigente.'
        )

    elif v is not None and v > VERSION_VIGENTE and rol == 'lectura':
        estado = 'no disponible'
        clase = 'bloqueada'
        detalle = (
            'esa versión aún no está publicada; '
            'el perfil de lectura no puede verla.'
        )

    else:
        estado = 'dato no válido'
        clase = 'invalido'
        detalle = (
            'la versión debe ser un número entero mayor que 0 y el rol debe '
            "ser 'lectura' o 'edicion'."
        )

    return render_template(
        'instrucciones.html',
        version=version,
        rol=rol,
        estado=estado,
        clase=clase,
        detalle=detalle,
        vigente=VERSION_VIGENTE
    )


@app.route('/expediente')
@app.route('/expediente/<perfil>/<entregados>')
def evaluar_expediente(perfil=None, entregados=None):
    if perfil is None:
        perfil = request.args.get('perfil', '')

    if entregados is None:
        entregados = request.args.get('entregados', '')

    perfil = str(perfil).strip().lower()
    n = a_entero(entregados)
    requeridos = DOCUMENTOS_POR_PERFIL.get(perfil)

    if requeridos is None or n is None:
        estado = 'dato no válido'
        clase = 'invalido'
        detalle = (
            'Perfil desconocido o cantidad de documentos '
            'que no es un número.'
        )

    elif n == 0:
        estado = 'sin iniciar'
        clase = 'obsoleta'
        detalle = (
            f'no se ha entregado ningún documento '
            f'de los {requeridos} requeridos.'
        )

    elif n < requeridos:
        estado = 'Incompleto'
        clase = 'borrador'
        detalle = f'Faltan {requeridos - n} de {requeridos} documentos.'

    elif n == requeridos:
        estado = 'Completo'
        clase = 'edicion'
        detalle = f'Se entregaron los {requeridos} documentos del checklist.'

    else:
        estado = 'revisar: más documentos de los requeridos'
        clase = 'invalido'
        detalle = (
            f'se registraron {n} documentos, '
            f'pero el perfil solo pide {requeridos}.'
        )

    progreso = 0

    if requeridos and n is not None:
        progreso = min(100, round(n * 100 / requeridos))

    return render_template(
        'expedientes.html',
        perfil=perfil,
        entregados=entregados,
        requeridos=requeridos,
        estado=estado,
        clase=clase,
        detalle=detalle,
        progreso=progreso
    )


if __name__ == '__main__':
    app.run(debug=True)