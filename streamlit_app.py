import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, date
import numpy as np
from PIL import Image
import uuid
import re
from typing import Tuple, Optional, Dict, Any
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la página
st.set_page_config(
    page_title="Parque La Amistad - Gestión de Residuos Sólidos",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2d5a27;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    .success-msg {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
    .error-msg {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #dc3545;
    }
    .warning-msg {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #ffc107;
    }
    .info-msg {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# Configuración de rutas mejorada
class Config:
    DATASET_DIR = "dataset"
    RESIDUOS_CSV = os.path.join(DATASET_DIR, "residuos_parque.csv")
    ZONAS_CRITICAS_CSV = os.path.join(DATASET_DIR, "zonas_criticas.csv")
    ENCUESTAS_CSV = os.path.join(DATASET_DIR, "encuesta_respuestas.csv")
    IMAGES_DIR = os.path.join(DATASET_DIR, "evidencias")
    BACKUP_DIR = os.path.join(DATASET_DIR, "backups")
    
    # Constantes de validación
    ZONAS_VALIDAS = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']
    TIPOS_RESIDUO = ['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Textil', 'Electrónico', 'Peligroso', 'Otros']
    PESO_MIN = 0.1
    PESO_MAX = 1000.0
    IMAGEN_TIPOS = ['jpg', 'jpeg', 'png', 'webp']
    IMAGEN_MAX_SIZE = 10 * 1024 * 1024  # 10MB

# Crear directorios necesarios
def crear_directorios():
    """Crea todos los directorios necesarios para el sistema"""
    try:
        for directorio in [Config.DATASET_DIR, Config.IMAGES_DIR, Config.BACKUP_DIR]:
            os.makedirs(directorio, exist_ok=True)
        logger.info("Directorios creados exitosamente")
    except Exception as e:
        logger.error(f"Error creando directorios: {e}")
        st.error(f"Error al crear directorios del sistema: {e}")

# ==============================
# FUNCIONES DE VALIDACIÓN MEJORADAS
# ==============================

def validar_coordenadas_gps(coordenadas: str) -> Tuple[bool, str]:
    """Valida formato de coordenadas GPS"""
    if not coordenadas or not coordenadas.strip():
        return False, "Las coordenadas GPS son obligatorias"
    
    # Patrón para coordenadas GPS (formato: lat, lon)
    patron = r'^-?\d+\.?\d*\s*,\s*-?\d+\.?\d*$'
    if not re.match(patron, coordenadas.strip()):
        return False, "Formato de coordenadas inválido. Use: latitud, longitud (ej: -8.111, -79.028)"
    
    try:
        partes = coordenadas.split(',')
        lat = float(partes[0].strip())
        lon = float(partes[1].strip())
        
        if not (-90 <= lat <= 90):
            return False, "Latitud debe estar entre -90 y 90 grados"
        if not (-180 <= lon <= 180):
            return False, "Longitud debe estar entre -180 y 180 grados"
            
        return True, ""
    except (ValueError, IndexError):
        return False, "Error al procesar las coordenadas"

def validar_imagen(uploaded_file) -> Tuple[bool, str]:
    """Valida archivo de imagen subido"""
    if uploaded_file is None:
        return True, ""  # Imagen es opcional
    
    # Validar tipo de archivo
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in Config.IMAGEN_TIPOS:
        return False, f"Tipo de archivo no válido. Use: {', '.join(Config.IMAGEN_TIPOS)}"
    
    # Validar tamaño
    if uploaded_file.size > Config.IMAGEN_MAX_SIZE:
        return False, f"Archivo muy grande. Máximo: {Config.IMAGEN_MAX_SIZE // (1024*1024)}MB"
    
    return True, ""

def validar_registro_completo(zona: str, ubicacion: str, tipo_residuo: str, peso: float, fecha: date, imagen=None) -> Tuple[bool, str]:
    """Validación completa de un registro de residuo"""
    # Validar campos obligatorios
    if not zona or zona not in Config.ZONAS_VALIDAS:
        return False, f"Zona debe ser una de: {', '.join(Config.ZONAS_VALIDAS)}"
    
    if not tipo_residuo or tipo_residuo not in Config.TIPOS_RESIDUO:
        return False, f"Tipo de residuo debe ser uno de: {', '.join(Config.TIPOS_RESIDUO)}"
    
    if not peso or peso < Config.PESO_MIN or peso > Config.PESO_MAX:
        return False, f"Peso debe estar entre {Config.PESO_MIN} y {Config.PESO_MAX} kg"
    
    if not fecha or fecha > datetime.now().date():
        return False, "La fecha no puede ser futura"
    
    # Validar coordenadas GPS
    es_valido_gps, mensaje_gps = validar_coordenadas_gps(ubicacion)
    if not es_valido_gps:
        return False, mensaje_gps
    
    # Validar imagen si se proporciona
    es_valido_img, mensaje_img = validar_imagen(imagen)
    if not es_valido_img:
        return False, mensaje_img
    
    return True, ""

# ==============================
# FUNCIONES DE GESTIÓN DE DATOS MEJORADAS
# ==============================

def crear_backup_datos():
    """Crea backup de los datos antes de modificaciones importantes"""
    try:
        if os.path.exists(Config.RESIDUOS_CSV):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(Config.BACKUP_DIR, f"residuos_backup_{timestamp}.csv")
            
            df = pd.read_csv(Config.RESIDUOS_CSV, encoding='utf-8')
            df.to_csv(backup_path, index=False, encoding='utf-8')
            logger.info(f"Backup creado: {backup_path}")
            return True
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        return False

def inicializar_archivo_residuos():
    """Inicializa el archivo CSV de residuos con estructura mejorada"""
    try:
        if not os.path.exists(Config.RESIDUOS_CSV):
            df = pd.DataFrame(columns=[
                'ID', 'Zona', 'Ubicación (GPS)', 'Tipo de residuo', 
                'Peso estimado (kg)', 'Fecha de registro', 'Fecha de creación',
                'Observaciones', 'Ruta Imagen', 'Estado', 'Usuario'
            ])
            df.to_csv(Config.RESIDUOS_CSV, index=False, encoding='utf-8')
            logger.info("Archivo de residuos inicializado")
    except Exception as e:
        logger.error(f"Error inicializando archivo: {e}")
        st.error(f"Error al inicializar el sistema: {e}")

def cargar_datos_residuos() -> pd.DataFrame:
    """Carga los datos de residuos con manejo robusto de errores"""
    try:
        if not os.path.exists(Config.RESIDUOS_CSV):
            return pd.DataFrame()
        
        df = pd.read_csv(Config.RESIDUOS_CSV, encoding='utf-8')
        
        if df.empty:
            return df
        
        # Convertir fechas con manejo de errores
        for col in ['Fecha de registro', 'Fecha de creación']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Asegurar tipos de datos correctos
        if 'Peso estimado (kg)' in df.columns:
            df['Peso estimado (kg)'] = pd.to_numeric(df['Peso estimado (kg)'], errors='coerce')
        
        if 'ID' in df.columns:
            df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
        
        # Agregar columnas faltantes con valores por defecto
        columnas_requeridas = {
            'Estado': 'Activo',
            'Usuario': 'Sistema',
            'Fecha de creación': datetime.now()
        }
        
        for col, valor_default in columnas_requeridas.items():
            if col not in df.columns:
                df[col] = valor_default
        
        return df
        
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

def guardar_datos_residuos(df: pd.DataFrame) -> bool:
    """Guarda los datos con validación y backup"""
    try:
        # Crear backup antes de guardar
        crear_backup_datos()
        
        # Validar DataFrame antes de guardar
        if df.empty:
            logger.warning("Intentando guardar DataFrame vacío")
            return False
        
        # Asegurar que las columnas requeridas existen
        columnas_requeridas = [
            'ID', 'Zona', 'Ubicación (GPS)', 'Tipo de residuo', 
            'Peso estimado (kg)', 'Fecha de registro'
        ]
        
        for col in columnas_requeridas:
            if col not in df.columns:
                logger.error(f"Columna requerida faltante: {col}")
                return False
        
        # Guardar con encoding UTF-8
        df.to_csv(Config.RESIDUOS_CSV, index=False, encoding='utf-8')
        logger.info("Datos guardados exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"Error guardando datos: {e}")
        st.error(f"Error al guardar los datos: {e}")
        return False

def guardar_imagen_mejorada(uploaded_file, registro_id: int) -> Optional[str]:
    """Guarda imagen con validación y manejo de errores mejorado"""
    if uploaded_file is None:
        return None
    
    try:
        # Validar imagen
        es_valido, mensaje = validar_imagen(uploaded_file)
        if not es_valido:
            st.error(mensaje)
            return None
        
        # Generar nombre único y seguro
        file_extension = uploaded_file.name.split('.')[-1].lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evidencia_{registro_id}_{timestamp}.{file_extension}"
        filepath = os.path.join(Config.IMAGES_DIR, filename)
        
        # Verificar que el directorio existe
        os.makedirs(Config.IMAGES_DIR, exist_ok=True)
        
        # Guardar imagen
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Verificar que se guardó correctamente
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            logger.info(f"Imagen guardada: {filepath}")
            return filepath
        else:
            logger.error("Error: imagen no se guardó correctamente")
            return None
            
    except Exception as e:
        logger.error(f"Error guardando imagen: {e}")
        st.error(f"Error al guardar la imagen: {e}")
        return None

def generar_id_unico(df_existente: pd.DataFrame) -> int:
    """Genera ID único de forma más robusta"""
    try:
        if df_existente.empty or 'ID' not in df_existente.columns:
            return 1
        
        # Limpiar IDs nulos o inválidos
        ids_validos = df_existente['ID'].dropna()
        if ids_validos.empty:
            return 1
        
        return int(ids_validos.max()) + 1
    except Exception as e:
        logger.error(f"Error generando ID: {e}")
        return 1

# ==============================
# FUNCIONES DE INTERFAZ MEJORADAS
# ==============================

def mostrar_estadisticas_resumen(df: pd.DataFrame):
    """Muestra estadísticas resumidas con mejor formato"""
    if df.empty:
        st.info("📊 No hay datos disponibles para mostrar estadísticas.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_registros = len(df)
        st.metric(
            label="📋 Total Registros",
            value=f"{total_registros:,}",
            help="Número total de registros de residuos"
        )
    
    with col2:
        peso_total = df['Peso estimado (kg)'].sum()
        st.metric(
            label="⚖️ Peso Total",
            value=f"{peso_total:,.1f} kg",
            help="Peso total de todos los residuos registrados"
        )
    
    with col3:
        zonas_unicas = df['Zona'].nunique()
        st.metric(
            label="📍 Zonas Afectadas",
            value=f"{zonas_unicas}",
            help="Número de zonas diferentes con residuos"
        )
    
    with col4:
        if not df.empty and 'Tipo de residuo' in df.columns:
            tipo_mas_comun = df['Tipo de residuo'].mode()
            tipo_display = tipo_mas_comun[0] if not tipo_mas_comun.empty else "N/A"
        else:
            tipo_display = "N/A"
        
        st.metric(
            label="🗂️ Tipo Más Común",
            value=tipo_display,
            help="Tipo de residuo más frecuentemente encontrado"
        )

def mostrar_dashboard_principal():
    """Dashboard principal mejorado con más visualizaciones"""
    st.header("📈 Dashboard Principal")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("📊 No hay datos de residuos registrados aún. Comience registrando algunos residuos.")
        return
    
    # Estadísticas principales
    mostrar_estadisticas_resumen(df_residuos)
    
    # Gráficos principales en dos columnas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🗂️ Distribución por Tipo de Residuo")
        try:
            tipo_counts = df_residuos['Tipo de residuo'].value_counts()
            fig_pie = px.pie(
                values=tipo_counts.values, 
                names=tipo_counts.index,
                title="Distribución de Tipos de Residuos",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.error(f"Error generando gráfico de tipos: {e}")
    
    with col2:
        st.subheader("📍 Residuos por Zona")
        try:
            zona_peso = df_residuos.groupby('Zona')['Peso estimado (kg)'].sum().reset_index()
            fig_bar = px.bar(
                zona_peso, 
                x='Zona', 
                y='Peso estimado (kg)',
                title="Peso Total por Zona",
                color='Peso estimado (kg)',
                color_continuous_scale='Greens',
                text='Peso estimado (kg)'
            )
            fig_bar.update_traces(texttemplate='%{text:.1f}kg', textposition='outside')
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Error generando gráfico de zonas: {e}")
    
    # Tendencias temporales
    st.subheader("📅 Tendencia Temporal de Registros")
    try:
        if 'Fecha de registro' in df_residuos.columns:
            df_residuos['Fecha de registro'] = pd.to_datetime(df_residuos['Fecha de registro'], errors='coerce')
            df_valido = df_residuos.dropna(subset=['Fecha de registro'])
            
            if not df_valido.empty:
                daily_counts = df_valido.groupby(df_valido['Fecha de registro'].dt.date).size().reset_index(name='Cantidad')
                daily_weight = df_valido.groupby(df_valido['Fecha de registro'].dt.date)['Peso estimado (kg)'].sum().reset_index()
                
                fig_line = go.Figure()
                
                # Línea de cantidad
                fig_line.add_trace(go.Scatter(
                    x=daily_counts['Fecha de registro'],
                    y=daily_counts['Cantidad'],
                    mode='lines+markers',
                    name='Cantidad de Registros',
                    line=dict(color='#2d5a27', width=3),
                    yaxis='y'
                ))
                
                # Línea de peso
                fig_line.add_trace(go.Scatter(
                    x=daily_weight['Fecha de registro'],
                    y=daily_weight['Peso estimado (kg)'],
                    mode='lines+markers',
                    name='Peso Total (kg)',
                    line=dict(color='#ff7f0e', width=3),
                    yaxis='y2'
                ))
                
                fig_line.update_layout(
                    title="Evolución Temporal de Registros y Peso",
                    xaxis_title="Fecha",
                    yaxis=dict(title="Cantidad de Registros", side="left"),
                    yaxis2=dict(title="Peso Total (kg)", side="right", overlaying="y"),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.warning("No hay datos válidos de fecha para mostrar tendencias.")
    except Exception as e:
        st.error(f"Error generando gráfico temporal: {e}")
    
    # Tabla de registros recientes
    st.subheader("📋 Registros Recientes")
    try:
        df_recientes = df_residuos.nlargest(10, 'ID') if 'ID' in df_residuos.columns else df_residuos.tail(10)
        columnas_mostrar = ['ID', 'Zona', 'Tipo de residuo', 'Peso estimado (kg)', 'Fecha de registro']
        columnas_disponibles = [col for col in columnas_mostrar if col in df_recientes.columns]
        
        if columnas_disponibles:
            st.dataframe(
                df_recientes[columnas_disponibles],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No se pueden mostrar los registros recientes debido a columnas faltantes.")
    except Exception as e:
        st.error(f"Error mostrando registros recientes: {e}")

def mostrar_registro_residuos():
    """Interfaz mejorada para registrar nuevos residuos"""
    st.header("📝 Registro de Residuos")
    
    with st.form("nuevo_residuo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            zona = st.selectbox(
                "🌍 Zona *:",
                [''] + Config.ZONAS_VALIDAS,
                help="Seleccione la zona donde se encontró el residuo"
            )
            
            tipo_residuo = st.selectbox(
                "🗂️ Tipo de Residuo *:",
                [''] + Config.TIPOS_RESIDUO,
                help="Seleccione el tipo principal de residuo encontrado"
            )
            
            peso = st.number_input(
                "⚖️ Peso estimado (kg) *:",
                min_value=Config.PESO_MIN,
                max_value=Config.PESO_MAX,
                step=0.1,
                value=1.0,
                help=f"Peso estimado entre {Config.PESO_MIN} y {Config.PESO_MAX} kg"
            )
        
        with col2:
            ubicacion = st.text_input(
                "📍 Ubicación GPS *:",
                placeholder="-8.111, -79.028",
                help="Coordenadas GPS en formato: latitud, longitud"
            )
            
            fecha = st.date_input(
                "📅 Fecha de registro *:",
                value=datetime.now().date(),
                max_value=datetime.now().date(),
                help="Fecha en que se encontró el residuo"
            )
            
            observaciones = st.text_area(
                "📝 Observaciones:",
                placeholder="Descripción adicional, estado del residuo, accesibilidad, etc.",
                help="Información adicional relevante sobre el hallazgo"
            )
        
        # Subir imagen con preview
        st.subheader("📸 Evidencia Fotográfica")
        imagen = st.file_uploader(
            "Subir imagen (opcional):",
            type=Config.IMAGEN_TIPOS,
            help=f"Formatos permitidos: {', '.join(Config.IMAGEN_TIPOS)}. Tamaño máximo: {Config.IMAGEN_MAX_SIZE // (1024*1024)}MB"
        )
        
        # Preview de la imagen
        if imagen is not None:
            try:
                img_preview = Image.open(imagen)
                st.image(img_preview, caption="Vista previa de la imagen", width=300)
            except Exception as e:
                st.error(f"Error al mostrar vista previa: {e}")
        
        # Botón de envío
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "✅ Registrar Residuo",
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            # Validación completa
            es_valido, mensaje_error = validar_registro_completo(
                zona, ubicacion, tipo_residuo, peso, fecha, imagen
            )
            
            if not es_valido:
                st.error(f"❌ {mensaje_error}")
            else:
                try:
                    # Cargar datos existentes
                    df_existente = cargar_datos_residuos()
                    
                    # Generar nuevo ID
                    nuevo_id = generar_id_unico(df_existente)
                    
                    # Guardar imagen si se subió
                    ruta_imagen = guardar_imagen_mejorada(imagen, nuevo_id)
                    
                    # Crear nuevo registro
                    nuevo_registro = {
                        'ID': nuevo_id,
                        'Zona': zona,
                        'Ubicación (GPS)': ubicacion,
                        'Tipo de residuo': tipo_residuo,
                        'Peso estimado (kg)': peso,
                        'Fecha de registro': fecha.strftime('%Y-%m-%d'),
                        'Fecha de creación': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Observaciones': observaciones if observaciones else '',
                        'Ruta Imagen': ruta_imagen if ruta_imagen else '',
                        'Estado': 'Activo',
                        'Usuario': 'Sistema'
                    }
                    
                    # Agregar a DataFrame
                    nuevo_df = pd.DataFrame([nuevo_registro])
                    if df_existente.empty:
                        df_final = nuevo_df
                    else:
                        df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
                    
                    # Guardar
                    if guardar_datos_residuos(df_final):
                        st.success("✅ ¡Residuo registrado exitosamente!")
                        st.balloons()
                        
                        # Mostrar resumen del registro
                        with st.expander("📋 Resumen del registro creado"):
                            st.write(f"**ID:** {nuevo_id}")
                            st.write(f"**Zona:** {zona}")
                            st.write(f"**Tipo:** {tipo_residuo}")
                            st.write(f"**Peso:** {peso} kg")
                            st.write(f"**Ubicación:** {ubicacion}")
                            if ruta_imagen:
                                st.write("**Imagen:** ✅ Guardada")
                    else:
                        st.error("❌ Error al guardar el registro. Intente nuevamente.")
                        
                except Exception as e:
                    logger.error(f"Error en registro: {e}")
                    st.error(f"❌ Error inesperado: {e}")

def mostrar_consulta_residuos():
    """Interfaz mejorada para consultar registros"""
    st.header("🔍 Consulta de Residuos")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("📊 No hay registros de residuos disponibles.")
        return
    
    # Filtros mejorados
    st.subheader("🔧 Filtros de Búsqueda")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        zonas = ['Todas'] + sorted(df_residuos['Zona'].unique().tolist())
        zona_filtro = st.selectbox("🌍 Zona:", zonas)
    
    with col2:
        tipos = ['Todos'] + sorted(df_residuos['Tipo de residuo'].unique().tolist())
        tipo_filtro = st.selectbox("🗂️ Tipo:", tipos)
    
    with col3:
        peso_min = st.number_input("⚖️ Peso mín (kg):", min_value=0.0, value=0.0, step=0.1)
        
    with col4:
        peso_max = st.number_input("⚖️ Peso máx (kg):", min_value=0.1, value=float(df_residuos['Peso estimado (kg)'].max()), step=0.1)
    
    # Filtro de fechas
    if 'Fecha de registro' in df_residuos.columns:
        df_residuos['Fecha de registro'] = pd.to_datetime(df_residuos['Fecha de registro'], errors='coerce')
        df_fechas_validas = df_residuos.dropna(subset=['Fecha de registro'])
        
        if not df_fechas_validas.empty:
            fecha_min = df_fechas_validas['Fecha de registro'].min().date()
            fecha_max = df_fechas_validas['Fecha de registro'].max().date()
            
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("📅 Fecha inicio:", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
            with col2:
                fecha_fin = st.date_input("📅 Fecha fin:", value=fecha_max, min_value=fecha_min, max_value=fecha_max)
    
    # Aplicar filtros
    df_filtrado = df_residuos.copy()
    
    try:
        if zona_filtro != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Zona'] == zona_filtro]
        
        if tipo_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Tipo de residuo'] == tipo_filtro]
        
        # Filtro de peso
        df_filtrado = df_filtrado[
            (df_filtrado['Peso estimado (kg)'] >= peso_min) & 
            (df_filtrado['Peso estimado (kg)'] <= peso_max)
        ]
        
        # Filtro de fechas
        if 'fecha_inicio' in locals() and 'fecha_fin' in locals():
            df_filtrado = df_filtrado[
                (df_filtrado['Fecha de registro'].dt.date >= fecha_inicio) & 
                (df_filtrado['Fecha de registro'].dt.date <= fecha_fin)
            ]
        
        # Mostrar resultados
        st.subheader(f"📋 Registros Encontrados: {len(df_filtrado)}")
        
        if not df_filtrado.empty:
            # Estadísticas de los resultados filtrados
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total registros", len(df_filtrado))
            with col2:
                st.metric("Peso total", f"{df_filtrado['Peso estimado (kg)'].sum():.1f} kg")
            with col3:
                st.metric("Zonas únicas", df_filtrado['Zona'].nunique())
            
            # Tabla de resultados
            columnas_mostrar = [col for col in ['ID', 'Zona', 'Tipo de residuo', 'Peso estimado (kg)', 'Fecha de registro', 'Observaciones'] if col in df_filtrado.columns]
            
            st.dataframe(
                df_filtrado[columnas_mostrar].sort_values('ID', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Exportar resultados filtrados
            if st.button("📥 Exportar Resultados Filtrados"):
                csv = df_filtrado.to_csv(index=False, encoding='utf-8')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"residuos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Mostrar evidencias fotográficas
            if 'Ruta Imagen' in df_filtrado.columns:
                registros_con_imagen = df_filtrado[df_filtrado['Ruta Imagen'].notna() & (df_filtrado['Ruta Imagen'] != '')]
                
                if not registros_con_imagen.empty:
                    st.subheader("📸 Evidencias Fotográficas")
                    
                    # Mostrar imágenes en grid
                    cols = st.columns(3)
                    for idx, (_, registro) in enumerate(registros_con_imagen.iterrows()):
                        col_idx = idx % 3
                        
                        with cols[col_idx]:
                            if os.path.exists(registro['Ruta Imagen']):
                                try:
                                    imagen = Image.open(registro['Ruta Imagen'])
                                    st.image(
                                        imagen, 
                                        caption=f"ID: {registro['ID']} - {registro['Zona']}", 
                                        use_column_width=True
                                    )
                                except Exception as e:
                                    st.error(f"Error cargando imagen ID {registro['ID']}: {e}")
        else:
            st.warning("🔍 No se encontraron registros con los filtros aplicados.")
            
    except Exception as e:
        logger.error(f"Error en consulta: {e}")
        st.error(f"Error al filtrar datos: {e}")

# Función principal mejorada
def main():
    """Función principal con manejo de errores mejorado"""
    try:
        # Crear directorios necesarios
        crear_directorios()
        
        # Inicializar sistema
        inicializar_archivo_residuos()
        
        # Header principal mejorado
        st.markdown("""
        <div class="main-header">
            <h1>🌳 Sistema de Gestión de Residuos Sólidos</h1>
            <h2>Parque La Amistad</h2>
            <p>Monitoreo, registro y análisis integral de residuos para la conservación ambiental</p>
            <small>Sistema mejorado con validaciones robustas y manejo de errores</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar mejorado
        st.sidebar.title("🧭 Navegación")
        st.sidebar.markdown("---")
        
        pagina = st.sidebar.selectbox(
            "Selecciona una sección:",
            [
                "📈 Dashboard Principal", 
                "📝 Registro de Residuos", 
                "🔍 Consulta de Residuos", 
                "✏️ Edición de Residuos", 
                "🗑️ Eliminación de Residuos", 
                "📊 Reportes y Estadísticas"
            ]
        )
        
        # Información del sistema en sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ℹ️ Información del Sistema")
        
        try:
            df_info = cargar_datos_residuos()
            if not df_info.empty:
                st.sidebar.metric("Total Registros", len(df_info))
                st.sidebar.metric("Peso Total", f"{df_info['Peso estimado (kg)'].sum():.1f} kg")
            else:
                st.sidebar.info("Sin datos registrados")
        except Exception as e:
            st.sidebar.error("Error cargando info")
        
        # Navegación entre páginas
        if pagina == "📈 Dashboard Principal":
            mostrar_dashboard_principal()
        elif pagina == "📝 Registro de Residuos":
            mostrar_registro_residuos()
        elif pagina == "🔍 Consulta de Residuos":
            mostrar_consulta_residuos()
        elif pagina == "✏️ Edición de Residuos":
            st.info("🚧 Función de edición en desarrollo. Próximamente disponible.")
        elif pagina == "🗑️ Eliminación de Residuos":
            st.info("🚧 Función de eliminación en desarrollo. Próximamente disponible.")
        elif pagina == "📊 Reportes y Estadísticas":
            st.info("🚧 Reportes avanzados en desarrollo. Próximamente disponible.")
        
        # Footer mejorado
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
            <p><strong>🌳 Sistema de Gestión de Residuos Sólidos - Parque La Amistad</strong></p>
            <p><small>Desarrollado para la conservación y monitoreo ambiental comunitario</small></p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Error en función principal: {e}")
        st.error(f"Error crítico del sistema: {e}")
        st.info("Por favor, recargue la página o contacte al administrador del sistema.")

if __name__ == "__main__":
    main()
