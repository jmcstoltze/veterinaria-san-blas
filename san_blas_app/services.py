from .models import Cliente, Consulta, Resena, Direccion, Comuna, Region
from .models import Mascota, Reserva, Horario, Vacuna, TipoVacuna, TipoCita
from .models import Contacto, Newsletter

from django.contrib.auth.models import User

from django.db.models import Q
from django.db import transaction

from django.utils.timezone import make_aware
from django.utils import timezone
from datetime import timedelta, datetime
from django.utils.dateparse import parse_date

from .utils import proxima_fecha_vacunacion # Funciones para calcular la fecha de vacunación
from .utils import utc_to_local


'''
CREATE


READ


UPDATE


DELETE


'''
#########################################################################################################################################
# Funciones del tipo Create #############################################################################################################

def crear_usuario(username, password, nombres, apellidos, email):
    # Crea un nuevo usuario
    usuario = User.objects.create_user(
        username=username,
        password=password,
        first_name=nombres,
        last_name=apellidos,
        email=email
    )
    # Guarda el usuario en la base de datos
    usuario.save()
    return usuario # Retorna el usuario creado

def crear_direccion(cliente, calle, numero, nombre_comuna, depto=None):
    # Busca la comuna por nombre
    nombre_comuna = nombre_comuna.title()
    comuna = Comuna.objects.get(nombre_comuna=nombre_comuna)

    # Crea la dirección con los datos proporcionados
    direccion = Direccion.objects.create(
        cliente=cliente,
        calle=calle,
        numero=numero,
        depto=depto,
        comuna=comuna
    )
    return direccion # Retorna la dirección creada

# Al emplear los tres métodos, lo realiza con una sola transación en la db
# Es decir, realiza un rollback si existe error en alguna de ellas
@transaction.atomic
def crear_cliente(username, password, rut, nombres, apellidos, email, telefono, calle, numero, depto, nombre_comuna):
    # Crea el usuario
    usuario = crear_usuario(username, password, nombres, apellidos, email)

    # Crea el cliente asociado al usuario y dirección
    cliente = Cliente.objects.create(
        usuario=usuario,
        rut=rut,
        telefono=telefono,
    )
    # Crea la dirección del cliente
    crear_direccion(cliente, calle, numero, nombre_comuna, depto)
    return cliente  # Retorna el cliente creado

def crear_mascota(nombre, especie, edad, sexo, raza, esterilizada, usuario, chip=None):
    # Obtiene el cliente asociado al usuario
    cliente = Cliente.objects.get(usuario=usuario)

    # Si el chip es una cadena vacía, se establece como None
    # if chip == "":
        # chip = None

    # Si el chip es una cadena vacía o solo espacios en blanco, se establece como None
    if chip and not chip.strip():
        chip = None

    # Crea la mascota asociada al cliente
    mascota = Mascota.objects.create(
        chip=chip,
        nombre=nombre.title(),
        especie=especie,
        edad=edad,
        sexo=sexo,
        raza=raza.capitalize(),
        esterilizada=esterilizada,
        cliente=cliente
    )
    return mascota  # Retorna la mascota creada

def crear_mascota_rut_cliente(nombre, especie, edad, sexo, raza, esterilizada, rut, chip):
    #Obtiene el cliente asociado al rut de cliente
    cliente = Cliente.objects.get(rut=rut)
    print(rut)
    print(cliente)
    # Crea la mascota asociada al cliente
    mascota = Mascota.objects.create(
        chip=chip,
        nombre=nombre.title(),
        especie=especie,
        edad=edad,
        sexo=sexo,
        raza=raza.capitalize(),
        esterilizada=esterilizada,
        cliente=cliente
    )
    return mascota  # Retorna la mascota creada

''' PARA DEPURACIÓN DE ERROR
def crear_mascota_rut_cliente(nombre, especie, edad, sexo, raza, esterilizada, rut, chip):
    try:
        # Obtiene el cliente asociado al rut de cliente
        cliente = Cliente.objects.get(rut=rut)
        # print(f"RUT: {rut}")
        # print(f"Cliente encontrado: {cliente}") #### Mensajes de depuración
        
        # Crea la mascota asociada al cliente
        mascota = Mascota.objects.create(
            chip=chip,
            nombre=nombre.title(),
            especie=especie,
            edad=edad,
            sexo=sexo,
            raza=raza.capitalize(),
            esterilizada=esterilizada,
            cliente=cliente
        )
        return mascota  # Retorna la mascota creada
    except Cliente.DoesNotExist:
        print(f"Cliente con RUT {rut} no encontrado.")
        return None  # O una lógica alternativa en caso de que el cliente no exista
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return None  # O manejar el error de otra manera adecuada '''

