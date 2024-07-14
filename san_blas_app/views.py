from django.db import IntegrityError
from django.db.models import DateField
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from san_blas_app.services import crear_cliente, crear_mascota, crear_reserva, crear_consulta, crear_vacuna
from san_blas_app.services import listar_resenas, listar_comunas_metropolitana
from san_blas_app.services import nombre_usuario_existe, mascota_existe, mascota_existe_global, obtener_listado_chips
from san_blas_app.services import obtener_usuario,obtener_primer_nombre_usuario, obtener_ruts_clientes
from san_blas_app.services import obtener_horarios_disponibles, obtener_horarios_reservados, obtener_horarios_disponibles_sin_tope
from san_blas_app.services import obtener_mascotas_cliente, obtener_mascotas,obtener_mascota
from san_blas_app.services import obtener_tipos_cita, obtener_tipos_vacuna, obtener_vacunas_mascotas

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

        # Convierte esterilizada_raw (Sí|No) a un valor booleano
        esterilizada = True if esterilizada_raw == 'Sí' else False

        try:
            # Cuando la solicitud la realiza el administrador, verifica si el cliente ya registra la misma
            if request.user.is_superuser and mascota_existe_global(nombre, rut):
                error_message = 'Cliente registra una mascota con igual nombre'
                return render(request, "registro_mascota.html", {'error_message': error_message, 'listado_ruts': listado_ruts}) 
            # Si se trata de un cliente la verificación se hace en base al usuario logeado
            elif mascota_existe(request.user, nombre):
                error_message = 'Ya existe una mascota registrada con este nombre'
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

############# Sesión de administrador o superusuario #####################

@login_required
def dashboard_admin(request):
    return render(request, "dashboard_admin.html", {})

@login_required
def agenda(request):
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
        descripcion = request.POST.get('descripcion')
        evaluacion = request.POST.get('evaluacion')
        antecedentes = request.POST.get('antecedentes')
        examen = request.POST.get('examen')
        diagnostico = request.POST.get('diagnostico')
        tratamiento = request.POST.get('tratamiento')

        try:
            consulta = crear_consulta(tipo_id, mascota_id, descripcion, evaluacion, antecedentes, examen, diagnostico, tratamiento)
            consulta_id = consulta.id # Recoge el id de la consulta creada
            mascota_id = consulta.mascota.id # Recoge el de la mascota consultada
                        
            # Mensaje de éxito
            success_message = 'Consulta registrada correctamente.'
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
    # Obtiene tipos de vacunas
    tipos_vacuna = obtener_tipos_vacuna()

    if request.method == 'POST':
        tipo_id = request.POST.get('type')
        try:
            crear_vacuna(tipo_id, mascota_id, consulta_id)
            success_message = 'Vacuna registrada correctamente.'
            return render(request, "registro_vacuna.html", {'tipos_vacuna': tipos_vacuna,
                                                            'success_message': success_message})        
        except Exception as e:
            error_message = str(e)
            return render(request, "registro_vacuna.html", {'tipos_vacuna': tipos_vacuna,
                                                            'error_message': error_message})

    return render(request, "registro_vacuna.html", {'tipos_vacuna': tipos_vacuna})

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
    tipos_vacuna = obtener_tipos_vacuna()
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

############# Para cerrar la sesión ####################################################################
@login_required
def cerrar_sesion(request):
    logout(request) # Solicitud de cierre de sesión
    return redirect('inicio')  # Redirige a la página de inicio

