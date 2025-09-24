import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import re
import logging
import os
from typing import Optional, Dict, List, Tuple
import io
from PIL import Image
import base64

try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    st.warning("⚠️ Folium no está disponible. Las funciones de mapas estarán deshabilitadas.")

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """Configuración centralizada del sistema"""
    ARCHIVO_RESIDUOS = "residuos_parque.csv"
    ARCHIVO_ZONAS_CRITICAS = "zonas_criticas.csv"
    ARCHIVO_ENCUESTAS = "encuestas_parque.csv"
    ARCHIVO_BACKUP = "backup_residuos.csv"
    
    TIPOS_RESIDUOS = ["Plástico", "Orgánico", "Vidrio/Metal", "Papel/Cartón", "Otros"]
    ZONAS_PARQUE = ["Norte", "Sur", "Este", "Oeste", "Centro"]
    NIVELES_RIESGO = ["Bajo", "Medio", "Alto"]
    
    COORDENADAS_CENTRO = (-8.1125, -79.0275)
    MAX_TAMAÑO_IMAGEN = 5 * 1024 * 1024  # 5MB
    FORMATOS_IMAGEN = ['jpg', 'jpeg', 'png', 'gif']

class DatasetManager:
    """Gestor de datasets del sistema"""
    
    @staticmethod
    def crear_datasets_iniciales():
        """Crea los datasets iniciales con datos de ejemplo"""
        
        # Dataset 1: Residuos del parque
        residuos_data = {
            'ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Zona': ['Norte', 'Sur', 'Oeste', 'Este', 'Centro', 'Norte', 'Sur', 'Este', 'Oeste', 'Centro'],
            'Ubicación (GPS)': [
                '-8.111, -79.028', '-8.112, -79.029', '-8.113, -79.027', 
                '-8.114, -79.026', '-8.115, -79.025', '-8.116, -79.024',
                '-8.117, -79.023', '-8.118, -79.022', '-8.119, -79.021', '-8.120, -79.020'
            ],
            'Tipo de residuo': [
                'Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Otros',
                'Plástico', 'Orgánico', 'Papel/Cartón', 'Vidrio/Metal', 'Otros'
            ],
            'Peso estimado (kg)': [5.2, 3.1, 1.8, 2.4, 0.9, 4.5, 2.8, 3.2, 1.5, 2.1],
            'Fecha de registro': [
                '2025-09-05', '2025-09-05', '2025-09-05', '2025-09-06', '2025-09-06',
                '2025-09-07', '2025-09-07', '2025-09-08', '2025-09-08', '2025-09-09'
            ],
            'Observaciones': [
                'Cerca de juegos infantiles',
                'Restos de comida y hojas acumuladas',
                'Botellas rotas junto a la banca',
                'Papeles cerca de la entrada principal',
                'Desechos varios dispersos en zona central',
                'Bolsas plásticas en área verde',
                'Residuos orgánicos bajo los árboles',
                'Cartones mojados por la lluvia',
                'Latas de bebidas en sendero',
                'Colillas y envolturas pequeñas'
            ]
        }
        
        # Dataset 2: Zonas críticas
        zonas_criticas_data = {
            'Codigo de Zona': ['Z1', 'Z2', 'Z3', 'Z4', 'Z5'],
            'Sector del Parque': [
                'Area verde con plantas',
                'Cesped lateral',
                'Cerca de bancas',
                'Zona junto a tacho',
                'Sendero principal'
            ],
            'Descripcion de Residuos': [
                'Escombros y restos de construccion mezclados con basura comun',
                'Plasticos y papeles dispersos en el cesped',
                'Botellas, envolturas y residuos de comida en bancas',
                'Desechos acumulados en el suelo a pesar de la presencia de tacho cercano',
                'Residuos esparcidos a lo largo del sendero principal'
            ],
            'Tipo de Residuos Predominantes': ['Inorganicos', 'Plasticos/Papel', 'Organicos/Inorganicos', 'Mixto', 'Plasticos'],
            'Nivel de Riesgo': ['Alto', 'Medio', 'Medio', 'Bajo', 'Medio'],
            'Observaciones': [
                'Riesgo de proliferacion de insectos y deterioro del area verde',
                'Afecta la estetica y puede atraer animales',
                'Zona de transito de personas y animales domesticos',
                'Indica problemas en el uso adecuado de tachos de basura',
                'Requiere limpieza frecuente por alto tráfico'
            ]
        }
        
        # Dataset 3: Encuestas (datos resumidos)
        encuestas_data = {
            'ID_Respuesta': list(range(1, 16)),
            'Frecuencia_Visita': ['Casi nunca'] * 8 + ['A veces'] * 4 + ['Pocas veces'] * 3,
            'Funcion_Ambiental': ['Sí'] * 12 + ['No'] * 3,
            'Refleja_Educacion': ['No', 'Sí', 'Sí', 'No', 'Sí', 'Sí', 'Sí', 'No', 'Sí', 'No', 'Sí', 'Sí', 'No', 'Sí', 'Sí'],
            'Eventos_Generan_Residuos': ['No', 'Sí'] * 7 + ['Sí'],
            'Tachos_Bien_Distribuidos': ['Sí'] * 12 + ['No'] * 3,
            'Sistema_Gestion_Mejoraria': ['Sí'] * 14 + ['No'],
            'Campañas_Mascotas': ['Sí'] * 15,
            'Proyecto_Cambio_Positivo': ['Sí'] * 14 + ['No'],
            'Dispuesto_Promover': ['Sí'] * 10 + ['Tal vez'] * 5
        }
        
        # Crear DataFrames
        df_residuos = pd.DataFrame(residuos_data)
        df_zonas = pd.DataFrame(zonas_criticas_data)
        df_encuestas = pd.DataFrame(encuestas_data)
        
        # Guardar datasets
        df_residuos.to_csv(Config.ARCHIVO_RESIDUOS, index=False)
        df_zonas.to_csv(Config.ARCHIVO_ZONAS_CRITICAS, index=False)
        df_encuestas.to_csv(Config.ARCHIVO_ENCUESTAS, index=False)
        
        return df_residuos, df_zonas, df_encuestas

