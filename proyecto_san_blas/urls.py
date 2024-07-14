"""
URL configuration for proyecto_san_blas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from san_blas_app.views import indice, registro, inicio_sesion, dashboard, cerrar_sesion, mascotas, registro_mascota
from san_blas_app.views import dashboard_admin, agenda, reservar_hora, consulta, vacunatorio, vacunas_mascota
from san_blas_app.views import registro_vacuna

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', indice, name="inicio"),
    path('home', indice, name="inicio"),
    path('register', registro, name="registro"),
    path('login', inicio_sesion, name="inicio_sesion"),
    path('home/dashboard', dashboard, name="dashboard"),
    path('home/dashboard/reservar-cita', reservar_hora, name="reservar_hora"),
    path('home/dashboard/vacunatorio', vacunatorio, name="vacunatorio"),
    path('home/dashboard/vacunatorio/historial-vacunas/<int:mascota_id>/', vacunas_mascota, name="vacunas_mascota"),
    path('home/dashboard-admin', dashboard_admin, name="dashboard_admin"),
    path('home/dashboard-admin/consulta', consulta, name="consulta"),
    path('home/dashboard-admin/consulta/registro-vacuna/<int:consulta_id>/<int:mascota_id>', registro_vacuna, name="registro_vacuna"),
    path('home/dashboard-admin/agenda', agenda, name="agenda"),
    path('home/dashboard/mis-mascotas', mascotas, name="mascotas"),
    path('home/dashboard/register-pet', registro_mascota, name="registro_mascota"),
    path('logout', cerrar_sesion, name="cerrar_sesion")
]
