from django.urls import resolve

def breadcrumbs_processor(request):
    # Aquí se definen los breadcrumbs predeterminados o dinámicos
    # Basado en la URL actual o alguna lógica
    url_name = resolve(request.path_info).url_name
    breadcrumbs = []

    if url_name == 'contacto':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Contacto', 'url': None}
        ]
    elif url_name == 'newsletter':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Newsletter', 'url': None}            
        ]
    elif url_name == 'registro':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Registro', 'url': None}            
        ]
    elif url_name == 'dashboard':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': None}
        ]
    elif url_name == 'perfil_usuario':
        if request.user.is_superuser: # Para el caso de superusuario
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home/dashboard-admin'},
                {'title': 'Clientes', 'url': '/home/dashboard-admin/clientes'},
                {'title': 'Perfil Cliente', 'url': None}
            ]
        else:
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home/dashboard'},
                {'title': 'Mi Perfil', 'url': None}
            ]
    elif url_name == 'editar_usuario':
        if request.user.is_superuser: # Para el caso de superusuario
            cliente_id = resolve(request.path_info).kwargs.get('cliente_id')
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home/dashboard-admin'},
                {'title': 'Clientes', 'url': '/home/dashboard-admin/clientes'},
                {'title': 'Perfil Cliente', 'url': '/home/dashboard-admin/clientes/{}'.format(cliente_id)},
                {'title': 'Editar Perfil', 'url': None}
            ]
        else:
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home/dashboard'},
                {'title': 'Perfil Usuario', 'url': '/home/dashboard/mi-perfil'},
                {'title': 'Editar Perfil', 'url': None}
            ]
    elif url_name == 'mascotas':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard'},
            {'title': 'Mascotas', 'url': None}
        ]
    elif url_name == 'registro_mascota':
        if request.user.is_superuser: # Para el caso de superusuario
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home/dashboard-admin'},
                {'title': 'Pacientes', 'url': '/home/dashboard-admin/pacientes'},
                {'title': 'Registrar Paciente', 'url': None},
            ]
        else:
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home/dashboard'},
                {'title': 'Mascotas', 'url': '/home/dashboard/mis-mascotas'},
                {'title': 'Registro Mascota', 'url': None},
            ]
        
    elif url_name == 'reservar_hora':
        if request.user.is_superuser: # Para el caso de superusuario
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home'},
                {'title': 'Agenda', 'url': '/home/dashboard-admin/agenda'},
                {'title': 'Reservar Cita', 'url': None}
            ]
        else:
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home/dashboard'},
                {'title': 'Reservar Cita', 'url': None}
            ]
    elif url_name == 'agendamientos':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard'},
            {'title': 'Agendamientos', 'url': None}
        ]
    elif url_name == 'resenas_usuarios':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard'},
            {'title': 'Comentarios', 'url': None}
        ]
    elif url_name == 'vacunatorio':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard'},
            {'title': 'Vacunatorio', 'url': None}
        ]
    elif url_name == 'vacunas_mascota':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard'},
            {'title': 'Historial Vacunas', 'url': None}
        ]
    elif url_name == 'dashboard_admin':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': None}
        ]
    elif url_name == 'clientes':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard-admin'},
            {'title': 'Clientes', 'url': None}
        ]
    elif url_name == 'pacientes':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard-admin'},
            {'title': 'Pacientes', 'url': None}
        ]
    elif url_name == 'perfil_paciente':
        if request.user.is_superuser: # Para administrador
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home/dashboard-admin'},
                {'title': 'Pacientes', 'url': '/home/dashboard-admin/pacientes'},
                {'title': 'Perfil Paciente', 'url': None},
            ]
        else: # Para cliente
            breadcrumbs = [
                {'title': 'Inicio', 'url': '/home'},
                {'title': 'Dashboard', 'url': '/home/dashboard'},
                {'title': 'Mascotas', 'url': '/home/dashboard/mis-mascotas'},
                {'title': 'Perfil Mascota', 'url': None},
            ]
    elif url_name == 'agenda':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard-admin'},            
            {'title': 'Agenda', 'url': None},
        ]
    elif url_name == 'consulta':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard-admin'},
            {'title': 'Agenda', 'url': '/home/dashboard-admin/agenda'},
            {'title': 'Consulta', 'url': None},
        ]
    elif url_name == 'registro_vacuna':
        breadcrumbs = [
            {'title': 'Inicio', 'url': '/home'},
            {'title': 'Dashboard', 'url': '/home/dashboard-admin'},
            {'title': 'Agenda', 'url': '/home/dashboard-admin/agenda'},
            {'title': 'Consulta', 'url': '/home/dashboard-admin/consulta'},
            {'title': 'Registro Vacuna', 'url': None},
        ]
    
    return {
        'breadcrumbs': breadcrumbs
    }
