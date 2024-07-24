from django.db import IntegrityError
from django.db.models import DateField
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from san_blas_app.services import crear_cliente, crear_mascota, crear_reserva, crear_consulta, crear_vacuna
from san_blas_app.services import listar_comunas_metropolitana, guardar_formulario_contacto, registrar_suscripcion
from san_blas_app.services import obtener_clientes, obtener_clientes_filtrados, obtener_reservas_cliente, eliminar_reserva
from san_blas_app.services import actualizar_usuario, obtener_pacientes, obtener_pacientes_filtrados
from san_blas_app.services import listar_resenas, crear_resena
from san_blas_app.services import nombre_usuario_existe, mascota_existe, mascota_existe_global, obtener_listado_chips
from san_blas_app.services import obtener_usuario,obtener_primer_nombre_usuario, obtener_ruts_clientes, obtener_cliente
from san_blas_app.services import obtener_horarios_disponibles, obtener_horarios_reservados, obtener_horarios_disponibles_sin_tope, obtener_horarios_reservados_filtrados, obtener_horarios_disponibles_filtrados
from san_blas_app.services import obtener_mascotas_cliente, obtener_mascotas,obtener_mascota
from san_blas_app.services import obtener_tipos_cita, obtener_tipos_vacuna, obtener_vacunas_mascotas, obtener_especie_mascota
from san_blas_app.services import verificar_vacuna_registrada, obtener_tipos_vacuna_todos

from san_blas_app.models import TipoCita

# Create your views here.

# Vista de inicio
def indice(request):
    # Llama las reseñas desde el crud
    resenas = listar_resenas()
    return render(request, "indice.html", {'resenas': resenas})

# Vista de registro de usuario
def registro(request):
    comunas = listar_comunas_metropolitana() # Comunas para el selector de la vista

    # Manejo de datos del formulario de registro
    if request.method == 'POST':
        # Obtiene los datos del formulario
        username = request.POST.get('username')
        password = request.POST.get('password') ###################
        repeat_password = request.POST.get('repeat_password') #################
        nombres = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        rut = request.POST.get('rut')
        telefono = request.POST.get('telefono')
        calle = request.POST.get('calle')
        numero = request.POST.get('numero')
        depto = request.POST.get('departamento', None)
        nombre_comuna = request.POST.get('comuna')

        # Se debe comprobar que las contraseñas coincidan, de lo contrario mensaje de error
        if password != repeat_password:
            error_message = 'Las contraseñas no coinciden.'
            return render(request, "registro.html", {'comunas': comunas, 'error_message': error_message})
        
        # Validar que el username no exista
        if nombre_usuario_existe(username):
            error_message = 'El nombre de usuario ya está en uso. Por favor, elija otro.'
            return render(request, "registro.html", {'comunas': comunas, 'error_message': error_message})
        
        try:
            # Crea el usuario, el cliente y la dirección asociada
            crear_cliente(username, password, rut, nombres, apellidos, email, telefono, calle, numero, depto, nombre_comuna)
            success_message = '¡Registro exitoso!'

            # Envía mensaje de éxito a la misma vista
            return render(request, "registro.html", {'comunas':comunas, 'success_message': success_message})
        except IntegrityError as e:
            # Para el caso de que se intente un registro de rut existente
            if 'duplicate key value violates unique constraint' in str(e):
                error_message = 'El Rut ingresado ya está registrado.'
            return render(request, "registro.html", {'comunas': comunas, 'error_message': error_message})
        except Exception as e:
            # Manejar de error de excepción
            return render(request, "registro.html", {'comunas': comunas, 'error_message': str(e)})
    return render(request, "registro.html", {'comunas': comunas}) # Inicialmente la vista es el form vación con comunas