def crear_reserva(tipo_id, horario_id, mascota_id):
    # Obtiene el tipo de cita, el horario y la mascota
    tipo_cita = TipoCita.objects.get(pk=tipo_id)
    horario = Horario.objects.get(pk=horario_id)
    mascota = Mascota.objects.get(pk=mascota_id)

    # Cambia el estado de horario a no disponible
    horario.disponible = False
    horario.save()

    # Crea la reserva
    reserva = Reserva.objects.create(
        tipo=tipo_cita,
        horario=horario,
        mascota=mascota
    )    
    # Devuelve la reserva creada
    return reserva

def crear_consulta(tipo_id, mascota_id, descripcion, evaluacion, antecedentes, examen, diagnostico, tratamiento):

    # Obtiene los objetos relacionados con clave foránea
    tipo_cita = TipoCita.objects.get(pk=tipo_id)
    mascota = Mascota.objects.get(pk=mascota_id)    

    # Crea la consulta
    consulta = Consulta.objects.create(
        tipo=tipo_cita,
        mascota=mascota,
        descripcion=descripcion,
        evaluacion=evaluacion,
        antecedentes=antecedentes,
        examen=examen,
        diagnostico=diagnostico,
        tratamiento=tratamiento
    )
    return consulta # Devuelve la consulta creada

def crear_vacuna(tipo_id, mascota_id, consulta_id):
    # Obtener instancias tipo, mascota y consulta
    tipo_vacuna = TipoVacuna.objects.get(pk=tipo_id)
    mascota = Mascota.objects.get(pk=mascota_id)
    consulta = Consulta.objects.get(pk=consulta_id)

    # Crea la vacuna y la guarda
    vacuna = Vacuna(tipo=tipo_vacuna, mascota=mascota, consulta=consulta)
    vacuna.save()

    # Calcula y actualiza la próxima fecha de vacunación
    vacuna.proxima_fecha = proxima_fecha_vacunacion(vacuna)

    if vacuna.proxima_fecha is None:
        print('no se está generando la próxima fecha') # Para efectos de testeo

    vacuna.save()  # Guarda la vacuna con la próxima fecha actualizada
    return vacuna # Retorna la vacuna creada

def crear_resena(user, comentario, calificacion):
    # Se crea un objeto reseña y se almacena en la DB
    nueva_resena = Resena (
        usuario = user,
        comentario = comentario,
        calificacion = calificacion
    )
    nueva_resena.save()
    return nueva_resena

def guardar_formulario_contacto(nombres, apellidos, email, mensaje):
    nuevo_contacto = Contacto (
        nombres = nombres,
        apellidos = apellidos,
        email = email,
        mensaje = mensaje
    )
    nuevo_contacto.save() # Guarda la información en la DB
    return nuevo_contacto

def registrar_suscripcion(nombres, apellidos, email):
    nueva_suscripcion = Newsletter (
        nombres = nombres,
        apellidos = apellidos,
        email = email
    )
    nueva_suscripcion.save()
    return nueva_suscripcion
    

##########################################################################
# Funciones del tipo Read (listar y buscar) ##############################

def listar_comunas_metropolitana():
    region_metropolitana = Region.objects.get(id=13) # Obtiene la región metropolitana
    comunas_metropolitana = Comuna.objects.filter(region=region_metropolitana)
    return comunas_metropolitana # Devuelve sólo las comunas de la region metropolitana para efectos del prototipo

def nombre_usuario_existe(username):
    # Verifica que el nombre de usuario ya se utilizó
    return User.objects.filter(username=username).exists() # Retorna True si el username existe

def obtener_usuario(username):
    # Obtiene el usuario mediante el username
    try:
        user = User.objects.get(username=username)
        return user # Retorna el usuario
    except User.DoesNotExist:
        return None

def obtener_usuario_rut(rut):
    cliente = Cliente.objects.get(rut=rut)
    return cliente.usuario

def obtener_cliente(user):
    try:
        cliente = Cliente.objects.get(usuario=user) # Obtiene cliente en base al usuario
        return cliente # Retorna cliente
    except Cliente.DoesNotExist:
        return None
    
def obtener_cliente_por_id(id):
    return Cliente.objects.get(id=id) # Retorna cliente de id específico

# Obtiene todos lo clientes almacenados
def obtener_clientes():
    clientes = Cliente.objects.all()
    return clientes # Retorna todos los clientes de la db

