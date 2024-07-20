from datetime import timedelta

def proxima_fecha_vacunacion(vacuna):
    print(f"Calculando próxima fecha para vacuna de tipo {vacuna.tipo.tipo} para mascota {vacuna.mascota.nombre} de especie {vacuna.mascota.especie}")

    if vacuna.mascota.especie == 'Canina':
        if vacuna.tipo.tipo == 'Óctuple':
            proxima_fecha = calcular_fecha_octuple(vacuna)
        elif vacuna.tipo.tipo == 'Antirrábica':
            proxima_fecha = calcular_fecha_antirrabica(vacuna)
        elif vacuna.tipo.tipo == 'KC':
            proxima_fecha = vacuna.fecha.replace(year=vacuna.fecha.year + 1)
    elif vacuna.mascota.especie == 'Felina':
        if vacuna.tipo.tipo == 'Triple felina' or vacuna.tipo.tipo == 'Leucemia felina':
            proxima_fecha = calcular_fecha_triple_leucemia(vacuna)
        elif vacuna.tipo.tipo == 'Antirrábica':
            proxima_fecha = calcular_fecha_antirrabica(vacuna)
    else:
        proxima_fecha = None

    if proxima_fecha is None:
        print('No se está generando la próxima fecha')
    else:
        print(f"Próxima fecha calculada: {proxima_fecha}")

    return proxima_fecha

# Cálculo para cada tipo de vacuna
def calcular_fecha_octuple(vacuna):
    if vacuna.mascota.edad < 4:
        return vacuna.fecha + timedelta(days=30)  # Vacunación dentro de un mes si tiene hasta 4 meses
    else:
        return vacuna.fecha.replace(year=vacuna.fecha.year + 1)  # Después de los 4 meses, vacunación anual

def calcular_fecha_antirrabica(vacuna):
    if vacuna.mascota.edad < 12:
        return vacuna.fecha + timedelta(days=180)  # Vacunación dentro de 6 meses antes del año de edad
    else:
        return vacuna.fecha.replace(year=vacuna.fecha.year + 1)  # Luego es cada 12 meses

def calcular_fecha_triple_leucemia(vacuna):
    if vacuna.mascota.edad < 4:
        return vacuna.fecha + timedelta(days=30)  # Cada un mes para edad hasta 4 meses
    else:
        return vacuna.fecha.replace(year=vacuna.fecha.year + 1)  # Luego es de manera anual

# Convierte fecha a zona horaria local (América/Santiago)
def utc_to_local(utc_dt):
    local_dt = utc_dt - timedelta(hours=3)  # Ajusta la zona horaria
    return local_dt