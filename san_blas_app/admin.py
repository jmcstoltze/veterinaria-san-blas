from django.contrib import admin
from .models import Cliente, Region, Comuna, Direccion, Mascota
from .models import TipoCita, Consulta, TipoVacuna, Vacuna, Horario, Reserva
from .models import Resena, Contacto, Newsletter

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Region)
admin.site.register(Comuna)
admin.site.register(Direccion)
admin.site.register(Mascota)
admin.site.register(TipoCita)
admin.site.register(Consulta)
admin.site.register(TipoVacuna)
admin.site.register(Vacuna)
admin.site.register(Horario)
admin.site.register(Reserva)
admin.site.register(Resena)
admin.site.register(Contacto)
admin.site.register(Newsletter)
