import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
import numpy as np
from PIL import Image
import uuid

# Configuración de la página
st.set_page_config(
    page_title="Parque La Amistad - Gestión de Residuos Sólidos",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para el tema
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2d5a27 0%, #4a7c59 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2d5a27;
        margin: 0.5rem 0;
    }
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-msg {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-msg {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuración de rutas
DATASET_DIR = "dataset"
RESIDUOS_CSV = os.path.join(DATASET_DIR, "residuos_parque.csv")
ZONAS_CRITICAS_CSV = os.path.join(DATASET_DIR, "zonas_criticas.csv")
ENCUESTAS_CSV = os.path.join(DATASET_DIR, "encuesta_respuestas.csv")
IMAGES_DIR = os.path.join(DATASET_DIR, "evidencias")

# Crear directorios si no existen
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# ==============================
# FUNCIONES DE GESTIÓN DE DATOS
# ==============================

def inicializar_archivo_residuos():
    """Inicializa el archivo CSV de residuos si no existe"""
    if not os.path.exists(RESIDUOS_CSV):
        df = pd.DataFrame(columns=[
            'ID', 'Zona', 'Ubicación (GPS)', 'Tipo de residuo', 
            'Peso estimado (kg)', 'Fecha de registro', 'Observaciones', 'Ruta Imagen'
        ])
        df.to_csv(RESIDUOS_CSV, index=False, encoding='utf-8')

def cargar_datos_residuos():
    """Carga los datos de residuos desde el CSV"""
    try:
        df = pd.read_csv(RESIDUOS_CSV, encoding='utf-8')
        # Asegurar que la columna de fecha sea datetime
        if 'Fecha de registro' in df.columns and not df.empty:
            df['Fecha de registro'] = pd.to_datetime(df['Fecha de registro'])
        return df
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return pd.DataFrame()

def guardar_datos_residuos(df):
    """Guarda los datos de residuos en el CSV"""
    df.to_csv(RESIDUOS_CSV, index=False, encoding='utf-8')

def guardar_imagen(uploaded_file, registro_id):
    """Guarda una imagen en el directorio de evidencias y devuelve la ruta"""
    if uploaded_file is not None:
        # Generar nombre único para la imagen
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f"evidencia_{registro_id}.{file_extension}"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Guardar la imagen
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filepath
    return ""

def generar_id_unico(df_existente):
    """Genera un ID único para un nuevo registro"""
    if df_existente.empty or 'ID' not in df_existente.columns:
        return 1
    return df_existente['ID'].max() + 1

def validar_registro(zona, ubicacion, tipo_residuo, peso):
    """Valida que los datos del registro no estén vacíos"""
    if not zona or not ubicacion or not tipo_residuo or not peso:
        return False, "Todos los campos obligatorios deben ser completados"
    if peso <= 0:
        return False, "El peso debe ser mayor a 0"
    return True, ""

# ==============================
# FUNCIONES DE LA INTERFAZ
# ==============================

def mostrar_dashboard_principal():
    """Muestra el dashboard principal con métricas y gráficos"""
    st.header("📈 Dashboard Principal")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("No hay datos de residuos registrados aún.")
        return
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Residuos Registrados",
            value=len(df_residuos)
        )
    
    with col2:
        peso_total = df_residuos['Peso estimado (kg)'].sum()
        st.metric(
            label="Peso Total (kg)",
            value=f"{peso_total:.1f}"
        )
    
    with col3:
        zonas_unicas = df_residuos['Zona'].nunique()
        st.metric(
            label="Zonas con Residuos",
            value=zonas_unicas
        )
    
    with col4:
        tipo_mas_comun = df_residuos['Tipo de residuo'].mode()[0] if not df_residuos.empty else "N/A"
        st.metric(
            label="Tipo Más Común",
            value=tipo_mas_comun
        )
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución de Residuos por Tipo")
        if not df_residuos.empty:
            tipo_counts = df_residuos['Tipo de residuo'].value_counts()
            fig_pie = px.pie(
                values=tipo_counts.values, 
                names=tipo_counts.index,
                title="Tipos de Residuos Encontrados",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("Residuos por Zona")
        if not df_residuos.empty:
            zona_peso = df_residuos.groupby('Zona')['Peso estimado (kg)'].sum().reset_index()
            fig_bar = px.bar(
                zona_peso, 
                x='Zona', 
                y='Peso estimado (kg)',
                title="Peso de Residuos por Zona",
                color='Peso estimado (kg)',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tendencias temporales
    st.subheader("Tendencia de Registros por Fecha")
    if not df_residuos.empty and 'Fecha de registro' in df_residuos.columns:
        df_residuos['Fecha de registro'] = pd.to_datetime(df_residuos['Fecha de registro'])
        daily_counts = df_residuos.groupby(df_residuos['Fecha de registro'].dt.date).size().reset_index(name='Cantidad')
        
        fig_line = px.line(
            daily_counts, 
            x='Fecha de registro', 
            y='Cantidad',
            title="Registros Diarios de Residuos",
            markers=True
        )
        fig_line.update_traces(line_color='#2d5a27')
        st.plotly_chart(fig_line, use_container_width=True)

def mostrar_registro_residuos():
    """Interfaz para registrar nuevos residuos"""
    st.header("📝 Registro de Residuos")
    
    with st.form("nuevo_residuo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            zona = st.selectbox("Zona:", ['', 'Norte', 'Sur', 'Este', 'Oeste', 'Centro'], key="zona_nueva")
            tipo_residuo = st.selectbox("Tipo de Residuo:", ['', 'Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Otros'], key="tipo_nuevo")
            peso = st.number_input("Peso estimado (kg):", min_value=0.1, max_value=100.0, step=0.1, key="peso_nuevo")
        
        with col2:
            ubicacion = st.text_input("Ubicación GPS:", placeholder="-8.111, -79.028", key="ubicacion_nueva")
            fecha = st.date_input("Fecha de registro:", value=datetime.now(), key="fecha_nueva")
            observaciones = st.text_area("Observaciones:", key="obs_nuevas")
        
        # Subir imagen
        imagen = st.file_uploader("Subir evidencia fotográfica (opcional):", type=['jpg', 'jpeg', 'png'], key="imagen_nueva")
        
        submitted = st.form_submit_button("Registrar Residuo")
        
        if submitted:
            # Validar datos
            es_valido, mensaje_error = validar_registro(zona, ubicacion, tipo_residuo, peso)
            
            if not es_valido:
                st.error(f"❌ {mensaje_error}")
            else:
                # Cargar datos existentes
                df_existente = cargar_datos_residuos()
                
                # Generar nuevo ID
                nuevo_id = generar_id_unico(df_existente)
                
                # Guardar imagen si se subió
                ruta_imagen = guardar_imagen(imagen, nuevo_id)
                
                # Crear nuevo registro
                nuevo_registro = {
                    'ID': nuevo_id,
                    'Zona': zona,
                    'Ubicación (GPS)': ubicacion,
                    'Tipo de residuo': tipo_residuo,
                    'Peso estimado (kg)': peso,
                    'Fecha de registro': fecha.strftime('%Y-%m-%d'),
                    'Observaciones': observaciones,
                    'Ruta Imagen': ruta_imagen
                }
                
                # Agregar a DataFrame
                nuevo_df = pd.DataFrame([nuevo_registro])
                if df_existente.empty:
                    df_final = nuevo_df
                else:
                    df_final = pd.concat([df_existente, nuevo_df], ignore_index=True)
                
                # Guardar
                guardar_datos_residuos(df_final)
                st.success("✅ Residuo registrado exitosamente!")

def mostrar_consulta_residuos():
    """Interfaz para consultar y filtrar registros"""
    st.header("🔍 Consulta de Residuos")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("No hay registros de residuos disponibles.")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        zonas = ['Todas'] + list(df_residuos['Zona'].unique())
        zona_filtro = st.selectbox("Filtrar por Zona:", zonas)
    
    with col2:
        tipos = ['Todos'] + list(df_residuos['Tipo de residuo'].unique())
        tipo_filtro = st.selectbox("Filtrar por Tipo:", tipos)
    
    with col3:
        # Convertir fecha a formato datetime si no lo está
        if 'Fecha de registro' in df_residuos.columns:
            df_residuos['Fecha de registro'] = pd.to_datetime(df_residuos['Fecha de registro'])
            fecha_min = df_residuos['Fecha de registro'].min().date()
            fecha_max = df_residuos['Fecha de registro'].max().date()
            rango_fechas = st.date_input(
                "Filtrar por rango de fechas:",
                value=(fecha_min, fecha_max),
                min_value=fecha_min,
                max_value=fecha_max
            )
    
    # Aplicar filtros
    df_filtrado = df_residuos.copy()
    
    if zona_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Zona'] == zona_filtro]
    
    if tipo_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Tipo de residuo'] == tipo_filtro]
    
    if len(rango_fechas) == 2 and 'Fecha de registro' in df_filtrado.columns:
        fecha_inicio, fecha_fin = rango_fechas
        df_filtrado = df_filtrado[
            (df_filtrado['Fecha de registro'].dt.date >= fecha_inicio) & 
            (df_filtrado['Fecha de registro'].dt.date <= fecha_fin)
        ]
    
    # Mostrar resultados
    st.subheader(f"Registros Encontrados: {len(df_filtrado)}")
    
    if not df_filtrado.empty:
        # Mostrar tabla sin la columna de ruta de imagen para mejor visualización
        columnas_mostrar = [col for col in df_filtrado.columns if col != 'Ruta Imagen']
        st.dataframe(df_filtrado[columnas_mostrar], use_container_width=True)
        
        # Opción para ver imagen si existe
        if 'Ruta Imagen' in df_filtrado.columns and not df_filtrado['Ruta Imagen'].isna().all():
            st.subheader("Evidencias Fotográficas")
            for _, registro in df_filtrado.iterrows():
                if registro['Ruta Imagen'] and os.path.exists(registro['Ruta Imagen']):
                    with st.expander(f"Evidencia del registro ID: {registro['ID']}"):
                        try:
                            imagen = Image.open(registro['Ruta Imagen'])
                            st.image(imagen, caption=f"Registro ID: {registro['ID']}", width=300)
                        except Exception as e:
                            st.error(f"Error al cargar la imagen: {e}")
    else:
        st.warning("No se encontraron registros con los filtros aplicados.")

def mostrar_edicion_residuos():
    """Interfaz para editar registros existentes"""
    st.header("✏️ Editar Registros de Residuos")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("No hay registros de residuos disponibles para editar.")
        return
    
    # Seleccionar registro a editar
    registros_lista = [f"ID: {row['ID']} - {row['Zona']} - {row['Tipo de residuo']}" for _, row in df_residuos.iterrows()]
    registro_seleccionado = st.selectbox("Seleccionar registro a editar:", registros_lista)
    
    if registro_seleccionado:
        # Extraer ID del registro seleccionado
        registro_id = int(registro_seleccionado.split("ID: ")[1].split(" -")[0])
        registro_original = df_residuos[df_residuos['ID'] == registro_id].iloc[0]
        
        # Formulario de edición
        with st.form("editar_residuo"):
            col1, col2 = st.columns(2)
            
            with col1:
                zona_edit = st.selectbox(
                    "Zona:", 
                    ['Norte', 'Sur', 'Este', 'Oeste', 'Centro'],
                    index=['Norte', 'Sur', 'Este', 'Oeste', 'Centro'].index(registro_original['Zona']) if registro_original['Zona'] in ['Norte', 'Sur', 'Este', 'Oeste', 'Centro'] else 0
                )
                tipo_edit = st.selectbox(
                    "Tipo de Residuo:", 
                    ['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Otros'],
                    index=['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Otros'].index(registro_original['Tipo de residuo']) if registro_original['Tipo de residuo'] in ['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Otros'] else 0
                )
                peso_edit = st.number_input(
                    "Peso estimado (kg):", 
                    min_value=0.1, 
                    max_value=100.0, 
                    step=0.1,
                    value=float(registro_original['Peso estimado (kg)'])
                )
            
            with col2:
                ubicacion_edit = st.text_input(
                    "Ubicación GPS:", 
                    value=registro_original['Ubicación (GPS)']
                )
                fecha_edit = st.date_input(
                    "Fecha de registro:",
                    value=pd.to_datetime(registro_original['Fecha de registro']).date() if pd.notna(registro_original['Fecha de registro']) else datetime.now()
                )
                observaciones_edit = st.text_area(
                    "Observaciones:",
                    value=registro_original['Observaciones'] if pd.notna(registro_original['Observaciones']) else ""
                )
            
            # Opción para cambiar imagen
            imagen_actual = registro_original.get('Ruta Imagen', '')
            if imagen_actual and os.path.exists(imagen_actual):
                st.info("Imagen actual:")
                try:
                    imagen = Image.open(imagen_actual)
                    st.image(imagen, caption="Imagen actual", width=200)
                except Exception as e:
                    st.error(f"Error al cargar la imagen actual: {e}")
            
            nueva_imagen = st.file_uploader("Subir nueva evidencia (opcional):", type=['jpg', 'jpeg', 'png'])
            
            submitted = st.form_submit_button("Actualizar Registro")
            
            if submitted:
                # Validar datos
                es_valido, mensaje_error = validar_registro(zona_edit, ubicacion_edit, tipo_edit, peso_edit)
                
                if not es_valido:
                    st.error(f"❌ {mensaje_error}")
                else:
                    # Actualizar ruta de imagen si se subió una nueva
                    ruta_imagen_edit = imagen_actual
                    if nueva_imagen is not None:
                        # Eliminar imagen anterior si existe
                        if imagen_actual and os.path.exists(imagen_actual):
                            os.remove(imagen_actual)
                        ruta_imagen_edit = guardar_imagen(nueva_imagen, registro_id)
                    
                    # Actualizar registro en el DataFrame
                    df_actualizado = df_residuos.copy()
                    mask = df_actualizado['ID'] == registro_id
                    
                    df_actualizado.loc[mask, 'Zona'] = zona_edit
                    df_actualizado.loc[mask, 'Ubicación (GPS)'] = ubicacion_edit
                    df_actualizado.loc[mask, 'Tipo de residuo'] = tipo_edit
                    df_actualizado.loc[mask, 'Peso estimado (kg)'] = peso_edit
                    df_actualizado.loc[mask, 'Fecha de registro'] = fecha_edit.strftime('%Y-%m-%d')
                    df_actualizado.loc[mask, 'Observaciones'] = observaciones_edit
                    df_actualizado.loc[mask, 'Ruta Imagen'] = ruta_imagen_edit
                    
                    # Guardar cambios
                    guardar_datos_residuos(df_actualizado)
                    st.success("✅ Registro actualizado exitosamente!")

def mostrar_eliminacion_residuos():
    """Interfaz para eliminar registros"""
    st.header("🗑️ Eliminar Registros de Residuos")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("No hay registros de residuos disponibles para eliminar.")
        return
    
    # Seleccionar registro a eliminar
    registros_lista = [f"ID: {row['ID']} - {row['Zona']} - {row['Tipo de residuo']}" for _, row in df_residuos.iterrows()]
    registro_seleccionado = st.selectbox("Seleccionar registro a eliminar:", registros_lista, key="eliminar_select")
    
    if registro_seleccionado:
        # Extraer ID del registro seleccionado
        registro_id = int(registro_seleccionado.split("ID: ")[1].split(" -")[0])
        registro_eliminar = df_residuos[df_residuos['ID'] == registro_id].iloc[0]
        
        # Mostrar información del registro
        st.warning("⚠️ Registro seleccionado para eliminar:")
        st.write(f"**ID:** {registro_eliminar['ID']}")
        st.write(f"**Zona:** {registro_eliminar['Zona']}")
        st.write(f"**Tipo de Residuo:** {registro_eliminar['Tipo de residuo']}")
        st.write(f"**Peso:** {registro_eliminar['Peso estimado (kg)']} kg")
        st.write(f"**Fecha:** {registro_eliminar['Fecha de registro']}")
        
        # Confirmación de eliminación
        if st.button("Confirmar Eliminación", type="primary"):
            # Eliminar imagen asociada si existe
            ruta_imagen = registro_eliminar.get('Ruta Imagen', '')
            if ruta_imagen and os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
            
            # Eliminar registro del DataFrame
            df_actualizado = df_residuos[df_residuos['ID'] != registro_id]
            guardar_datos_residuos(df_actualizado)
            
            st.success("✅ Registro eliminado exitosamente!")
            st.rerun()

def mostrar_reportes_estadisticas():
    """Interfaz para generar reportes y estadísticas"""
    st.header("📊 Reportes y Estadísticas")
    
    df_residuos = cargar_datos_residuos()
    
    if df_residuos.empty:
        st.info("No hay datos suficientes para generar reportes.")
        return
    
    # Métricas resumen
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_registros = len(df_residuos)
        st.metric("Total Registros", total_registros)
    
    with col2:
        peso_total = df_residuos['Peso estimado (kg)'].sum()
        st.metric("Peso Total (kg)", f"{peso_total:.1f}")
    
    with col3:
        zonas_unicas = df_residuos['Zona'].nunique()
        st.metric("Zonas Afectadas", zonas_unicas)
    
    with col4:
        tipo_mas_comun = df_residuos['Tipo de residuo'].mode()[0]
        st.metric("Tipo Más Común", tipo_mas_comun)
    
    # Gráficos de reportes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución por Tipo de Residuo")
        tipo_counts = df_residuos['Tipo de residuo'].value_counts()
        fig_bar = px.bar(
            x=tipo_counts.index,
            y=tipo_counts.values,
            title="Cantidad de Residuos por Tipo",
            labels={'x': 'Tipo de Residuo', 'y': 'Cantidad'},
            color=tipo_counts.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("Porcentaje de Residuos por Tipo")
        fig_pie = px.pie(
            values=tipo_counts.values,
            names=tipo_counts.index,
            title="Distribución Porcentual de Residuos"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Gráfico adicional: Residuos por Zona
    st.subheader("Residuos por Zona (Peso)")
    zona_peso = df_residuos.groupby('Zona')['Peso estimado (kg)'].sum().reset_index()
    fig_zona = px.bar(
        zona_peso,
        x='Zona',
        y='Peso estimado (kg)',
        title="Peso Total de Residuos por Zona",
        color='Peso estimado (kg)',
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_zona, use_container_width=True)
    
    # Exportar datos
    st.subheader("Exportar Datos")
    if st.button("Descargar Reporte en CSV"):
        csv = df_residuos.to_csv(index=False, encoding='utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"reporte_residuos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ==============================
# INTERFAZ PRINCIPAL
# ==============================

def main():
    # Inicializar archivo de residuos si no existe
    inicializar_archivo_residuos()
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🌳 Sistema de Gestión de Residuos Sólidos</h1>
        <h2>Parque La Amistad</h2>
        <p>Monitoreo, registro y análisis integral de residuos para la conservación ambiental</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para navegación
    st.sidebar.title("📊 Navegación")
    pagina = st.sidebar.selectbox(
        "Selecciona una sección:",
        [
            "Dashboard Principal", 
            "Registro de Residuos", 
            "Consulta de Residuos", 
            "Edición de Residuos", 
            "Eliminación de Residuos", 
            "Reportes y Estadísticas"
        ]
    )
    
    # Navegación entre páginas
    if pagina == "Dashboard Principal":
        mostrar_dashboard_principal()
    elif pagina == "Registro de Residuos":
        mostrar_registro_residuos()
    elif pagina == "Consulta de Residuos":
        mostrar_consulta_residuos()
    elif pagina == "Edición de Residuos":
        mostrar_edicion_residuos()
    elif pagina == "Eliminación de Residuos":
        mostrar_eliminacion_residuos()
    elif pagina == "Reportes y Estadísticas":
        mostrar_reportes_estadisticas()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🌳 Sistema de Gestión de Residuos Sólidos - Parque La Amistad</p>
        <p>Desarrollado para la conservación y monitoreo ambiental comunitario</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