# Vista de formulario de Inicio de Sesión
def inicio_sesion(request):
    if request.method == 'POST':
        # Obtiene los datos del formulario
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        usuario = obtener_usuario(username) # Obtiene el usuario

        if not usuario:
            return render(request, 'inicio_sesion.html', {'error_message': 'Usuario ingresado no existe'})

        # Autentica al usuario utilizando el username y la contraseña
        user = authenticate(request, username=usuario.username, password=password)
        
        # Si el usuario existe logea
        if user is not None:            
            login(request, user)

            # Verifica si usuario logeado es superuser
            if request.user.is_superuser:
                return redirect('dashboard_admin') # Redirige a dashboard de administrador 
            else:
                return redirect('dashboard') # Redirige a dashboard de cliente
            
            # Esta línea fue utilizada para comprobar el correcto inicio de sesión en la vista sin redirigir
            # return render(request, 'inicio_sesion.html', {'success_message': 'Sesión iniciada correctamente'})
        else:
            # Si el usuario no existe o las credenciales son incorrectas se pasa un mensaje de error al contexto
            return render(request, 'inicio_sesion.html', {'error_message': 'Credenciales inválidas'})
    else:
        return render(request, "inicio_sesion.html", {})  # Renderiza la página

@login_required
def dashboard(request):
    # Rescata el primer nombre del user, en caso de que tenga dos nombres, toma solo el primero
    nombre = obtener_primer_nombre_usuario(request.user).title()
    return render(request, "dashboard.html", {'nombre': nombre})

@login_required
def mascotas(request):
    # Obtiene el cliente y sus mascotas asociadas en base al user logeado
    mascotas = obtener_mascotas_cliente(request.user)
    # Si el cliente no tiene mascotas se pasa un mensaje adecuado para mostrar en la vista
    if not mascotas: 
        message = "No tienes mascotas registradas"
        return render(request, "mascotas.html", {'mascotas': mascotas, 'message': message})
    return render(request, "mascotas.html", {'mascotas': mascotas}) # Pasa como contexto las mascotas

@login_required
def registro_mascota(request):
    # El listado de ruts de clientes debe estar disponible, en caso de que el usuario sea el administrador
    listado_ruts = obtener_ruts_clientes()
    # Obtiene listado de todos los chips de mascotas ingresados
    listado_chips = obtener_listado_chips() 

    if request.method == 'POST':
        # Obtiene los datos del formulario
        rut = request.POST.get('rut', None)
        chip = request.POST.get('chip', None)
        nombre = request.POST.get('nombre')
        especie = request.POST.get('especie')
        raza = request.POST.get('raza')
        edad = request.POST.get('edad')
        sexo = request.POST.get('sexo')
        esterilizada_raw = request.POST.get('esterilizada')
        # print(f"Valor de esterilizada_raw: {esterilizada_raw}")  # Para depurar

        # Convierte esterilizada_raw (Sí|No) a un valor booleano
        esterilizada = True if esterilizada_raw == 'Sí' else False

        try:
            # Cuando la solicitud la realiza el administrador, verifica si el cliente ya registra la misma
            if request.user.is_superuser and mascota_existe_global(nombre, rut):
                error_message = 'Cliente registra una mascota con igual nombre'
                return render(request, "registro_mascota.html", {'error_message': error_message, 'listado_ruts': listado_ruts}) 
            # Si se trata de un cliente la verificación se hace en base al usuario logeado
            elif mascota_existe(request.user, nombre):
                error_message = 'Ya tienes una mascota registrada con este nombre'
                # Si ya existe la mascota que se intenta registrar, la acción no es posible
                return render(request, "registro_mascota.html", {'error_message': error_message})
            elif chip in listado_chips:
                error_message = 'El chip ingresado ya existe en los registros'
                return render(request, "registro_mascota.html", {'error_message': error_message})
            
            # Crea la mascota con los datos ingresados
            crear_mascota(nombre=nombre, especie=especie, edad=edad, sexo=sexo, raza=raza, esterilizada=esterilizada, usuario=request.user, chip=chip)
            success_message = '¡Registro exitoso!'
            # Envía mensaje de éxito a la misma vista
            return render(request, "registro_mascota.html", {'success_message': success_message})
        except Exception as e:
            return render(request, "registro_mascota.html", {'error_message': str(e)})

    return render(request, "registro_mascota.html", {'listado': listado_ruts})