class ValidadorDatos:
    """Validador de datos del sistema"""
    
    @staticmethod
    def validar_coordenadas_gps(coordenadas: str) -> bool:
        """Valida formato de coordenadas GPS"""
        if not coordenadas or not coordenadas.strip():
            return False
        
        patron = r'^-?\d+\.?\d*\s*,\s*-?\d+\.?\d*$'
        return bool(re.match(patron, coordenadas.strip()))
    
    @staticmethod
    def validar_imagen(archivo_imagen) -> Tuple[bool, str]:
        """Valida archivo de imagen"""
        if archivo_imagen is None:
            return True, ""
        
        try:
            # Verificar tamaño
            if archivo_imagen.size > Config.MAX_TAMAÑO_IMAGEN:
                return False, f"La imagen es muy grande. Máximo {Config.MAX_TAMAÑO_IMAGEN/1024/1024:.1f}MB"
            
            # Verificar formato
            extension = archivo_imagen.name.split('.')[-1].lower()
            if extension not in Config.FORMATOS_IMAGEN:
                return False, f"Formato no válido. Use: {', '.join(Config.FORMATOS_IMAGEN)}"
            
            # Verificar que se puede abrir
            Image.open(archivo_imagen)
            return True, ""
            
        except Exception as e:
            return False, f"Error al procesar imagen: {str(e)}"
    
    @staticmethod
    def validar_peso(peso: float) -> bool:
        """Valida que el peso esté en un rango razonable"""
        return 0.1 <= peso <= 1000.0

