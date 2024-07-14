# Veterinaria San Blas

Prototipo de aplicación web desarrollado para Veterinaria San Blas, cumpliendo con los requerimientos específicos de la implementación. Esta aplicación está construida utilizando Django/Python y un modelo relacional en PostgreSQL, aprovechando el ORM del framework Django.

## Tabla de Contenidos

- [Veterinaria San Blas](#veterinaria-san-blas)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Descripción](#descripción)
    - [Características](#características)
  - [Instalación](#instalación)
  - [Uso](#uso)
    - [Ejemplos de Uso](#ejemplos-de-uso)
  - [Contribución](#contribución)
  - [Licencia](#licencia)
  - [Contacto](#contacto)

## Descripción

El proyecto de Veterinaria San Blas es una aplicación web diseñada para gestionar diversos aspectos de la clínica veterinaria, incluyendo el registro de mascotas, citas médicas, vacunaciones, y más. Esta aplicación busca optimizar el manejo de la información y mejorar la eficiencia operativa de la clínica.

### Características

- **Gestión de Mascotas**: Registro y seguimiento de información detallada de las mascotas.
- **Citas Médicas**: Programación y administración de consultas veterinarias.
- **Vacunaciones**: Registro y seguimiento de las vacunaciones de las mascotas.
- **Usuarios**: Administración de usuarios con diferentes roles y permisos.

## Instalación

Siga los pasos a continuación para configurar el entorno de desarrollo:

1. Clonar el repositorio:

    ```sh
    git clone https://github.com/usuario/proyecto-veterinaria-san-blas.git
    cd proyecto-veterinaria-san-blas
    ```

2. Crear y activar un entorno virtual:

    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instalar las dependencias:

    ```sh
    pip install -r requirements.txt
    ```

4. Configurar la base de datos:
    ```sh
    python manage.py migrate
    ```

5. Crear un superusuario:
    ```sh
    python manage.py createsuperuser
    ```

6. Ejecutar el servidor de desarrollo:
    ```sh
    python manage.py runserver
    ```

## Uso

Una vez que el servidor esté en funcionamiento, puede acceder a la aplicación a través de su navegador web en `http://localhost:8000`.

### Ejemplos de Uso

- **Registrar Mascota**: Navegue a la sección de mascotas y complete el formulario de registro.
- **Programar Cita**: Acceda a la sección de citas y seleccione una fecha y hora disponibles.
- **Registrar Vacunación**: En la ficha de la mascota, registre las vacunaciones aplicadas.

## Contribución

Para contribuir al proyecto, siga estos pasos:

1. Hacer un fork del repositorio.
2. Clonar el fork:
    ```sh
    git clone https://github.com/tu-usuario/proyecto-veterinaria-san-blas.git
    cd proyecto-veterinaria-san-blas
    ```

3. Crear una rama para sus cambios:
    ```sh
    git checkout -b mi-nueva-rama
    ```

4. Hacer cambios y commitearlos:
    ```sh
    git add .
    git commit -m 'Descripción de los cambios'
    ```

5. Enviar los cambios a su fork:
    ```sh
    git push origin mi-nueva-rama
    ```

6. Enviar un pull request a la rama principal del repositorio original.

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## Contacto

Para más información, por favor contactar:

- Nombre: [Su Nombre]
- Email: [su.email@ejemplo.com]
- LinkedIn: [Su Perfil de LinkedIn]
- GitHub: [Su Perfil de GitHub]
