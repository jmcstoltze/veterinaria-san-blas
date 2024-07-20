from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
###################################################################################

# La clase cliente se complementa con el usuario por defecto de Django, 
# que incluye [username, password, first_name, last_name e email]
class Cliente(models.Model):
    # Relación 1:1 con auth_user
    usuario = models.OneToOneField(User, on_delete=models.PROTECT) # No se pude eliminar User sin eliminar Cliente
    rut = models.CharField(max_length=10, null=False, blank=False, unique=True)
    telefono = models.CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return f"{self.rut} - {self.usuario.last_name} - {self.usuario.first_name}"
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["rut", "usuario__last_name", "usuario__first_name"]

class Region(models.Model):
    nombre_region = models.CharField(max_length=80, null=False, blank=False)

    def __str__(self):
        return self.nombre_region
    
    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regiones"
        ordering = ["nombre_region"]

class Comuna(models.Model):
    nombre_comuna = models.CharField(max_length=80, null=False, blank=False)
    region = models.ForeignKey(Region, null=False, blank=False, on_delete=models.PROTECT) # No se puede eliminar región sin eliminar las comunas asociadas

    def __str__(self):
        return self.nombre_comuna
    
    class Meta:
        verbose_name = "Comuna"
        verbose_name_plural = "Comunas"
        ordering = ["nombre_comuna"]

class Direccion(models.Model):
    # Relación 1:1 con cada Cliente
    cliente = models.OneToOneField(Cliente, on_delete=models.PROTECT) # No se puede eliminar cliente sin eliminar su dirección previamente
    calle = models.CharField(max_length=80, null=False, blank=False)
    numero = models.CharField(max_length=20, null=False, blank=False)
    depto = models.CharField(max_length=20, null=True, blank=True)
    comuna = models.ForeignKey(Comuna, null=False, blank=False, on_delete=models.PROTECT) # No se puede eliminar comuna sin eliminar las direcciones asociadas a la misma

    def __str__(self):
        if self.depto:        
            return f"{self.calle}, {self.numero}, {self.depto}, {self.comuna}, {self.comuna.region.nombre_region}"
        else:        
            return f"{self.calle}, {self.numero}, {self.comuna}, {self.comuna.region.nombre_region}"

    class Meta:
        verbose_name = "Direccion"
        verbose_name_plural = "Direcciones"
        ordering = ["comuna"]

class Mascota(models.Model):
    ESPECIE_CHOICES = [
        ('felina', 'Felina'),
        ('canina', 'Canina'),
    ]
    SEXO_CHOICES = [
        ('macho', 'Macho'),
        ('hembra', 'Hembra'),
    ]

    chip = models.CharField(max_length=20, null=False, blank=False, unique=True)
    nombre = models.CharField(max_length=80, null=False, blank=False)
    especie = models.CharField(max_length=10, choices=ESPECIE_CHOICES, null=False, blank=False)
    edad = models.IntegerField(null=False, blank=False)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, null=False, blank=False)
    raza = models.CharField(max_length=20, null=False, blank=False)
    esterilizada = models.BooleanField(default=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT) # No se puede eliminar cliente sin eliminar primero las mascotas 

    def __str__(self):
        return f"{self.nombre} ({self.especie}) | Cliente: {self.cliente.rut} - {self.cliente.usuario.last_name}, {self.cliente.usuario.first_name}"

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ["nombre"]

class TipoCita(models.Model):
    TIPO_CHOICES = [
        ('general', 'General'),
        ('vacuna', 'Vacuna'),
        ('preventiva', 'Preventiva'),
        ('cirugía esterilización', 'Cirugía esterilización'),
        ('cirugía tumor menor', 'Cirugía tumor menor'),
        ('certificado', 'Certificado'),
        ('destartraje', 'Destartraje'),
        ('tratamiento/curación', 'Tratamiento/curación')
    ]

    tipo = models.CharField(max_length=60, choices=TIPO_CHOICES, null=False, blank=False)
    
    def __str__(self):
        return self.tipo

    class Meta:
        verbose_name = "Tipo de cita"
        verbose_name_plural = "Tipos de citas"
        ordering = ["tipo"]

