from django.contrib import admin

from .models import Cliente, Region, Comuna, Direccion, Mascota
from .models import TipoCita, Consulta, TipoVacuna, Vacuna, Horario, Reserva
from .models import Resena, Contacto, Newsletter

import csv
from django.http import HttpResponse
from django.utils import timezone
# from .utils import utc_to_local

# Register your models here.

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    actions = ['export_to_csv']

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_clientes.csv"'
        response.write('\ufeff') # Manejo de caracteres especiales

        writer = csv.writer(response)
        writer.writerow(["Rut", "Nombres", "Apellidos", "Email", "Telefono", "Direccion", "Mascotas"])
        
        for cliente in queryset:            
            mascotas = Mascota.objects.filter(cliente=cliente) # Obtiene las mascotas del cliente            
            
            if mascotas:
                if len(mascotas) == 1:
                    mascotas_str = mascotas[0].nombre # Evita separador si hay solo una mascota
                else:                   
                    mascotas_str = " / ".join(mascota.nombre for mascota in mascotas) # Crea una lista con los nombres de las mascotas
            else:
                mascotas_str = ""
            
            direccion = Direccion.objects.filter(cliente=cliente).first() # Obtiene la dirección del cliente
            
            if direccion:
                direccion_str = f"{direccion.calle}, {direccion.numero}, {direccion.depto or ''}, {direccion.comuna.nombre_comuna}, {direccion.comuna.region.nombre_region}"
            else:
                direccion_str = "No disponible"

            # Inluye toda la información para el archivo
            writer.writerow(
                [
                    cliente.rut,
                    cliente.usuario.first_name,
                    cliente.usuario.last_name,
                    cliente.usuario.email,                
                    cliente.telefono,
                    direccion_str,
                    mascotas_str # Listado de mascotas                    
                ]
            )
        return response
    export_to_csv.short_description = "Exportar a CSV seleccionado/s"

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    actions = ['export_to_csv']
    # Permite descargar la información en CSV
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_mascotas.csv"'
        response.write('\ufeff') # Manejo de caracteres especiales

        writer = csv.writer(response)
        writer.writerow(["Chip", "Nombre", "Especie", "Edad", "Sexo", "Raza", "Esterilización", "Nombre Cliente", "Rut Cliente"])
        
        for mascota in queryset:            
            # Dueño de la mascota
            cliente_str = f'{mascota.cliente.usuario.first_name.title()} {mascota.cliente.usuario.last_name.title()}'

            # Inluye toda la información para el archivo
            writer.writerow(
                [
                    mascota.chip,
                    mascota.nombre,
                    mascota.especie,
                    mascota.edad,
                    mascota.sexo,
                    mascota.raza,
                    "Sí" if mascota.esterilizada == True else "No",
                    cliente_str,
                    mascota.cliente.rut       
                ]
            )
        return response
    export_to_csv.short_description = "Exportar a CSV seleccionado/s"

@admin.register(Consulta)
class Consulta(admin.ModelAdmin):
    actions = ['export_to_csv']
    # Permite descargar la información en CSV
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_consultas.csv"'
        response.write('\ufeff') # Manejo de caracteres especiales

        writer = csv.writer(response)
        writer.writerow(["Fecha", "Hora", "Tipo", "Nombre Mascota", "Especie", "Descripción / Motivo", "Evaluación / Curso ", "Antecedentes", "Examen / Observaciones", "Diagnóstico / Prediagnóstico", "Tratamiento / Indicaciones", "Nombre Cliente", "Rut Cliente"])
        
        for consulta in queryset:            
            # Dueño de la mascota
            cliente_str = f'{consulta.mascota.cliente.usuario.first_name.title()} {consulta.mascota.cliente.usuario.last_name.title()}'

            # Inluye toda la información para el archivo
            writer.writerow(
                [
                    consulta.fecha.strftime('%Y-%m-%d'),
                    # utc_to_local(consulta.fecha).strftime('%H:%M'),
                    consulta.tipo.tipo.title(),
                    consulta.mascota.nombre.title(),
                    consulta.mascota.especie.capitalize(),
                    consulta.descripcion.capitalize(),
                    consulta.evaluacion.capitalize(),
                    consulta.antecedentes.capitalize(),
                    consulta.examen.capitalize(),
                    consulta.diagnostico.capitalize(),
                    consulta.tratamiento.capitalize(),
                    cliente_str,
                    consulta.mascota.cliente.rut                            
                ]
            )
        return response
    export_to_csv.short_description = "Exportar a CSV seleccionado/s"

