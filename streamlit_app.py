import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, date
from PIL import Image
import re
import logging

# ==============================
# CONFIGURACIÓN BÁSICA
# ==============================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Parque La Amistad - Gestión de Residuos",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

class Config:
    DATASET_DIR = "dataset"
    RESIDUOS_CSV = os.path.join(DATASET_DIR, "residuos_parque.csv")
    IMAGES_DIR = os.path.join(DATASET_DIR, "evidencias")
    ZONAS_VALIDAS = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']
    TIPOS_RESIDUO = ['Plástico', 'Orgánico', 'Vidrio/Metal', 'Papel/Cartón', 'Textil', 'Electrónico', 'Peligroso', 'Otros']
    PESO_MIN = 0.1
    PESO_MAX = 1000.0

os.makedirs(Config.DATASET_DIR, exist_ok=True)
os.makedirs(Config.IMAGES_DIR, exist_ok=True)

# ==============================
# FUNCIONES DE DATOS
# ==============================

def inicializar_csv():
    if not os.path.exists(Config.RESIDUOS_CSV):
        df = pd.DataFrame(columns=['ID','Zona','Ubicación (GPS)','Tipo de residuo','Peso estimado (kg)','Fecha de registro','Observaciones','Ruta Imagen','Estado'])
        df.to_csv(Config.RESIDUOS_CSV, index=False)

def cargar_datos():
    if not os.path.exists(Config.RESIDUOS_CSV):
        inicializar_csv()
    return pd.read_csv(Config.RESIDUOS_CSV)

def guardar_datos(df):
    df.to_csv(Config.RESIDUOS_CSV, index=False)

# ==============================
# FUNCIONES DE CRUD
# ==============================

def registrar_residuo():
    st.header("📝 Registro de Residuos")
    df = cargar_datos()
    with st.form("form_registro"):
        zona = st.selectbox("Zona", Config.ZONAS_VALIDAS)
        ubicacion = st.text_input("Ubicación (GPS)")
        tipo = st.selectbox("Tipo de Residuo", Config.TIPOS_RESIDUO)
        peso = st.number_input("Peso estimado (kg)", min_value=Config.PESO_MIN, max_value=Config.PESO_MAX, value=1.0)
        fecha = st.date_input("Fecha", value=datetime.now().date())
        obs = st.text_area("Observaciones")
        img = st.file_uploader("Imagen", type=["jpg","png","jpeg"])

        submit = st.form_submit_button("Registrar")
        if submit:
            nuevo_id = df['ID'].max()+1 if not df.empty else 1
            ruta_img = ""
            if img:
                ruta_img = os.path.join(Config.IMAGES_DIR, f"residuo_{nuevo_id}_{img.name}")
                with open(ruta_img, "wb") as f:
                    f.write(img.getbuffer())
            nuevo = {
                'ID': nuevo_id,
                'Zona': zona,
                'Ubicación (GPS)': ubicacion,
                'Tipo de residuo': tipo,
                'Peso estimado (kg)': peso,
                'Fecha de registro': fecha,
                'Observaciones': obs,
                'Ruta Imagen': ruta_img,
                'Estado': 'Activo'
            }
            df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
            guardar_datos(df)
            st.success("Residuo registrado con éxito ✅")

def consultar_residuos():
    st.header("🔍 Consulta de Residuos")
    df = cargar_datos()
    if df.empty:
        st.info("No hay registros.")
        return
    st.dataframe(df)

def editar_residuo():
    st.header("✏️ Edición de Residuos")
    df = cargar_datos()
    if df.empty:
        st.warning("No hay registros.")
        return
    id_sel = st.selectbox("Seleccione ID", df['ID'])
    registro = df[df['ID']==id_sel].iloc[0]
    zona = st.selectbox("Zona", Config.ZONAS_VALIDAS, index=Config.ZONAS_VALIDAS.index(registro['Zona']))
    tipo = st.selectbox("Tipo", Config.TIPOS_RESIDUO, index=Config.TIPOS_RESIDUO.index(registro['Tipo de residuo']))
    peso = st.number_input("Peso", min_value=Config.PESO_MIN, max_value=Config.PESO_MAX, value=float(registro['Peso estimado (kg)']))
    obs = st.text_area("Observaciones", value=registro['Observaciones'])

    if st.button("Guardar cambios"):
        df.loc[df['ID']==id_sel, ['Zona','Tipo de residuo','Peso estimado (kg)','Observaciones']] = [zona,tipo,peso,obs]
        guardar_datos(df)
        st.success("Registro actualizado ✅")

def eliminar_residuo():
    st.header("🗑️ Eliminación de Residuos")
    df = cargar_datos()
    if df.empty:
        st.warning("No hay registros.")
        return
    id_sel = st.selectbox("Seleccione ID", df['ID'])
    if st.button("Confirmar eliminación"):
        df.loc[df['ID']==id_sel,'Estado'] = 'Inactivo'
        guardar_datos(df)
        st.success("Registro marcado como eliminado ❌")

# ==============================
# DASHBOARD SIMPLE
# ==============================

def dashboard():
    st.header("📊 Dashboard")
    df = cargar_datos()
    if df.empty:
        st.info("No hay datos aún.")
        return
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names='Tipo de residuo', title='Distribución por Tipo')
        st.plotly_chart(fig)
    with col2:
        fig = px.bar(df, x='Zona', y='Peso estimado (kg)', title='Peso por Zona')
        st.plotly_chart(fig)

# ==============================
# MAIN APP
# ==============================

def main():
    inicializar_csv()
    st.sidebar.title("Navegación")
    page = st.sidebar.radio("Ir a:", ["Dashboard","Registrar","Consultar","Editar","Eliminar"])
    if page=="Dashboard":
        dashboard()
    elif page=="Registrar":
        registrar_residuo()
    elif page=="Consultar":
        consultar_residuos()
    elif page=="Editar":
        editar_residuo()
    elif page=="Eliminar":
        eliminar_residuo()

if __name__ == "__main__":
    main()