@login_required
def vacunatorio(request):
    mascotas = obtener_mascotas_cliente(request.user) # Obtiene mascota cliente

    # Si no hay mascotas muestra mensaje
    if not mascotas:
        message = 'No tienes mascotas registradas'
        return render(request, "vacunas_mascota.html", {'message': message})

    # Toma el id de la mascota desde el formulario
    if request.method == "POST":
        mascota_id = request.POST.get('mascota')
        # Redirige a la siguiente vista con el submit pasando como parámetro el id de la mascota
        return redirect('vacunas_mascota', mascota_id=mascota_id)
    # El listado de mascotas del cliente es parte del contexto
    return render(request, "vacunatorio.html", {'mascotas' :mascotas})

@login_required
def vacunas_mascota(request, mascota_id):
    tipos_vacuna = obtener_tipos_vacuna_todos()
    vacunas = obtener_vacunas_mascotas(mascota_id)
    mascota = obtener_mascota(mascota_id)

    if not vacunas:
        message = 'No existen vacunas registradas'

        return render(request, "vacunas_mascota.html", {'message': message, 'mascota': mascota})

    # Ordena las vacunas por tipo y fecha, indicando la
    # próxima fecha de la última vacuna aplicada de cada tipo
    vacunas_por_tipo = {}
    for tipo in tipos_vacuna:
        vacunas_tipo = vacunas.filter(tipo=tipo).order_by('-fecha')
        if vacunas_tipo.exists():
            vacunas_por_tipo[tipo.tipo] = {
                'vacunas': vacunas_tipo,
                'proxima_fecha': vacunas_tipo.first().proxima_fecha
            }
    contexto = {
        'mascota': mascota,
        'vacunas_por_tipo': vacunas_por_tipo
    }
    # Renderiza la vista entregando la mascota al contexto y sus vacunas clasficadas
    return render(request, "vacunas_mascota.html", contexto)

# Vista de perfil de usuario
@login_required
def perfil_usuario(request):
    cliente = obtener_cliente(request.user) # Obtiene los datos del cliente logeado
    return render(request, "perfil_usuario.html", {"cliente": cliente}) # Retorna la vista y pasa el usuario al contexto

# Vista de edición de perfil
@login_required
def editar_usuario(request):
    comunas = listar_comunas_metropolitana() # Obtiene comunas de la región metropolitana
    cliente = obtener_cliente(request.user) # Obtiene los datos del cliente del usuario logeado

    if request.method == "POST":
        # Obtiene los datos del formulario
        rut = cliente.rut
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')

        # Actualiza dirección
        calle = request.POST.get('calle')
        numero = request.POST.get('numero')
        depto = request.POST.get('departamento', '')
        nombre_comuna = request.POST.get('comuna')
        
        
        try:
            # Edita la información del cliente
            actualizar_usuario(rut, nombres, apellidos, email, telefono, calle, numero, nombre_comuna, depto)
            success_message = '¡Datos actualizados correctamente!'
            # Retorna la vista con mensaje al contexto
            return render(request, "editar_usuario.html", {'comunas':comunas, 'success_message': success_message, 'cliente': cliente})
        except Exception as e:
            # Maneja excepción
            return render(request, "editar_usuario.html", {'comunas': comunas, 'error_message': str(e), 'cliente': cliente})
    return render(request, "editar_usuario.html", {'comunas': comunas, 'cliente': cliente}) # Retorna vista y contexto

@login_required
def citas_usuario(request):

    reservas = obtener_reservas_cliente(request.user) # Obtiene las reservas del cliente

    if request.method == 'POST':
        reserva_id = request.POST.get('reserva_id')
        action = request.POST.get('action')

        # Pendiente implementar el modificar
        if action == 'eliminar':
            eliminar_reserva(reserva_id) # Elimina reserva por id
            delete_message = "Reserva eliminada"
            reservas = obtener_reservas_cliente(request.user) # Obtiene las reservas del cliente

            # Si no existen reservas pasa un mensaje
            if not reservas:
                empty_message = "No tienes citas reservadas"
                return render(request, "agendamientos.html", {'reservas': reservas, 'empty_message': empty_message})
            return render(request, "agendamientos.html", {'reservas': reservas, 'delete_message': delete_message})

    # Si no existen reservas pasa un mensaje adecuado
    if not reservas:
        empty_message = "No tienes citas reservadas"
        return render(request, "agendamientos.html", {'reservas': reservas, 'empty_message': empty_message})
    return render(request, "agendamientos.html", {'reservas': reservas})

