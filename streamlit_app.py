"""
Script para generar datasets simulados para el Sistema de Gestión de Residuos
Parque La Amistad
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
# 1. DATASET DE RESIDUOS
# ============================================

def generar_residuos():
    """Genera dataset de residuos recolectados"""
    
    zonas = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']
    tipos_residuo = ['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 
                     'Textil', 'Electrónico', 'Peligroso', 'Otros']
    
    # Coordenadas base del Parque La Amistad (Panamá)
    coordenadas_base = {
        'Norte': (-8.105, -79.025),
        'Sur': (-8.115, -79.030),
        'Este': (-8.110, -79.020),
        'Oeste': (-8.110, -79.035),
        'Centro': (-8.110, -79.028)
    }
    
    registros = []
    fecha_inicio = datetime.now() - timedelta(days=180)  # 6 meses de datos
    
    for i in range(500):  # 500 registros
        zona = random.choice(zonas)
        tipo = random.choice(tipos_residuo)
        
        # Generar coordenadas cercanas a la base de cada zona
        lat_base, lon_base = coordenadas_base[zona]
        lat = lat_base + np.random.uniform(-0.005, 0.005)
        lon = lon_base + np.random.uniform(-0.005, 0.005)
        
        # Peso variable según tipo de residuo
        if tipo == 'Plástico':
            peso = round(np.random.uniform(0.5, 15.0), 2)
        elif tipo == 'Orgánico':
            peso = round(np.random.uniform(1.0, 25.0), 2)
        elif tipo == 'Vidrio/Metal':
            peso = round(np.random.uniform(0.3, 10.0), 2)
        elif tipo == 'Papel/Cartón':
            peso = round(np.random.uniform(0.2, 8.0), 2)
        elif tipo == 'Electrónico':
            peso = round(np.random.uniform(0.5, 5.0), 2)
        else:
            peso = round(np.random.uniform(0.1, 12.0), 2)
        
        # Fecha aleatoria en los últimos 6 meses
        dias_atras = random.randint(0, 180)
        fecha = fecha_inicio + timedelta(days=dias_atras)
        
        # Descripción
        descripciones = [
            f"Acumulación de {tipo.lower()} encontrada cerca de área recreativa",
            f"Residuos de {tipo.lower()} dispersos en zona de senderos",
            f"{tipo} abandonado en área de picnic",
            f"Concentración de {tipo.lower()} cerca de zona de fauna",
            f"Residuos de {tipo.lower()} en área de vegetación"
        ]
        
        registro = {
            'id': f'RES-{i+1:04d}',
            'fecha': fecha.strftime('%Y-%m-%d'),
            'zona': zona,
            'coordenadas_gps': f"{lat:.6f}, {lon:.6f}",
            'tipo_residuo': tipo,
            'peso_kg': peso,
            'descripcion': random.choice(descripciones),
            'recolectado': random.choice([True, True, True, False]),  # 75% recolectado
            'voluntarios': random.randint(2, 8),
            'estado': random.choice(['Crítico', 'Moderado', 'Leve'])
        }
        
        registros.append(registro)
    
    df = pd.DataFrame(registros)
    df.to_csv('dataset/residuos_parque.csv', index=False, encoding='utf-8')
    print(f"✓ Dataset de residuos creado: {len(df)} registros")
    return df


# ============================================
# 2. DATASET DE ZONAS CRÍTICAS
# ============================================

def generar_zonas_criticas():
    """Genera dataset de zonas críticas identificadas"""
    
    zonas_criticas = [
        {
            'id': 'ZC-001',
            'nombre': 'Área de Picnic Principal',
            'zona': 'Centro',
            'coordenadas_gps': '-8.110, -79.028',
            'nivel_riesgo': 'Alto',
            'tipo_contaminacion': 'Plástico, Orgánico',
            'frecuencia_limpieza': 'Diaria',
            'area_m2': 250,
            'fauna_afectada': 'Aves, Mamíferos pequeños',
            'observaciones': 'Alta concentración de residuos plásticos y orgánicos. Requiere intervención urgente.',
            'ultima_inspeccion': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        },
        {
            'id': 'ZC-002',
            'nombre': 'Sendero Norte',
            'zona': 'Norte',
            'coordenadas_gps': '-8.105, -79.025',
            'nivel_riesgo': 'Medio',
            'tipo_contaminacion': 'Papel/Cartón, Plástico',
            'frecuencia_limpieza': 'Semanal',
            'area_m2': 180,
            'fauna_afectada': 'Aves',
            'observaciones': 'Residuos dispersos a lo largo del sendero. Necesita señalización.',
            'ultima_inspeccion': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        },
        {
            'id': 'ZC-003',
            'nombre': 'Zona de Juegos Infantiles',
            'zona': 'Este',
            'coordenadas_gps': '-8.110, -79.020',
            'nivel_riesgo': 'Alto',
            'tipo_contaminacion': 'Plástico, Vidrio/Metal',
            'frecuencia_limpieza': 'Diaria',
            'area_m2': 150,
            'fauna_afectada': 'Ninguna (área urbana)',
            'observaciones': 'Riesgo para niños por presencia de vidrios. Prioridad alta.',
            'ultima_inspeccion': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        },
        {
            'id': 'ZC-004',
            'nombre': 'Laguna Sur',
            'zona': 'Sur',
            'coordenadas_gps': '-8.115, -79.030',
            'nivel_riesgo': 'Crítico',
            'tipo_contaminacion': 'Plástico, Peligroso',
            'frecuencia_limpieza': 'Diaria',
            'area_m2': 320,
            'fauna_afectada': 'Aves acuáticas, Peces, Anfibios',
            'observaciones': 'Contaminación severa del cuerpo de agua. Afecta directamente fauna acuática.',
            'ultima_inspeccion': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        },
        {
            'id': 'ZC-005',
            'nombre': 'Estacionamiento Oeste',
            'zona': 'Oeste',
            'coordenadas_gps': '-8.110, -79.035',
            'nivel_riesgo': 'Medio',
            'tipo_contaminacion': 'Plástico, Papel/Cartón',
            'frecuencia_limpieza': 'Semanal',
            'area_m2': 200,
            'fauna_afectada': 'Aves',
            'observaciones': 'Residuos generados por visitantes. Necesita más contenedores.',
            'ultima_inspeccion': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        },
        {
            'id': 'ZC-006',
            'nombre': 'Área de Camping',
            'zona': 'Norte',
            'coordenadas_gps': '-8.107, -79.027',
            'nivel_riesgo': 'Alto',
            'tipo_contaminacion': 'Orgánico, Plástico, Vidrio/Metal',
            'frecuencia_limpieza': 'Diaria',
            'area_m2': 280,
            'fauna_afectada': 'Mamíferos, Aves',
            'observaciones': 'Residuos orgánicos atraen fauna silvestre. Riesgo de conflicto humano-animal.',
            'ultima_inspeccion': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')
        }
    ]
    
    df = pd.DataFrame(zonas_criticas)
    df.to_csv('dataset/zonas_criticas.csv', index=False, encoding='utf-8')
    print(f"✓ Dataset de zonas críticas creado: {len(df)} registros")
    return df


# ============================================
# 3. DATASET DE REPORTES VETERINARIOS
# ============================================

def generar_reportes_veterinarios():
    """Genera dataset de reportes veterinarios sobre impacto en fauna"""
    
    reportes = []
    fecha_inicio = datetime.now() - timedelta(days=180)
    
    especies = [
        'Ardilla común', 'Paloma doméstica', 'Garza blanca', 'Iguana verde',
        'Pato silvestre', 'Tortuga de agua', 'Conejo silvestre', 'Zorro gris'
    ]
    
    tipos_afectacion = [
        'Ingestión de plástico',
        'Enredo en materiales',
        'Intoxicación por residuos',
        'Lesiones por vidrio/metal',
        'Alteración de hábitat',
        'Contaminación de fuente de agua'
    ]
    
    for i in range(50):  # 50 reportes veterinarios
        dias_atras = random.randint(0, 180)
        fecha = fecha_inicio + timedelta(days=dias_atras)
        
        especie = random.choice(especies)
        afectacion = random.choice(tipos_afectacion)
        
        # Severidad correlacionada con tipo de afectación
        if afectacion in ['Ingestión de plástico', 'Intoxicación por residuos', 'Lesiones por vidrio/metal']:
            severidad = random.choice(['Alta', 'Alta', 'Media'])
        else:
            severidad = random.choice(['Media', 'Baja', 'Baja'])
        
        reporte = {
            'id': f'VET-{i+1:03d}',
            'fecha': fecha.strftime('%Y-%m-%d'),
            'especie': especie,
            'tipo_afectacion': afectacion,
            'severidad': severidad,
            'zona': random.choice(['Norte', 'Sur', 'Este', 'Oeste', 'Centro']),
            'numero_individuos': random.randint(1, 5),
            'tratamiento_aplicado': random.choice([True, False]),
            'recuperacion': random.choice(['Completa', 'Parcial', 'En proceso', 'No recuperado']),
            'observaciones': f'Caso de {afectacion.lower()} en {especie.lower()}. Requiere monitoreo continuo.',
            'veterinario': random.choice(['Dr. García', 'Dra. Martínez', 'Dr. López', 'Dra. Rodríguez'])
        }
        
        reportes.append(reporte)
    
    df = pd.DataFrame(reportes)
    df.to_csv('dataset/reportes_veterinarios.csv', index=False, encoding='utf-8')
    print(f"✓ Dataset de reportes veterinarios creado: {len(df)} registros")
    return df


# ============================================
# 4. DATASET DE ACTIVIDADES COMUNITARIAS
# ============================================

def generar_actividades_comunitarias():
    """Genera dataset de actividades de sensibilización comunitaria"""
    
    actividades = []
    fecha_inicio = datetime.now() - timedelta(days=180)
    
    tipos_actividad = [
        'Jornada de limpieza',
        'Taller educativo',
        'Charla de sensibilización',
        'Campaña de reciclaje',
        'Actividad con escuelas',
        'Evento comunitario'
    ]
    
    for i in range(35):  # 35 actividades
        dias_atras = random.randint(0, 180)
        fecha = fecha_inicio + timedelta(days=dias_atras)
        
        tipo = random.choice(tipos_actividad)
        participantes = random.randint(15, 120)
        
        # Residuos recolectados solo para jornadas de limpieza
        residuos_kg = round(random.uniform(50, 300), 2) if tipo == 'Jornada de limpieza' else 0
        
        actividad = {
            'id': f'ACT-{i+1:03d}',
            'fecha': fecha.strftime('%Y-%m-%d'),
            'tipo_actividad': tipo,
            'titulo': f'{tipo} - {fecha.strftime("%B %Y")}',
            'participantes': participantes,
            'zona': random.choice(['Norte', 'Sur', 'Este', 'Oeste', 'Centro', 'Todo el parque']),
            'duracion_horas': random.randint(2, 6),
            'residuos_recolectados_kg': residuos_kg,
            'organizador': random.choice(['Municipalidad', 'ONG Ambiental', 'Escuela Local', 'Comunidad']),
            'satisfaccion': round(random.uniform(3.5, 5.0), 1),
            'observaciones': f'Actividad exitosa con {participantes} participantes. Alto nivel de compromiso comunitario.'
        }
        
        actividades.append(actividad)
    
    df = pd.DataFrame(actividades)
    df.to_csv('dataset/actividades_comunitarias.csv', index=False, encoding='utf-8')
    print(f"✓ Dataset de actividades comunitarias creado: {len(df)} registros")
    return df


# ============================================
# 5. DATASET DE ENCUESTAS
# ============================================

def generar_encuestas():
    """Genera dataset de respuestas de encuestas ciudadanas"""
    
    respuestas = []
    fecha_inicio = datetime.now() - timedelta(days=90)
    
    for i in range(150):  # 150 encuestas
        dias_atras = random.randint(0, 90)
        fecha = fecha_inicio + timedelta(days=dias_atras)
        
        # Respuestas con distribución realista
        respuesta = {
            'id': f'ENC-{i+1:04d}',
            'fecha': fecha.strftime('%Y-%m-%d'),
            'edad': random.choice(['18-25', '26-35', '36-45', '46-55', '56+']),
            'frecuencia_visita': random.choice(['Diaria', 'Semanal', 'Mensual', 'Ocasional']),
            'percepcion_limpieza': random.randint(1, 5),
            'conoce_zonas_criticas': random.choice(['Sí', 'No']),
            'ha_participado_limpieza': random.choice(['Sí', 'No', 'No']),
            'dispuesto_voluntario': random.choice(['Sí', 'Sí', 'Tal vez', 'No']),
            'principal_problema': random.choice([
                'Falta de contenedores',
                'Falta de conciencia ciudadana',
                'Poca frecuencia de limpieza',
                'Acumulación en zonas específicas',
                'Falta de señalización'
            ]),
            'sugerencias': random.choice([
                'Más contenedores de reciclaje',
                'Campañas educativas',
                'Mayor vigilancia',
                'Jornadas de limpieza regulares',
                'Mejor señalización'
            ])
        }
        
        respuestas.append(respuesta)
    
    df = pd.DataFrame(respuestas)
    df.to_csv('dataset/encuestas_ciudadanas.csv', index=False, encoding='utf-8')
    print(f"✓ Dataset de encuestas ciudadanas creado: {len(df)} registros")
    return df


# ============================================
# EJECUTAR GENERACIÓN
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("GENERANDO DATASETS PARA SISTEMA PARQUE LA AMISTAD")
    print("=" * 60)
    print()
    
    df_residuos = generar_residuos()
    df_zonas = generar_zonas_criticas()
    df_veterinarios = generar_reportes_veterinarios()
    df_actividades = generar_actividades_comunitarias()
    df_encuestas = generar_encuestas()
    
    print()
    print("=" * 60)
    print("RESUMEN DE DATASETS GENERADOS")
    print("=" * 60)
    print(f"Residuos: {len(df_residuos)} registros")
    print(f"Zonas Críticas: {len(df_zonas)} registros")
    print(f"Reportes Veterinarios: {len(df_veterinarios)} registros")
    print(f"Actividades Comunitarias: {len(df_actividades)} registros")
    print(f"Encuestas Ciudadanas: {len(df_encuestas)} registros")
    print()
    print("✓ Todos los datasets han sido generados exitosamente")
    print("✓ Archivos guardados en la carpeta 'dataset/'")
