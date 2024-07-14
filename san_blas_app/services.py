from .models import Cliente, Mascota, Consulta, Resena, Direccion, Comuna, Region, TipoCita, Horario, Reserva, Vacuna, TipoVacuna
from django.contrib.auth.models import User

from django.db.models import Q
from django.db import transaction

from django.utils import timezone
from datetime import timedelta

from .utils import proxima_fecha_vacunacion


'''
Métodos necesarios para implementar las funcionalidades de la aplicación:

CREATE
- Registrar cliente: el usuario debe poder registrarse a sí mismo y el administrador debe poder crear un cliente o usuario
- Para crear un cliente debe crearse un usuario y también una direción. El orden sería: 1. Crear el User, 2. Crear el cliente, 3. Crear la dirección

- Cliente o administrador deben poder crear una mascota o paciente.
- Se manejará por separado: crear mascota y crear paciente. Esto debido a que el cliente siempre estará logeado, en cambio, si lo creao el admin, debe manejarse la excepción de que el usuario o cliente no exista.
- Hay que asegurarse que la función crear mascota reciba como parámetro el usuario con sessión iniciada desde views.py
- Para crear paciente debemos asegurarnos de que la vista tenga un selector que despliegue todo los ruts de los clientes.

- Función para crear una reserva, recibiendo como parámetro el tipo, el horario y la mascota

- Función para crear una vacuna a partir del id de consulta, de mascota y de  tipo de vacuna
----- proxima fecha

READ
- Buscar cliente o clientes: esta función debe retornar un lista de clientes que puede estar vacía o contener uno o más usuario. El parámetro de la búsqueda puede ser el nombre, el apellido, utilizando coincidencias parciales.

- Función para leer los comentarios o reseñas desde la db y desplegarlos en la vista que corresponda
- Función para leer todas la comunas DE LA REGIÓN METROPOLITANA que se cargarán en los selectores de las vistas
- Métodos para validar usuarios y obtener usuarios

- Método para obtener un listado de mascotas de un cliente o usuario
- Método que retorne el primer nombre de un usuario (en caso de que tenga dos nombre, entregar solo el primero)
- Se necesita obtener los rut de los clientes

- Se necesita saber si una mascota existe a partir del su nombre y del cliente/usuario asociado a la mascota
- Se necesita saber si una mascota existe en el contexto global, cuando es el administrador quien registra
- Se debe verificar que el chip ingresado no exista en el global

- Se necesita obtener los horarios disponibles, tanto reservado, como no reservados para mostrarlos en forma de agenda.
- También obtener todas las reservas

- Se requiere obtener mascotas según cliente (usuario)
- Se requiere obtener todas las mascotas

- Se requiere obtener los tipos de citas médicas que existen

- Se requiere lista las vacunas de una mascota. El parámetro es el id de la mascota
- Función para obtener una mascota según id


DELETE


'''

# Funciones del tipo Create #########################################

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

''' Es idéntica a la función anterior
def crear_paciente(nombre, especie, edad, sexo, raza, esterilizada, rut, chip=None):
    # Obtiene el cliente asociado al rut
    cliente = Cliente.objects.get(rut=rut)
        
    # Crea la mascota asociada al cliente
    mascota = Mascota.objects.create(
        chip=chip,
        nombre=nombre,
        especie=especie,
        edad=edad,
        sexo=sexo,
        raza=raza,
        esterilizada=esterilizada,
        cliente=cliente
    )        
    return mascota  # Retorna la mascota creada '''

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
    horarios_disponibles = Horario.objects.filter(
        fecha__date=ahora.date(), # Fecha del día actual
        fecha__gt=ahora_menos_media_hora, # Menor al tiempo - 30 minutos | margen de error
        disponible=True # Horarios disponibles
    )
    # Retorna todos los horarios disponibles de la fecha actual a partir de 30 minutos atrás máximo
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
    horarios_reservados = Horario.objects.filter(
        fecha__date=ahora.date(), # Fecha del día actual
        fecha__gt=ahora_menos_media_hora, # 30 minutos atrás máximo
        disponible=False # Horarios no disponibles
    )
    # Retorna todos los horarios reservados filtrados por fecha y hora
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

# Funciones del tipo Update

def editar_usuario():  # Pendiente de implementación
    pass

# Funciones del tipo Delete