@admin.register(Vacuna)
class Vacuna(admin.ModelAdmin):
    actions = ['export_to_csv']
    # Permite descargar la información en CSV
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_vacunas.csv"'
        response.write('\ufeff') # Manejo de caracteres especiales

        writer = csv.writer(response)
        writer.writerow(["Fecha", "Tipo Vacuna", "Próxima Fecha Vacunación", "Nombre Mascota", "Especie", "Edad (en meses)", "Nombre Cliente", "Rut Cliente"])                

        for vacuna in queryset:            
            # Dueño de la mascota
            cliente_str = f'{vacuna.mascota.cliente.usuario.first_name.title()} {vacuna.mascota.cliente.usuario.last_name.title()}'

            # Inluye toda la información para el archivo
            writer.writerow(
                [
                    vacuna.fecha.strftime('%Y-%m-%d'),
                    vacuna.tipo.tipo.title(),
                    vacuna.proxima_fecha.strftime('%Y-%m-%d'),                    
                    vacuna.mascota.nombre.title(),
                    vacuna.mascota.especie.capitalize(),
                    vacuna.mascota.edad,
                    cliente_str,
                    vacuna.mascota.cliente.rut                            
                ]
            )
        return response
    export_to_csv.short_description = "Exportar a CSV seleccionado/s"

''' 

NOTA: Se posterga debido a que no se logra configurar la zona horaria en el admin panel

@admin.register(Horario)
class Horario(admin.ModelAdmin):
    actions = ['export_to_csv']

    # Permite descargar la información en CSV
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_horarios.csv"'
        response.write('\ufeff') # Manejo de caracteres especiales

        writer = csv.writer(response)
        writer.writerow(["Fecha", "Hora", "Disponible", "Nombre Mascota", "Especie", "Nombre Cliente", "RUT Cliente"])
                
        for horario in queryset:
            # Trata de obtener reserva. mascota y cliente asociado al horario
            try:                                
                reserva = Reserva.objects.get(horario=horario) # Objeto reserva del horario
                mascota = reserva.mascota # Objeto mascota de la reserva si hay reserva
                cliente = mascota.cliente # Objeto cliente de la mascota si hay reserva
                cliente_rut = cliente.rut
            except Reserva.DoesNotExist: # Si no hay reserva asociada
                mascota = ""
                cliente = ""
                cliente_rut = ""

            # Incluye toda la información para el archivo
            writer.writerow(
                [
                    horario.fecha.strftime('%Y-%m-%d'),                                    
                    utc_to_local(horario.fecha).strftime('%H:%M'), # Considera el cambio de zona horaria                                    
                    'Reservada' if horario.disponible == False else "",
                    mascota.nombre if mascota != "" else "",
                    mascota.especie if mascota != "" else "",
                    f'{cliente.usuario.last_name.title()}, {cliente.usuario.first_name.title()}' if cliente != "" else "",
                    cliente_rut if cliente_rut != "" else ""
                ]
            )
        return response
    export_to_csv.short_description = "Exportar a CSV seleccionado/s" '''

'''

NOTA: Se posterga debido a que no se logra configurar la zona horaria en el admin panel

@admin.register(Reserva)
class Reserva(admin.ModelAdmin):
    actions = ['export_to_csv']
    # Permite descargar la información en CSV
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_reservas.csv"'
        response.write('\ufeff') # Manejo de caracteres especiales

        writer = csv.writer(response)
        writer.writerow(["Fecha", "Hora", "Nombre Mascota", "Especie", "Nombre Cliente", "RUT Cliente"])
                
        for reserva in queryset:
            # Incluye toda la información para el archivo
            writer.writerow(
                [
                    reserva.horario.fecha.strftime('%Y-%m-%d'),                                    
                    utc_to_local(reserva.horario.fecha).strftime('%H:%M'), # Considera el cambio de zona horaria                                                        
                    reserva.mascota.nombre,
                    reserva.mascota.especie,
                    f'{reserva.mascota.cliente.usuario.last_name.title()}, {reserva.mascota.cliente.usuario.first_name.title()}',
                    reserva.mascota.cliente.rut
                ]
            )
        return response
    export_to_csv.short_description = "Exportar a CSV seleccionado/s" '''


####################################################################################
# Traspaso simple del modelo al panel de administración ############################
####################################################################################
# admin.site.register(Cliente) Se personalizó CSV
# admin.site.register(Region)
# admin.site.register(Comuna)
# admin.site.register(Direccion)
# admin.site.register(Mascota) Se personalizó CSV 
# admin.site.register(TipoCita)
# admin.site.register(Consulta) Se personalizó CSV
# admin.site.register(TipoVacuna)
# admin.site.register(Vacuna) Se personalizó CSV
# admin.site.register(Horario) SE POSTERGA POR ZONA HORARIA
# admin.site.register(Reserva) SE POSTERGA POR ZONA HORARIA
admin.site.register(Resena)
admin.site.register(Contacto)
admin.site.register(Newsletter)
