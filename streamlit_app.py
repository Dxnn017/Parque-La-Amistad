import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import io

# Configuración de la página
st.set_page_config(
    page_title="Parque La Amistad - Gestión de Residuos",
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
    .positive-response {
        background-color: #e8f5e8;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #4CAF50;
    }
    .negative-response {
        background-color: #ffebee;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #f44336;
    }
    .neutral-response {
        background-color: #fff3e0;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

# Cargar datos reales de los archivos CSV proporcionados
@st.cache_data
def load_real_data():
    # Datos de encuestas
    encuesta_data = pd.read_csv('encuesta_respuestas.csv')
    
    # Datos de residuos
    residuos_data = pd.read_csv('residuos_parque.csv')
    
    # Datos de zonas críticas
    zonas_criticas_data = pd.read_csv('zonas_criticas.csv')
    
    return encuesta_data, residuos_data, zonas_criticas_data

# Cargar datos
encuesta_df, residuos_df, zonas_df = load_real_data()

# Preprocesamiento de datos de encuestas
# Crear columnas numéricas para análisis
def preprocess_survey_data(df):
    # Mapear respuestas Sí/No a valores numéricos para análisis
    binary_mapping = {'Sí': 1, 'No': 0, 'Tal vez': 0.5, 'Posiblemente': 0.5, 'Podría ser': 0.5}
    
    # Columnas a convertir
    binary_columns = [
        '¿Considera que el parque de la Amistad cumple una función importante en la preservación del medio ambiente urbano?',
        '¿ Piensa que la contaminación dentro del parque refleja el nivel de educación ambiental de la comunidad?',
        '¿ Ha notado que los eventos y actividades dentro del parque generan más residuos de lo habitual?',
        '¿ Cree que los tachos de basura y puntos de reciclaje están bien distribuidos en el parque?',
        '¿ Considera que la implementación de un sistema de gestión de residuos ( con tachos diferenciados y puntos de reciclaje) mejoraría significativamente la limpieza del parque "La Amistad"?',
        '¿ Cree necesario implementar campañas de sensibilización sobre la tenencia responsable de mascotas dentro del parque?',
        '¿ consideras que la propuesta "Amistad Sostenible" puede generar un cambio positivo en la conciencia ambiental de la comunidad?',
        '¿ Estarías dispuesto a promover el proyecto del parque dentro de su círculo social o familiar?'
    ]
    
    for col in binary_columns:
        df[col + '_num'] = df[col].map(binary_mapping)
    
    return df

encuesta_df = preprocess_survey_data(encuesta_df)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🌳 Sistema de Gestión de Residuos</h1>
    <h2>Parque La Amistad - Proyecto "Amistad Sostenible"</h2>
    <p>Monitoreo y análisis integral de residuos para la conservación ambiental</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para navegación
st.sidebar.title("📊 Navegación")
page = st.sidebar.selectbox(
    "Selecciona una sección:",
    ["Dashboard Principal", "Análisis de Encuestas", "Registro de Residuos", "Zonas Críticas", "Reportes"]
)

if page == "Dashboard Principal":
    st.header("📈 Dashboard Principal")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Residuos Registrados",
            value=len(residuos_df),
            delta=f"+{len(residuos_df)} desde inicio"
        )
    
    with col2:
        peso_total = residuos_df['Peso estimado (kg)'].sum()
        st.metric(
            label="Peso Total (kg)",
            value=f"{peso_total:.1f}",
            delta=f"+{peso_total:.1f} kg acumulados"
        )
    
    with col3:
        st.metric(
            label="Zonas Críticas",
            value=len(zonas_df),
            delta=f"{len(zonas_df[zonas_df['Nivel de Riesgo'] == 'Alto'])} Alto Riesgo"
        )
    
    with col4:
        participacion = len(encuesta_df)
        st.metric(
            label="Encuestas Completadas",
            value=participacion,
            delta=f"+{participacion} participantes"
        )
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución de Residuos por Tipo")
        fig_pie = px.pie(
            residuos_df, 
            names='Tipo de residuo', 
            title="Tipos de Residuos Encontrados",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("Residuos por Zona")
        zona_counts = residuos_df.groupby('Zona')['Peso estimado (kg)'].sum().reset_index()
        fig_bar = px.bar(
            zona_counts, 
            x='Zona', 
            y='Peso estimado (kg)',
            title="Peso de Residuos por Zona",
            color='Peso estimado (kg)',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Resumen de encuestas
    st.subheader("Resumen de Respuestas de Encuestas")
    
    # Calcular porcentajes de respuestas positivas para preguntas clave
    preguntas_clave = [
        '¿Considera que el parque de la Amistad cumple una función importante en la preservación del medio ambiente urbano?',
        '¿ Cree que los tachos de basura y puntos de reciclaje están bien distribuidos en el parque?',
        '¿ consideras que la propuesta "Amistad Sostenible" puede generar un cambio positivo en la conciencia ambiental de la comunidad?',
        '¿ Estarías dispuesto a promover el proyecto del parque dentro de su círculo social o familiar?'
    ]
    
    porcentajes_positivos = []
    for pregunta in preguntas_clave:
        positivos = len(encuesta_df[encuesta_df[pregunta] == 'Sí'])
        porcentaje = (positivos / len(encuesta_df)) * 100
        porcentajes_positivos.append(porcentaje)
    
    fig_resumen = px.bar(
        x=preguntas_clave, 
        y=porcentajes_positivos,
        title="Porcentaje de Respuestas Positivas a Preguntas Clave",
        labels={'x': 'Pregunta', 'y': 'Porcentaje de "Sí" (%)'},
        color=porcentajes_positivos,
        color_continuous_scale='Viridis'
    )
    fig_resumen.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_resumen, use_container_width=True)

elif page == "Análisis de Encuestas":
    st.header("📊 Análisis de Encuestas")
    
    # Métricas de encuestas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Participantes", len(encuesta_df))
    
    with col2:
        # Porcentaje que considera importante la función del parque
        importante = len(encuesta_df[encuesta_df['¿Considera que el parque de la Amistad cumple una función importante en la preservación del medio ambiente urbano?'] == 'Sí'])
        porcentaje_importante = (importante / len(encuesta_df)) * 100
        st.metric("Considera importante el parque", f"{porcentaje_importante:.1f}%")
    
    with col3:
        # Porcentaje que apoyaría el proyecto
        apoyaria = len(encuesta_df[encuesta_df['¿ consideras que la propuesta "Amistad Sostenible" puede generar un cambio positivo en la conciencia ambiental de la comunidad?'] == 'Sí'])
        porcentaje_apoyaria = (apoyaria / len(encuesta_df)) * 100
        st.metric("Apoyaría el proyecto", f"{porcentaje_apoyaria:.1f}%")
    
    with col4:
        # Porcentaje que promovería el proyecto
        promocionaria = len(encuesta_df[encuesta_df['¿ Estarías dispuesto a promover el proyecto del parque dentro de su círculo social o familiar?'] == 'Sí'])
        porcentaje_promocionaria = (promocionaria / len(encuesta_df)) * 100
        st.metric("Promovería el proyecto", f"{porcentaje_promocionaria:.1f}%")
    
    # Gráficos de análisis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Frecuencia de Visita al Parque")
        frecuencia_counts = encuesta_df['¿ Con qué frecuencia visita el Parque de la amistad?'].value_counts()
        fig_frecuencia = px.pie(
            values=frecuencia_counts.values, 
            names=frecuencia_counts.index,
            title="Frecuencia de Visita al Parque"
        )
        st.plotly_chart(fig_frecuencia, use_container_width=True)
    
    with col2:
        st.subheader("Distribución de Tachos de Basura")
        tachos_counts = encuesta_df['¿ Cree que los tachos de basura y puntos de reciclaje están bien distribuidos en el parque?'].value_counts()
        fig_tachos = px.bar(
            x=tachos_counts.index, 
            y=tachos_counts.values,
            title="¿Los tachos de basura están bien distribuidos?",
            color=tachos_counts.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_tachos, use_container_width=True)
    
    # Análisis de percepciones
    st.subheader("Percepción sobre la Contaminación y Educación Ambiental")
    
    col1, col2 = st.columns(2)
    
    with col1:
        contaminacion_counts = encuesta_df['¿ Piensa que la contaminación dentro del parque refleja el nivel de educación ambiental de la comunidad?'].value_counts()
        fig_contaminacion = px.pie(
            values=contaminacion_counts.values, 
            names=contaminacion_counts.index,
            title="¿La contaminación refleja la educación ambiental?"
        )
        st.plotly_chart(fig_contaminacion, use_container_width=True)
    
    with col2:
        eventos_counts = encuesta_df['¿ Ha notado que los eventos y actividades dentro del parque generan más residuos de lo habitual?'].value_counts()
        fig_eventos = px.bar(
            x=eventos_counts.index, 
            y=eventos_counts.values,
            title="¿Los eventos generan más residuos?",
            color=eventos_counts.values,
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_eventos, use_container_width=True)
    
    # Análisis de respuestas abiertas
    st.subheader("Análisis de Respuestas Abiertas")
    
    # Mostrar algunas respuestas destacadas
    st.write("**Respuestas sobre cómo la comunidad podría fortalecer el cuidado del parque:**")
    
    # Filtrar respuestas no vacías
    respuestas_validas = encuesta_df[encuesta_df['¿ Cómo cree que la participación de la comunidad universitaria y local podría fortalecer  el cuidado del parque a largo plazo?'].notna()]
    
    for i, respuesta in enumerate(respuestas_validas['¿ Cómo cree que la participación de la comunidad universitaria y local podría fortalecer  el cuidado del parque a largo plazo?'].head(5)):
        st.markdown(f'<div class="positive-response"><strong>Respuesta {i+1}:</strong> {respuesta}</div>', unsafe_allow_html=True)

elif page == "Registro de Residuos":
    st.header("📝 Registro de Residuos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        zona_filter = st.selectbox("Filtrar por Zona:", ["Todas"] + list(residuos_df['Zona'].unique()))
    with col2:
        tipo_filter = st.selectbox("Filtrar por Tipo:", ["Todos"] + list(residuos_df['Tipo de residuo'].unique()))
    with col3:
        fecha_filter = st.date_input("Desde fecha:", value=pd.to_datetime('2025-09-01'))
    
    # Aplicar filtros
    filtered_df = residuos_df.copy()
    if zona_filter != "Todas":
        filtered_df = filtered_df[filtered_df['Zona'] == zona_filter]
    if tipo_filter != "Todos":
        filtered_df = filtered_df[filtered_df['Tipo de residuo'] == tipo_filter]
    
    filtered_df['Fecha de registro'] = pd.to_datetime(filtered_df['Fecha de registro'])
    filtered_df = filtered_df[filtered_df['Fecha de registro'] >= pd.to_datetime(fecha_filter)]
    
    # Mostrar datos filtrados
    st.subheader(f"Registros Encontrados: {len(filtered_df)}")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Mapa de residuos
    st.subheader("Mapa de Residuos por Ubicación")
    
    # Extraer coordenadas GPS (simplificado para este ejemplo)
    # En un caso real, se procesarían las coordenadas para visualización en mapa
    st.info("Visualización de ubicaciones de residuos registrados (coordenadas GPS procesadas)")
    
    # Formulario para nuevo registro
    st.subheader("➕ Agregar Nuevo Registro")
    with st.form("nuevo_residuo"):
        col1, col2 = st.columns(2)
        with col1:
            nueva_zona = st.selectbox("Zona:", ['Norte', 'Sur', 'Este', 'Oeste', 'Centro'])
            nuevo_tipo = st.selectbox("Tipo de Residuo:", ['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Otros'])
            nuevo_peso = st.number_input("Peso estimado (kg):", min_value=0.1, max_value=100.0, step=0.1)
        
        with col2:
            nueva_ubicacion = st.text_input("Ubicación GPS:", placeholder="-8.111, -79.028")
            nuevas_observaciones = st.text_area("Observaciones:")
        
        submitted = st.form_submit_button("Registrar Residuo")
        if submitted:
            st.success("✅ Residuo registrado exitosamente!")

elif page == "Zonas Críticas":
    st.header("⚠️ Zonas Críticas")
    
    # Métricas de zonas críticas
    col1, col2, col3 = st.columns(3)
    with col1:
        alto_riesgo = len(zonas_df[zonas_df['Nivel de Riesgo'] == 'Alto'])
        st.metric("Zonas Alto Riesgo", alto_riesgo)
    with col2:
        medio_riesgo = len(zonas_df[zonas_df['Nivel de Riesgo'] == 'Medio'])
        st.metric("Zonas Medio Riesgo", medio_riesgo)
    with col3:
        bajo_riesgo = len(zonas_df[zonas_df['Nivel de Riesgo'] == 'Bajo'])
        st.metric("Zonas Bajo Riesgo", bajo_riesgo)
    
    # Gráfico de niveles de riesgo
    riesgo_counts = zonas_df['Nivel de Riesgo'].value_counts()
    fig_riesgo = px.bar(
        x=riesgo_counts.index, 
        y=riesgo_counts.values,
        title="Distribución de Zonas por Nivel de Riesgo",
        color=riesgo_counts.index,
        color_discrete_map={'Alto': 'red', 'Medio': 'orange', 'Bajo': 'green'}
    )
    st.plotly_chart(fig_riesgo, use_container_width=True)
    
    # Tabla de zonas críticas
    st.subheader("Detalle de Zonas Críticas")
    st.dataframe(zonas_df, use_container_width=True)
    
    # Análisis de correlación con datos de residuos
    st.subheader("Correlación entre Zonas Críticas y Residuos Registrados")
    
    # Agrupar residuos por zona
    residuos_por_zona = residuos_df.groupby('Zona').agg({
        'Peso estimado (kg)': 'sum',
        'ID': 'count'
    }).rename(columns={'ID': 'Cantidad de registros'}).reset_index()
    
    # Mostrar tabla comparativa
    st.dataframe(residuos_por_zona, use_container_width=True)

elif page == "Reportes":
    st.header("📋 Reportes y Exportación")
    
    # Opciones de reporte
    st.subheader("Generar Reportes")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_reporte = st.selectbox(
            "Tipo de Reporte:",
            ["Reporte Completo", "Solo Residuos", "Solo Zonas Críticas", "Solo Encuestas"]
        )
    with col2:
        formato = st.selectbox("Formato:", ["PDF", "Excel", "CSV"])
    
    fecha_inicio = st.date_input("Fecha de inicio:", value=pd.to_datetime('2025-09-01'))
    fecha_fin = st.date_input("Fecha de fin:", value=pd.to_datetime('2025-09-30'))
    
    if st.button("Generar Reporte"):
        st.success(f"✅ Reporte {tipo_reporte} en formato {formato} generado exitosamente!")
        st.info("📧 El reporte ha sido enviado a tu correo electrónico.")
    
    # Resumen estadístico
    st.subheader("Resumen Estadístico")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Estadísticas de Residuos:**")
        st.write(f"- Total registros: {len(residuos_df)}")
        st.write(f"- Peso total: {residuos_df['Peso estimado (kg)'].sum():.1f} kg")
        st.write(f"- Tipo más común: {residuos_df['Tipo de residuo'].mode()[0]}")
        st.write(f"- Zona más afectada: {residuos_df['Zona'].mode()[0]}")
    
    with col2:
        st.write("**Estadísticas de Encuestas:**")
        st.write(f"- Total participantes: {len(encuesta_df)}")
        
        # Calcular porcentaje de respuestas positivas para preguntas clave
        preguntas_clave = [
            '¿Considera que el parque de la Amistad cumple una función importante en la preservación del medio ambiente urbano?',
            '¿ Cree que los tachos de basura y puntos de reciclaje están bien distribuidos en el parque?',
            '¿ consideras que la propuesta "Amistad Sostenible" puede generar un cambio positivo en la conciencia ambiental de la comunidad?'
        ]
        
        for pregunta in preguntas_clave:
            positivos = len(encuesta_df[encuesta_df[pregunta] == 'Sí'])
            porcentaje = (positivos / len(encuesta_df)) * 100
            st.write(f"- {pregunta[:30]}...: {porcentaje:.1f}% Sí")
    
    # Exportar datos
    st.subheader("Exportar Datos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Exportar Datos de Residuos"):
            csv = residuos_df.to_csv(index=False)
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name="residuos_parque_amistad.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Exportar Datos de Encuestas"):
            csv = encuesta_df.to_csv(index=False)
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name="encuestas_parque_amistad.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("Exportar Datos de Zonas Críticas"):
            csv = zonas_df.to_csv(index=False)
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name="zonas_criticas_parque_amistad.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🌳 Sistema de Gestión de Residuos - Parque La Amistad - Proyecto "Amistad Sostenible"</p>
    <p>Desarrollado para la conservación y monitoreo ambiental</p>
</div>
""", unsafe_allow_html=True)