@login_required
def resenas_usuarios(request):

    if request.method == 'POST':
        comentario = request.POST.get('comentario')
        calificacion = request.POST.get('calificacion')

        crear_resena(request.user, comentario, calificacion) # Crea la reseña
        succes_message = 'Comentario posteado con éxito'

        resenas = listar_resenas() # Lista las reseñas existentes
        return render(request, "resenas.html", {'resenas': resenas, 'success_message': succes_message}) # Renderiza con las reseñas existentes

    resenas = listar_resenas() # Lista las reseñas existentes
    
    return render(request, "resenas.html", {'resenas': resenas}) # Renderiza con las reseñas existentes


##########################################################################################################################
############# Sesión de administrador o superusuario #####################################################################

@login_required
def dashboard_admin(request):
    return render(request, "dashboard_admin.html", {})

@login_required
def agenda(request):
    # Obtiene el término de búsqueda
    query = request.GET.get('filtro')
    horarios_disponibles = []
    message = None
    conteo = 0

    # Filtra los horarios disponibles y reservados basados en la búsqueda
    if query:
        # horarios_disponibles = obtener_horarios_disponibles_filtrados(query) Se necesitan?? Tal vez no.
        horarios_reservados = obtener_horarios_reservados_filtrados(query)
        # conteo = len(horarios_disponibles) + len(horarios_reservados)
        conteo = horarios_reservados.count()

        # if not horarios_disponibles.exists() and not horarios_reservados.exists():

        if not horarios_reservados.exists():
            message = 'No existen coincidencias en la búsqueda'

    # Si no hay una solicitud de búsqueda obtiene los horarios disponibles y reservados 
    else:
        horarios_disponibles = obtener_horarios_disponibles()
        horarios_reservados = obtener_horarios_reservados()

    # Lista de diccionarios que se pasará al contexto
    citas = []
    
    
    # Se añaden horarios disponibles
    for horario in horarios_disponibles:
        citas.append({
            'fecha': horario.fecha
        })
    
    # Se añaden horarios reservados con fecha, tipo, paciente y dueño
    for reserva in horarios_reservados:
        citas.append({
            'fecha': reserva.horario.fecha,
            'tipo': reserva.tipo.tipo,
            'paciente': reserva.mascota.nombre,
            'dueño': f"{reserva.mascota.cliente.usuario.first_name.split()[0]} {reserva.mascota.cliente.usuario.last_name.split()[0]}"
        })

    # Ordena citas por fecha y hora
    citas.sort(key=lambda x: x['fecha'])

    # Si hay conteo (Se solicitó búsqueda y hay coincidencias) 
    if conteo != 0:
        return render(request, "agenda.html", {
            'citas': citas,
            'conteo': conteo
        })    
    # Si hay mensaje (Se solicitó búsqueda pero no hay coincidencias)
    if message != None:
        return render(request, "agenda.html", {
            'citas': citas,
            'message': message
        })

    # No hay búsqueda
    return render(request, "agenda.html", {'citas': citas}) # Al contexto se pasa el conjunto de citas reservadas y no reservadas