class Consulta(models.Model):

    fecha = models.DateTimeField(default=timezone.now) 
    descripcion = models.CharField(max_length=255, null=False, blank=False)
    
    # Pueden quedar en blanco excepto la descripción
    evaluacion = models.CharField(max_length=255, null=True, blank=True)
    antecedentes = models.CharField(max_length=255, null=True, blank=True)
    examen = models.CharField(max_length=255, null=True, blank=True)
    diagnostico = models.CharField(max_length=255, null=True, blank=True)
    tratamiento = models.CharField(max_length=255, null=True, blank=True)

    tipo = models.ForeignKey(TipoCita, on_delete=models.PROTECT) # Protegido
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT) # Protegido

    def __str__(self):
        return f"Fecha: {self.fecha.strftime('%Y-%m-%d %H:%M:%S')} | Tipo: {self.tipo.tipo} | Paciente: {self.mascota.nombre} | Rut Cliente: {self.mascota.cliente.rut}"
    
    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ['-fecha']  # Ordenar por fecha descendente

class TipoVacuna(models.Model):
    TIPO_CHOICES = [
        ('óctuple', 'Óctuple'),
        ('antirrábica', 'Antirrábica'),
        ('kc', 'KC'),
        ('triple felina', 'Triple felina'),
        ('leucemia felina', 'Leucemia felina'),
    ]

    tipo = models.CharField(max_length=60, choices=TIPO_CHOICES, null=False, blank=False)

    def __str__(self):
        return self.tipo

    class Meta:
        verbose_name = "Tipo de vacuna"
        verbose_name_plural = "Tipos de vacunas"
        ordering = ["tipo"]

class Vacuna(models.Model):
    fecha = models.DateField(default=timezone.now)
    proxima_fecha = models.DateField(null=True, blank=True)
    tipo = models.ForeignKey(TipoVacuna, on_delete=models.PROTECT) # Protegido
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT) # Protegido
    consulta = models.ForeignKey(Consulta, on_delete=models.PROTECT) # Protegido

    def __str__(self):
        return f"Fecha: {self.fecha.strftime('%Y-%m-%d')} | Tipo: {self.tipo.tipo} | Mascota: {self.mascota.nombre} | Rut Cliente: {self.mascota.cliente.rut}"

    class Meta:
        verbose_name = "Vacuna"
        verbose_name_plural = "Vacunas"
        ordering = ["tipo"]

class Resena(models.Model):
    fecha = models.DateField(default=timezone.now)
    calificacion = models.IntegerField()
    comentario = models.CharField(max_length=255, null=False, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT) # Para eliminar usuario primero se deben borrar sus reseñas 

    def __str__(self):        
        return f"Fecha: {self.fecha.strftime('%Y-%m-%d')} | Usuario: {self.usuario.username}"

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ["-fecha"]

# Hace referencia a las horas que están disponibilizadas. Cuando se agenden su atributo disponible parsará a False
class Horario(models.Model):
    fecha = models.DateTimeField(null=False, blank=False)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.fecha}"

    class Meta:
        verbose_name = "Horario"  # Si hay error es porque hubo cambio posterior a la migración
        verbose_name_plural = "Horarios"
        ordering = ["-fecha"] ################## se invirtió

class Reserva(models.Model):
    
    # Foreign keys protegidos para su borrado
    tipo = models.ForeignKey(TipoCita, on_delete=models.PROTECT)
    horario = models.OneToOneField(Horario, on_delete=models.PROTECT)
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT)
    
    def __str__(self):
        return f"Fecha: {self.horario.fecha} | Mascota: {self.mascota.nombre} | Rut Cliente: {self.mascota.cliente.rut}"

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["horario__fecha"]

class Contacto(models.Model):
    nombres = models.CharField(max_length=80, null=False, blank=False)
    apellidos = models.CharField(max_length=80, null=False, blank=False)
    email = models.CharField(max_length=80, null=False, blank=False)
    mensaje = models.CharField(max_length=255, null=False, blank=False)
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Fecha: {self.fecha} | Nombre: {self.nombres} {self.apellidos}"
    
    # Define opciones del modelo
    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ["-fecha"]

class Newsletter(models.Model):        
    nombres = models.CharField(max_length=80, null=False, blank=False)
    apellidos = models.CharField(max_length=80, null=False, blank=False)
    email = models.CharField(max_length=80, null=False, blank=False)
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Fecha: {self.fecha} | Nombres: {self.nombres} {self.apellidos} | Email: {self.email}"
    
    class Meta:
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletters"
        ordering = ["-fecha"]
