from .models import Cliente, Consulta, Resena, Direccion, Comuna, Region
from .models import Mascota, Reserva, Horario, Vacuna, TipoVacuna, TipoCita
from .models import Contacto

from django.contrib.auth.models import User

from django.db.models import Q
from django.db import transaction

from django.utils import timezone
from datetime import timedelta

from .utils import proxima_fecha_vacunacion # Funciones para calcular la fecha de vacunación


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
        print('no se está generando la próxima fecha')

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
    
def obtener_cliente(user):
    try:
        cliente = Cliente.objects.get(usuario=user) # Obtiene cliente en base al usuario
        return cliente # Retorna cliente
    except Cliente.DoesNotExist:
        return None
    
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

def mascota_existe(user, nombre_mascota):
    cliente = Cliente.objects.get(usuario=user)
    nombre_mascota = nombre_mascota.title()
    return Mascota.objects.filter(cliente=cliente, nombre=nombre_mascota).exists() # True si la mascota existe

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

def obtener_tipos_cita(user):
    if user.is_superuser:
        return TipoCita.objects.all() # Retorna todos los tipos para superusuario
    else:
        # Retorna tipos filtrados para el usuario normal
        return TipoCita.objects.exclude(tipo__in=['cirugía esterilización', 'cirugía tumor menor'])
    
def obtener_tipos_vacuna():
    return TipoVacuna.objects.all() # Retorna los tipos de vacunas
    
def obtener_vacunas_mascotas(mascota_id):
    mascota = Mascota.objects.get(id=mascota_id)
    return Vacuna.objects.filter(mascota=mascota) # Retorna las vacunas de la mascota, según id o None

def listar_resenas():
    # Obtiene todas las reseñas
    resenas = Resena.objects.all()
    return resenas # Retorna los objetos

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

#########################################################################################################################
# Funciones del tipo Update #############################################################################################

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

# Elimina reserva
def eliminar_reserva(reserva_id):
    reserva = Reserva.objects.get(id=reserva_id)
    
    horario = reserva.horario
    horario.disponible = True  # Cambia el horario a disponible
    
    horario.save()  # Guarda el horario actualizado
    reserva.delete() # Elimina la reserva invocada