@login_required
def reservar_hora(request):
    # Obtiene los tipos de cita que el usuario tiene permitido agendar
    tipos_cita = obtener_tipos_cita(request.user)
    horarios_disponibles = obtener_horarios_disponibles_sin_tope() # Horas disponibles para el agendamiento

    # Si es superusuario obtiene todas las mascotas
    if request.user.is_superuser:
        mascotas = obtener_mascotas()
    # Si es cliente obtiene las que le son propias
    else:
        mascotas = obtener_mascotas_cliente(request.user)

    # Si la lista está vacía entrega mensaje al contexto
    if not mascotas:
        error_message = 'No hay mascotas registradas'
        return render(request, "reservar_hora.html", {'error_message': error_message,
                                                      'mascotas':mascotas,                                                      
                                                      'tipos_cita': tipos_cita,
                                                      'horarios_disponibles': horarios_disponibles})    
    if request.method == 'POST':
        # Obtiene los datos del formulario
        mascota_id = request.POST.get('pet')
        tipo_id = request.POST.get('type')
        horario_id = request.POST.get('date')

        try:
            crear_reserva(tipo_id, horario_id, mascota_id)
            success_message = 'Reserva realizada con éxito'
            return render(request, "reservar_hora.html", {'success_message': success_message,
                                                          'mascotas': mascotas,
                                                          'tipos_cita': tipos_cita,
                                                          'horarios_disponibles': horarios_disponibles})
        # Maneja otro tipo de excepciones útiles en la etapa de testeo
        except Exception as e:
            error_message = str(e)
            return render(request, "reservar_hora.html", {'error_message': error_message,
                                                          'mascotas': mascotas,
                                                          'tipos_cita': tipos_cita,
                                                          'horarios_disponibles': horarios_disponibles})
    
    return render(request, "reservar_hora.html", {'mascotas': mascotas,
                                                  'tipos_cita': tipos_cita,
                                                  'horarios_disponibles': horarios_disponibles})

@login_required
def consulta(request):
    tipos_cita = obtener_tipos_cita(request.user)
    mascotas = obtener_mascotas()
    button = False

    if request.method == 'POST':
        # Si se trata de un post de consulta ya registrada redirige al registro de vacuna
        if ('consulta_id' and 'mascota_id') in request.POST:
            consulta_id = request.POST.get('consulta_id')            
            mascota_id = request.POST.get('mascota_id')        
            # Redirige a la vista de registro de vacuna con el id de consulta
            return redirect('registro_vacuna', consulta_id=consulta_id, mascota_id=mascota_id)
        
        # Obtiene los datos desde el formulario
        tipo_id = request.POST.get('tipo')
        mascota_id = request.POST.get('mascota')
        descripcion = request.POST.get('descripcion').capitalize()
        evaluacion = request.POST.get('evaluacion').capitalize()
        antecedentes = request.POST.get('antecedentes').capitalize()
        examen = request.POST.get('examen').capitalize()
        diagnostico = request.POST.get('diagnostico').capitalize()
        tratamiento = request.POST.get('tratamiento').capitalize()

        try:
            consulta = crear_consulta(tipo_id, mascota_id, descripcion, evaluacion, antecedentes, examen, diagnostico, tratamiento)
            consulta_id = consulta.id # Recoge el id de la consulta creada
            mascota_id = consulta.mascota.id # Recoge el de la mascota consultada
                        
            # Mensaje de éxito
            success_message = 'Consulta registrada exitosamente.'
            if int(tipo_id) == 2: # Si es vacuna cambia el booleano a True
                button = True
            return render(request, "consulta.html", {'mascotas': mascotas,
                                                     'consulta_id': consulta_id,
                                                     'mascota_id': mascota_id,
                                                     'tipos_cita': tipos_cita,
                                                     'success_message': success_message,
                                                     'button': button}) # Pasa un booleano para manipular la vista
        except Exception as e:
            error_message = str(e)
            return render(request, "consulta.html", {'mascotas': mascotas,
                                                     'tipos_cita': tipos_cita,
                                                     'error_message': error_message})
                
    return render(request, "consulta.html",{'mascotas': mascotas, 'tipos_cita': tipos_cita})

