import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

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
</style>
""", unsafe_allow_html=True)

# Datos de ejemplo (simulando la base de datos)
@st.cache_data
def load_sample_data():
    # Datos de residuos
    residuos_data = {
        'ID': [1, 2, 3, 4, 5, 6, 7, 8],
        'Zona': ['Norte', 'Sur', 'Oeste', 'Este', 'Centro', 'Norte', 'Sur', 'Centro'],
        'Ubicación (GPS)': ['-8.111, -79.028', '-8.112, -79.029', '-8.113, -79.027', 
                           '-8.114, -79.026', '-8.115, -79.025', '-8.116, -79.024',
                           '-8.117, -79.023', '-8.118, -79.022'],
        'Tipo de residuo': ['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 
                           'Otros', 'Plástico', 'Orgánico', 'Papel/Cartón'],
        'Peso estimado (kg)': [5.2, 3.1, 1.8, 2.4, 0.9, 4.3, 2.7, 1.6],
        'Fecha de registro': ['2025-01-10', '2025-01-10', '2025-01-10', '2025-01-11',
                             '2025-01-11', '2025-01-12', '2025-01-12', '2025-01-13'],
        'Observaciones': ['Cerca de juegos infantiles', 'Restos de comida y hojas acumuladas',
                         'Botellas rotas junto a la banca', 'Papeles cerca de la entrada principal',
                         'Desechos varios dispersos en zona central', 'Bolsas plásticas en área verde',
                         'Residuos orgánicos en descomposición', 'Periódicos y cartones mojados']
    }
    
    # Datos de zonas críticas
    zonas_criticas_data = {
        'Código de Zona': ['Z1', 'Z2', 'Z3', 'Z4'],
        'Sector del Parque': ['Área verde con plantas', 'Césped lateral', 'Cerca de bancas', 'Zona junto a techo'],
        'Descripción de Residuos': [
            'Encuentros y restos de construcción mezclados con basura común',
            'Plásticos y papeles dispersos en el césped',
            'Botellas, envolturas y residuos de comida en bancas',
            'Desechos acumulados en el suelo a pesar de la presencia de techo cercano'
        ],
        'Tipo de Residuos Predominantes': ['Inorgánicos', 'Plásticos/Papel', 'Orgánicos/Inorgánicos', 'Mixto'],
        'Nivel de Riesgo': ['Alto', 'Medio', 'Medio', 'Bajo'],
        'Observaciones': [
            'Riesgo de proliferación de insectos y deterioro del área verde',
            'Afecta la estética y puede atraer animales',
            'Zona de tránsito de personas y animales domésticos',
            'Indica problemas en el uso adecuado de tachos de basura'
        ]
    }
    
    # Datos de encuestas
    encuestas_data = {
        'ID': range(1, 51),
        'Edad': np.random.choice(['18-25', '26-35', '36-45', '46-55', '56+'], 50),
        'Frecuencia_Visita': np.random.choice(['Diario', 'Semanal', 'Mensual', 'Ocasional'], 50),
        'Percepcion_Limpieza': np.random.choice([1, 2, 3, 4, 5], 50, p=[0.1, 0.2, 0.3, 0.3, 0.1]),
        'Dispuesto_Colaborar': np.random.choice(['Sí', 'No', 'Tal vez'], 50, p=[0.6, 0.1, 0.3]),
        'Fecha': pd.date_range('2025-01-01', periods=50, freq='D').strftime('%Y-%m-%d')
    }
    
    return (pd.DataFrame(residuos_data), 
            pd.DataFrame(zonas_criticas_data), 
            pd.DataFrame(encuestas_data))

# Cargar datos
residuos_df, zonas_df, encuestas_df = load_sample_data()

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🌳 Sistema de Gestión de Residuos</h1>
    <h2>Parque La Amistad</h2>
    <p>Monitoreo y análisis integral de residuos para la conservación ambiental</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para navegación
st.sidebar.title("📊 Navegación")
page = st.sidebar.selectbox(
    "Selecciona una sección:",
    ["Dashboard Principal", "Registro de Residuos", "Zonas Críticas", "Análisis de Encuestas", "Reportes"]
)

if page == "Dashboard Principal":
    st.header("📈 Dashboard Principal")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Residuos Registrados",
            value=len(residuos_df),
            delta=f"+{len(residuos_df[residuos_df['Fecha de registro'] >= '2025-01-12'])}"
        )
    
    with col2:
        peso_total = residuos_df['Peso estimado (kg)'].sum()
        st.metric(
            label="Peso Total (kg)",
            value=f"{peso_total:.1f}",
            delta=f"+{residuos_df[residuos_df['Fecha de registro'] >= '2025-01-12']['Peso estimado (kg)'].sum():.1f}"
        )
    
    with col3:
        st.metric(
            label="Zonas Críticas",
            value=len(zonas_df),
            delta=f"{len(zonas_df[zonas_df['Nivel de Riesgo'] == 'Alto'])} Alto Riesgo"
        )
    
    with col4:
        participacion = len(encuestas_df)
        st.metric(
            label="Encuestas Completadas",
            value=participacion,
            delta=f"+{len(encuestas_df[encuestas_df['Fecha'] >= '2025-01-10'])}"
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
    
    # Tendencias temporales
    st.subheader("Tendencia de Registros por Fecha")
    residuos_df['Fecha de registro'] = pd.to_datetime(residuos_df['Fecha de registro'])
    daily_counts = residuos_df.groupby('Fecha de registro').size().reset_index(name='Cantidad')
    
    fig_line = px.line(
        daily_counts, 
        x='Fecha de registro', 
        y='Cantidad',
        title="Registros Diarios de Residuos",
        markers=True
    )
    fig_line.update_traces(line_color='#2d5a27')
    st.plotly_chart(fig_line, use_container_width=True)

elif page == "Registro de Residuos":
    st.header("📝 Registro de Residuos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        zona_filter = st.selectbox("Filtrar por Zona:", ["Todas"] + list(residuos_df['Zona'].unique()))
    with col2:
        tipo_filter = st.selectbox("Filtrar por Tipo:", ["Todos"] + list(residuos_df['Tipo de residuo'].unique()))
    with col3:
        fecha_filter = st.date_input("Desde fecha:", value=pd.to_datetime('2025-01-10'))
    
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
        color=riesgo_counts.values,
        color_continuous_scale=['green', 'yellow', 'red']
    )
    st.plotly_chart(fig_riesgo, use_container_width=True)
    
    # Tabla de zonas críticas
    st.subheader("Detalle de Zonas Críticas")
    st.dataframe(zonas_df, use_container_width=True)

elif page == "Análisis de Encuestas":
    st.header("📊 Análisis de Encuestas")
    
    # Métricas de encuestas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Participantes", len(encuestas_df))
    with col2:
        promedio_percepcion = encuestas_df['Percepcion_Limpieza'].mean()
        st.metric("Percepción Promedio", f"{promedio_percepcion:.1f}/5")
    with col3:
        dispuestos = len(encuestas_df[encuestas_df['Dispuesto_Colaborar'] == 'Sí'])
        porcentaje = (dispuestos / len(encuestas_df)) * 100
        st.metric("Dispuestos a Colaborar", f"{porcentaje:.1f}%")
    with col4:
        visitantes_frecuentes = len(encuestas_df[encuestas_df['Frecuencia_Visita'].isin(['Diario', 'Semanal'])])
        st.metric("Visitantes Frecuentes", visitantes_frecuentes)
    
    # Gráficos de análisis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Percepción de Limpieza")
        percepcion_counts = encuestas_df['Percepcion_Limpieza'].value_counts().sort_index()
        fig_percepcion = px.bar(
            x=percepcion_counts.index, 
            y=percepcion_counts.values,
            title="Distribución de Calificaciones (1-5)",
            labels={'x': 'Calificación', 'y': 'Cantidad de Respuestas'}
        )
        st.plotly_chart(fig_percepcion, use_container_width=True)
    
    with col2:
        st.subheader("Disposición a Colaborar")
        colaborar_counts = encuestas_df['Dispuesto_Colaborar'].value_counts()
        fig_colaborar = px.pie(
            values=colaborar_counts.values, 
            names=colaborar_counts.index,
            title="¿Dispuesto a Colaborar?"
        )
        st.plotly_chart(fig_colaborar, use_container_width=True)
    
    # Análisis por edad
    st.subheader("Análisis por Grupo Etario")
    edad_percepcion = encuestas_df.groupby('Edad')['Percepcion_Limpieza'].mean().reset_index()
    fig_edad = px.bar(
        edad_percepcion, 
        x='Edad', 
        y='Percepcion_Limpieza',
        title="Percepción Promedio por Grupo de Edad"
    )
    st.plotly_chart(fig_edad, use_container_width=True)

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
    
    fecha_inicio = st.date_input("Fecha de inicio:", value=pd.to_datetime('2025-01-01'))
    fecha_fin = st.date_input("Fecha de fin:", value=pd.to_datetime('2025-01-31'))
    
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
        st.write(f"- Total participantes: {len(encuestas_df)}")
        st.write(f"- Percepción promedio: {encuestas_df['Percepcion_Limpieza'].mean():.1f}/5")
        dispuestos_pct = (len(encuestas_df[encuestas_df['Dispuesto_Colaborar'] == 'Sí']) / len(encuestas_df)) * 100
        st.write(f"- Dispuestos a colaborar: {dispuestos_pct:.1f}%")
        st.write(f"- Grupo etario más participativo: {encuestas_df['Edad'].mode()[0]}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🌳 Sistema de Gestión de Residuos - Parque La Amistad</p>
    <p>Desarrollado para la conservación y monitoreo ambiental</p>
</div>
""", unsafe_allow_html=True)