# Obtener clientes según filtro
def obtener_clientes_filtrados(query):
    return Cliente.objects.filter(
            Q(usuario__first_name__icontains=query) | 
            Q(usuario__last_name__icontains=query) |
            Q(usuario__email__icontains=query)
        )

# Obtiene todos lo pacientes almacenados
def obtener_pacientes():
    pacientes = Mascota.objects.all()
    return pacientes # Retorna todos los clientes de la db

# Obtiene paciente por id
def obtener_paciente(id):
    return Mascota.objects.get(id=id) # Retorna paciente de determinado id

# Obtener paciente según filtro
def obtener_pacientes_filtrados(query):
    return Mascota.objects.filter(Q(nombre__icontains=query))


def buscar_cliente(consulta):
    # Divide la consulta en palabras clave
    terminos = consulta.split()

    # Inicializa un objeto de consulta con todos los clientes
    clientes = Cliente.objects.all()

    # Filtra por cada término de búsqueda
    for term in terminos:
        # Filtra por coincidencias parciales en first_name o last_name
        clientes = clientes.filter(
            Q(usuario__first_name__icontains=term) | Q(usuario__last_name__icontains=term)
        )
    # Elimina registros duplicados
    clientes = clientes.distinct()
    return clientes # Retorna ninguno, uno o más clientes
    
def obtener_reservas_cliente(user):
    cliente = Cliente.objects.get(usuario=user) # Obtiene cliente
    hoy = timezone.now().date() # Obtiene fecha actual
    reservas = Reserva.objects.filter(mascota__cliente=cliente, horario__fecha__gte=hoy) # Obtiene cliente
    return reservas # Retorna reservas del cliente
    
def obtener_primer_nombre_usuario(user):
    # Rescata el primer nombre del user, en caso de que tenga dos nombres, toma solo el primero
    return user.first_name.split()[0] if user.first_name else ""

def obtener_ruts_clientes():
    clientes = Cliente.objects.all()
    listado_rut = [cliente.rut for cliente in clientes]
    return listado_rut # Retorna un listado de ruts de todos los clientes

def obtener_mascotas_cliente(user):
    # Obtiene el cliente asociado el user
    cliente = Cliente.objects.get(usuario=user)
    mascotas = Mascota.objects.filter(cliente=cliente) # El parámetro de búsqueda es el cliente
    return mascotas # Retorna un listado de mascotas o None

def obtener_mascotas():
    return Mascota.objects.all() # Retorna todas las mascotas

def obtener_mascota(id):
    return Mascota.objects.get(id=id) # Retorna mascota de un id específico

''' Se comenta para manejo de excepción ---------------------------------------
def mascota_existe(user, nombre_mascota):
    cliente = Cliente.objects.get(usuario=user)
    nombre_mascota = nombre_mascota.title()
    return Mascota.objects.filter(cliente=cliente, nombre=nombre_mascota).exists() # True si la mascota existe '''

# Esta función se creó porque la original arrojaba error con el superusuario.
def mascota_existe(user, nombre):
    try:
        cliente = Cliente.objects.get(usuario=user)
        nombre_mascota = nombre.title()
        return Mascota.objects.filter(cliente=cliente, nombre=nombre_mascota).exists() # True si la mascota existe
    except Cliente.DoesNotExist:
        return False # Al ser superusuario arroja que el cliente no existe, puesto que superusuario no tiene cliente asociado

def mascota_existe_global(nombre_mascota, rut_cliente):
    cliente = Cliente.objects.get(rut=rut_cliente)
    # Verifica si la mascota existe para un usuario específico
    return Mascota.objects.filter(cliente=cliente, nombre=nombre_mascota).exists()

def obtener_listado_chips():
    return Mascota.objects.values_list('chip', flat=True) # Retorna un listado de chips existentes

def obtener_horarios_disponibles():
    ahora = timezone.now()
    ahora_menos_media_hora = ahora - timedelta(minutes=30)

    # Define el rango de fechas para los próximos días
    fecha_inicio = ahora.date()
    fecha_fin = ahora.date() + timedelta(days=2)  # Incluye mañana y pasado mañana

    horarios_disponibles = Horario.objects.filter(
        #fecha__date=ahora.date(), # Fecha del día actual
        fecha__date__range=(fecha_inicio, fecha_fin),  # Fecha entre hoy y pasado mañana
        fecha__gt=ahora_menos_media_hora, # Menor al tiempo - 30 minutos | margen de error
        disponible=True # Horarios disponibles
    )
    # Retorna todos los horarios disponibles de la fecha actual y dos días más a partir de 30 minutos atrás máximo
    return horarios_disponibles