@login_required
def registro_vacuna(request, consulta_id, mascota_id):
    especie = obtener_especie_mascota(mascota_id) # Obtiene especie de la mascota
    # Obtiene tipos de vacunas para la especie
    tipos_vacuna = obtener_tipos_vacuna(especie)
    vacuna_registrada = verificar_vacuna_registrada(mascota_id, consulta_id) # Verificación para que la vacuna no sea registrada más de una vez 
    if request.method == 'POST':
        tipo_id = request.POST.get('type')        
        # Si la vacuna no ha sido registrada
        if not vacuna_registrada:
            try:
                vacuna = crear_vacuna(tipo_id, mascota_id, consulta_id)
                success_message = 'Vacuna registrada exitosamente.'
                vacuna_registrada = True # Cambia el estado a registrada con True                
                return render(request, "registro_vacuna.html", {
                    'tipos_vacuna': tipos_vacuna,
                    'success_message': success_message,
                    'vacuna_registrada': vacuna_registrada,
                    'vacuna': vacuna})        
            except Exception as e:
                error_message = str(e)
                return render(request, "registro_vacuna.html", {
                    'tipos_vacuna': tipos_vacuna,
                    'error_message': error_message,
                    'vacuna_registrada': vacuna_registrada})
        else:
            # Esta línea de código no debiese accederse puesto que el botón debiese estar deshabilitado
            error_message = 'La vacuna ya ha sido registrada para esta consulta y mascota'
            return render(request, "registro_vacuna.html", {'tipos_vacuna': tipos_vacuna,
                                                            'error_message': error_message,
                                                            'vacuna_registrada': vacuna_registrada})

    return render(request, "registro_vacuna.html", {'tipos_vacuna': tipos_vacuna, 'vacuna_registrada': vacuna_registrada})

# Vista de listado de clientes con buscador
@login_required
def clientes(request):
    query = request.GET.get('filtro')
    message = None

    if query:
        clientes = obtener_clientes_filtrados(query) # Obtiene listado de clientes según filtro de búsqueda
        conteo = clientes.count()  # Obtiene la cantidad de resultados

        # Si no se obtienen clientes en la búsqueda
        if not clientes.exists():
            message = 'No existen coincidencias en la búsqueda'
        return render(request, "clientes.html", {'clientes': clientes,
                                                 'message': message,
                                                 'conteo': conteo})
    else:
        clientes = obtener_clientes() # Llama al listado de clientes
    # Si no hay clientes registrados debería indicarlo
    if not clientes.exists():
        message = 'No hay clientes ingresados'
    return render(request, "clientes.html", {'clientes': clientes, 'message': message})

# Vista de listado de pacientes con buscador
@login_required
def pacientes(request):
    query = request.GET.get('filtro')
    message = None
    conteo = None

    if query:
        pacientes = obtener_pacientes_filtrados(query) # Obtiene listado de pacientes según filtro de búsqueda
        conteo = pacientes.count()  # Obtiene la cantidad de resultados

        # Si no se obtienen clientes en la búsqueda
        if not pacientes.exists():
            message = 'No existen coincidencias en la búsqueda'
        return render(request, "pacientes.html", {'pacientes': pacientes,
                                                 'message': message,
                                                 'conteo': conteo})
    else:
        pacientes = obtener_pacientes() # Llama al listado de pacientes
    # Si no hay pacientes registrados debería indicarlo
    if not pacientes.exists():
        message = 'No hay pacientes ingresados'

    return render(request, "pacientes.html", {'pacientes': pacientes, 'message': message, 'conteo': conteo})


##########################################################################################################################
############# Para cerrar sesión #########################################################################################
@login_required
def cerrar_sesion(request):
    logout(request) # Solicitud de cierre de sesión
    return redirect('inicio')  # Redirige a la página de inicio


#############################################################################################################
# No requieren login el formulario de contacto ##############################################################
#############################################################################################################
def formulario_contacto(request):
    if request.method == 'POST':
        nombres =  request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')

        guardar_formulario_contacto(nombres, apellidos, email, mensaje) # Guarda la información del formulario en la DB

        success_message = 'Hemos recibido su mensaje. Pronto le contactaremos'

        return render(request, "contacto.html", {'success_message': success_message})    
    return render(request, "contacto.html", {}) # Retorna la vista 

def suscripcion_newsletter(request):
    if request.method == 'POST':
        nombres =  request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        
        registrar_suscripcion(nombres, apellidos, email)

        success_message = '¡Listo! ¡Pronto recibirás nuestras noticias!'
        return render(request, "newsletter.html", {'success_message': success_message})

    return render(request, "newsletter.html", {})
