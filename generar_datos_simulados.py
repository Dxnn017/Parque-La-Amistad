"""
Script para generar datos simulados completos para el sistema de gestión de residuos
Ejecutar este script para poblar la base de datos con datos de prueba realistas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Configuración
np.random.seed(42)
random.seed(42)

# Crear directorio dataset si no existe
os.makedirs('dataset', exist_ok=True)

# ============================================
# GENERAR DATOS DE RESIDUOS
# ============================================

def generar_residuos_parque(num_registros=100):
    """Genera datos simulados de residuos del parque"""
    
    zonas = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']
    tipos_residuo = ['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Textil', 'Electrónico', 'Peligroso', 'Otros']
    estados = ['Activo', 'Procesado', 'Archivado']
    
    # Coordenadas base del Parque La Amistad (Surco, Lima)
    lat_base = -12.1391
    lon_base = -76.9969
    
    datos = []
    
    fecha_inicio = datetime.now() - timedelta(days=180)  # 6 meses atrás
    
    for i in range(1, num_registros + 1):
        # Generar fecha aleatoria en los últimos 6 meses
        dias_aleatorios = random.randint(0, 180)
        fecha_registro = fecha_inicio + timedelta(days=dias_aleatorios)
        
        # Generar coordenadas aleatorias cercanas al parque
        lat = lat_base + random.uniform(-0.005, 0.005)
        lon = lon_base + random.uniform(-0.005, 0.005)
        
        # Peso con distribución realista (más residuos ligeros)
        peso = round(np.random.lognormal(0, 1) + 0.5, 2)
        peso = min(peso, 50.0)  # Limitar peso máximo
        
        # Zona con distribución no uniforme (algunas zonas más afectadas)
        zona_pesos = [0.25, 0.15, 0.20, 0.30, 0.10]  # Norte y Oeste más afectados
        zona = np.random.choice(zonas, p=zona_pesos)
        
        # Tipo de residuo con distribución realista
        tipo_pesos = [0.35, 0.25, 0.10, 0.15, 0.05, 0.02, 0.03, 0.05]
        tipo_residuo = np.random.choice(tipos_residuo, p=tipo_pesos)
        
        # Estado (mayoría activos)
        estado_pesos = [0.70, 0.20, 0.10]
        estado = np.random.choice(estados, p=estado_pesos)
        
        # Observaciones variadas
        observaciones_opciones = [
            f"Residuos encontrados cerca de {random.choice(['juegos infantiles', 'bancas', 'sendero', 'área verde', 'estacionamiento'])}",
            f"Acumulación de residuos en {random.choice(['esquina', 'entrada', 'zona central', 'perímetro'])}",
            f"Residuos dispersos en área de {random.choice(['picnic', 'deportes', 'descanso', 'tránsito'])}",
            "Residuos junto a tacho de basura lleno",
            "Área con alta concentración de residuos",
            "Residuos recientes, posiblemente del día",
            "Zona requiere limpieza urgente",
            ""
        ]
        observacion = random.choice(observaciones_opciones)
        
        registro = {
            'ID': i,
            'Zona': zona,
            'Ubicación (GPS)': f"{lat:.6f}, {lon:.6f}",
            'Tipo de residuo': tipo_residuo,
            'Peso estimado (kg)': peso,
            'Fecha de registro': fecha_registro.strftime('%Y-%m-%d'),
            'Fecha de creación': fecha_registro.strftime('%Y-%m-%d %H:%M:%S'),
            'Observaciones': observacion,
            'Ruta Imagen': '',
            'Estado': estado,
            'Usuario': random.choice(['Sistema', 'Voluntario', 'Guardaparque', 'Estudiante'])
        }
        
        datos.append(registro)
    
    df = pd.DataFrame(datos)
    return df

# ============================================
# GENERAR ZONAS CRÍTICAS
# ============================================

def generar_zonas_criticas():
    """Genera datos de zonas críticas del parque"""
    
    zonas_criticas = [
        {
            'Codigo de Zona': 'Z1',
            'Sector del Parque': 'Entrada Principal Norte',
            'Descripcion de Residuos': 'Alta concentración de plásticos y envases de bebidas',
            'Tipo de Residuos Predominantes': 'Plástico',
            'Nivel de Riesgo': 'Alto',
            'Observaciones': 'Zona de mayor tránsito, requiere tachos adicionales'
        },
        {
            'Codigo de Zona': 'Z2',
            'Sector del Parque': 'Área de Juegos Infantiles',
            'Descripcion de Residuos': 'Residuos orgánicos y envolturas de alimentos',
            'Tipo de Residuos Predominantes': 'Mixto',
            'Nivel de Riesgo': 'Medio',
            'Observaciones': 'Familias con niños, educación ambiental necesaria'
        },
        {
            'Codigo de Zona': 'Z3',
            'Sector del Parque': 'Zona de Picnic Este',
            'Descripcion de Residuos': 'Restos de comida, platos desechables, botellas',
            'Tipo de Residuos Predominantes': 'Orgánico',
            'Nivel de Riesgo': 'Alto',
            'Observaciones': 'Atrae fauna no deseada, limpieza frecuente requerida'
        },
        {
            'Codigo de Zona': 'Z4',
            'Sector del Parque': 'Sendero Sur',
            'Descripcion de Residuos': 'Papel, cartón y residuos ligeros dispersos',
            'Tipo de Residuos Predominantes': 'Papel/Cartón',
            'Nivel de Riesgo': 'Bajo',
            'Observaciones': 'Viento dispersa residuos, necesita barreras'
        },
        {
            'Codigo de Zona': 'Z5',
            'Sector del Parque': 'Estacionamiento Oeste',
            'Descripcion de Residuos': 'Residuos automotrices y envases',
            'Tipo de Residuos Predominantes': 'Peligroso',
            'Nivel de Riesgo': 'Alto',
            'Observaciones': 'Contaminación por aceites y fluidos, atención especial'
        },
        {
            'Codigo de Zona': 'Z6',
            'Sector del Parque': 'Área Deportiva Centro',
            'Descripcion de Residuos': 'Botellas plásticas y envases de bebidas energéticas',
            'Tipo de Residuos Predominantes': 'Plástico',
            'Nivel de Riesgo': 'Medio',
            'Observaciones': 'Deportistas, promover uso de botellas reutilizables'
        },
        {
            'Codigo de Zona': 'Z7',
            'Sector del Parque': 'Zona de Mascotas Norte',
            'Descripcion de Residuos': 'Desechos de mascotas y bolsas plásticas',
            'Tipo de Residuos Predominantes': 'Orgánico',
            'Nivel de Riesgo': 'Medio',
            'Observaciones': 'Necesita más dispensadores de bolsas y tachos específicos'
        },
        {
            'Codigo de Zona': 'Z8',
            'Sector del Parque': 'Laguna Artificial',
            'Descripcion de Residuos': 'Plásticos flotantes y residuos en orillas',
            'Tipo de Residuos Predominantes': 'Plástico',
            'Nivel de Riesgo': 'Alto',
            'Observaciones': 'Afecta fauna acuática, limpieza urgente y prevención'
        }
    ]
    
    df = pd.DataFrame(zonas_criticas)
    return df

# ============================================
# GENERAR RESPUESTAS DE ENCUESTAS
# ============================================

def generar_encuestas(num_respuestas=50):
    """Genera respuestas simuladas de encuestas"""
    
    nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Rosa', 'Miguel', 'Laura']
    apellidos = ['García', 'Rodríguez', 'Martínez', 'López', 'González', 'Pérez', 'Sánchez', 'Ramírez', 'Torres', 'Flores']
    carreras = [
        'Ing. Ambiental', 'Biología', 'Veterinaria', 'Ing. Civil', 
        'Arquitectura', 'Trabajo Social', 'Educación', 'Medicina', 
        'Derecho', 'Administración', 'Comerciante', 'Profesor', 'Estudiante'
    ]
    
    frecuencias = ['Diariamente', 'Varias veces por semana', 'Una vez por semana', 'Ocasionalmente', 'Casi nunca']
    respuestas_si_no = ['Sí', 'No']
    
    datos = []
    
    fecha_inicio = datetime.now() - timedelta(days=60)
    
    for i in range(num_respuestas):
        dias_aleatorios = random.randint(0, 60)
        fecha = fecha_inicio + timedelta(days=dias_aleatorios)
        
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        
        # Generar respuestas con tendencia positiva hacia la conservación
        respuesta = {
            'Marca temporal': fecha.strftime('%d/%m/%Y %H:%M:%S'),
            'Dirección de correo electrónico': f"{nombre.lower()}.{apellido.lower()}@email.com",
            'Nombre': nombre,
            'Apellidos': apellido,
            'ID': f"{random.randint(100000, 999999)}",
            'Carrera y/o oficio': random.choice(carreras),
            '¿ Con qué frecuencia visita el Parque de la amistad?': random.choice(frecuencias),
            '¿Considera que el parque de la Amistad cumple una función importante en la preservación del medio ambiente urbano?': np.random.choice(respuestas_si_no, p=[0.9, 0.1]),
            '¿ Piensa que la contaminación dentro del parque refleja el nivel de educación ambiental de la comunidad?': np.random.choice(respuestas_si_no, p=[0.85, 0.15]),
            '¿ Ha notado que los eventos y actividades dentro del parque generan más residuos de lo habitual?': np.random.choice(respuestas_si_no, p=[0.8, 0.2]),
            '¿ Cree que los tachos de basura y puntos de reciclaje están bien distribuidos en el parque?': np.random.choice(respuestas_si_no, p=[0.4, 0.6]),
            '¿ Considera que la implementación de un sistema de gestión de residuos ( con tachos diferenciados y puntos de reciclaje) mejoraría significativamente la limpieza del parque "La Amistad"?': np.random.choice(respuestas_si_no, p=[0.95, 0.05]),
            '¿ Cree necesario implementar campañas de sensibilización sobre la tenencia responsable de mascotas dentro del parque?': np.random.choice(respuestas_si_no, p=[0.9, 0.1]),
            'Teniendo en cuenta la breve explicación de nuestro proyecto,¿ consideras que la propuesta "Amistad Sostenible" puede generar un cambio positivo en la conciencia ambiental de la comunidad?': np.random.choice(respuestas_si_no, p=[0.92, 0.08]),
            '¿ Estarías dispuesto a promover el proyecto del parque dentro de su círculo social o familiar?': np.random.choice(respuestas_si_no, p=[0.88, 0.12]),
            '¿ Cómo cree que la participación de la comunidad universitaria y local podría fortalecer  el cuidado del parque a largo plazo?': random.choice([
                'Organizando jornadas de limpieza regulares',
                'Educación ambiental en escuelas cercanas',
                'Creando grupos de voluntarios',
                'Implementando programas de reciclaje',
                'Promoviendo el uso responsable del parque',
                'Desarrollando campañas en redes sociales',
                'Coordinando con autoridades locales'
            ])
        }
        
        datos.append(respuesta)
    
    df = pd.DataFrame(datos)
    return df

# ============================================
# EJECUTAR GENERACIÓN
# ============================================

if __name__ == "__main__":
    print("🌳 Generando datos simulados para el Sistema de Gestión de Residuos...")
    print("=" * 60)
    
    # Generar residuos
    print("\n📊 Generando datos de residuos...")
    df_residuos = generar_residuos_parque(100)
    df_residuos.to_csv('dataset/residuos_parque.csv', index=False, encoding='utf-8')
    print(f"✅ Generados {len(df_residuos)} registros de residuos")
    print(f"   - Peso total: {df_residuos['Peso estimado (kg)'].sum():.2f} kg")
    print(f"   - Zonas afectadas: {df_residuos['Zona'].nunique()}")
    
    # Generar zonas críticas
    print("\n🗺️ Generando datos de zonas críticas...")
    df_zonas = generar_zonas_criticas()
    df_zonas.to_csv('dataset/zonas_criticas.csv', index=False, encoding='utf-8')
    print(f"✅ Generadas {len(df_zonas)} zonas críticas")
    
    # Generar encuestas
    print("\n📋 Generando respuestas de encuestas...")
    df_encuestas = generar_encuestas(50)
    df_encuestas.to_csv('dataset/encuesta_respuestas.csv', index=False, encoding='utf-8')
    print(f"✅ Generadas {len(df_encuestas)} respuestas de encuestas")
    
    print("\n" + "=" * 60)
    print("✅ ¡Datos simulados generados exitosamente!")
    print("\nArchivos creados:")
    print("  - dataset/residuos_parque.csv")
    print("  - dataset/zonas_criticas.csv")
    print("  - dataset/encuesta_respuestas.csv")
    print("\n🚀 Ahora puede ejecutar la aplicación Streamlit con estos datos.")