class GestorDatos:
    """Gestor principal de datos"""
    
    @staticmethod
    def cargar_datos() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Carga todos los datasets"""
        try:
            # Verificar si existen los archivos, si no, crearlos
            if not all(os.path.exists(archivo) for archivo in [
                Config.ARCHIVO_RESIDUOS, 
                Config.ARCHIVO_ZONAS_CRITICAS, 
                Config.ARCHIVO_ENCUESTAS
            ]):
                logger.info("Creando datasets iniciales...")
                return DatasetManager.crear_datasets_iniciales()
            
            df_residuos = pd.read_csv(Config.ARCHIVO_RESIDUOS)
            df_zonas = pd.read_csv(Config.ARCHIVO_ZONAS_CRITICAS)
            df_encuestas = pd.read_csv(Config.ARCHIVO_ENCUESTAS)
            
            if df_residuos.empty or df_zonas.empty or df_encuestas.empty:
                logger.warning("Algunos datasets están vacíos, recreando...")
                return DatasetManager.crear_datasets_iniciales()
            
            return df_residuos, df_zonas, df_encuestas
            
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            st.error(f"Error al cargar datos: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    @staticmethod
    def crear_backup():
        """Crea backup de los datos"""
        try:
            if os.path.exists(Config.ARCHIVO_RESIDUOS):
                df = pd.read_csv(Config.ARCHIVO_RESIDUOS)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = f"backup_residuos_{timestamp}.csv"
                df.to_csv(backup_file, index=False)
                logger.info(f"Backup creado: {backup_file}")
                return backup_file
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return None

class VisualizadorDatos:
    """Clase para visualización de datos"""
    
    @staticmethod
    def crear_mapa_residuos(df_residuos: pd.DataFrame, df_zonas: pd.DataFrame):
        """Crea mapa interactivo con residuos y zonas críticas"""
        if not FOLIUM_AVAILABLE:
            st.error("🗺️ Funcionalidad de mapas no disponible. Instale folium para habilitar mapas.")
            return None
        
        try:
            mapa = folium.Map(
                location=Config.COORDENADAS_CENTRO,
                zoom_start=16,
                tiles='OpenStreetMap'
            )
            
            # Agregar marcadores de residuos
            for _, row in df_residuos.iterrows():
                try:
                    coords = row['Ubicación (GPS)'].split(',')
                    if len(coords) != 2:
                        continue
                        
                    lat, lon = float(coords[0].strip()), float(coords[1].strip())
                    
                    # Color según tipo de residuo
                    color_map = {
                        'Plástico': 'blue',
                        'Orgánico': 'green',
                        'Vidrio/Metal': 'red',
                        'Papel/Cartón': 'orange',
                        'Otros': 'purple'
                    }
                    
                    folium.Marker(
                        [lat, lon],
                        popup=f"""
                        <b>ID:</b> {row['ID']}<br>
                        <b>Zona:</b> {row['Zona']}<br>
                        <b>Tipo:</b> {row['Tipo de residuo']}<br>
                        <b>Peso:</b> {row['Peso estimado (kg)']} kg<br>
                        <b>Fecha:</b> {row['Fecha de registro']}<br>
                        <b>Observaciones:</b> {row['Observaciones']}
                        """,
                        tooltip=f"Residuo {row['ID']} - {row['Tipo de residuo']}",
                        icon=folium.Icon(
                            color=color_map.get(row['Tipo de residuo'], 'gray'),
                            icon='trash'
                        )
                    ).add_to(mapa)
                    
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error procesando coordenadas para residuo {row['ID']}: {e}")
                    continue
            
            return mapa
            
        except Exception as e:
            logger.error(f"Error creando mapa: {e}")
            st.error(f"Error al crear mapa: {e}")
            return None
    
    @staticmethod
    def crear_dashboard_metricas(df_residuos: pd.DataFrame, df_zonas: pd.DataFrame, df_encuestas: pd.DataFrame):
        """Crea dashboard con métricas principales"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_residuos = len(df_residuos) if not df_residuos.empty else 0
            st.metric("🗑️ Total Residuos", total_residuos)
        
        with col2:
            peso_total = df_residuos['Peso estimado (kg)'].sum() if not df_residuos.empty else 0
            st.metric("⚖️ Peso Total", f"{peso_total:.1f} kg")
        
        with col3:
            zonas_criticas = len(df_zonas[df_zonas['Nivel de Riesgo'] == 'Alto']) if not df_zonas.empty else 0
            st.metric("⚠️ Zonas Críticas", zonas_criticas)
        
        with col4:
            if not df_encuestas.empty:
                satisfaccion = (df_encuestas['Sistema_Gestion_Mejoraria'] == 'Sí').mean() * 100
            else:
                satisfaccion = 0
            st.metric("👥 Apoyo al Proyecto", f"{satisfaccion:.0f}%")

    @staticmethod
    def crear_mapa_alternativo(df_residuos: pd.DataFrame):
        """Crea visualización alternativa cuando folium no está disponible"""
        st.subheader("📍 Ubicaciones de Residuos (Vista de Coordenadas)")
        
        if df_residuos.empty:
            st.info("No hay datos de residuos para mostrar")
            return
        
        # Extraer coordenadas para visualización
        coords_data = []
        for _, row in df_residuos.iterrows():
            try:
                coords = row['Ubicación (GPS)'].split(',')
                if len(coords) == 2:
                    lat, lon = float(coords[0].strip()), float(coords[1].strip())
                    coords_data.append({
                        'ID': row['ID'],
                        'Latitud': lat,
                        'Longitud': lon,
                        'Tipo': row['Tipo de residuo'],
                        'Zona': row['Zona'],
                        'Peso': row['Peso estimado (kg)']
                    })
            except (ValueError, IndexError):
                continue
        
        if coords_data:
            df_coords = pd.DataFrame(coords_data)
            
            # Gráfico de dispersión como alternativa al mapa
            fig = px.scatter(
                df_coords,
                x='Longitud',
                y='Latitud',
                color='Tipo',
                size='Peso',
                hover_data=['ID', 'Zona'],
                title="Distribución Geográfica de Residuos",
                labels={'Longitud': 'Longitud (°)', 'Latitud': 'Latitud (°)'}
            )
            
            fig.update_layout(
                xaxis_title="Longitud",
                yaxis_title="Latitud",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de coordenadas
            st.subheader("📋 Tabla de Coordenadas")
            st.dataframe(df_coords, use_container_width=True)
        else:
            st.warning("No se pudieron procesar las coordenadas GPS")

def main():
    """Función principal de la aplicación"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="Sistema de Gestión de Residuos - Parque La Amistad",
        page_icon="🌳",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Título principal
    st.title("🌳 Sistema de Gestión de Residuos - Parque La Amistad")
    st.markdown("### Proyecto 'Amistad Sostenible' - Gestión Inteligente de Residuos")
    st.markdown("---")
    
    try:
        df_residuos, df_zonas_criticas, df_encuestas = GestorDatos.cargar_datos()
    except Exception as e:
        st.error(f"Error crítico al cargar datos: {e}")
        st.stop()
    
    # Sidebar para navegación
    st.sidebar.title("📊 Navegación")
    st.sidebar.markdown("---")
    
    opcion = st.sidebar.selectbox(
        "Seleccione una opción:",
        [
            "🏠 Dashboard Principal",
            "📍 Mapa Interactivo", 
            "📊 Análisis de Residuos",
            "⚠️ Zonas Críticas",
            "📋 Encuestas Comunitarias",
            "➕ Registrar Residuo",
            "🔍 Consultar Datos",
            "✏️ Editar Registros",
            "📈 Reportes y Estadísticas"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Información del Sistema")
    st.sidebar.info(f"""
    **Registros:** {len(df_residuos)}
    **Zonas Críticas:** {len(df_zonas_criticas)}
    **Encuestas:** {len(df_encuestas)}
    **Mapas:** {'✅' if FOLIUM_AVAILABLE else '❌'}
    """)

    # Dashboard Principal
    if opcion == "🏠 Dashboard Principal":
        st.header("🏠 Dashboard Principal")
        
        # Métricas principales
        VisualizadorDatos.crear_dashboard_metricas(df_residuos, df_zonas_criticas, df_encuestas)
        
        st.markdown("---")
        
        if df_residuos.empty:
            st.warning("⚠️ No hay datos de residuos disponibles")
        else:
            # Gráficos en columnas
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Distribución por Tipo de Residuo")
                fig_tipos = px.pie(
                    df_residuos, 
                    names='Tipo de residuo',
                    title="Tipos de Residuos Registrados",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_tipos, use_container_width=True)
            
            with col2:
                st.subheader("🗺️ Distribución por Zona")
                zona_counts = df_residuos.groupby('Zona').size().reset_index(name='Cantidad')
                fig_zonas = px.bar(
                    zona_counts,
                    x='Zona', y='Cantidad',
                    title="Residuos por Zona del Parque",
                    color='Cantidad',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_zonas, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📋 Resumen Ejecutivo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Objetivos del Proyecto:**")
            st.markdown("""
            - Monitoreo sistemático de residuos
            - Identificación de zonas críticas
            - Participación comunitaria activa
            - Mejora continua del sistema de gestión
            """)
        
        with col2:
            st.markdown("**📈 Indicadores Clave:**")
            if not df_residuos.empty:
                tipo_mas_comun = df_residuos['Tipo de residuo'].mode().iloc[0]
                zona_mas_afectada = df_residuos['Zona'].mode().iloc[0]
                st.markdown(f"""
                - Tipo más común: **{tipo_mas_comun}**
                - Zona más afectada: **{zona_mas_afectada}**
                - Peso promedio: **{df_residuos['Peso estimado (kg)'].mean():.1f} kg**
                """)
    
    # Mapa Interactivo
    elif opcion == "📍 Mapa Interactivo":
        st.header("📍 Mapa Interactivo de Residuos")
        
        if FOLIUM_AVAILABLE and not df_residuos.empty:
            mapa = VisualizadorDatos.crear_mapa_residuos(df_residuos, df_zonas_criticas)
            if mapa:
                st_folium(mapa, width=700, height=500)
                st.info("💡 Haga clic en los marcadores para ver detalles de cada residuo")
        else:
            VisualizadorDatos.crear_mapa_alternativo(df_residuos)


    # Registrar Residuo
    elif opcion == "➕ Registrar Residuo":
        st.header("➕ Registrar Nuevo Residuo")
        
        with st.form("form_registro"):
            col1, col2 = st.columns(2)
            
            with col1:
                zona = st.selectbox("🗺️ Zona del Parque", Config.ZONAS_PARQUE)
                tipo_residuo = st.selectbox("🗑️ Tipo de Residuo", Config.TIPOS_RESIDUOS)
                peso = st.number_input("⚖️ Peso Estimado (kg)", min_value=0.1, max_value=100.0, step=0.1, value=1.0)
                coordenadas = st.text_input("📍 Coordenadas GPS", placeholder="-8.111, -79.028", help="Formato: latitud, longitud")
            
            with col2:
                fecha = st.date_input("📅 Fecha de Registro", value=date.today())
                observaciones = st.text_area("📝 Observaciones", height=100, placeholder="Describa la ubicación y condiciones del residuo...")
                imagen = st.file_uploader("📷 Imagen (opcional)", type=Config.FORMATOS_IMAGEN)
            
            if imagen:
                st.subheader("🖼️ Preview de Imagen")
                st.image(imagen, caption="Imagen a registrar", width=300)
            
            submitted = st.form_submit_button("🗂️ Registrar Residuo", type="primary")
            
            if submitted:
                errores = []
                
                if not ValidadorDatos.validar_coordenadas_gps(coordenadas):
                    errores.append("❌ Formato de coordenadas GPS inválido. Use formato: -8.111, -79.028")
                
                if not ValidadorDatos.validar_peso(peso):
                    errores.append("❌ El peso debe estar entre 0.1 y 1000.0 kg")
                
                valido_imagen, error_imagen = ValidadorDatos.validar_imagen(imagen)
                if not valido_imagen:
                    errores.append(f"❌ {error_imagen}")
                
                if not observaciones.strip():
                    errores.append("❌ Las observaciones son obligatorias")
                
                if errores:
                    for error in errores:
                        st.error(error)
                else:
                    try:
                        # Crear backup
                        backup_file = GestorDatos.crear_backup()
                        
                        # Nuevo registro
                        nuevo_id = df_residuos['ID'].max() + 1 if not df_residuos.empty else 1
                        
                        nuevo_registro = {
                            'ID': nuevo_id,
                            'Zona': zona,
                            'Ubicación (GPS)': coordenadas.strip(),
                            'Tipo de residuo': tipo_residuo,
                            'Peso estimado (kg)': peso,
                            'Fecha de registro': fecha.strftime('%Y-%m-%d'),
                            'Observaciones': observaciones.strip()
                        }
                        
                        # Agregar al DataFrame
                        df_residuos = pd.concat([df_residuos, pd.DataFrame([nuevo_registro])], ignore_index=True)
                        
                        # Guardar
                        df_residuos.to_csv(Config.ARCHIVO_RESIDUOS, index=False)
                        
                        st.success(f"✅ Residuo registrado exitosamente con ID: {nuevo_id}")
                        if backup_file:
                            st.info(f"💾 Backup creado: {backup_file}")
                        
                        logger.info(f"Nuevo residuo registrado: ID {nuevo_id}")
                        
                        if st.button("➕ Registrar Otro Residuo"):
                            st.experimental_rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al registrar: {e}")
                        logger.error(f"Error en registro: {e}")


if __name__ == "__main__":
    main()
