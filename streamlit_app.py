import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from datetime import datetime, date
import re
import logging
import os
from typing import Optional, Dict, List, Tuple
import io
from PIL import Image
import base64

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
            'ID': [1, 2, 3, 4, 5],
            'Zona': ['Norte', 'Sur', 'Oeste', 'Este', 'Centro'],
            'Ubicación (GPS)': ['-8.111, -79.028', '-8.112, -79.029', '-8.113, -79.027', '-8.114, -79.026', '-8.115, -79.025'],
            'Tipo de residuo': ['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Otros'],
            'Peso estimado (kg)': [5.2, 3.1, 1.8, 2.4, 0.9],
            'Fecha de registro': ['2025-09-05', '2025-09-05', '2025-09-05', '2025-09-06', '2025-09-06'],
            'Observaciones': [
                'Cerca de juegos infantiles',
                'Restos de comida y hojas acumuladas',
                'Botellas rotas junto a la banca',
                'Papeles cerca de la entrada principal',
                'Desechos varios dispersos en zona central'
            ]
        }
        
        # Dataset 2: Zonas críticas
        zonas_criticas_data = {
            'Codigo de Zona': ['Z1', 'Z2', 'Z3', 'Z4'],
            'Sector del Parque': [
                'Area verde con plantas',
                'Cesped lateral',
                'Cerca de bancas',
                'Zona junto a tacho'
            ],
            'Descripcion de Residuos': [
                'Escombros y restos de construccion mezclados con basura comun',
                'Plasticos y papeles dispersos en el cesped',
                'Botellas, envolturas y residuos de comida en bancas',
                'Desechos acumulados en el suelo a pesar de la presencia de tacho cercano'
            ],
            'Tipo de Residuos Predominantes': ['Inorganicos', 'Plasticos/Papel', 'Organicos/Inorganicos', 'Mixto'],
            'Nivel de Riesgo': ['Alto', 'Medio', 'Medio', 'Bajo'],
            'Observaciones': [
                'Riesgo de proliferacion de insectos y deterioro del area verde',
                'Afecta la estetica y puede atraer animales',
                'Zona de transito de personas y animales domesticos',
                'Indica problemas en el uso adecuado de tachos de basura'
            ]
        }
        
        # Dataset 3: Encuestas (datos resumidos)
        encuestas_data = {
            'ID_Respuesta': list(range(1, 11)),
            'Frecuencia_Visita': ['Casi nunca'] * 7 + ['A veces', 'Pocas veces', 'Pocas veces'],
            'Funcion_Ambiental': ['Sí'] * 7 + ['No'] * 3,
            'Refleja_Educacion': ['No', 'Sí', 'Sí', 'No', 'Sí', 'Sí', 'Sí', 'No', 'Sí', 'No'],
            'Eventos_Generan_Residuos': ['No', 'Sí', 'Sí', 'Sí', 'Sí', 'Sí', 'No', 'No', 'Sí', 'Sí'],
            'Tachos_Bien_Distribuidos': ['Sí'] * 8 + ['No', 'No'],
            'Sistema_Gestion_Mejoraria': ['Sí'] * 9 + ['Sí'],
            'Campañas_Mascotas': ['Sí'] * 10,
            'Proyecto_Cambio_Positivo': ['Sí'] * 9 + ['Sí'],
            'Dispuesto_Promover': ['Sí'] * 6 + ['Tal vez'] * 4
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
        patron = r'^-?\d+\.?\d*,\s*-?\d+\.?\d*$'
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
                df.to_csv(Config.ARCHIVO_BACKUP, index=False)
                logger.info("Backup creado exitosamente")
        except Exception as e:
            logger.error(f"Error creando backup: {e}")

class VisualizadorDatos:
    """Clase para visualización de datos"""
    
    @staticmethod
    def crear_mapa_residuos(df_residuos: pd.DataFrame, df_zonas: pd.DataFrame) -> folium.Map:
        """Crea mapa interactivo con residuos y zonas críticas"""
        mapa = folium.Map(
            location=Config.COORDENADAS_CENTRO,
            zoom_start=16,
            tiles='OpenStreetMap'
        )
        
        # Agregar marcadores de residuos
        for _, row in df_residuos.iterrows():
            try:
                coords = row['Ubicación (GPS)'].split(',')
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
                
            except Exception as e:
                logger.warning(f"Error procesando coordenadas para residuo {row['ID']}: {e}")
        
        return mapa
    
    @staticmethod
    def crear_dashboard_metricas(df_residuos: pd.DataFrame, df_zonas: pd.DataFrame, df_encuestas: pd.DataFrame):
        """Crea dashboard con métricas principales"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_residuos = len(df_residuos)
            st.metric("Total Residuos", total_residuos)
        
        with col2:
            peso_total = df_residuos['Peso estimado (kg)'].sum()
            st.metric("Peso Total", f"{peso_total:.1f} kg")
        
        with col3:
            zonas_criticas = len(df_zonas[df_zonas['Nivel de Riesgo'] == 'Alto'])
            st.metric("Zonas Críticas", zonas_criticas)
        
        with col4:
            satisfaccion = (df_encuestas['Sistema_Gestion_Mejoraria'] == 'Sí').mean() * 100
            st.metric("Apoyo al Proyecto", f"{satisfaccion:.0f}%")

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
    st.markdown("---")
    
    # Cargar datos
    df_residuos, df_zonas_criticas, df_encuestas = GestorDatos.cargar_datos()
    
    if df_residuos.empty:
        st.error("No se pudieron cargar los datos. Verifique los archivos.")
        return
    
    # Sidebar para navegación
    st.sidebar.title("📊 Navegación")
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
            "📈 Reportes y Estadísticas"
        ]
    )
    
    # Dashboard Principal
    if opcion == "🏠 Dashboard Principal":
        st.header("Dashboard Principal")
        
        # Métricas principales
        VisualizadorDatos.crear_dashboard_metricas(df_residuos, df_zonas_criticas, df_encuestas)
        
        st.markdown("---")
        
        # Gráficos en columnas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Distribución por Tipo de Residuo")
            fig_tipos = px.pie(
                df_residuos, 
                names='Tipo de residuo',
                title="Tipos de Residuos Registrados"
            )
            st.plotly_chart(fig_tipos, use_container_width=True)
        
        with col2:
            st.subheader("🗺️ Distribución por Zona")
            fig_zonas = px.bar(
                df_residuos.groupby('Zona').size().reset_index(name='Cantidad'),
                x='Zona', y='Cantidad',
                title="Residuos por Zona del Parque"
            )
            st.plotly_chart(fig_zonas, use_container_width=True)
    
    # Mapa Interactivo
    elif opcion == "📍 Mapa Interactivo":
        st.header("Mapa Interactivo de Residuos")
        
        mapa = VisualizadorDatos.crear_mapa_residuos(df_residuos, df_zonas_criticas)
        st_folium(mapa, width=700, height=500)
        
        st.info("💡 Haga clic en los marcadores para ver detalles de cada residuo")
    
    # Análisis de Residuos
    elif opcion == "📊 Análisis de Residuos":
        st.header("Análisis Detallado de Residuos")
        
        # Análisis temporal
        df_residuos['Fecha de registro'] = pd.to_datetime(df_residuos['Fecha de registro'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Tendencia Temporal")
            residuos_por_fecha = df_residuos.groupby('Fecha de registro').size().reset_index(name='Cantidad')
            fig_temporal = px.line(
                residuos_por_fecha,
                x='Fecha de registro', y='Cantidad',
                title="Residuos Registrados por Fecha"
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
        
        with col2:
            st.subheader("⚖️ Peso por Tipo de Residuo")
            peso_por_tipo = df_residuos.groupby('Tipo de residuo')['Peso estimado (kg)'].sum().reset_index()
            fig_peso = px.bar(
                peso_por_tipo,
                x='Tipo de residuo', y='Peso estimado (kg)',
                title="Peso Total por Tipo de Residuo"
            )
            st.plotly_chart(fig_peso, use_container_width=True)
    
    # Zonas Críticas
    elif opcion == "⚠️ Zonas Críticas":
        st.header("Análisis de Zonas Críticas")
        
        # Mostrar tabla de zonas críticas
        st.subheader("📋 Registro de Zonas Críticas")
        st.dataframe(df_zonas_criticas, use_container_width=True)
        
        # Análisis por nivel de riesgo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚠️ Distribución por Nivel de Riesgo")
            fig_riesgo = px.pie(
                df_zonas_criticas,
                names='Nivel de Riesgo',
                title="Zonas por Nivel de Riesgo",
                color_discrete_map={'Alto': 'red', 'Medio': 'orange', 'Bajo': 'green'}
            )
            st.plotly_chart(fig_riesgo, use_container_width=True)
        
        with col2:
            st.subheader("🏷️ Tipos de Residuos Predominantes")
            fig_tipos_criticos = px.bar(
                df_zonas_criticas.groupby('Tipo de Residuos Predominantes').size().reset_index(name='Cantidad'),
                x='Tipo de Residuos Predominantes', y='Cantidad',
                title="Tipos de Residuos en Zonas Críticas"
            )
            st.plotly_chart(fig_tipos_criticos, use_container_width=True)
    
    # Encuestas Comunitarias
    elif opcion == "📋 Encuestas Comunitarias":
        st.header("Análisis de Encuestas Comunitarias")
        
        # Métricas de encuestas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_respuestas = len(df_encuestas)
            st.metric("Total Respuestas", total_respuestas)
        
        with col2:
            apoyo_proyecto = (df_encuestas['Proyecto_Cambio_Positivo'] == 'Sí').mean() * 100
            st.metric("Apoyo al Proyecto", f"{apoyo_proyecto:.0f}%")
        
        with col3:
            dispuestos_promover = (df_encuestas['Dispuesto_Promover'] == 'Sí').mean() * 100
            st.metric("Dispuestos a Promover", f"{dispuestos_promover:.0f}%")
        
        # Gráficos de análisis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Frecuencia de Visitas")
            fig_frecuencia = px.pie(
                df_encuestas,
                names='Frecuencia_Visita',
                title="Frecuencia de Visitas al Parque"
            )
            st.plotly_chart(fig_frecuencia, use_container_width=True)
        
        with col2:
            st.subheader("🗳️ Opiniones sobre Tachos de Basura")
            fig_tachos = px.pie(
                df_encuestas,
                names='Tachos_Bien_Distribuidos',
                title="¿Están bien distribuidos los tachos?"
            )
            st.plotly_chart(fig_tachos, use_container_width=True)
    
    # Registrar Residuo
    elif opcion == "➕ Registrar Residuo":
        st.header("Registrar Nuevo Residuo")
        
        with st.form("form_registro"):
            col1, col2 = st.columns(2)
            
            with col1:
                zona = st.selectbox("Zona del Parque", Config.ZONAS_PARQUE)
                tipo_residuo = st.selectbox("Tipo de Residuo", Config.TIPOS_RESIDUOS)
                peso = st.number_input("Peso Estimado (kg)", min_value=0.1, max_value=100.0, step=0.1)
                coordenadas = st.text_input("Coordenadas GPS", placeholder="-8.111, -79.028")
            
            with col2:
                fecha = st.date_input("Fecha de Registro", value=date.today())
                observaciones = st.text_area("Observaciones", height=100)
                imagen = st.file_uploader("Imagen (opcional)", type=Config.FORMATOS_IMAGEN)
            
            submitted = st.form_submit_button("🗂️ Registrar Residuo")
            
            if submitted:
                # Validaciones
                errores = []
                
                if not ValidadorDatos.validar_coordenadas_gps(coordenadas):
                    errores.append("Formato de coordenadas GPS inválido")
                
                valido_imagen, error_imagen = ValidadorDatos.validar_imagen(imagen)
                if not valido_imagen:
                    errores.append(error_imagen)
                
                if errores:
                    for error in errores:
                        st.error(error)
                else:
                    try:
                        # Crear backup
                        GestorDatos.crear_backup()
                        
                        # Nuevo registro
                        nuevo_id = df_residuos['ID'].max() + 1 if not df_residuos.empty else 1
                        
                        nuevo_registro = {
                            'ID': nuevo_id,
                            'Zona': zona,
                            'Ubicación (GPS)': coordenadas,
                            'Tipo de residuo': tipo_residuo,
                            'Peso estimado (kg)': peso,
                            'Fecha de registro': fecha.strftime('%Y-%m-%d'),
                            'Observaciones': observaciones
                        }
                        
                        # Agregar al DataFrame
                        df_residuos = pd.concat([df_residuos, pd.DataFrame([nuevo_registro])], ignore_index=True)
                        
                        # Guardar
                        df_residuos.to_csv(Config.ARCHIVO_RESIDUOS, index=False)
                        
                        st.success(f"✅ Residuo registrado exitosamente con ID: {nuevo_id}")
                        logger.info(f"Nuevo residuo registrado: ID {nuevo_id}")
                        
                        # Mostrar preview de imagen si existe
                        if imagen:
                            st.image(imagen, caption="Imagen registrada", width=300)
                        
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")
                        logger.error(f"Error en registro: {e}")
    
    # Consultar Datos
    elif opcion == "🔍 Consultar Datos":
        st.header("Consultar y Filtrar Datos")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_zona = st.multiselect("Filtrar por Zona", Config.ZONAS_PARQUE, default=Config.ZONAS_PARQUE)
        
        with col2:
            filtro_tipo = st.multiselect("Filtrar por Tipo", Config.TIPOS_RESIDUOS, default=Config.TIPOS_RESIDUOS)
        
        with col3:
            rango_fechas = st.date_input("Rango de Fechas", value=[date.today(), date.today()])
        
        # Aplicar filtros
        df_filtrado = df_residuos.copy()
        df_filtrado['Fecha de registro'] = pd.to_datetime(df_filtrado['Fecha de registro'])
        
        if filtro_zona:
            df_filtrado = df_filtrado[df_filtrado['Zona'].isin(filtro_zona)]
        
        if filtro_tipo:
            df_filtrado = df_filtrado[df_filtrado['Tipo de residuo'].isin(filtro_tipo)]
        
        if len(rango_fechas) == 2:
            fecha_inicio, fecha_fin = rango_fechas
            df_filtrado = df_filtrado[
                (df_filtrado['Fecha de registro'].dt.date >= fecha_inicio) &
                (df_filtrado['Fecha de registro'].dt.date <= fecha_fin)
            ]
        
        # Mostrar resultados
        st.subheader(f"📋 Resultados ({len(df_filtrado)} registros)")
        
        if not df_filtrado.empty:
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Botón de descarga
            csv = df_filtrado.to_csv(index=False)
            st.download_button(
                label="📥 Descargar datos filtrados",
                data=csv,
                file_name=f"residuos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No se encontraron registros con los filtros aplicados")
    
    # Reportes y Estadísticas
    elif opcion == "📈 Reportes y Estadísticas":
        st.header("Reportes y Estadísticas Avanzadas")
        
        # Estadísticas generales
        st.subheader("📊 Estadísticas Generales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Resumen de Residuos:**")
            st.write(f"- Total de registros: {len(df_residuos)}")
            st.write(f"- Peso total: {df_residuos['Peso estimado (kg)'].sum():.2f} kg")
            st.write(f"- Peso promedio: {df_residuos['Peso estimado (kg)'].mean():.2f} kg")
            st.write(f"- Tipo más común: {df_residuos['Tipo de residuo'].mode().iloc[0]}")
            st.write(f"- Zona más afectada: {df_residuos['Zona'].mode().iloc[0]}")
        
        with col2:
            st.write("**Resumen de Encuestas:**")
            st.write(f"- Total de respuestas: {len(df_encuestas)}")
            apoyo = (df_encuestas['Sistema_Gestion_Mejoraria'] == 'Sí').mean() * 100
            st.write(f"- Apoyo al sistema: {apoyo:.1f}%")
            promover = (df_encuestas['Dispuesto_Promover'] == 'Sí').mean() * 100
            st.write(f"- Dispuestos a promover: {promover:.1f}%")
            tachos = (df_encuestas['Tachos_Bien_Distribuidos'] == 'Sí').mean() * 100
            st.write(f"- Satisfacción con tachos: {tachos:.1f}%")
        
        st.markdown("---")
        
        # Gráfico combinado
        st.subheader("📈 Análisis Temporal y Comparativo")
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Residuos por Fecha', 'Peso por Zona', 'Nivel de Riesgo', 'Apoyo Comunitario'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"type": "pie"}, {"type": "pie"}]]
        )
        
        # Gráfico 1: Residuos por fecha
        df_residuos['Fecha de registro'] = pd.to_datetime(df_residuos['Fecha de registro'])
        residuos_fecha = df_residuos.groupby('Fecha de registro').size().reset_index(name='Cantidad')
        fig.add_trace(
            go.Scatter(x=residuos_fecha['Fecha de registro'], y=residuos_fecha['Cantidad'], name="Residuos"),
            row=1, col=1
        )
        
        # Gráfico 2: Peso por zona
        peso_zona = df_residuos.groupby('Zona')['Peso estimado (kg)'].sum().reset_index()
        fig.add_trace(
            go.Bar(x=peso_zona['Zona'], y=peso_zona['Peso estimado (kg)'], name="Peso"),
            row=1, col=2
        )
        
        # Gráfico 3: Nivel de riesgo
        riesgo_counts = df_zonas_criticas['Nivel de Riesgo'].value_counts()
        fig.add_trace(
            go.Pie(labels=riesgo_counts.index, values=riesgo_counts.values, name="Riesgo"),
            row=2, col=1
        )
        
        # Gráfico 4: Apoyo comunitario
        apoyo_counts = df_encuestas['Sistema_Gestion_Mejoraria'].value_counts()
        fig.add_trace(
            go.Pie(labels=apoyo_counts.index, values=apoyo_counts.values, name="Apoyo"),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