def obtener_horarios_disponibles_sin_tope():
    ahora = timezone.now()
    horarios_disponibles = Horario.objects.filter(
        fecha__gte=ahora,  # Fecha igual o posterior a la fecha y hora actual
        disponible=True  # Horarios disponibles
    )
    # Retorna todos los horarios disponibles desde la fecha y hora actual
    return horarios_disponibles

# Obtiene horarios disponibles para una fecha determinada
def obtener_horarios_disponibles_filtrados(query):    
    # Intentar parsear la fecha del query
    fecha = parse_date(query)
    # Si no es una fecha la búsqueda retorna un queryset vacío
    if not fecha:
        return Horario.objects.none()
    # Ajusta fecha para incluir el rango completo del día
    start_date = make_aware(datetime.combine(fecha, datetime.min.time()))
    end_date = make_aware(datetime.combine(fecha, datetime.max.time()))

    # Filtra reservas por rango de fechas y obtiene los horarios asociados
    reservas_filtradas = Reserva.objects.filter(horario__fecha__range=(start_date, end_date))
    horarios = Horario.objects.filter(id__in=reservas_filtradas.values_list('horario_id', flat=True))    

    return horarios # Retorna los horarios de la fecha específica

# Obtiene las reservas asociadas a horarios reservados
def obtener_horarios_reservados():
    ahora = timezone.now()
    ahora_menos_media_hora = ahora - timedelta(minutes=30)

    # Horarios del mismo día con rango de 30 minutos
    horarios_reservados_hoy = Horario.objects.filter(
        fecha__date=ahora.date(), # Fecha del día actual
        fecha__gt=ahora_menos_media_hora, # 30 minutos atrás máximo
        disponible=False # Horarios no disponibles
    )

    # Horarios reservados para mañana y pasado mañana
    fecha_inicio = ahora.date() + timedelta(days=1)  # Mañana
    fecha_fin = ahora.date() + timedelta(days=2)  # Pasado mañana

    horarios_reservados_futuros = Horario.objects.filter(
        fecha__date__range=(fecha_inicio, fecha_fin),  # Fechas de mañana y pasado mañana
        disponible=False  # Horarios no disponibles o reservados
    )

    # Combina los resultados
    horarios_reservados = horarios_reservados_hoy | horarios_reservados_futuros

     # Retorna las reservas asociadas a los horarios reservados de hoy, mañana y pasado
    return Reserva.objects.filter(horario__in=horarios_reservados)

# Obtiene los horarios reservados por filtro de búsqueda
def obtener_horarios_reservados_filtrados(query):
    # Intenta parsear la fecha del query
    fecha = parse_date(query)
    
    # Si el filtro es una fecha
    if fecha:
        # Ajusta fecha para incluir el rango completo del día
        start_date = make_aware(datetime.combine(fecha, datetime.min.time()))
        end_date = make_aware(datetime.combine(fecha, datetime.max.time()))
        
        # Filtra por rango de fechas si query es una fecha
        return Reserva.objects.filter(
            horario__fecha__range=(start_date, end_date)
        )
    # Si el filtro no es una fecha (nombre de mascota o nombre de cliente)
    else:
        # Filtra por nombre de mascota o cliente si query no es una fecha
        return Reserva.objects.filter(
            Q(mascota__nombre__icontains=query) |
            Q(mascota__cliente__usuario__first_name__icontains=query) |
            Q(mascota__cliente__usuario__last_name__icontains=query)
        )

def obtener_tipos_cita(user):
    if user.is_superuser:
        return TipoCita.objects.all() # Retorna todos los tipos para superusuario
    else:
        # Retorna tipos filtrados para el usuario normal
        return TipoCita.objects.exclude(tipo__in=['cirugía esterilización', 'cirugía tumor menor'])
    
def obtener_especie_mascota(id):
    mascota = Mascota.objects.get(id=id)
    return mascota.especie # De acuerdo con id obtiene especie de la mascota

def obtener_tipos_vacuna(especie):
    if especie == 'Canina':
        return TipoVacuna.objects.filter(tipo__in=['Óctuple', 'Antirrábica', 'KC']) # Retorna vacunas para perros
    elif especie == 'Felina':
        return TipoVacuna.objects.filter(tipo__in=['Triple felina', 'Leucemia felina', 'Antirrábica']) # Retorna vacunas para gatos
    
def obtener_tipos_vacuna_todos():
    return TipoVacuna.objects.all() # Retorna todos los tipos de vacunas
    
