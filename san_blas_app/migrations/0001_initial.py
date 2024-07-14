# Generated by Django 4.2.11 on 2024-07-14 18:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rut', models.CharField(max_length=10, unique=True)),
                ('telefono', models.CharField(max_length=10)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'ordering': ['rut', 'usuario__last_name', 'usuario__first_name'],
            },
        ),
        migrations.CreateModel(
            name='Comuna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_comuna', models.CharField(max_length=80)),
            ],
            options={
                'verbose_name': 'Comuna',
                'verbose_name_plural': 'Comunas',
                'ordering': ['nombre_comuna'],
            },
        ),
        migrations.CreateModel(
            name='Consulta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('descripcion', models.CharField(max_length=255)),
                ('evaluacion', models.CharField(blank=True, max_length=255, null=True)),
                ('antecedentes', models.CharField(blank=True, max_length=255, null=True)),
                ('examen', models.CharField(blank=True, max_length=255, null=True)),
                ('diagnostico', models.CharField(blank=True, max_length=255, null=True)),
                ('tratamiento', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Consulta',
                'verbose_name_plural': 'Consultas',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Contacto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombres', models.CharField(max_length=80)),
                ('apellidos', models.CharField(max_length=80)),
                ('email', models.CharField(max_length=80)),
                ('mensaje', models.CharField(max_length=255)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Contacto',
                'verbose_name_plural': 'Contactos',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField()),
                ('disponible', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Cita',
                'verbose_name_plural': 'Citas',
                'ordering': ['fecha'],
            },
        ),
        migrations.CreateModel(
            name='Mascota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chip', models.CharField(max_length=20, unique=True)),
                ('nombre', models.CharField(max_length=80)),
                ('especie', models.CharField(choices=[('felina', 'Felina'), ('canina', 'Canina')], max_length=10)),
                ('edad', models.IntegerField()),
                ('sexo', models.CharField(choices=[('macho', 'Macho'), ('hembra', 'Hembra')], max_length=10)),
                ('raza', models.CharField(max_length=20)),
                ('esterilizada', models.BooleanField(default=False)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.cliente')),
            ],
            options={
                'verbose_name': 'Mascota',
                'verbose_name_plural': 'Mascotas',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombres', models.CharField(max_length=80)),
                ('apellidos', models.CharField(max_length=80)),
                ('email', models.CharField(max_length=80)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Newsletter',
                'verbose_name_plural': 'Newsletters',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_region', models.CharField(max_length=80)),
            ],
            options={
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regiones',
                'ordering': ['nombre_region'],
            },
        ),
        migrations.CreateModel(
            name='TipoCita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('general', 'General'), ('vacuna', 'Vacuna'), ('preventiva', 'Preventiva'), ('cirugía esterilización', 'Cirugía esterilización'), ('cirugía tumor menor', 'Cirugía tumor menor'), ('certificado', 'Certificado'), ('destartraje', 'Destartraje'), ('tratamiento/curación', 'Tratamiento/curación')], max_length=60)),
            ],
            options={
                'verbose_name': 'Tipo de cita',
                'verbose_name_plural': 'Tipos de citas',
                'ordering': ['tipo'],
            },
        ),
        migrations.CreateModel(
            name='TipoVacuna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('óctuple', 'Óctuple'), ('antirrábica', 'Antirrábica'), ('kc', 'KC'), ('triple felina', 'Triple felina'), ('leucemia felina', 'Leucemia felina')], max_length=60)),
            ],
            options={
                'verbose_name': 'Tipo de vacuna',
                'verbose_name_plural': 'Tipos de vacunas',
                'ordering': ['tipo'],
            },
        ),
        migrations.CreateModel(
            name='Vacuna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('proxima_fecha', models.DateField(blank=True, null=True)),
                ('consulta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.consulta')),
                ('mascota', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.mascota')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.tipovacuna')),
            ],
            options={
                'verbose_name': 'Vacuna',
                'verbose_name_plural': 'Vacunas',
                'ordering': ['tipo'],
            },
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horario', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.horario')),
                ('mascota', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.mascota')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.tipocita')),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'ordering': ['horario__fecha'],
            },
        ),
        migrations.CreateModel(
            name='Resena',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('calificacion', models.IntegerField()),
                ('comentario', models.CharField(max_length=255)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reseña',
                'verbose_name_plural': 'Reseñas',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Direccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calle', models.CharField(max_length=80)),
                ('numero', models.CharField(max_length=20)),
                ('depto', models.CharField(blank=True, max_length=20, null=True)),
                ('cliente', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.cliente')),
                ('comuna', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.comuna')),
            ],
            options={
                'verbose_name': 'Direccion',
                'verbose_name_plural': 'Direcciones',
                'ordering': ['comuna'],
            },
        ),
        migrations.AddField(
            model_name='consulta',
            name='mascota',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.mascota'),
        ),
        migrations.AddField(
            model_name='consulta',
            name='tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.tipocita'),
        ),
        migrations.AddField(
            model_name='comuna',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='san_blas_app.region'),
        ),
    ]
