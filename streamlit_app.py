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

# ==============================
# FUNCIONES DE EDICIÓN Y ELIMINACIÓN (NUEVAS)
# ==============================

def mostrar_edicion_residuos():
    """Interfaz completa para editar registros existentes"""
    st.header("✏️ Edición de Residuos")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("📊 No hay registros disponibles para editar.")
        return
    
    # Selector de registro a editar
    st.subheader("🔍 Seleccionar Registro")
    
    # Crear lista de opciones con información relevante
    opciones_registros = []
    for _, row in df_residuos.iterrows():
        opcion = f"ID {row['ID']} - {row['Zona']} - {row['Tipo de residuo']} ({row['Peso estimado (kg)']} kg)"
        opciones_registros.append(opcion)
    
    registro_seleccionado = st.selectbox(
        "Seleccione el registro a editar:",
        opciones_registros,
        help="Seleccione el registro que desea modificar"
    )
    
    if registro_seleccionado:
        # Extraer ID del registro seleccionado
        id_seleccionado = int(registro_seleccionado.split(' ')[1])
        registro_actual = df_residuos[df_residuos['ID'] == id_seleccionado].iloc[0]
        
        # Mostrar información actual
        with st.expander("📋 Información Actual del Registro", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**ID:** {registro_actual['ID']}")
                st.write(f"**Zona:** {registro_actual['Zona']}")
                st.write(f"**Tipo:** {registro_actual['Tipo de residuo']}")
            with col2:
                st.write(f"**Peso:** {registro_actual['Peso estimado (kg)']} kg")
                st.write(f"**Ubicación:** {registro_actual['Ubicación (GPS)']}")
                st.write(f"**Fecha:** {registro_actual['Fecha de registro']}")
            with col3:
                st.write(f"**Estado:** {registro_actual.get('Estado', 'Activo')}")
                if registro_actual.get('Ruta Imagen') and os.path.exists(registro_actual['Ruta Imagen']):
                    st.write("**Imagen:** ✅ Disponible")
                    try:
                        img = Image.open(registro_actual['Ruta Imagen'])
                        st.image(img, width=200)
                    except:
                        pass
        
        # Formulario de edición
        st.subheader("✏️ Editar Información")
        
        with st.form("editar_residuo"):
            col1, col2 = st.columns(2)
            
            with col1:
                nueva_zona = st.selectbox(
                    "🌍 Zona *:",
                    Config.ZONAS_VALIDAS,
                    index=Config.ZONAS_VALIDAS.index(registro_actual['Zona']) if registro_actual['Zona'] in Config.ZONAS_VALIDAS else 0
                )
                
                nuevo_tipo = st.selectbox(
                    "🗂️ Tipo de Residuo *:",
                    Config.TIPOS_RESIDUO,
                    index=Config.TIPOS_RESIDUO.index(registro_actual['Tipo de residuo']) if registro_actual['Tipo de residuo'] in Config.TIPOS_RESIDUO else 0
                )
                
                nuevo_peso = st.number_input(
                    "⚖️ Peso estimado (kg) *:",
                    min_value=Config.PESO_MIN,
                    max_value=Config.PESO_MAX,
                    value=float(registro_actual['Peso estimado (kg)']),
                    step=0.1
                )
            
            with col2:
                nueva_ubicacion = st.text_input(
                    "📍 Ubicación GPS *:",
                    value=registro_actual['Ubicación (GPS)']
                )
                
                # Convertir fecha actual a date object
                fecha_actual = pd.to_datetime(registro_actual['Fecha de registro']).date() if pd.notna(registro_actual['Fecha de registro']) else datetime.now().date()
                nueva_fecha = st.date_input(
                    "📅 Fecha de registro *:",
                    value=fecha_actual,
                    max_value=datetime.now().date()
                )
                
                nuevo_estado = st.selectbox(
                    "📊 Estado:",
                    ['Activo', 'Procesado', 'Archivado'],
                    index=['Activo', 'Procesado', 'Archivado'].index(registro_actual.get('Estado', 'Activo')) if registro_actual.get('Estado', 'Activo') in ['Activo', 'Procesado', 'Archivado'] else 0
                )
            
            nuevas_observaciones = st.text_area(
                "📝 Observaciones:",
                value=registro_actual.get('Observaciones', '')
            )
            
            # Opción para cambiar imagen
            st.subheader("📸 Actualizar Evidencia Fotográfica")
            cambiar_imagen = st.checkbox("¿Desea cambiar la imagen?")
            
            nueva_imagen = None
            if cambiar_imagen:
                nueva_imagen = st.file_uploader(
                    "Subir nueva imagen:",
                    type=Config.IMAGEN_TIPOS
                )
                if nueva_imagen:
                    try:
                        img_preview = Image.open(nueva_imagen)
                        st.image(img_preview, caption="Vista previa de la nueva imagen", width=300)
                    except Exception as e:
                        st.error(f"Error al mostrar vista previa: {e}")
            
            # Botones de acción
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submitted = st.form_submit_button(
                    "💾 Guardar Cambios",
                    type="primary",
                    use_container_width=True
                )
            
            if submitted:
                # Validar datos
                es_valido, mensaje_error = validar_registro_completo(
                    nueva_zona, nueva_ubicacion, nuevo_tipo, nuevo_peso, nueva_fecha, nueva_imagen
                )
                
                if not es_valido:
                    st.error(f"❌ {mensaje_error}")
                else:
                    try:
                        # Actualizar registro
                        df_residuos.loc[df_residuos['ID'] == id_seleccionado, 'Zona'] = nueva_zona
                        df_residuos.loc[df_residuos['ID'] == id_seleccionado, 'Tipo de residuo'] = nuevo_tipo
                        df_residuos.loc[df_residuos['ID'] == id_seleccionado, 'Peso estimado (kg)'] = nuevo_peso
                        df_residuos.loc[df_residuos['ID'] == id_seleccionado, 'Ubicación (GPS)'] = nueva_ubicacion
                        df_residuos.loc[df_residuos['ID'] == id_seleccionado, 'Fecha de registro'] = nueva_fecha.strftime('%Y-%m-%d')
                        df_residuos.loc[df_residuos['ID'] == id_seleccionado, 'Observaciones'] = nuevas_observaciones
                        df_residuos.loc[df_residuos['ID'] == id_seleccionado, 'Estado'] = nuevo_estado
                        
                        # Actualizar imagen si se cambió
                        if cambiar_imagen and nueva_imagen:
                            ruta_imagen = guardar_imagen_mejorada(nueva_imagen, id_seleccionado)
                            if ruta_imagen:
                                df_residuos.loc[df_residuos['ID'] == id_seleccionado, 'Ruta Imagen'] = ruta_imagen
                        
                        # Guardar cambios
                        if guardar_datos_residuos(df_residuos):
                            st.success("✅ ¡Registro actualizado exitosamente!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar los cambios.")
                    
                    except Exception as e:
                        logger.error(f"Error actualizando registro: {e}")
                        st.error(f"❌ Error inesperado: {e}")

def mostrar_eliminacion_residuos():
    """Interfaz completa para eliminar registros"""
    st.header("🗑️ Eliminación de Residuos")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("📊 No hay registros disponibles para eliminar.")
        return
    
    # Advertencia
    st.warning("⚠️ **Advertencia:** La eliminación de registros es permanente y no se puede deshacer. Use con precaución.")
    
    # Selector de registro a eliminar
    st.subheader("🔍 Seleccionar Registro")
    
    # Crear lista de opciones
    opciones_registros = []
    for _, row in df_residuos.iterrows():
        opcion = f"ID {row['ID']} - {row['Zona']} - {row['Tipo de residuo']} ({row['Peso estimado (kg)']} kg) - {row['Fecha de registro']}"
        opciones_registros.append(opcion)
    
    registro_seleccionado = st.selectbox(
        "Seleccione el registro a eliminar:",
        opciones_registros,
        help="Seleccione el registro que desea eliminar permanentemente"
    )
    
    if registro_seleccionado:
        # Extraer ID
        id_seleccionado = int(registro_seleccionado.split(' ')[1])
        registro_actual = df_residuos[df_residuos['ID'] == id_seleccionado].iloc[0]
        
        # Mostrar información del registro
        with st.expander("📋 Información del Registro a Eliminar", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**ID:** {registro_actual['ID']}")
                st.write(f"**Zona:** {registro_actual['Zona']}")
                st.write(f"**Tipo:** {registro_actual['Tipo de residuo']}")
                st.write(f"**Peso:** {registro_actual['Peso estimado (kg)']} kg")
            
            with col2:
                st.write(f"**Ubicación:** {registro_actual['Ubicación (GPS)']}")
                st.write(f"**Fecha:** {registro_actual['Fecha de registro']}")
                st.write(f"**Observaciones:** {registro_actual.get('Observaciones', 'N/A')}")
            
            # Mostrar imagen si existe
            if registro_actual.get('Ruta Imagen') and os.path.exists(registro_actual['Ruta Imagen']):
                try:
                    img = Image.open(registro_actual['Ruta Imagen'])
                    st.image(img, caption="Evidencia fotográfica", width=300)
                except:
                    pass
        
        # Confirmación de eliminación
        st.subheader("⚠️ Confirmar Eliminación")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            confirmar = st.checkbox(
                "Confirmo que deseo eliminar este registro permanentemente",
                help="Marque esta casilla para habilitar el botón de eliminación"
            )
            
            if confirmar:
                if st.button(
                    "🗑️ ELIMINAR REGISTRO",
                    type="primary",
                    use_container_width=True
                ):
                    try:
                        # Crear backup antes de eliminar
                        crear_backup_datos()
                        
                        # Eliminar imagen asociada si existe
                        if registro_actual.get('Ruta Imagen') and os.path.exists(registro_actual['Ruta Imagen']):
                            try:
                                os.remove(registro_actual['Ruta Imagen'])
                                logger.info(f"Imagen eliminada: {registro_actual['Ruta Imagen']}")
                            except Exception as e:
                                logger.warning(f"No se pudo eliminar la imagen: {e}")
                        
                        # Eliminar registro del DataFrame
                        df_residuos = df_residuos[df_residuos['ID'] != id_seleccionado]
                        
                        # Guardar cambios
                        if guardar_datos_residuos(df_residuos):
                            st.success(f"✅ Registro ID {id_seleccionado} eliminado exitosamente.")
                            st.info("💾 Se ha creado un backup automático antes de la eliminación.")
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar los cambios.")
                    
                    except Exception as e:
                        logger.error(f"Error eliminando registro: {e}")
                        st.error(f"❌ Error inesperado: {e}")
            else:
                st.info("👆 Marque la casilla de confirmación para habilitar la eliminación.")

def mostrar_reportes_estadisticas():
    """Interfaz completa de reportes y estadísticas avanzadas"""
    st.header("📊 Reportes y Estadísticas Avanzadas")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("📊 No hay datos disponibles para generar reportes.")
        return
    
    # Tabs para diferentes tipos de reportes
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Análisis General",
        "🗺️ Análisis por Zona",
        "📅 Análisis Temporal",
        "📥 Exportar Reportes"
    ])
    
    with tab1:
        st.subheader("📈 Análisis General de Residuos")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Registros", f"{len(df_residuos):,}")
        with col2:
            st.metric("Peso Total", f"{df_residuos['Peso estimado (kg)'].sum():,.1f} kg")
        with col3:
            st.metric("Peso Promedio", f"{df_residuos['Peso estimado (kg)'].mean():.2f} kg")
        with col4:
            st.metric("Zonas Afectadas", df_residuos['Zona'].nunique())
        
        # Gráficos comparativos
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por tipo
            tipo_counts = df_residuos['Tipo de residuo'].value_counts()
            fig_tipo = px.bar(
                x=tipo_counts.index,
                y=tipo_counts.values,
                title="Cantidad de Registros por Tipo de Residuo",
                labels={'x': 'Tipo de Residuo', 'y': 'Cantidad'},
                color=tipo_counts.values,
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_tipo, use_container_width=True)
        
        with col2:
            # Peso por tipo
            peso_tipo = df_residuos.groupby('Tipo de residuo')['Peso estimado (kg)'].sum().sort_values(ascending=False)
            fig_peso = px.bar(
                x=peso_tipo.index,
                y=peso_tipo.values,
                title="Peso Total por Tipo de Residuo (kg)",
                labels={'x': 'Tipo de Residuo', 'y': 'Peso (kg)'},
                color=peso_tipo.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_peso, use_container_width=True)
        
        # Tabla de resumen por tipo
        st.subheader("📋 Resumen Detallado por Tipo")
        resumen_tipo = df_residuos.groupby('Tipo de residuo').agg({
            'ID': 'count',
            'Peso estimado (kg)': ['sum', 'mean', 'min', 'max']
        }).round(2)
        resumen_tipo.columns = ['Cantidad', 'Peso Total (kg)', 'Peso Promedio (kg)', 'Peso Mínimo (kg)', 'Peso Máximo (kg)']
        st.dataframe(resumen_tipo, use_container_width=True)
    
    with tab2:
        st.subheader("🗺️ Análisis por Zona del Parque")
        
        # Métricas por zona
        zona_stats = df_residuos.groupby('Zona').agg({
            'ID': 'count',
            'Peso estimado (kg)': 'sum'
        }).reset_index()
        zona_stats.columns = ['Zona', 'Cantidad', 'Peso Total']
        
        # Gráfico de mapa de calor
        fig_zona = px.bar(
            zona_stats,
            x='Zona',
            y=['Cantidad', 'Peso Total'],
            title="Comparación de Zonas: Cantidad vs Peso Total",
            barmode='group',
            color_discrete_sequence=['#2d5a27', '#ff7f0e']
        )
        st.plotly_chart(fig_zona, use_container_width=True)
        
        # Análisis detallado por zona seleccionada
        zona_seleccionada = st.selectbox(
            "Seleccione una zona para análisis detallado:",
            df_residuos['Zona'].unique()
        )
        
        df_zona = df_residuos[df_residuos['Zona'] == zona_seleccionada]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Registros en Zona", len(df_zona))
        with col2:
            st.metric("Peso Total", f"{df_zona['Peso estimado (kg)'].sum():.1f} kg")
        with col3:
            tipo_predominante = df_zona['Tipo de residuo'].mode()[0] if not df_zona.empty else "N/A"
            st.metric("Tipo Predominante", tipo_predominante)
        
        # Distribución de tipos en la zona
        tipo_zona = df_zona['Tipo de residuo'].value_counts()
        fig_tipo_zona = px.pie(
            values=tipo_zona.values,
            names=tipo_zona.index,
            title=f"Distribución de Tipos de Residuo en {zona_seleccionada}",
            hole=0.4
        )
        st.plotly_chart(fig_tipo_zona, use_container_width=True)
    
    with tab3:
        st.subheader("📅 Análisis Temporal")
        
        if 'Fecha de registro' in df_residuos.columns:
            df_residuos['Fecha de registro'] = pd.to_datetime(df_residuos['Fecha de registro'], errors='coerce')
            df_temporal = df_residuos.dropna(subset=['Fecha de registro'])
            
            if not df_temporal.empty:
                # Agregar columnas temporales
                df_temporal['Año'] = df_temporal['Fecha de registro'].dt.year
                df_temporal['Mes'] = df_temporal['Fecha de registro'].dt.month
                df_temporal['Día Semana'] = df_temporal['Fecha de registro'].dt.day_name()
                
                # Tendencia mensual
                mensual = df_temporal.groupby(df_temporal['Fecha de registro'].dt.to_period('M')).agg({
                    'ID': 'count',
                    'Peso estimado (kg)': 'sum'
                }).reset_index()
                mensual['Fecha de registro'] = mensual['Fecha de registro'].astype(str)
                
                fig_mensual = go.Figure()
                fig_mensual.add_trace(go.Scatter(
                    x=mensual['Fecha de registro'],
                    y=mensual['ID'],
                    name='Cantidad',
                    mode='lines+markers',
                    line=dict(color='#2d5a27', width=3)
                ))
                fig_mensual.add_trace(go.Scatter(
                    x=mensual['Fecha de registro'],
                    y=mensual['Peso estimado (kg)'],
                    name='Peso (kg)',
                    mode='lines+markers',
                    line=dict(color='#ff7f0e', width=3),
                    yaxis='y2'
                ))
                fig_mensual.update_layout(
                    title="Tendencia Mensual de Residuos",
                    xaxis_title="Mes",
                    yaxis=dict(title="Cantidad de Registros"),
                    yaxis2=dict(title="Peso Total (kg)", overlaying='y', side='right'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig_mensual, use_container_width=True)
                
                # Análisis por día de la semana
                col1, col2 = st.columns(2)
                
                with col1:
                    dia_semana = df_temporal['Día Semana'].value_counts()
                    fig_dia = px.bar(
                        x=dia_semana.index,
                        y=dia_semana.values,
                        title="Registros por Día de la Semana",
                        labels={'x': 'Día', 'y': 'Cantidad'}
                    )
                    st.plotly_chart(fig_dia, use_container_width=True)
                
                with col2:
                    mes_stats = df_temporal.groupby('Mes')['Peso estimado (kg)'].sum()
                    fig_mes = px.line(
                        x=mes_stats.index,
                        y=mes_stats.values,
                        title="Peso Total por Mes",
                        labels={'x': 'Mes', 'y': 'Peso (kg)'},
                        markers=True
                    )
                    st.plotly_chart(fig_mes, use_container_width=True)
    
    with tab4:
        st.subheader("📥 Exportar Reportes")
        
        st.write("Genere y descargue reportes personalizados en diferentes formatos.")
        
        # Opciones de exportación
        col1, col2 = st.columns(2)
        
        with col1:
            formato = st.selectbox(
                "Formato de exportación:",
                ["CSV", "Excel", "JSON"]
            )
        
        with col2:
            incluir_imagenes = st.checkbox("Incluir rutas de imágenes", value=True)
        
        # Generar reporte
        if st.button("📥 Generar y Descargar Reporte", type="primary"):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Preparar datos
                df_export = df_residuos.copy()
                if not incluir_imagenes and 'Ruta Imagen' in df_export.columns:
                    df_export = df_export.drop(columns=['Ruta Imagen'])
                
                if formato == "CSV":
                    csv = df_export.to_csv(index=False, encoding='utf-8')
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"reporte_residuos_{timestamp}.csv",
                        mime="text/csv"
                    )
                
                elif formato == "JSON":
                    json_str = df_export.to_json(orient='records', date_format='iso', indent=2)
                    st.download_button(
                        label="📥 Descargar JSON",
                        data=json_str,
                        file_name=f"reporte_residuos_{timestamp}.json",
                        mime="application/json"
                    )
                
                st.success("✅ Reporte generado exitosamente!")
                
            except Exception as e:
                st.error(f"❌ Error generando reporte: {e}")

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
            <small>Sistema completo con operaciones CRUD</small>
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
        
        # Navegación con todas las funciones CRUD implementadas
        if pagina == "📈 Dashboard Principal":
            mostrar_dashboard_principal()
        elif pagina == "📝 Registro de Residuos":
            mostrar_registro_residuos()
        elif pagina == "🔍 Consulta de Residuos":
            mostrar_consulta_residuos()
        elif pagina == "✏️ Edición de Residuos":
            mostrar_edicion_residuos()
        elif pagina == "🗑️ Eliminación de Residuos":
            mostrar_eliminacion_residuos()
        elif pagina == "📊 Reportes y Estadísticas":
            mostrar_reportes_estadisticas()
        
        # Footer mejorado
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
            <p><strong>🌳 Sistema de Gestión de Residuos Sólidos - Parque La Amistad</strong></p>
            <p><small>Sistema completo con operaciones CRUD - Desarrollado para la conservación ambiental</small></p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Error en función principal: {e}")
        st.error(f"Error crítico del sistema: {e}")
        st.info("Por favor, recargue la página o contacte al administrador del sistema.")

if __name__ == "__main__":
    main()