def verificar_vacuna_registrada(mascota_id, consulta_id):
    return Vacuna.objects.filter(mascota_id=mascota_id, consulta_id=consulta_id).exists() # Retorna booleano si la vacuna ya se registró
    
def obtener_vacunas_mascotas(mascota_id):
    mascota = Mascota.objects.get(id=mascota_id)
    return Vacuna.objects.filter(mascota=mascota) # Retorna las vacunas de la mascota, según id o None

def listar_resenas():
    # Obtiene todas las reseñas
    resenas = Resena.objects.all()
    return resenas # Retorna los objetos


#########################################################################################################################
# Funciones del tipo Update #############################################################################################
#########################################################################################################################

def actualizar_usuario(rut, nombres, apellidos, email, telefono, calle, numero, nombre_comuna, depto=None):
    # Obtiene el cliente con el rut
    cliente = Cliente.objects.get(rut=rut)
    # Actualiza los campos del cliente y usuario
    cliente.usuario.first_name = nombres
    cliente.usuario.last_name = apellidos
    cliente.usuario.email = email
    cliente.telefono = telefono
    # Guarda los cambios
    cliente.usuario.save()
    cliente.save()
    # Actualiza los campos de la dirección del cliente
    direccion = cliente.direccion # LLama a la dirección del cliente
    direccion.calle = calle
    direccion.numero = numero
    direccion.depto = depto if depto is not None else ''
    # Obtiene la comuna con el id
    comuna = Comuna.objects.get(nombre_comuna=nombre_comuna)
    direccion.comuna = comuna # Setea la comuna en la dirección
    direccion.save() # Guarda los cambios de la dirección
    return cliente # Retorna el cliente

'''
# Vuelve a disponibilizar un horario
def disponibilizar_horario(id):
    horario = Horario.objects.get(id=id)
    horario.disponible = True '''

##########################################################################################################################
# Funciones del tipo Delete ##############################################################################################
##########################################################################################################################

# Elimina reserva
def eliminar_reserva(reserva_id):
    reserva = Reserva.objects.get(id=reserva_id)
    horario = reserva.horario
    horario.disponible = True  # Cambia el horario a disponible
    horario.save()  # Guarda el horario actualizado
    reserva.delete() # Elimina la reserva invocada

# Elimina paciente y toda su información asociada
def eliminar_paciente(id):

    # Obtiene la mascota que se va a eliminar
    mascota = Mascota.objects.get(id=id)

    # Si no se logra la acción se hace un rollback de todo
    with transaction.atomic():
    
        # Obtiene las consultas y las reservas asociadas a la mascota
        consultas = Consulta.objects.filter(mascota=mascota)
        reservas = Reserva.objects.filter(mascota=mascota)
    
        # Elimina todas las vacunas asociadas a las consultas de la mascota
        Vacuna.objects.filter(consulta__in=consultas).delete()
        # Elimina las consultas
        consultas.delete()
    
        # Disponibiliza todos los horarios asociados a las reservas
        horarios = Horario.objects.filter(reserva__in=reservas)
        horarios.update(disponible=True)
        # Elimina las reservas
        reservas.delete()
    
        # Elimina la mascota
        mascota.delete()

# Elimina cliente y toda su información asociada
def eliminar_cliente(id):
    # Obtiene el cliente que se va a eliminar
    cliente = Cliente.objects.get(id=id)
    direccion = Direccion.objects.get(cliente=cliente)

    # Se obtienen las reseñas del usuario
    resenas = Resena.objects.filter(usuario=cliente.usuario)
    resenas.delete()

    # Obtiene las mascotas del cliente
    mascotas = Mascota.objects.filter(cliente=cliente)

    # Si no se logra la acción se hace un rollback de todo
    # with transaction.atomic():
    
    for mascota in mascotas:
        consultas = Consulta.objects.filter(mascota=mascota)
        reservas = Reserva.objects.filter(mascota=mascota)
        # Elimina todas las vacunas asociadas a las consultas de la mascota
        Vacuna.objects.filter(consulta__in=consultas).delete()
        # Elimina las consultas
        consultas.delete()
        # Disponibiliza todos los horarios asociados a las reservas
        horarios = Horario.objects.filter(reserva__in=reservas)
        horarios.update(disponible=True)
        # Elimina las reservas
        reservas.delete()
        # Elimina el cliente
        mascota.delete()

    # Elimina la dirección y el cliente
    direccion.delete()    
    cliente.delete()
    # Elimina el usuario asociado al cliente
    cliente.usuario.delete()
